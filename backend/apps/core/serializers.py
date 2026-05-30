"""
core app — umumiy serializers.
"""

from __future__ import annotations

from django.conf import settings
from rest_framework import serializers


class LanguagePreferenceSerializer(serializers.Serializer):
    """Til afzalligini o'zgartirish — bitta `language` field."""

    language = serializers.ChoiceField(
        choices=[code for code, _ in settings.LANGUAGES]
    )
