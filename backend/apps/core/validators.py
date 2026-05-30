"""
Reusable validators.
"""

from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

UZ_PHONE_RE = re.compile(r"^\+998\d{9}$")


def validate_uz_phone(value: str) -> None:
    """O'zbekiston telefoni: +998XXXXXXXXX (jami 13 belgi)."""
    if not UZ_PHONE_RE.match(value):
        raise ValidationError(
            _("Telefon raqami +998XXXXXXXXX formatida bo'lishi kerak."),
            code="invalid_phone",
        )
