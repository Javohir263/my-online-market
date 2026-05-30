"""
Notification serializers.
"""

from __future__ import annotations

from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "type",
            "title",
            "message",
            "data",
            "is_read",
            "created_at",
            "read_at",
        )
        read_only_fields = fields
