"""
Notifications admin — read-only audit views.
"""

from __future__ import annotations

from django.contrib import admin

from apps.notifications.models import EmailLog, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "type", "title", "is_read", "created_at"
    )
    list_filter = ("type", "is_read", "created_at")
    search_fields = ("user__email", "title", "message")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "read_at")


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = (
        "id", "recipient", "subject", "template",
        "status", "sent_at", "created_at",
    )
    list_filter = ("status", "template", "created_at")
    search_fields = ("recipient", "subject", "error_message")
    readonly_fields = (
        "recipient", "subject", "template", "body",
        "status", "sent_at", "error_message",
        "created_at", "updated_at",
    )

    def has_add_permission(self, request) -> bool:
        return False  # faqat task orqali yoziladi
