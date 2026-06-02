"""
Development settings — lokal ishlash uchun.

`DJANGO_SETTINGS_MODULE=config.settings.development` default'i `manage.py` da.
"""

from __future__ import annotations

from .base import *  # noqa: F401,F403
from .base import MIDDLEWARE, INSTALLED_APPS, env

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------
DEBUG = True
ALLOWED_HOSTS = ["*"]

# ---------------------------------------------------------------------------
# Dev-only apps + middleware
# ---------------------------------------------------------------------------
INSTALLED_APPS = INSTALLED_APPS + [
    "debug_toolbar",
]

MIDDLEWARE = MIDDLEWARE + [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = ["127.0.0.1", "::1"]
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
}

# ---------------------------------------------------------------------------
# Email — console backend
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ---------------------------------------------------------------------------
# Security — relaxed for dev
# ---------------------------------------------------------------------------
AUTH_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Default dev CORS (Next.js dev server)
CORS_ALLOWED_ORIGINS = env(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000", "http://127.0.0.1:3000"],
)
CSRF_TRUSTED_ORIGINS = env(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default=["http://localhost:3000", "http://127.0.0.1:3000"],
)

# ---------------------------------------------------------------------------
# Cache — Redis lokal dev'da ixtiyoriy.
# Redis (6379) o'chiq bo'lsa, throttling/cache har so'rovda unga ulanishga
# urinib ~20s timeout berardi. LocMem in-process va tezkor.
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "mom-dev",
    }
}
