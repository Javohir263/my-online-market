"""
accounts model tests — constraints, soft validations, business logic.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from apps.accounts.models import Address, OtpCode, User
from apps.accounts.tests.factories import (
    AddressFactory,
    OtpFactory,
    UserFactory,
)

pytestmark = pytest.mark.django_db


# =============================================================================
# User
# =============================================================================
class TestUser:
    def test_str_is_email(self):
        u = UserFactory(email="hello@example.com")
        assert str(u) == "hello@example.com"

    def test_uuid_primary_key(self):
        u = UserFactory()
        assert isinstance(u.pk, type(u.id))
        assert len(str(u.id)) == 36  # uuid4 string form

    def test_phone_invalid_format_raises(self):
        u = UserFactory.build(phone="998901234567")  # without +
        with pytest.raises(ValidationError):
            u.full_clean()

    def test_phone_unique_when_set(self):
        UserFactory(phone="+998901234567")
        with pytest.raises(IntegrityError):
            UserFactory(phone="+998901234567")

    def test_phone_empty_allowed_for_multiple_users(self):
        # Phone is empty string by default; constraint excludes that.
        UserFactory(phone="")
        UserFactory(phone="")  # must not raise

    def test_is_admin_role_property(self):
        admin = UserFactory(role=User.Role.ADMIN)
        customer = UserFactory(role=User.Role.CUSTOMER)
        assert admin.is_admin_role
        assert not customer.is_admin_role

    def test_is_admin_role_superuser(self):
        u = UserFactory(role=User.Role.CUSTOMER, is_superuser=True)
        assert u.is_admin_role


# =============================================================================
# Address
# =============================================================================
class TestAddress:
    def test_str_includes_recipient_and_city(self, address):
        s = str(address)
        assert address.recipient_name in s
        assert address.city in s

    def test_setting_default_unsets_old(self, user):
        a = AddressFactory(user=user, is_default=True)
        b = AddressFactory(user=user, is_default=True)
        a.refresh_from_db()
        assert b.is_default is True
        assert a.is_default is False

    def test_default_uniqueness_constraint_per_type(self, user):
        AddressFactory(user=user, type=Address.Type.SHIPPING, is_default=True)
        AddressFactory(user=user, type=Address.Type.BILLING, is_default=True)
        # Both can be default since they have different types — no error.

    def test_non_default_can_be_many(self, user):
        AddressFactory(user=user, is_default=False)
        AddressFactory(user=user, is_default=False)
        assert Address.objects.filter(user=user).count() == 2


# =============================================================================
# OtpCode
# =============================================================================
class TestOtp:
    def test_generate_code_is_6_digits(self):
        for _ in range(20):
            code = OtpCode.generate_code()
            assert len(code) == 6
            assert code.isdigit()

    def test_set_code_hashes(self, otp):
        # raw code "123456" via factory
        assert otp.code_hash != "123456"
        assert len(otp.code_hash) == 64  # sha256 hex

    def test_verify_correct_code(self, otp):
        assert otp.verify(otp.raw_code) is True

    def test_verify_wrong_code(self, otp):
        assert otp.verify("000000") is False

    def test_is_expired(self):
        past = OtpFactory.build(
            expires_at=timezone.now() - timedelta(seconds=1)
        )
        assert past.is_expired is True

    def test_is_not_expired_when_future(self, otp):
        assert otp.is_expired is False

    def test_is_used_after_mark_used(self, otp):
        assert otp.is_used is False
        otp.mark_used()
        assert otp.is_used is True
        assert otp.is_valid is False

    def test_increment_attempt(self, otp):
        otp.increment_attempt()
        assert otp.attempts == 1
        otp.increment_attempt()
        assert otp.attempts == 2

    def test_is_exhausted(self, otp):
        otp.attempts = otp.max_attempts
        otp.save(update_fields=["attempts"])
        assert otp.is_exhausted is True
        assert otp.is_valid is False

    def test_is_valid_when_fresh(self, otp):
        assert otp.is_valid is True
