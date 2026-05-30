"""
ASGI config — production'da `DJANGO_SETTINGS_MODULE=config.settings.production`
environment variable orqali override qilinadi.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

application = get_asgi_application()
