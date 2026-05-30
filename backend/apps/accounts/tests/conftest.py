"""
Shared fixtures for accounts tests.
"""

from __future__ import annotations

import pytest

from apps.accounts.tests.factories import (
    AddressFactory,
    OtpFactory,
    SuperUserFactory,
    UserFactory,
)


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def admin_user(db):
    return SuperUserFactory()


@pytest.fixture
def address(db, user):
    return AddressFactory(user=user)


@pytest.fixture
def otp(db):
    return OtpFactory()
