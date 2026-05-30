"""
Notification URLs — `/api/v1/notifications/`.
"""

from __future__ import annotations

from django.urls import path

from apps.notifications.views import (
    NotificationListView,
    NotificationReadAllView,
    NotificationReadView,
)

app_name = "notifications"

urlpatterns = [
    path("", NotificationListView.as_view(), name="list"),
    path("read-all/", NotificationReadAllView.as_view(), name="read-all"),
    path("<int:pk>/read/", NotificationReadView.as_view(), name="read"),
]
