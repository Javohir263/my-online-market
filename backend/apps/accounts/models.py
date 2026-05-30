"""
accounts modellari — `User` (custom, email login), `Address`, `OtpCode`.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts.managers import UserManager
from apps.core.models import TimeStampedModel
from apps.core.validators import validate_uz_phone


# =============================================================================
# User
# =============================================================================
class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """Custom user — email USERNAME_FIELD, UUID id, uz/ru/en language."""

    class Role(models.TextChoices):
        CUSTOMER = "customer", _("Customer")
        STAFF = "staff", _("Staff")
        ADMIN = "admin", _("Admin")

    class Language(models.TextChoices):
        UZ = "uz", "O'zbek"
        RU = "ru", "Русский"
        EN = "en", "English"

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    email = models.EmailField(
        _("email"), unique=True, db_index=True, max_length=254
    )
    phone = models.CharField(
        _("phone"),
        max_length=13,
        blank=True,
        default="",
        validators=[validate_uz_phone],
        help_text=_("+998XXXXXXXXX formatida"),
    )
    full_name = models.CharField(_("full name"), max_length=120)

    language = models.CharField(
        _("preferred language"),
        max_length=2,
        choices=Language.choices,
        default=Language.UZ,
    )
    role = models.CharField(
        _("role"),
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        db_index=True,
    )

    is_email_verified = models.BooleanField(_("email verified"), default=False)
    is_phone_verified = models.BooleanField(_("phone verified"), default=False)

    # Django admin / permissions
    is_active = models.BooleanField(_("active"), default=True)
    is_staff = models.BooleanField(_("staff status"), default=False)

    last_login_ip = models.GenericIPAddressField(
        _("last login IP"), null=True, blank=True
    )

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["phone"],
                condition=~Q(phone=""),
                name="user_unique_phone_when_set",
            ),
        ]
        indexes = [
            models.Index(fields=["is_email_verified", "is_active"]),
            models.Index(fields=["role", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.email

    @property
    def is_customer(self) -> bool:
        return self.role == self.Role.CUSTOMER

    @property
    def is_admin_role(self) -> bool:
        return self.role == self.Role.ADMIN or self.is_superuser

    def get_full_name(self) -> str:
        return self.full_name or self.email

    def get_short_name(self) -> str:
        return self.full_name.split(" ", 1)[0] if self.full_name else self.email


# =============================================================================
# Address
# =============================================================================
class Address(TimeStampedModel):
    """Yetkazib berish / hisob-kitob manzili."""

    class Type(models.TextChoices):
        SHIPPING = "shipping", _("Shipping")
        BILLING = "billing", _("Billing")

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="addresses"
    )
    type = models.CharField(
        _("type"), max_length=10, choices=Type.choices, default=Type.SHIPPING
    )

    recipient_name = models.CharField(_("recipient name"), max_length=120)
    recipient_phone = models.CharField(
        _("recipient phone"), max_length=13, validators=[validate_uz_phone]
    )

    region = models.CharField(_("region / viloyat"), max_length=100)
    city = models.CharField(_("city / shahar"), max_length=100)
    district = models.CharField(
        _("district / tuman"), max_length=100, blank=True, default=""
    )
    street = models.CharField(_("street"), max_length=200)
    building = models.CharField(_("building"), max_length=30)
    apartment = models.CharField(
        _("apartment"), max_length=30, blank=True, default=""
    )
    postal_code = models.CharField(
        _("postal code"), max_length=10, blank=True, default=""
    )
    landmark = models.CharField(
        _("landmark / mo'ljal"), max_length=200, blank=True, default=""
    )

    is_default = models.BooleanField(_("default"), default=False)

    class Meta:
        verbose_name = _("address")
        verbose_name_plural = _("addresses")
        ordering = ("-is_default", "-created_at")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "type"],
                condition=Q(is_default=True),
                name="address_unique_default_per_type",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "type"]),
        ]

    def __str__(self) -> str:
        return f"{self.recipient_name} — {self.city}, {self.street} {self.building}"

    def save(self, *args, **kwargs) -> None:
        """Yangi default'ni yoqsa, eskisini avtomatik o'chiradi (per type)."""
        if self.is_default:
            Address.objects.filter(
                user=self.user, type=self.type, is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


# =============================================================================
# OtpCode — email/phone verification + password reset + login OTP
# =============================================================================
class OtpCode(TimeStampedModel):
    """6 raqamli OTP. Raw kod hech qachon DB'da saqlanmaydi — faqat hash."""

    DEFAULT_TTL_MINUTES = 10
    MAX_ATTEMPTS = 5
    CODE_LENGTH = 6

    class Purpose(models.TextChoices):
        EMAIL_VERIFY = "email_verify", _("Email verification")
        PHONE_VERIFY = "phone_verify", _("Phone verification")
        PASSWORD_RESET = "password_reset", _("Password reset")
        LOGIN = "login", _("Login OTP")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target = models.CharField(
        _("target"),
        max_length=128,
        db_index=True,
        help_text=_("Email yoki phone qiymati"),
    )
    code_hash = models.CharField(max_length=128)
    purpose = models.CharField(
        _("purpose"), max_length=20, choices=Purpose.choices
    )
    expires_at = models.DateTimeField(_("expires at"), db_index=True)
    used_at = models.DateTimeField(_("used at"), null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(_("attempts"), default=0)
    max_attempts = models.PositiveSmallIntegerField(
        _("max attempts"), default=MAX_ATTEMPTS
    )

    # Audit
    ip_address = models.GenericIPAddressField(
        _("IP address"), null=True, blank=True
    )
    user_agent = models.CharField(
        _("user agent"), max_length=500, blank=True, default=""
    )

    class Meta:
        verbose_name = _("OTP code")
        verbose_name_plural = _("OTP codes")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["target", "purpose", "-created_at"]),
            models.Index(fields=["expires_at", "used_at"]),
        ]

    def __str__(self) -> str:
        return f"OTP {self.purpose} → {self.target}"

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    @classmethod
    def generate_code(cls) -> str:
        """Cryptographically secure 6-digit code."""
        return f"{secrets.randbelow(10**cls.CODE_LENGTH):0{cls.CODE_LENGTH}d}"

    @staticmethod
    def _hash(raw_code: str) -> str:
        return hashlib.sha256(raw_code.encode("utf-8")).hexdigest()

    def set_code(self, raw_code: str) -> None:
        self.code_hash = self._hash(raw_code)

    def verify(self, raw_code: str) -> bool:
        """Constant-time comparison; doesn't mark as used (caller's job)."""
        return hmac.compare_digest(self.code_hash, self._hash(raw_code))

    def mark_used(self) -> None:
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])

    def increment_attempt(self) -> None:
        OtpCode.objects.filter(pk=self.pk).update(
            attempts=models.F("attempts") + 1
        )
        self.refresh_from_db(fields=["attempts"])

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------
    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_exhausted(self) -> bool:
        return self.attempts >= self.max_attempts

    @property
    def is_valid(self) -> bool:
        return not (self.is_expired or self.is_used or self.is_exhausted)
