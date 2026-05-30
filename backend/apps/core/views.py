"""
core app — umumiy view'lar (healthcheck, i18n list, language switch).
"""

from __future__ import annotations

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers import LanguagePreferenceSerializer


# =============================================================================
# Health check
# =============================================================================
@never_cache
@require_GET
def healthcheck(request):
    """200 OK if DB is reachable, 503 otherwise."""
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
        return JsonResponse({"status": "ok"})
    except Exception as exc:  # noqa: BLE001
        return JsonResponse(
            {"status": "error", "detail": str(exc)}, status=503
        )


# =============================================================================
# i18n — supported tillar
# =============================================================================
class LanguageListView(APIView):
    """`GET /api/v1/i18n/languages/` — qo'llab-quvvatlanadigan tillar."""

    permission_classes = [AllowAny]
    authentication_classes = []  # public

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Supported languages list",
                response={
                    "type": "object",
                    "properties": {
                        "default": {"type": "string"},
                        "current": {"type": "string"},
                        "languages": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "code": {"type": "string"},
                                    "name": {"type": "string"},
                                },
                            },
                        },
                    },
                },
            )
        }
    )
    def get(self, request):
        return Response(
            {
                "default": settings.LANGUAGE_CODE,
                "current": getattr(
                    request, "LANGUAGE_CODE", settings.LANGUAGE_CODE
                ),
                "languages": [
                    {"code": code, "name": name}
                    for code, name in settings.LANGUAGES
                ],
            }
        )


# =============================================================================
# i18n — preference (cookie + user.language)
# =============================================================================
class LanguagePreferenceView(APIView):
    """`PATCH /api/v1/i18n/preference/` — tilni o'rnatadi.

    Anonim foydalanuvchi uchun `django_language` cookie o'rnatadi.
    Authenticated foydalanuvchi uchun esa `user.language`'ni ham yangilaydi
    (boshqa qurilmalarda ham qo'llanadi).
    """

    permission_classes = [AllowAny]

    @extend_schema(
        request=LanguagePreferenceSerializer,
        responses={
            200: OpenApiResponse(description="Language preference saved"),
        },
    )
    def patch(self, request):
        serializer = LanguagePreferenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lang = serializer.validated_data["language"]

        # Authenticated user — DB'ga yozish
        if request.user.is_authenticated:
            request.user.language = lang
            request.user.save(update_fields=["language"])

        response = Response(
            {"language": lang, "detail": _("Til afzalligi saqlandi.")},
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key=settings.LANGUAGE_COOKIE_NAME,
            value=lang,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
        )
        return response
