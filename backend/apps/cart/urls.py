"""
Cart URLs — mounted at `/api/v1/cart/`.
"""

from __future__ import annotations

from django.urls import path

from apps.cart.views import (
    CartCouponView,
    CartDetailView,
    CartItemDetailView,
    CartItemListView,
    CartMergeView,
)

app_name = "cart"

urlpatterns = [
    path("", CartDetailView.as_view(), name="detail"),
    path("items/", CartItemListView.as_view(), name="items"),
    path("items/<int:pk>/", CartItemDetailView.as_view(), name="item-detail"),
    path("coupon/", CartCouponView.as_view(), name="coupon"),
    path("coupon/apply/", CartCouponView.as_view(), name="coupon-apply"),
    path("merge/", CartMergeView.as_view(), name="merge"),
]
