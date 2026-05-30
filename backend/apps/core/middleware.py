"""
Custom middlewares.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.utils import translation

logger = logging.getLogger(__name__)


class UserLanguageMiddleware:
    """Authenticated user'ning `user.language` ni LocaleMiddleware tanlagan
    tildan ustuvor qiladi.

    Ikki turdagi authentication'ni qo'llab-quvvatlaydi:
        1. Session-based (Django admin va boshqa) — `request.user` mavjud bo'ladi
           AuthenticationMiddleware tomonidan.
        2. JWT cookie-based (DRF API) — `CookieJWTAuthentication`'ni mahalliy
           ravishda chaqiradi. Bu DRF view dispatch'idan oldin ishlaydi.

    Tartib (priority):
        1. User.language (agar authenticated va valid)
        2. Accept-Language header / django_language cookie (LocaleMiddleware)
        3. Default LANGUAGE_CODE

    MIDDLEWARE'da `django.middleware.locale.LocaleMiddleware` VA
    `django.contrib.auth.middleware.AuthenticationMiddleware`'dan
    KEYIN turishi shart.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._supported = {code for code, _ in settings.LANGUAGES}

    def __call__(self, request):
        lang = self._resolve_user_language(request)
        if lang:
            translation.activate(lang)
            request.LANGUAGE_CODE = lang

        response = self.get_response(request)
        translation.deactivate()
        return response

    def _resolve_user_language(self, request) -> str | None:
        # 1. Session-authenticated user (admin va boshqa)
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            lang = getattr(user, "language", None)
            if lang in self._supported:
                return lang

        # 2. JWT cookie — DRF API request'lar
        if settings.AUTH_COOKIE_ACCESS in request.COOKIES:
            return self._extract_from_jwt(request)

        return None

    def _extract_from_jwt(self, request) -> str | None:
        try:
            from apps.authn.authentication import CookieJWTAuthentication
        except ImportError:
            return None

        auth = CookieJWTAuthentication()
        try:
            # CSRF'ni middleware bosqichida tekshirmaymiz — bu faqat til
            # detection. Real authentication DRF view'da qaytadan bajariladi.
            raw_token = request.COOKIES.get(settings.AUTH_COOKIE_ACCESS)
            if not raw_token:
                return None
            validated = auth.get_validated_token(raw_token)
            jwt_user = auth.get_user(validated)
            lang = getattr(jwt_user, "language", None)
            if lang in self._supported:
                return lang
        except Exception:  # noqa: BLE001
            # JWT noto'g'ri / muddati o'tgan — sukut bilan o'tkazib yuboramiz
            logger.debug("UserLanguageMiddleware: JWT extract failed", exc_info=True)
        return None
