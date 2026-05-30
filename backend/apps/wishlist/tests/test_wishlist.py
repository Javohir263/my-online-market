"""
Wishlist API tests.
"""

from __future__ import annotations

import pytest

from apps.accounts.tests.factories import UserFactory
from apps.catalog.tests.factories import ProductFactory
from apps.wishlist.models import WishlistItem

pytestmark = pytest.mark.django_db

LIST_URL = "/api/v1/wishlist/"
ADD_URL = "/api/v1/wishlist/items/"


@pytest.fixture(autouse=True)
def _clear_cache():
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def user_password():
    return "TestPass123!"


@pytest.fixture
def user(user_password):
    return UserFactory(email="wish@example.com", password=user_password)


@pytest.fixture
def authed_api(user, user_password):
    from rest_framework.test import APIClient

    api = APIClient()
    resp = api.post(
        "/api/v1/auth/login/",
        data={"email": user.email, "password": user_password},
        format="json",
    )
    assert resp.status_code == 200
    return api


@pytest.fixture
def product():
    return ProductFactory()


class TestWishlistList:
    def test_anon_forbidden(self):
        from rest_framework.test import APIClient

        api = APIClient()
        resp = api.get(LIST_URL)
        assert resp.status_code in (401, 403)

    def test_empty_list(self, authed_api):
        resp = authed_api.get(LIST_URL)
        assert resp.status_code == 200
        assert resp.data["count"] == 0


class TestWishlistAdd:
    def test_add_creates(self, authed_api, user, product):
        resp = authed_api.post(
            ADD_URL, {"product_id": str(product.id)}, format="json"
        )
        assert resp.status_code == 201
        assert WishlistItem.objects.filter(user=user, product=product).exists()

    def test_add_duplicate_returns_200(self, authed_api, user, product):
        authed_api.post(
            ADD_URL, {"product_id": str(product.id)}, format="json"
        )
        resp = authed_api.post(
            ADD_URL, {"product_id": str(product.id)}, format="json"
        )
        # Idempotent — 200 emas 201 (already exists)
        assert resp.status_code == 200
        assert WishlistItem.objects.filter(user=user).count() == 1

    def test_add_unknown_product_404(self, authed_api):
        from uuid import uuid4

        resp = authed_api.post(
            ADD_URL, {"product_id": str(uuid4())}, format="json"
        )
        assert resp.status_code == 404


class TestWishlistRemove:
    def test_remove(self, authed_api, user, product):
        WishlistItem.objects.create(user=user, product=product)
        resp = authed_api.delete(f"{ADD_URL}{product.id}/")
        assert resp.status_code == 204
        assert WishlistItem.objects.count() == 0

    def test_remove_not_in_wishlist_404(self, authed_api, product):
        resp = authed_api.delete(f"{ADD_URL}{product.id}/")
        assert resp.status_code == 404


class TestWishlistUserScope:
    def test_users_dont_see_others_items(self, authed_api, user, product):
        WishlistItem.objects.create(user=user, product=product)
        other = UserFactory(email="other@example.com")
        other_product = ProductFactory()
        WishlistItem.objects.create(user=other, product=other_product)

        resp = authed_api.get(LIST_URL)
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["product"]["id"] == str(product.id)
