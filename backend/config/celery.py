"""
Celery app — async task processor.

Workerni ishga tushirish:
    celery -A config worker -l info
Beat (periodic tasks):
    celery -A config beat -l info -S django
"""

from __future__ import annotations

import os

from celery import Celery
from celery.signals import setup_logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("mom")

# CELERY_ namespace bilan boshlangan barcha settings'larni o'qiydi
app.config_from_object("django.conf:settings", namespace="CELERY")

# apps/<app>/tasks.py fayllarini auto-discover qiladi
app.autodiscover_tasks()


@setup_logging.connect
def _configure_logging(**kwargs) -> None:  # noqa: ANN003
    """Django LOGGING settings'ni Celery uchun ham qabul qilish."""
    from logging.config import dictConfig

    from django.conf import settings

    dictConfig(settings.LOGGING)


@app.task(bind=True)
def debug_task(self) -> str:
    """Celery ishlashini tekshirish uchun namuna task."""
    return f"Request: {self.request!r}"
