"""
Shared fixtures for orders tests.
"""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Address
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
    return UserFactory(email="orderer@example.com", password=user_password)


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
def shipping_address(user):
    return Address.objects.create(
        user=user,
        type=Address.Type.SHIPPING,
        recipient_name="Test Recipient",
        recipient_phone="+998901234567",
        region="Toshkent viloyati",
        city="Toshkent",
        street="Mustaqillik",
        building="42",
    )


@pytest.fixture
def product():
    return ProductFactory(stock_quantity=10)


@pytest.fixture
def variant(product):
    return ProductVariantFactory(product=product, stock_quantity=5)


def _add_to_cart(api, product, quantity=1, variant_id=None):
    payload = {"product_id": str(product.id), "quantity": quantity}
    if variant_id is not None:
        payload["variant_id"] = variant_id
    resp = api.post("/api/v1/cart/items/", payload, format="json")
    assert resp.status_code == 201, resp.data
    return resp.data
