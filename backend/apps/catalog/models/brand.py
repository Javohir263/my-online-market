"""
Brand model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class Brand(TimeStampedModel):
    """Mahsulot brendi (Apple, Samsung, ...)."""

    name = models.CharField(_("name"), max_length=120)
    slug = models.SlugField(
        _("slug"), max_length=140, unique=True, db_index=True
    )
    description = models.TextField(
        _("description"), blank=True, default=""
    )
    logo = models.ImageField(
        _("logo"), upload_to="brands/", blank=True, null=True
    )
    is_active = models.BooleanField(_("active"), default=True, db_index=True)

    class Meta:
        verbose_name = _("brand")
        verbose_name_plural = _("brands")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name
