"""
JWT cookie helpers — token'larni httpOnly cookie'da o'rnatish/tozalash.

Cookie nomlari va xavfsizlik parametrlari `settings.py` da centralized:
- AUTH_COOKIE_ACCESS / AUTH_COOKIE_REFRESH
- AUTH_COOKIE_SECURE (prod'da True)
- AUTH_COOKIE_SAMESITE ("Lax")
"""

from __future__ import annotations

from django.conf import settings
from rest_framework.response import Response

# Refresh token'ni faqat refresh endpoint'i o'qiy oladi (extra security)
REFRESH_COOKIE_PATH = "/api/v1/auth/"


def _common_kwargs(secure: bool) -> dict:
    return {
        "httponly": True,  # JS read qila olmaydi — XSS-safe
        "secure": secure,
        "samesite": settings.AUTH_COOKIE_SAMESITE,
        "domain": getattr(settings, "AUTH_COOKIE_DOMAIN", None),
    }


def set_access_cookie(response: Response, access_token: str) -> None:
    response.set_cookie(
        key=settings.AUTH_COOKIE_ACCESS,
        value=access_token,
        max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        path="/",
        **_common_kwargs(settings.AUTH_COOKIE_SECURE),
    )


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.AUTH_COOKIE_REFRESH,
        value=refresh_token,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        path=REFRESH_COOKIE_PATH,
        **_common_kwargs(settings.AUTH_COOKIE_SECURE),
    )


def set_auth_cookies(
    response: Response, access_token: str, refresh_token: str
) -> None:
    set_access_cookie(response, access_token)
    set_refresh_cookie(response, refresh_token)


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        settings.AUTH_COOKIE_ACCESS,
        path="/",
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )
    response.delete_cookie(
        settings.AUTH_COOKIE_REFRESH,
        path=REFRESH_COOKIE_PATH,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )
