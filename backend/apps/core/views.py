"""
Health-check view — load balancer / uptime monitoring uchun.
"""

from __future__ import annotations

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET


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
