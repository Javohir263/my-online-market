"""
Test settings — pytest uchun.

`pytest.ini` da `DJANGO_SETTINGS_MODULE=config.settings.test` ko'rsatilgan.
Asosiy farqlar: tezroq password hashing, eager Celery, dummy cache, in-process email.
"""

from __future__ import annotations

from .base import *  # noqa: F401,F403

# ---------------------------------------------------------------------------
# Tez password hashing (testlar sekinligi uchun)
# ---------------------------------------------------------------------------
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# ---------------------------------------------------------------------------
# Email — in-memory backend
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# ---------------------------------------------------------------------------
# Cache — local memory (Redis'siz ham testlar ishlasin)
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "tests",
    }
}

# ---------------------------------------------------------------------------
# Celery — eager (sync) — testlar Redis'siz ishlasin
# ---------------------------------------------------------------------------
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ---------------------------------------------------------------------------
# Disable debug-toolbar in tests if it sneaks in
# ---------------------------------------------------------------------------
DEBUG = False
