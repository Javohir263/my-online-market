"""
Cart-specific exceptions.
"""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException


class InsufficientStock(APIException):
    status_code = 400
    default_code = "insufficient_stock"
    default_detail = _("Talab qilingan miqdor stok'dan ko'p.")


class CartItemNotFound(APIException):
    status_code = 404
    default_code = "cart_item_not_found"
    default_detail = _("Savat elementi topilmadi.")


class ProductInactive(APIException):
    status_code = 400
    default_code = "product_inactive"
    default_detail = _("Mahsulot hozir mavjud emas.")
