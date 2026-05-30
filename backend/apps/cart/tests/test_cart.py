"""
Cart API + merge flow tests.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from apps.cart.models import Cart, CartItem
from apps.catalog.tests.factories import ProductFactory

pytestmark = pytest.mark.django_db

CART_URL = "/api/v1/cart/"
ITEMS_URL = "/api/v1/cart/items/"
MERGE_URL = "/api/v1/cart/merge/"


class TestCartDetail:
    def test_anon_get_creates_session_cart(self, api):
        resp = api.get(CART_URL)
        assert resp.status_code == 200
        assert resp.data["items"] == []
        # Yangi session_key bilan cart yaratildi
        assert Cart.objects.filter(session_key__isnull=False).count() == 1

    def test_auth_get_creates_user_cart(self, authed_api, user):
        resp = authed_api.get(CART_URL)
        assert resp.status_code == 200
        assert Cart.objects.filter(user=user).count() == 1


class TestCartItemAdd:
    def test_add_creates_item(self, api, product):
        resp = api.post(
            ITEMS_URL, {"product_id": str(product.id), "quantity": 2}, format="json"
        )
        assert resp.status_code == 201
        assert resp.data["quantity"] == 2
        assert Decimal(resp.data["price_snapshot"]) == product.current_price

    def test_add_is_idempotent(self, api, product):
        api.post(ITEMS_URL, {"product_id": str(product.id), "quantity": 2}, format="json")
        resp = api.post(
            ITEMS_URL, {"product_id": str(product.id), "quantity": 3}, format="json"
        )
        assert resp.status_code == 201
        assert resp.data["quantity"] == 5  # 2 + 3
        assert CartItem.objects.count() == 1

    def test_add_respects_stock(self, api, product):
        resp = api.post(
            ITEMS_URL, {"product_id": str(product.id), "quantity": 99}, format="json"
        )
        assert resp.status_code == 400

    def test_add_with_variant(self, api, product, variant):
        resp = api.post(
            ITEMS_URL,
            {"product_id": str(product.id), "variant_id": variant.id, "quantity": 3},
            format="json",
        )
        assert resp.status_code == 201
        assert resp.data["variant"]["id"] == variant.id

    def test_add_inactive_product_404(self, api):
        p = ProductFactory(is_active=False, stock_quantity=10)
        resp = api.post(
            ITEMS_URL, {"product_id": str(p.id), "quantity": 1}, format="json"
        )
        assert resp.status_code == 404


class TestCartItemUpdate:
    def test_update_quantity(self, api, product):
        add = api.post(
            ITEMS_URL, {"product_id": str(product.id), "quantity": 1}, format="json"
        )
        item_id = add.data["id"]
        resp = api.patch(
            f"{ITEMS_URL}{item_id}/", {"quantity": 4}, format="json"
        )
        assert resp.status_code == 200
        assert resp.data["quantity"] == 4

    def test_update_respects_stock(self, api, product):
        add = api.post(
            ITEMS_URL, {"product_id": str(product.id), "quantity": 1}, format="json"
        )
        item_id = add.data["id"]
        resp = api.patch(
            f"{ITEMS_URL}{item_id}/", {"quantity": 99}, format="json"
        )
        assert resp.status_code == 400

    def test_update_unknown_item_404(self, api):
        resp = api.patch(f"{ITEMS_URL}999/", {"quantity": 1}, format="json")
        assert resp.status_code == 404


class TestCartItemRemove:
    def test_remove(self, api, product):
        add = api.post(
            ITEMS_URL, {"product_id": str(product.id), "quantity": 1}, format="json"
        )
        item_id = add.data["id"]
        resp = api.delete(f"{ITEMS_URL}{item_id}/")
        assert resp.status_code == 204
        assert CartItem.objects.count() == 0


class TestCartClear:
    def test_clear(self, api, product):
        api.post(ITEMS_URL, {"product_id": str(product.id), "quantity": 1}, format="json")
        resp = api.delete(CART_URL)
        assert resp.status_code == 204
        assert CartItem.objects.count() == 0


class TestCartSubtotal:
    def test_subtotal_is_sum_of_line_totals(self, api):
        p1 = ProductFactory(stock_quantity=10)
        p2 = ProductFactory(stock_quantity=10)
        api.post(
            ITEMS_URL, {"product_id": str(p1.id), "quantity": 2}, format="json"
        )
        api.post(
            ITEMS_URL, {"product_id": str(p2.id), "quantity": 3}, format="json"
        )
        resp = api.get(CART_URL)
        expected = (p1.current_price * 2) + (p2.current_price * 3)
        assert Decimal(resp.data["subtotal"]) == expected
        assert resp.data["items_count"] == 5


class TestCartMerge:
    def test_login_auto_merges_anon_cart(self, api, user, user_password, product):
        # 1. Anon sifatida cart'ga add
        api.post(
            ITEMS_URL, {"product_id": str(product.id), "quantity": 2}, format="json"
        )
        # 2. Login → signal anon cart'ni user cart'ga ko'chiradi
        resp = api.post(
            "/api/v1/auth/login/",
            data={"email": user.email, "password": user_password},
            format="json",
        )
        assert resp.status_code == 200

        # 3. Endi /cart/ chaqirsak user cart'ni ko'ramiz, va anon item'lar bor
        cart_resp = api.get(CART_URL)
        assert cart_resp.status_code == 200
        assert len(cart_resp.data["items"]) == 1
        assert cart_resp.data["items"][0]["quantity"] == 2

        # Anon cart o'chirilgan
        assert not Cart.objects.filter(session_key__isnull=False).exists()

    def test_merge_combines_quantities(
        self, api, user, user_password, product
    ):
        # 1. Anon: 2x product
        api.post(
            ITEMS_URL, {"product_id": str(product.id), "quantity": 2}, format="json"
        )
        # 2. User'ga manual cart yaratamiz (avval login bo'lmagan boshqa session
        #    — bu testda biz simulyatsiya qilamiz)
        from apps.cart.models import Cart, CartItem

        user_cart = Cart.objects.create(user=user)
        CartItem.objects.create(
            cart=user_cart,
            product=product,
            quantity=3,
            price_snapshot=product.current_price,
        )
        # 3. Login → merge: 2 + 3 = 5
        api.post(
            "/api/v1/auth/login/",
            data={"email": user.email, "password": user_password},
            format="json",
        )
        cart_resp = api.get(CART_URL)
        items = cart_resp.data["items"]
        assert len(items) == 1
        assert items[0]["quantity"] == 5

    def test_manual_merge_endpoint(self, authed_api, user, product):
        # Already authed_api; manual merge — empty merge (no anon cart)
        resp = authed_api.post(MERGE_URL)
        assert resp.status_code == 200
