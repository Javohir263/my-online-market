"""
Custom DRF permissions.
"""

from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """Faqat egasi yozish/o'chirish uchun. Boshqalarga read-only."""

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "user_id", None) == getattr(request.user, "id", None)


class IsAdminOrReadOnly(BasePermission):
    """Admin yozadi, hammasi o'qiydi."""

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsStaffOrOwner(BasePermission):
    """Staff hammasini ko'radi, oddiy user faqat o'zinikini."""

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        return getattr(obj, "user_id", None) == user.id
