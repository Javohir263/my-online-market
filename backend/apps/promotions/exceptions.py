"""
Promotion-specific exceptions.
"""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException


class CouponNotFound(APIException):
    status_code = 404
    default_code = "coupon_not_found"
    default_detail = _("Kupon topilmadi.")


class CouponInactive(APIException):
    status_code = 400
    default_code = "coupon_inactive"
    default_detail = _("Kupon faol emas.")


class CouponExpired(APIException):
    status_code = 400
    default_code = "coupon_expired"
    default_detail = _("Kupon muddati o'tgan yoki hali boshlanmagan.")


class CouponMinNotMet(APIException):
    status_code = 400
    default_code = "coupon_min_not_met"
    default_detail = _("Buyurtma summasi kupon talabidan past.")


class CouponLimitReached(APIException):
    status_code = 400
    default_code = "coupon_limit_reached"
    default_detail = _("Kuponning umumiy limiti tugagan.")


class CouponPerUserLimitReached(APIException):
    status_code = 400
    default_code = "coupon_user_limit_reached"
    default_detail = _("Siz bu kupondan maksimal foydalanib bo'lgansiz.")
