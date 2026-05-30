"""
factory-boy fixtures for accounts models.
"""

from __future__ import annotations

from datetime import timedelta

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from apps.accounts.models import Address, OtpCode, User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    full_name = factory.Faker("name")
    role = User.Role.CUSTOMER
    is_active = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):  # noqa: N805
        raw = extracted or "password123"
        obj.set_password(raw)
        if create:
            obj.save(update_fields=["password"])


class SuperUserFactory(UserFactory):
    is_staff = True
    is_superuser = True
    is_email_verified = True
    role = User.Role.ADMIN


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address

    user = factory.SubFactory(UserFactory)
    type = Address.Type.SHIPPING
    recipient_name = factory.Faker("name")
    recipient_phone = factory.Sequence(lambda n: f"+9989012345{n:02d}")
    region = "Toshkent viloyati"
    city = "Toshkent"
    district = "Yunusobod"
    street = factory.Faker("street_name")
    building = factory.Sequence(lambda n: str(n + 1))
    is_default = False


class OtpFactory(DjangoModelFactory):
    class Meta:
        model = OtpCode
        skip_postgeneration_save = True

    target = factory.Sequence(lambda n: f"user{n}@example.com")
    purpose = OtpCode.Purpose.EMAIL_VERIFY
    expires_at = factory.LazyFunction(
        lambda: timezone.now() + timedelta(minutes=10)
    )

    @factory.post_generation
    def code(obj, create, extracted, **kwargs):  # noqa: N805
        raw = extracted or "123456"
        obj.set_code(raw)
        if create:
            obj.save(update_fields=["code_hash"])
        # Store on instance for tests to inspect (not persisted)
        obj.raw_code = raw  # type: ignore[attr-defined]
