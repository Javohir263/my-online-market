"""
Shared fixtures for authn tests.
"""

from __future__ import annotations

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def _reset_throttle_cache():
    """Throttle counter'lar testlar orasida o'tib ketmasin."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api():
    """DRF API client — enforce_csrf_checks=False by default in tests."""
    return APIClient()


@pytest.fixture
def user_password():
    return "TestPass123!"


@pytest.fixture
def user(db, user_password):
    return UserFactory(email="alice@example.com", password=user_password)


@pytest.fixture
def authed_api(api, user, user_password):
    """API client logged in via /api/v1/auth/login/ (with cookies)."""
    resp = api.post(
        "/api/v1/auth/login/",
        data={"email": user.email, "password": user_password},
        format="json",
    )
    assert resp.status_code == 200, resp.data
    return api
