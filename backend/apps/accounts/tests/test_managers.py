"""
UserManager unit tests.
"""

from __future__ import annotations

import pytest

from apps.accounts.models import User

pytestmark = pytest.mark.django_db


def test_create_user_normalizes_email():
    user = User.objects.create_user(
        email="John.Doe@Example.COM",
        password="x",
        full_name="John",
    )
    assert user.email == "john.doe@example.com"


def test_create_user_hashes_password():
    user = User.objects.create_user(
        email="x@example.com", password="raw-secret", full_name="X"
    )
    assert user.password != "raw-secret"
    assert user.check_password("raw-secret")


def test_create_user_defaults_to_inactive_admin_off():
    user = User.objects.create_user(
        email="x@example.com", password="x", full_name="X"
    )
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.role == User.Role.CUSTOMER
    assert user.is_email_verified is False


def test_create_superuser_sets_all_admin_flags():
    user = User.objects.create_superuser(
        email="admin@example.com", password="x", full_name="A"
    )
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.is_email_verified is True
    assert user.role == User.Role.ADMIN


def test_create_user_requires_email():
    with pytest.raises(ValueError, match="Email is required"):
        User.objects.create_user(email="", password="x", full_name="X")


def test_create_superuser_rejects_non_staff():
    with pytest.raises(ValueError, match="is_staff=True"):
        User.objects.create_superuser(
            email="a@b.com", password="x", full_name="A", is_staff=False
        )


def test_create_superuser_rejects_non_superuser():
    with pytest.raises(ValueError, match="is_superuser=True"):
        User.objects.create_superuser(
            email="a@b.com", password="x", full_name="A", is_superuser=False
        )
