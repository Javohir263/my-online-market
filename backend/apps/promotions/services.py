"""
Promotion services — coupon validation + discount calculation.
"""

from __future__ import annotations

from decimal import Decimal

from django.db.models import Q

from apps.promotions.exceptions import (
    CouponExpired,
    CouponInactive,
    CouponLimitReached,
    CouponMinNotMet,
    CouponNotFound,
    CouponPerUserLimitReached,
)
from apps.promotions.models import Coupon, CouponUsage


def _user_usage_count(coupon: Coupon, user) -> int:
    if user is None or not getattr(user, "is_authenticated", False):
        return 0
    return CouponUsage.objects.filter(coupon=coupon, user=user).count()


def find_coupon(code: str) -> Coupon:
    code = (code or "").strip().upper()
    coupon = Coupon.objects.filter(code__iexact=code).first()
    if coupon is None:
        raise CouponNotFound()
    return coupon


def validate_coupon(
    *, code: str, user, subtotal: Decimal
) -> Coupon:
    """Kupon validatsiyasi — tahliliy xato'lar bilan.

    user: anonim user uchun None yoki AnonymousUser bo'lishi mumkin.
    """
    coupon = find_coupon(code)

    if not coupon.is_active:
        raise CouponInactive()
    if not coupon.is_within_window:
        raise CouponExpired()
    if subtotal < coupon.min_order_amount:
        raise CouponMinNotMet()
    if not coupon.is_globally_available:
        raise CouponLimitReached()

    if user is not None and getattr(user, "is_authenticated", False):
        used = _user_usage_count(coupon, user)
        if used >= coupon.per_user_limit:
            raise CouponPerUserLimitReached()

    return coupon


def calc_discount(coupon: Coupon, subtotal: Decimal) -> Decimal:
    """Discount qiymati. Percentage'da max_discount cap qo'llanadi.

    Returns Decimal >= 0, ammo subtotal'dan oshmaydi.
    """
    if coupon.type == Coupon.Type.PERCENTAGE:
        amount = (subtotal * coupon.value) / Decimal("100")
        if coupon.max_discount is not None:
            amount = min(amount, coupon.max_discount)
    else:  # FIXED
        amount = coupon.value

    # Subtotal'dan ko'p chegirma berib bo'lmaydi
    amount = min(amount, subtotal)
    return amount.quantize(Decimal("0.01"))
