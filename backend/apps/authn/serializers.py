"""
DRF serializers for authentication endpoints.

Security choices:
- Generic "Invalid credentials" on login (prevents email enumeration).
- Password validators delegated to Django settings.
- Email lowercased + normalized in serializer (matches UserManager).
"""

from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.accounts.models import OtpCode

User = get_user_model()


# =============================================================================
# Helpers
# =============================================================================
def _normalize_email(email: str) -> str:
    return email.strip().lower()


# =============================================================================
# Public user shape (used by /auth/me/)
# =============================================================================
class UserSerializer(serializers.ModelSerializer):
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
        read_only_fields = fields


# =============================================================================
# Register
# =============================================================================
class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )
    password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )
    full_name = serializers.CharField(max_length=120, trim_whitespace=True)
    language = serializers.ChoiceField(
        choices=User.Language.choices,
        default=User.Language.UZ,
        required=False,
    )
    phone = serializers.CharField(
        max_length=13, required=False, allow_blank=True, default=""
    )

    def validate_email(self, value: str) -> str:
        value = _normalize_email(value)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                _("Bu email allaqachon ro'yxatdan o'tgan."),
                code="email_taken",
            )
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": _("Parollar mos kelmaydi.")}
            )
        # Django built-in password validators
        validate_password(attrs["password"])
        return attrs


# =============================================================================
# Login
# =============================================================================
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    GENERIC_ERROR = _("Email yoki parol noto'g'ri.")

    def validate(self, attrs: dict) -> dict:
        email = _normalize_email(attrs["email"])
        request = self.context.get("request")
        user = authenticate(
            request=request, username=email, password=attrs["password"]
        )
        if not user:
            raise serializers.ValidationError(
                {"detail": self.GENERIC_ERROR}, code="invalid_credentials"
            )
        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": _("Akkaunt faol emas.")}, code="inactive"
            )
        attrs["user"] = user
        return attrs


# =============================================================================
# Logout — refresh token cookie'dan o'qiladi, body kerak emas
# =============================================================================
class LogoutSerializer(serializers.Serializer):
    """Empty body — refresh token cookie'dan o'qiladi."""


# =============================================================================
# Email verification
# =============================================================================
class EmailVerifyConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(
        min_length=OtpCode.CODE_LENGTH,
        max_length=OtpCode.CODE_LENGTH,
    )


# =============================================================================
# Password reset
# =============================================================================
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        return _normalize_email(value)


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(
        min_length=OtpCode.CODE_LENGTH,
        max_length=OtpCode.CODE_LENGTH,
    )
    new_password = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )
    new_password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    def validate_email(self, value: str) -> str:
        return _normalize_email(value)

    def validate(self, attrs: dict) -> dict:
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": _("Parollar mos kelmaydi.")}
            )
        validate_password(attrs["new_password"])
        return attrs
