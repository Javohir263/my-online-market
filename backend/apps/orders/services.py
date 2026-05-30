"""
Orders service layer — eng kritik biznes logika.

Senior nuanslar:
- `SELECT FOR UPDATE` on Product/Variant — race-free stock decrement
- Atomic transaction butun checkout uchun — partial failure yo'q
- Idempotency key: cache'da saqlanadi (TTL 24h), takroriy POST oldini oladi
- Snapshot pattern: product_name/image/price snapshot orderItem'da
- Order number: per-year atomic counter (SELECT FOR UPDATE)
- FSM: status transition validation
- Stock restore on cancel
"""

from __future__ import annotations

import logging
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Address
from apps.cart.models import Cart, CartItem
from apps.catalog.models import Product, ProductVariant
from apps.orders.exceptions import (
    EmptyCart,
    InvalidStatusTransition,
    OrderNotCancellable,
    StockChanged,
)
from apps.orders.models import Order, OrderItem, OrderNumberSequence
from apps.vendors.models import Vendor

logger = logging.getLogger(__name__)

IDEMPOTENCY_CACHE_PREFIX = "orders:idem:"
IDEMPOTENCY_TTL = 60 * 60 * 24  # 24h


# =============================================================================
# Order number — per year, atomic
# =============================================================================
def generate_order_number(year: int | None = None) -> str:
    """`MOM-2026-000123` — atomic counter per year via SELECT FOR UPDATE."""
    year = year or timezone.now().year
    seq, _created = OrderNumberSequence.objects.select_for_update().get_or_create(
        year=year
    )
    seq.last_number += 1
    seq.save(update_fields=["last_number"])
    return f"MOM-{year}-{seq.last_number:06d}"


# =============================================================================
# FSM — Order status transitions
# =============================================================================
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    Order.Status.PENDING: {Order.Status.CONFIRMED, Order.Status.CANCELLED},
    Order.Status.CONFIRMED: {Order.Status.SHIPPED, Order.Status.CANCELLED},
    Order.Status.SHIPPED: {Order.Status.DELIVERED},
    Order.Status.DELIVERED: set(),
    Order.Status.CANCELLED: set(),
}

STATUS_TIMESTAMP_FIELD = {
    Order.Status.CONFIRMED: "confirmed_at",
    Order.Status.SHIPPED: "shipped_at",
    Order.Status.DELIVERED: "delivered_at",
    Order.Status.CANCELLED: "cancelled_at",
}


@transaction.atomic
def transition(
    order: Order,
    new_status: str,
    *,
    cancel_reason: str = "",
) -> Order:
    """FSM transition with timestamp + cancel-time stock restore."""
    current = order.status
    if new_status not in ALLOWED_TRANSITIONS.get(current, set()):
        raise InvalidStatusTransition()

    update_fields = ["status"]
    order.status = new_status

    ts_field = STATUS_TIMESTAMP_FIELD.get(new_status)
    if ts_field:
        setattr(order, ts_field, timezone.now())
        update_fields.append(ts_field)

    if new_status == Order.Status.CANCELLED:
        order.cancel_reason = cancel_reason or "Cancelled by user."
        update_fields.append("cancel_reason")
        _restore_stock_on_cancel(order)

    order.save(update_fields=update_fields)
    return order


def _restore_stock_on_cancel(order: Order) -> None:
    """Bekor qilingan buyurtma elementlari stokka qaytadi."""
    for item in order.items.select_related("product", "variant"):
        if item.variant_id is not None:
            ProductVariant.objects.filter(pk=item.variant_id).update(
                stock_quantity=models_F("stock_quantity") + item.quantity
            )
            # Trigger product stock denorm later if needed
        else:
            Product.objects.filter(pk=item.product_id).update(
                stock_quantity=models_F("stock_quantity") + item.quantity,
            )
            # is_in_stock flag'ni ham yangilash
            Product.objects.filter(
                pk=item.product_id, stock_quantity__gt=0
            ).update(is_in_stock=True)


# Helper because `from django.db.models import F` shadow above
def models_F(name):
    from django.db.models import F as _F

    return _F(name)


# =============================================================================
# Cancel — public API
# =============================================================================
def cancel_order(order: Order, reason: str = "") -> Order:
    if not order.is_cancellable:
        raise OrderNotCancellable()
    return transition(order, Order.Status.CANCELLED, cancel_reason=reason)


