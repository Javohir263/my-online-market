"""
EmailBackend tests — case-insensitive email login.
"""

from __future__ import annotations

import pytest
from django.contrib.auth import authenticate

from apps.accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_login_with_exact_email():
    UserFactory(email="user@example.com", password="secret123")
    user = authenticate(username="user@example.com", password="secret123")
    assert user is not None
    assert user.email == "user@example.com"


def test_login_with_mixed_case_email():
    UserFactory(email="user@example.com", password="secret123")
    user = authenticate(username="User@Example.COM", password="secret123")
    assert user is not None
    assert user.email == "user@example.com"


def test_login_with_wrong_password_fails():
    UserFactory(email="user@example.com", password="secret123")
    assert authenticate(username="user@example.com", password="wrong") is None


def test_login_with_unknown_email_fails():
    assert (
        authenticate(username="nobody@example.com", password="any") is None
    )


def test_login_inactive_user_fails():
    UserFactory(email="user@example.com", password="x", is_active=False)
    assert authenticate(username="user@example.com", password="x") is None


def test_login_strips_whitespace():
    UserFactory(email="user@example.com", password="secret123")
    user = authenticate(username="  user@example.com  ", password="secret123")
    assert user is not None
