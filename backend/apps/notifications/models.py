"""
Notification + EmailLog models.

Notification.title/message — user.language'da snapshot saqlanadi
(yuborilgan paytdagi til). Frontend bitta til ko'radi (user'ning til).

EmailLog — har email yuborilganda yoziladi (audit + debug).
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class Notification(models.Model):
    class Type(models.TextChoices):
        ORDER_CREATED = "order_created", _("Order created")
        ORDER_CONFIRMED = "order_confirmed", _("Order confirmed")
        ORDER_SHIPPED = "order_shipped", _("Order shipped")
        ORDER_DELIVERED = "order_delivered", _("Order delivered")
        ORDER_CANCELLED = "order_cancelled", _("Order cancelled")
        PAYMENT_PAID = "payment_paid", _("Payment confirmed")
        REVIEW_APPROVED = "review_approved", _("Review approved")
        SYSTEM = "system", _("System message")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(
        _("type"), max_length=40, choices=Type.choices, db_index=True
    )
    title = models.CharField(_("title"), max_length=200)
    message = models.TextField(_("message"))
    data = models.JSONField(
        _("payload"),
        default=dict,
        blank=True,
        help_text=_(
            "Tegishli ma'lumotlar (order_number, link, image_url, ...)"
        ),
    )
    is_read = models.BooleanField(_("read"), default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(_("read at"), null=True, blank=True)

    class Meta:
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
            models.Index(fields=["user", "type"]),
        ]

    def __str__(self) -> str:
        return f"[{self.type}] {self.user.email}: {self.title[:40]}"


class EmailLog(TimeStampedModel):
    """Har yuborilgan email uchun audit log."""

    class Status(models.TextChoices):
        QUEUED = "queued", _("Queued")
        SENT = "sent", _("Sent")
        FAILED = "failed", _("Failed")

    recipient = models.EmailField(_("recipient"), db_index=True)
    subject = models.CharField(_("subject"), max_length=300)
    template = models.CharField(
        _("template"),
        max_length=80,
        blank=True,
        default="",
        help_text=_("Template name yoki bo'sh (raw message)"),
    )
    body = models.TextField(_("body"), blank=True, default="")
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.QUEUED,
        db_index=True,
    )
    sent_at = models.DateTimeField(_("sent at"), null=True, blank=True)
    error_message = models.TextField(
        _("error message"), blank=True, default=""
    )

    class Meta:
        verbose_name = _("email log")
        verbose_name_plural = _("email logs")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["recipient", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.recipient}: {self.subject[:50]} [{self.status}]"