# =============================================================================
# Checkout — main entry point
# =============================================================================
@transaction.atomic
def checkout_cart(
    *,
    user,
    cart: Cart,
    shipping_address: Address | dict,
    customer_note: str = "",
    idempotency_key: str | None = None,
) -> Order:
    """Cart'ni Order'ga konvertatsiya qiladi (atomic, race-free).

    Bosqichlar:
        1. Idempotency check (cache → DB)
        2. Cart bo'sh emasligini tekshirish
        3. Har item uchun SELECT FOR UPDATE — stock dec
        4. Order + OrderItem'lar yaratish (snapshots)
        5. Cart clear
        6. Idempotency cache'ga saqlash
    """

    # 1. Idempotency check
    if idempotency_key:
        cached_order_id = cache.get(IDEMPOTENCY_CACHE_PREFIX + idempotency_key)
        if cached_order_id:
            existing = Order.objects.filter(id=cached_order_id).first()
            if existing:
                return existing
        # DB-level check (cache evicted)
        existing = Order.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            cache.set(
                IDEMPOTENCY_CACHE_PREFIX + idempotency_key,
                str(existing.id),
                IDEMPOTENCY_TTL,
            )
            return existing

    # 2. Cart'ni qattiq tekshirish
    items = list(
        cart.items.select_related("product", "variant").all()
    )
    if not items:
        raise EmptyCart()

    # 3. Lock + stock dec atomic
    subtotal = Decimal("0.00")
    order_items_data: list[dict] = []
    default_vendor = Vendor.objects.get_default()

    for item in items:
        # Lock product
        product = Product.objects.select_for_update().get(pk=item.product_id)
        variant = None
        if item.variant_id is not None:
            variant = ProductVariant.objects.select_for_update().get(
                pk=item.variant_id
            )

        available = (
            variant.stock_quantity if variant else product.stock_quantity
        )
        if available < item.quantity:
            raise StockChanged()

        # Dec stock
        if variant:
            variant.stock_quantity -= item.quantity
            variant.save(update_fields=["stock_quantity"])
        else:
            product.stock_quantity -= item.quantity
            if product.stock_quantity == 0:
                product.is_in_stock = False
                product.save(update_fields=["stock_quantity", "is_in_stock"])
            else:
                product.save(update_fields=["stock_quantity"])

        # Snapshots
        primary_image = (
            product.images.filter(is_primary=True).first()
            or product.images.order_by("order").first()
        )
        image_url = primary_image.image.url if primary_image and primary_image.image else ""

        variant_label = ""
        if variant:
            parts = [p for p in (variant.color, variant.size) if p]
            variant_label = " / ".join(parts)

        price = item.price_snapshot  # cart snapshot
        subtotal += price * item.quantity

        order_items_data.append(
            {
                "product": product,
                "variant": variant,
                "vendor": product.vendor or default_vendor,
                "quantity": item.quantity,
                "price_at_purchase": price,
                "product_name_snapshot": product.name,
                "product_sku_snapshot": product.sku,
                "variant_label_snapshot": variant_label,
                "product_image_snapshot": image_url,
            }
        )

    # 4. Address snapshot
    if isinstance(shipping_address, Address):
        addr_data = _address_to_dict(shipping_address)
    else:
        addr_data = dict(shipping_address)

    # 5. Order yaratish
    number = generate_order_number()
    total = subtotal  # shipping + discount B10'da hisoblanadi
    order = Order.objects.create(
        number=number,
        user=user,
        status=Order.Status.PENDING,
        currency=getattr(settings, "DEFAULT_CURRENCY", "UZS"),
        subtotal=subtotal,
        shipping_cost=Decimal("0.00"),
        discount_amount=Decimal("0.00"),
        total=total,
        shipping_address=addr_data,
        customer_note=customer_note,
        idempotency_key=idempotency_key or None,
    )

    OrderItem.objects.bulk_create(
        [OrderItem(order=order, **data) for data in order_items_data]
    )

    # 6. Cart clear
    cart.items.all().delete()

    # 7. Cache idempotency
    if idempotency_key:
        cache.set(
            IDEMPOTENCY_CACHE_PREFIX + idempotency_key,
            str(order.id),
            IDEMPOTENCY_TTL,
        )

    logger.info(
        "Order created: number=%s user=%s total=%s",
        order.number,
        user.email,
        total,
    )
    return order


def _address_to_dict(address: Address) -> dict:
    return {
        "recipient_name": address.recipient_name,
        "recipient_phone": address.recipient_phone,
        "region": address.region,
        "city": address.city,
        "district": address.district,
        "street": address.street,
        "building": address.building,
        "apartment": address.apartment,
        "postal_code": address.postal_code,
        "landmark": address.landmark,
    }
