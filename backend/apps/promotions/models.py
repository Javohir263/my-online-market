"""
Promotions models — Banner + Coupon + CouponUsage.
"""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


# =============================================================================
# Banner — homepage / sidebar / footer carousels
# =============================================================================
class Banner(TimeStampedModel):
    class Position(models.TextChoices):
        HERO = "hero", _("Hero (asosiy)")
        SIDEBAR = "sidebar", _("Sidebar")
        CATEGORY = "category", _("Category")
        FOOTER = "footer", _("Footer")

    title = models.CharField(_("title"), max_length=200, blank=True, default="")
    subtitle = models.CharField(
        _("subtitle"), max_length=300, blank=True, default=""
    )
    image = models.ImageField(_("image"), upload_to="banners/")
    link = models.CharField(
        _("link"),
        max_length=500,
        blank=True,
        default="",
        help_text=_("Internal slug yoki to'liq URL"),
    )

    position = models.CharField(
        _("position"),
        max_length=20,
        choices=Position.choices,
        default=Position.HERO,
        db_index=True,
    )
    order = models.PositiveIntegerField(_("display order"), default=0)
    is_active = models.BooleanField(_("active"), default=True, db_index=True)

    valid_from = models.DateTimeField(_("valid from"), null=True, blank=True)
    valid_to = models.DateTimeField(_("valid to"), null=True, blank=True)

    class Meta:
        verbose_name = _("banner")
        verbose_name_plural = _("banners")
        ordering = ("position", "order")
        indexes = [
            models.Index(fields=["position", "is_active", "order"]),
        ]

    def __str__(self) -> str:
        return f"{self.position}: {self.title or '(no title)'}"

    @property
    def is_visible_now(self) -> bool:
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        return True


# =============================================================================
# Coupon — full logic
# =============================================================================
class Coupon(TimeStampedModel):
    class Type(models.TextChoices):
        PERCENTAGE = "percentage", _("Percentage")
        FIXED = "fixed", _("Fixed amount")

    code = models.CharField(
        _("code"), max_length=64, unique=True, db_index=True
    )
    type = models.CharField(
        _("type"),
        max_length=20,
        choices=Type.choices,
        default=Type.PERCENTAGE,
    )
    value = models.DecimalField(
        _("value"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=_("Percentage'da 0..100, fixed'da UZS miqdori"),
    )

    # --- Constraints ---
    min_order_amount = models.DecimalField(
        _("min order amount"),
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=_("Buyurtma summasi shu qiymatdan yuqori bo'lishi kerak"),
    )
    max_discount = models.DecimalField(
        _("max discount (percentage type only)"),
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        help_text=_("Percentage uchun chegirma cap (NULL = chegirma yo'q)"),
    )

    # --- Usage ---
    usage_limit = models.PositiveIntegerField(
        _("global usage limit"),
        null=True,
        blank=True,
        help_text=_("NULL = cheksiz"),
    )
    per_user_limit = models.PositiveSmallIntegerField(
        _("per-user limit"),
        default=1,
        help_text=_("Har user qancha marta ishlatishi mumkin"),
    )
    used_count = models.PositiveIntegerField(_("used count"), default=0)

    # --- Validity window ---
    valid_from = models.DateTimeField(_("valid from"), null=True, blank=True)
    valid_to = models.DateTimeField(_("valid to"), null=True, blank=True)
    is_active = models.BooleanField(_("active"), default=True, db_index=True)

    class Meta:
        verbose_name = _("coupon")
        verbose_name_plural = _("coupons")
        ordering = ("-created_at",)
        constraints = [
            models.CheckConstraint(
                condition=Q(value__gte=0),
                name="coupon_value_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return self.code

    @property
    def is_within_window(self) -> bool:
        now = timezone.now()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        return True

    @property
    def is_globally_available(self) -> bool:
        if self.usage_limit is None:
            return True
        return self.used_count < self.usage_limit


# =============================================================================
# CouponUsage — per-user, per-order tracking
# =============================================================================
class CouponUsage(models.Model):
    coupon = models.ForeignKey(
        Coupon, on_delete=models.CASCADE, related_name="usages"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coupon_usages",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="coupon_usages",
    )
    used_at = models.DateTimeField(auto_now_add=True, db_index=True)
    discount_applied = models.DecimalField(
        _("discount applied"),
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    class Meta:
        verbose_name = _("coupon usage")
        verbose_name_plural = _("coupon usages")
        ordering = ("-used_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["coupon", "user", "order"],
                name="coupon_usage_unique_per_order",
            ),
        ]
        indexes = [
            models.Index(fields=["coupon", "user"]),
        ]

    def __str__(self) -> str:
        return f"{self.coupon.code} → {self.user.email} (order {self.order_id})"
