"""
Account URLs — `/api/v1/accounts/`.
"""

from __future__ import annotations

from django.urls import path

from apps.accounts.views import (
    AddressDetailView,
    AddressListCreateView,
    PasswordChangeView,
    ProfileView,
)

app_name = "accounts"

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path(
        "profile/password/",
        PasswordChangeView.as_view(),
        name="password-change",
    ),
    path("addresses/", AddressListCreateView.as_view(), name="address-list"),
    path(
        "addresses/<int:pk>/",
        AddressDetailView.as_view(),
        name="address-detail",
    ),
]
