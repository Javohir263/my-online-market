"""
ProductTag — kichik label'lar ("new", "hit", "sale").
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class ProductTag(TimeStampedModel):
    """Mahsulot yorlig'i (kichik rangli label)."""

    class ColorChoices(models.TextChoices):
        PRIMARY = "primary", _("Primary (bordoviy)")
        ACCENT = "accent", _("Accent (yashil)")
        WARNING = "warning", _("Warning (oltin)")
        SALE = "sale", _("Sale (qizil)")
        NEW = "new", _("New (ko'k)")
        NEUTRAL = "neutral", _("Neutral (kulrang)")

    name = models.CharField(_("name"), max_length=40)
    slug = models.SlugField(_("slug"), max_length=60, unique=True)
    color = models.CharField(
        _("color"),
        max_length=20,
        choices=ColorChoices.choices,
        default=ColorChoices.PRIMARY,
    )
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        verbose_name = _("product tag")
        verbose_name_plural = _("product tags")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name
