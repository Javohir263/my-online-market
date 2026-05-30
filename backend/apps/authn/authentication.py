"""
CookieJWTAuthentication — JWT'ni Authorization header o'rniga httpOnly
cookie'dan o'qiydi. Bu XSS-safe (JS token'ga teginolmaydi), lekin
cookie-auth bo'lgani uchun CSRF protection majburiy (unsafe methods'da).
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)


class _CSRFCheck(CsrfViewMiddleware):
    """SessionAuthentication kabi — CSRF tokenni mantiqan tekshirish."""

    def _reject(self, request, reason):  # type: ignore[override]
        return reason


def enforce_csrf(request) -> None:
    """Unsafe HTTP methods'da CSRF tokenni tekshiradi."""
    if request.method in ("GET", "HEAD", "OPTIONS", "TRACE"):
        return
    check = _CSRFCheck(lambda req: None)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise exceptions.PermissionDenied(f"CSRF Failed: {reason}")


class CookieJWTAuthentication(JWTAuthentication):
    """SimpleJWT'ning auth class'i — token'ni cookie'dan o'qiydi."""

    def authenticate(self, request):
        raw_token = request.COOKIES.get(settings.AUTH_COOKIE_ACCESS)
        if not raw_token:
            # Fallback: header (mobile mijoz yoki testlar uchun)
            header = self.get_header(request)
            if header is None:
                return None
            raw_token = self.get_raw_token(header)
            if raw_token is None:
                return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except exceptions.AuthenticationFailed:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.warning("JWT decode failed: %s", exc)
            return None

        # Cookie-based authentication — CSRF kerak
        enforce_csrf(request)

        user = self.get_user(validated_token)
        return user, validated_token
