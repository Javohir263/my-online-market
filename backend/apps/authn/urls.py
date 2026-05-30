"""
URL conf for `apps.authn` — mounted at `/api/v1/auth/`.
"""

from __future__ import annotations

from django.urls import path

from .views import (
    EmailVerifyConfirmView,
    EmailVerifySendView,
    LoginView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RefreshView,
    RegisterView,
)

app_name = "authn"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("me/", MeView.as_view(), name="me"),
    # Email verification
    path(
        "email/verify/send/",
        EmailVerifySendView.as_view(),
        name="email-verify-send",
    ),
    path(
        "email/verify/confirm/",
        EmailVerifyConfirmView.as_view(),
        name="email-verify-confirm",
    ),
    # Password reset
    path(
        "password/reset/request/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]
