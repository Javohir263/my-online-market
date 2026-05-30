"""
Umumiy model base'lari.

Barcha business modellar `TimeStampedModel` dan meros oladi. Kerakli joylarda
`UUIDModel` (Product, Order kabi) yoki `SoftDeleteModel` (Product, Vendor kabi)
ham qo'shiladi.
"""

from __future__ import annotations

import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """`created_at` / `updated_at` audit ustunlari."""

    created_at = models.DateTimeField(
        _("created at"), auto_now_add=True, db_index=True
    )
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)


class UUIDModel(models.Model):
    """Public-facing modellar uchun (Product, Order, User) — sequential ID
    leak qilmaslik uchun."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def alive(self) -> "SoftDeleteQuerySet":
        return self.filter(deleted_at__isnull=True)

    def dead(self) -> "SoftDeleteQuerySet":
        return self.filter(deleted_at__isnull=False)

    def hard_delete(self):
        return super().delete()

    def delete(self):
        return super().update(deleted_at=timezone.now())


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Default — faqat alive obyektlarni qaytaradi."""

    def get_queryset(self) -> SoftDeleteQuerySet:
        return super().get_queryset().alive()


class SoftDeleteModel(models.Model):
    """`deleted_at` orqali soft delete. Default manager faqat alive obyektlarni
    qaytaradi; `all_objects` orqali to'liq queryset olinadi."""

    deleted_at = models.DateTimeField(
        _("deleted at"), null=True, blank=True, db_index=True
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager.from_queryset(SoftDeleteQuerySet)()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents: bool = False) -> None:
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(self, using=None, keep_parents: bool = False):
        return super().delete(using=using, keep_parents=keep_parents)
