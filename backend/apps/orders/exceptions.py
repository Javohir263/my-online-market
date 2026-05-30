"""
Order-specific exceptions.
"""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException


class EmptyCart(APIException):
    status_code = 400
    default_code = "empty_cart"
    default_detail = _("Savatcha bo'sh — checkout qilib bo'lmaydi.")


class StockChanged(APIException):
    status_code = 409
    default_code = "stock_changed"
    default_detail = _("Mahsulot stok'i o'zgargan — sahifani yangilang.")


class InvalidStatusTransition(APIException):
    status_code = 400
    default_code = "invalid_transition"
    default_detail = _("Buyurtma statusi bunday o'zgarishi mumkin emas.")


class OrderNotCancellable(APIException):
    status_code = 400
    default_code = "order_not_cancellable"
    default_detail = _(
        "Bu buyurtmani bekor qilib bo'lmaydi (allaqachon jo'natilgan)."
    )
