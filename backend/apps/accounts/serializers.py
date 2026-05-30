"""
Account serializers — profile + addresses + password change.
"""

from __future__ import annotations

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.accounts.models import Address, User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "phone",
            "language",
            "role",
            "is_email_verified",
            "is_phone_verified",
            "created_at",
        )
        read_only_fields = (
            "id",
            "email",
            "role",
            "is_email_verified",
            "is_phone_verified",
            "created_at",
        )


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError(
                {"old_password": "Joriy parol noto'g'ri."}
            )
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Parollar mos kelmaydi."}
            )
        validate_password(attrs["new_password"], user)
        return attrs


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            "id",
            "type",
            "recipient_name",
            "recipient_phone",
            "region",
            "city",
            "district",
            "street",
            "building",
            "apartment",
            "postal_code",
            "landmark",
            "is_default",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
