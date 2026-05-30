"""
WishlistItem — foydalanuvchining sevimli mahsulotlari.

UNIQUE(user, product) — bir mahsulot bir marta wishlist'da.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class WishlistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="wishlist_entries",
    )
    created_at = models.DateTimeField(
        _("added at"), auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = _("wishlist item")
        verbose_name_plural = _("wishlist items")
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="wishlist_unique_user_product",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} ♥ {self.product.name}"
