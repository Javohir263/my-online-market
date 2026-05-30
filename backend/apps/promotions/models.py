"""
Promotions stub — B10 da to'liq logic qo'shiladi (Coupon, Banner, CouponUsage).

Hozircha faqat `Coupon` stub modeli — `orders.Order.coupon` FK uchun.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class Coupon(TimeStampedModel):
    """Skidka kuponi. Stub — B10 da to'liq logic (usage_limit, per_user_limit,
    used_count, validity windows, percentage/fixed type)."""

    class Type(models.TextChoices):
        PERCENTAGE = "percentage", _("Percentage")
        FIXED = "fixed", _("Fixed amount")

    code = models.CharField(_("code"), max_length=64, unique=True, db_index=True)
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
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        verbose_name = _("coupon")
        verbose_name_plural = _("coupons")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.code
