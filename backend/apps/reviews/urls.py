"""
Reviews URLs — mounted at `/api/v1/reviews/`.
"""

from __future__ import annotations

from django.urls import path

from apps.reviews.views import (
    ProductReviewsView,
    ReviewCreateView,
    ReviewDetailView,
    ReviewHelpfulToggleView,
)

app_name = "reviews"

urlpatterns = [
    path("", ReviewCreateView.as_view(), name="create"),
    path(
        "products/<slug:slug>/",
        ProductReviewsView.as_view(),
        name="product-reviews",
    ),
    path("<int:pk>/", ReviewDetailView.as_view(), name="detail"),
    path(
        "<int:pk>/helpful/",
        ReviewHelpfulToggleView.as_view(),
        name="helpful-toggle",
    ),
]
