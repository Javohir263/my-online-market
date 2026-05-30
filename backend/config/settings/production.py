"""
Production settings — prod muhitida `DJANGO_SETTINGS_MODULE=config.settings.production`.
Asosiy farqlar: DEBUG=False, security headers, Sentry, Cloudinary media, prod logging.
"""

from __future__ import annotations

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F401,F403
from .base import STORAGES, env

# ---------------------------------------------------------------------------
# Debug + hosts
# ---------------------------------------------------------------------------
DEBUG = False
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")  # required, fail-fast if missing

# ---------------------------------------------------------------------------
# Security headers (HTTPS + HSTS + secure cookies)
# ---------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31_536_000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
AUTH_COOKIE_SECURE = True

# ---------------------------------------------------------------------------
# Media storage — Cloudinary CDN
# ---------------------------------------------------------------------------
STORAGES["default"] = {
    "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
}

# ---------------------------------------------------------------------------
# Sentry
# ---------------------------------------------------------------------------
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.1),
        send_default_pii=False,
        environment=env("SENTRY_ENVIRONMENT", default="production"),
    )

# ---------------------------------------------------------------------------
# Logging — JSON-style structured (best for log aggregators)
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "celery": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "apps": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
