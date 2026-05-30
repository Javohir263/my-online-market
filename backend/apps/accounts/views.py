"""
Account API views — profile, password change, addresses CRUD.
"""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Address
from apps.accounts.serializers import (
    AddressSerializer,
    PasswordChangeSerializer,
    ProfileSerializer,
)


class ProfileView(generics.RetrieveUpdateAPIView):
    """`GET/PUT/PATCH /accounts/profile/` 🔒"""

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    """`PUT /accounts/profile/password/` 🔒"""

    permission_classes = [IsAuthenticated]

    @extend_schema(request=PasswordChangeSerializer)
    def put(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return Response({"detail": "Parol o'zgartirildi."})


class AddressListCreateView(generics.ListCreateAPIView):
    """`GET/POST /accounts/addresses/` 🔒"""

    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """`GET/PUT/PATCH/DELETE /accounts/addresses/<id>/` 🔒"""

    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
