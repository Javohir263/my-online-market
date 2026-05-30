"""
Yagona API xato javob formati.

Barcha DRF xatolari `{ "error": { "code", "message", "details" } }` shaklida
qaytadi — frontend uchun aniq va prognozlanadigan.
"""

from __future__ import annotations

import logging
from typing import Any

from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def api_exception_handler(exc: Exception, context: dict) -> Response | None:
    """REST_FRAMEWORK['EXCEPTION_HANDLER'] sifatida ishlatiladi."""

    response = exception_handler(exc, context)

    if response is None:
        # 500 — unexpected. Sentry'ga yo'naltirish uchun log.
        logger.exception("Unhandled API exception: %s", exc)
        return Response(
            {
                "error": {
                    "code": "server_error",
                    "message": "Internal server error.",
                    "details": None,
                }
            },
            status=500,
        )

    code = "error"
    details: Any = None

    if isinstance(exc, APIException):
        code = getattr(exc, "default_code", "error")

    data = response.data
    if isinstance(data, dict):
        message = data.get("detail") or "An error occurred."
        details = {k: v for k, v in data.items() if k != "detail"} or None
    elif isinstance(data, list):
        message = data[0] if data else "An error occurred."
        details = data
    else:
        message = str(data)

    response.data = {
        "error": {
            "code": code,
            "message": str(message),
            "details": details,
        }
    }
    return response
