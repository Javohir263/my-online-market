"""
Notification API views — 3 endpoint, hammasi 🔒:
    GET   /notifications/?is_read=             list
    PATCH /notifications/<id>/read/             single mark-read
    POST  /notifications/read-all/              bulk mark-read
"""

from __future__ import annotations

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer


class NotificationListView(ListAPIView):
    """`GET /notifications/?is_read=true|false` 🔒"""

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            qs = qs.filter(is_read=is_read.lower() in ("1", "true", "yes"))
        return qs


class NotificationReadView(APIView):
    """`PATCH /notifications/<id>/read/` 🔒 — bitta notification."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None, responses={200: NotificationSerializer}
    )
    def patch(self, request, pk: int):
        notif = get_object_or_404(
            Notification, pk=pk, user=request.user
        )
        if not notif.is_read:
            notif.is_read = True
            notif.read_at = timezone.now()
            notif.save(update_fields=["is_read", "read_at"])
        return Response(NotificationSerializer(notif).data)


class NotificationReadAllView(APIView):
    """`POST /notifications/read-all/` 🔒 — barchasini read qiladi."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(description="{marked: int}")
        },
    )
    def post(self, request):
        updated = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({"marked": updated})
