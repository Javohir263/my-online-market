"""
Promotions URLs — mounted at `/api/v1/promotions/`.
"""

from __future__ import annotations

from django.urls import path

from apps.promotions.views import BannerListView, CouponValidateView

app_name = "promotions"

urlpatterns = [
    path("banners/", BannerListView.as_view(), name="banners"),
    path(
        "coupons/validate/",
        CouponValidateView.as_view(),
        name="coupon-validate",
    ),
]
