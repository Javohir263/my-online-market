"""
Cart + CartItem models.

Cart anonim (`session_key`) yoki authenticated (`user`) bo'lishi mumkin —
ikkalasi ham emas, bittasi shart (CheckConstraint).
"""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Sum
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class Cart(TimeStampedModel):
    """Foydalanuvchi yoki anonim sessiyaning savatchasi."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        null=True,
        blank=True,
    )
    session_key = models.CharField(
        _("session key"),
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
        unique=True,
    )

    coupon = models.ForeignKey(
        "promotions.Coupon",
        on_delete=models.SET_NULL,
        related_name="carts",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("cart")
        verbose_name_plural = _("carts")
        constraints = [
            # Bittasi to'lib turishi shart — ikkalasi NULL bo'lmaydi
            models.CheckConstraint(
                condition=(
                    Q(user__isnull=False) | Q(session_key__isnull=False)
                ),
                name="cart_owner_required",
            ),
        ]

    def __str__(self) -> str:
        owner = self.user.email if self.user_id else f"anon:{self.session_key}"
        return f"Cart({owner})"

    # --- Aggregates -------------------------------------------------------
    @property
    def items_count(self) -> int:
        return self.items.aggregate(total=Sum("quantity"))["total"] or 0

    @property
    def subtotal(self) -> Decimal:
        total = Decimal("0.00")
        for item in self.items.all():
            total += item.line_total
        return total

    @property
    def discount_amount(self) -> Decimal:
        """Coupon orqali chegirma. Coupon yo'q bo'lsa 0."""
        if not self.coupon_id:
            return Decimal("0.00")
        from apps.promotions.services import calc_discount

        try:
            return calc_discount(self.coupon, self.subtotal)
        except Exception:
            return Decimal("0.00")

    @property
    def total(self) -> Decimal:
        return self.subtotal - self.discount_amount


class CartItem(TimeStampedModel):
    """Savatchadagi mahsulot. UNIQUE(cart, product, variant) — duplikat yo'q."""

    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        "catalog.Product", on_delete=models.CASCADE, related_name="+"
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="+",
    )
    quantity = models.PositiveIntegerField(_("quantity"), default=1)

    # Snapshot — savatchaga qo'shilgan paytdagi narx (price-change protection)
    price_snapshot = models.DecimalField(
        _("price snapshot"),
        max_digits=12,
        decimal_places=2,
        help_text=_("Mahsulot savatchaga qo'shilgan paytdagi narx."),
    )

    class Meta:
        verbose_name = _("cart item")
        verbose_name_plural = _("cart items")
        ordering = ("-created_at",)
        constraints = [
            # variant=null bo'lganda ham UNIQUE ishlashi uchun ikkita constraint
            models.UniqueConstraint(
                fields=["cart", "product", "variant"],
                name="cart_item_unique_with_variant",
                condition=Q(variant__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="cart_item_unique_no_variant",
                condition=Q(variant__isnull=True),
            ),
            models.CheckConstraint(
                condition=Q(quantity__gte=1),
                name="cart_item_qty_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.product.name} × {self.quantity}"

    @property
    def line_total(self) -> Decimal:
        return self.price_snapshot * self.quantity

    @property
    def available_stock(self) -> int:
        if self.variant_id is not None:
            return self.variant.stock_quantity
        return self.product.stock_quantity

    def clean(self) -> None:
        if self.quantity > self.available_stock:
            raise ValidationError(
                _("Talab qilingan miqdor stok'dan ko'p.")
            )
