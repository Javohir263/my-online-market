"""
Shared fixtures for cart tests.
"""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.catalog.tests.factories import ProductFactory, ProductVariantFactory


@pytest.fixture(autouse=True)
def _clear_cache():
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def user_password():
    return "TestPass123!"


@pytest.fixture
def user(user_password):
    return UserFactory(email="cart@example.com", password=user_password)


@pytest.fixture
def authed_api(api, user, user_password):
    resp = api.post(
        "/api/v1/auth/login/",
        data={"email": user.email, "password": user_password},
        format="json",
    )
    assert resp.status_code == 200
    return api


@pytest.fixture
def product():
    return ProductFactory(stock_quantity=10)


@pytest.fixture
def variant(product):
    return ProductVariantFactory(product=product, stock_quantity=5)
