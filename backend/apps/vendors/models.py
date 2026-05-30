"""
Vendor model — single-vendor MVP, lekin schema multi-vendor uchun
extensible (Product.vendor FK hozirdan mavjud).
"""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class VendorManager(models.Manager):
    def get_default(self) -> "Vendor":
        """`settings.DEFAULT_VENDOR_SLUG` bo'yicha asosiy vendorni qaytaradi.

        Yaratilmagan bo'lsa, fallback sifatida birinchi mavjud vendorni qaytaradi.
        Data migration shu vendorni yaratib qo'yadi.
        """
        slug = getattr(settings, "DEFAULT_VENDOR_SLUG", "my-online-market")
        obj = self.filter(slug=slug).first()
        if obj is None:
            obj = self.first()
        if obj is None:
            raise self.model.DoesNotExist("No vendor seeded yet.")
        return obj


class Vendor(TimeStampedModel):
    """Marketplace dagi sotuvchi. MVP'da bitta DEFAULT_VENDOR."""

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        PENDING = "pending", _("Pending")
        SUSPENDED = "suspended", _("Suspended")

    slug = models.SlugField(
        _("slug"), max_length=120, unique=True, db_index=True
    )
    name = models.CharField(_("name"), max_length=200)
    description = models.TextField(_("description"), blank=True, default="")
    logo = models.ImageField(
        _("logo"), upload_to="vendors/logos/", blank=True, null=True
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_vendors",
        null=True,
        blank=True,
        help_text=_("Multi-vendor rejimida vendor egasi."),
    )

    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    commission_rate = models.DecimalField(
        _("commission rate (%)"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=_("0.00 dan 100.00 gacha"),
    )

    objects = VendorManager()

    class Meta:
        verbose_name = _("vendor")
        verbose_name_plural = _("vendors")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name
