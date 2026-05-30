"""
Wishlist URLs — mounted at `/api/v1/wishlist/`.
"""

from __future__ import annotations

from django.urls import path

from apps.wishlist.views import (
    WishlistAddView,
    WishlistListView,
    WishlistRemoveView,
)

app_name = "wishlist"

urlpatterns = [
    path("", WishlistListView.as_view(), name="list"),
    path("items/", WishlistAddView.as_view(), name="items"),
    path(
        "items/<uuid:product_id>/",
        WishlistRemoveView.as_view(),
        name="item-remove",
    ),
]
