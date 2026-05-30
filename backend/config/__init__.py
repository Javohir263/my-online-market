"""
Django auto-loads `celery_app` at startup so that `@shared_task` decorators
work properly across apps.
"""

from .celery import app as celery_app

__all__ = ("celery_app",)
