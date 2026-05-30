"""
Cart service layer — view'lar bu yerdagi funksiyalarni chaqiradi.

Senior nuanslar:
- Anonim user → session_key based cart (Django sessions middleware).
- Authenticated user → OneToOne `cart` (har user'ga bittadan).
- Login paytida anon cart → user cart MERGE (signal yoki view orqali).
- Stock check har add/update'da.
- Atomic transactions har modifikatsiya uchun.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.cart.exceptions import (
    InsufficientStock,
    ProductInactive,
)
from apps.cart.models import Cart, CartItem
from apps.catalog.models import Product, ProductVariant


# =============================================================================
# Cart resolver — anon yoki auth
# =============================================================================
def _ensure_session_key(request) -> str:
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def resolve_cart(request) -> Cart:
    """Mavjud cart'ni qaytaradi yoki yaratadi.

    Authenticated → user cart. Anon → session-based cart.
    """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    session_key = _ensure_session_key(request)
    cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart


# =============================================================================
# Item operations — atomic
# =============================================================================
def _check_stock(stock: int, requested: int) -> None:
    if requested > stock:
        raise InsufficientStock()


def _resolve_price(product: Product, variant: ProductVariant | None) -> Decimal:
    if variant is not None:
        return variant.final_price
    return product.current_price


@transaction.atomic
def add_item(
    cart: Cart,
    *,
    product_id,
    variant_id=None,
    quantity: int = 1,
) -> CartItem:
    """Idempotent — agar shu (product, variant) juftlik allaqachon bor bo'lsa,
    quantity'ni `+quantity` qiladi. Stock check'dan o'tadi."""

    product = get_object_or_404(
        Product.objects.select_for_update(), pk=product_id, is_active=True
    )
    if not product.is_active:
        raise ProductInactive()

    variant: ProductVariant | None = None
    if variant_id is not None:
        variant = get_object_or_404(
            ProductVariant.objects.select_for_update(),
            pk=variant_id,
            product=product,
            is_active=True,
        )

    available = (
        variant.stock_quantity if variant is not None else product.stock_quantity
    )

    item = (
        cart.items.select_for_update()
        .filter(product=product, variant=variant)
        .first()
    )
    new_qty = (item.quantity if item else 0) + quantity
    _check_stock(available, new_qty)

    price = _resolve_price(product, variant)

    if item is None:
        item = CartItem.objects.create(
            cart=cart,
            product=product,
            variant=variant,
            quantity=quantity,
            price_snapshot=price,
        )
    else:
        item.quantity = new_qty
        # price_snapshot original — narx fragmentini saqlash
        item.save(update_fields=["quantity"])

    return item


@transaction.atomic
def update_quantity(item: CartItem, quantity: int) -> CartItem:
    if quantity < 1:
        raise InsufficientStock()
    available = item.available_stock
    _check_stock(available, quantity)
    item.quantity = quantity
    item.save(update_fields=["quantity"])
    return item


@transaction.atomic
def remove_item(item: CartItem) -> None:
    item.delete()


@transaction.atomic
def clear_cart(cart: Cart) -> None:
    cart.items.all().delete()


# =============================================================================
# Merge — anon cart → user cart (login paytida)
# =============================================================================
@transaction.atomic
def merge_carts(*, anon_cart: Cart, user_cart: Cart) -> Cart:
    """Anonim cart elementlarini user cart'iga ko'chiradi.

    - Bir xil (product, variant) juftlik bo'lsa quantities qo'shiladi.
    - Stock cheklovi bo'lsa, user cart'da bor bo'lgan max quantity'ga cheklanadi.
    - Anon cart so'ngida o'chiriladi.
    """
    if anon_cart.pk == user_cart.pk:
        return user_cart

    for anon_item in anon_cart.items.select_related("product", "variant"):
        existing = user_cart.items.filter(
            product=anon_item.product, variant=anon_item.variant
        ).first()
        if existing:
            available = anon_item.available_stock
            new_qty = min(existing.quantity + anon_item.quantity, available)
            existing.quantity = new_qty
            existing.save(update_fields=["quantity"])
        else:
            # Move
            anon_item.cart = user_cart
            anon_item.save(update_fields=["cart"])

    anon_cart.delete()
    return user_cart


def merge_on_login(request, user) -> Cart | None:
    """user_logged_in signal'ida chaqiriladi.

    Anon cart bo'lsa, user cart bilan birlashtiradi.
    """
    session_key = request.session.session_key
    if not session_key:
        return None

    anon_cart = Cart.objects.filter(session_key=session_key).first()
    if anon_cart is None:
        return None

    user_cart, _ = Cart.objects.get_or_create(user=user)
    return merge_carts(anon_cart=anon_cart, user_cart=user_cart)
