"""
WSGI config — production'da `DJANGO_SETTINGS_MODULE=config.settings.production`
environment variable orqali override qilinadi.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

application = get_wsgi_application()
