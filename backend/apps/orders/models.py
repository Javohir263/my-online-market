"""
Order + OrderItem models.

**Snapshot pattern**: OrderItem'da product_name_snapshot, product_image_snapshot,
price_at_purchase saqlanadi — kelajakda mahsulot o'zgartirilsa ham, buyurtma
ma'lumotlari tarixiy ko'rinishda qoladi.

shipping_address ham `JSONField` snapshot — user manzili o'zgargandan keyin
ham, eski buyurtmada eski manzil saqlanadi (uchun yetkazib berishga muhim).
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel, UUIDModel


# =============================================================================
# OrderNumberSequence — atomic counter per year
# =============================================================================
class OrderNumberSequence(models.Model):
    """Yiliga buyurtma raqami avtomatik o'sib boradi.

    Format: `MOM-2026-000123`. Race-free chunki SELECT FOR UPDATE bilan
    ishlatamiz (services.py'da).
    """

    year = models.PositiveSmallIntegerField(unique=True)
    last_number = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("order number sequence")
        verbose_name_plural = _("order number sequences")

    def __str__(self) -> str:
        return f"{self.year}: {self.last_number}"


# =============================================================================
# Order
# =============================================================================
class Order(UUIDModel, TimeStampedModel):
    """Buyurtma — to'liq tarixiy snapshot."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        CONFIRMED = "confirmed", _("Confirmed")
        SHIPPED = "shipped", _("Shipped")
        DELIVERED = "delivered", _("Delivered")
        CANCELLED = "cancelled", _("Cancelled")

    number = models.CharField(
        _("order number"),
        max_length=32,
        unique=True,
        db_index=True,
        help_text=_("Format: MOM-2026-000123"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # --- Pricing ---
    currency = models.CharField(_("currency"), max_length=3, default="UZS")
    subtotal = models.DecimalField(
        _("subtotal"),
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    shipping_cost = models.DecimalField(
        _("shipping cost"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    discount_amount = models.DecimalField(
        _("discount amount"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total = models.DecimalField(
        _("total"),
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )

    # --- Shipping address snapshot (JSON) ---
    shipping_address = models.JSONField(
        _("shipping address (snapshot)"),
        help_text=_("Address modeli'dan snapshot olingan JSON."),
    )

    customer_note = models.TextField(
        _("customer note"), blank=True, default=""
    )

    # --- Coupon (B10'da Coupon model bilan ulanadi) ---
    coupon = models.ForeignKey(
        "promotions.Coupon",
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
    )

    # --- Status timestamps ---
    confirmed_at = models.DateTimeField(_("confirmed at"), null=True, blank=True)
    shipped_at = models.DateTimeField(_("shipped at"), null=True, blank=True)
    delivered_at = models.DateTimeField(_("delivered at"), null=True, blank=True)
    cancelled_at = models.DateTimeField(_("cancelled at"), null=True, blank=True)
    cancel_reason = models.TextField(
        _("cancel reason"), blank=True, default=""
    )

    # --- Idempotency tracking ---
    idempotency_key = models.CharField(
        _("idempotency key"),
        max_length=64,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        help_text=_(
            "Frontend X-Idempotency-Key header — bir xil key bilan duplikat "
            "checkout oldini olish."
        ),
    )

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(total__gte=0),
                name="order_total_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return self.number

    @property
    def is_cancellable(self) -> bool:
        """Faqat pending va confirmed status'lardagi buyurtma bekor qilinishi mumkin."""
        return self.status in (self.Status.PENDING, self.Status.CONFIRMED)

    @property
    def is_active(self) -> bool:
        return self.status not in (self.Status.CANCELLED,)


# =============================================================================
# OrderItem — snapshot pattern
# =============================================================================
class OrderItem(models.Model):
    """Buyurtma elementi. Snapshot pattern: product/variant FK saqlanadi
    (relational), lekin name/image/price ham snapshot sifatida saqlanadi
    (tarixiy ko'rinish)."""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )

    # Live references (history tracking uchun)
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="+",
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )
    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.PROTECT,
        related_name="+",
        help_text=_(
            "Multi-vendor extensibility: har item o'z vendor'iga tegishli "
            "bo'lishi mumkin (kelajakda)."
        ),
    )

    quantity = models.PositiveIntegerField(_("quantity"))
    price_at_purchase = models.DecimalField(
        _("price at purchase"), max_digits=12, decimal_places=2
    )

    # Snapshots — mahsulot o'zgartirilsa ham buyurtmada eski qoladi
    product_name_snapshot = models.CharField(
        _("product name (snapshot)"), max_length=200
    )
    product_sku_snapshot = models.CharField(
        _("product SKU (snapshot)"), max_length=64
    )
    variant_label_snapshot = models.CharField(
        _("variant label (snapshot)"),
        max_length=200,
        blank=True,
        default="",
        help_text=_("Masalan: 'Red / XL'"),
    )
    product_image_snapshot = models.URLField(
        _("product image URL (snapshot)"),
        max_length=500,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("order item")
        verbose_name_plural = _("order items")
        ordering = ("id",)
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["vendor", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.product_name_snapshot} × {self.quantity}"

    @property
    def line_total(self) -> Decimal:
        return self.price_at_purchase * self.quantity
