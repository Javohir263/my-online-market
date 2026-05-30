"""
Orders API + services tests:
- Atomic checkout, stock dec, snapshot fields
- Order number unique + format
- Idempotency key returns same order
- FSM transitions allowed/rejected
- Cancel restores stock
- User-scoped detail (no leak)
"""

from __future__ import annotations

import re
from decimal import Decimal

import pytest

from apps.catalog.models import Product, ProductVariant
from apps.orders import services
from apps.orders.models import Order, OrderNumberSequence

from .conftest import _add_to_cart

pytestmark = pytest.mark.django_db

ORDERS_URL = "/api/v1/orders/"


# =============================================================================
# Order number generator
# =============================================================================
class TestOrderNumber:
    def test_format_is_mom_year_padded(self):
        n = services.generate_order_number(year=2026)
        assert re.match(r"^MOM-2026-\d{6}$", n)

    def test_sequential_per_year(self):
        n1 = services.generate_order_number(year=2026)
        n2 = services.generate_order_number(year=2026)
        assert int(n2.split("-")[-1]) == int(n1.split("-")[-1]) + 1

    def test_separate_counters_per_year(self):
        services.generate_order_number(year=2026)
        services.generate_order_number(year=2026)
        first_2027 = services.generate_order_number(year=2027)
        assert first_2027.endswith("000001")


# =============================================================================
# Checkout flow
# =============================================================================
class TestCheckout:
    def test_creates_order_with_snapshots(
        self, authed_api, user, product, shipping_address
    ):
        _add_to_cart(authed_api, product, quantity=2)
        resp = authed_api.post(
            ORDERS_URL,
            {"address_id": shipping_address.id, "customer_note": "leave at door"},
            format="json",
        )
        assert resp.status_code == 201, resp.data
        assert resp.data["status"] == "pending"
        items = resp.data["items"]
        assert len(items) == 1
        assert items[0]["product_name_snapshot"] == product.name
        assert items[0]["product_sku_snapshot"] == product.sku
        assert Decimal(items[0]["price_at_purchase"]) == product.current_price
        assert Decimal(resp.data["total"]) == product.current_price * 2
        assert resp.data["shipping_address"]["city"] == "Toshkent"

    def test_decrements_product_stock(
        self, authed_api, user, product, shipping_address
    ):
        before = product.stock_quantity
        _add_to_cart(authed_api, product, quantity=3)
        authed_api.post(
            ORDERS_URL, {"address_id": shipping_address.id}, format="json"
        )
        product.refresh_from_db()
        assert product.stock_quantity == before - 3

    def test_decrements_variant_stock(
        self, authed_api, user, product, variant, shipping_address
    ):
        before = variant.stock_quantity
        _add_to_cart(authed_api, product, quantity=2, variant_id=variant.id)
        authed_api.post(
            ORDERS_URL, {"address_id": shipping_address.id}, format="json"
        )
        variant.refresh_from_db()
        assert variant.stock_quantity == before - 2

    def test_clears_cart(self, authed_api, user, product, shipping_address):
        _add_to_cart(authed_api, product, quantity=1)
        authed_api.post(
            ORDERS_URL, {"address_id": shipping_address.id}, format="json"
        )
        cart_resp = authed_api.get("/api/v1/cart/")
        assert cart_resp.data["items"] == []

    def test_empty_cart_400(self, authed_api, user, shipping_address):
        resp = authed_api.post(
            ORDERS_URL, {"address_id": shipping_address.id}, format="json"
        )
        assert resp.status_code == 400

    def test_address_must_belong_to_user(
        self, authed_api, user, product, shipping_address
    ):
        # Boshqa user manzili
        from apps.accounts.models import Address
        from apps.accounts.tests.factories import UserFactory

        other = UserFactory(email="other-order@example.com")
        other_addr = Address.objects.create(
            user=other,
            type=Address.Type.SHIPPING,
            recipient_name="X",
            recipient_phone="+998901111111",
            region="X",
            city="X",
            street="X",
            building="1",
        )
        _add_to_cart(authed_api, product, quantity=1)
        resp = authed_api.post(
            ORDERS_URL, {"address_id": other_addr.id}, format="json"
        )
        assert resp.status_code == 404

    def test_anon_forbidden(self, api):
        resp = api.post(ORDERS_URL, {"address_id": 1}, format="json")
        assert resp.status_code in (401, 403)


# =============================================================================
# Idempotency
# =============================================================================
class TestIdempotency:
    def test_same_key_returns_same_order(
        self, authed_api, user, product, shipping_address
    ):
        _add_to_cart(authed_api, product, quantity=1)
        key = "checkout-abc-123"
        r1 = authed_api.post(
            ORDERS_URL,
            {"address_id": shipping_address.id},
            format="json",
            HTTP_X_IDEMPOTENCY_KEY=key,
        )
        # Cart bo'shadi — ikkinchi POST yangi item bo'lmasa ham,
        # idempotency cache shu order'ni qaytaradi
        r2 = authed_api.post(
            ORDERS_URL,
            {"address_id": shipping_address.id},
            format="json",
            HTTP_X_IDEMPOTENCY_KEY=key,
        )
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.data["id"] == r2.data["id"]
        assert Order.objects.count() == 1

    def test_different_keys_different_orders(
        self, authed_api, user, product, shipping_address
    ):
        # 1
        _add_to_cart(authed_api, product, quantity=1)
        r1 = authed_api.post(
            ORDERS_URL,
            {"address_id": shipping_address.id},
            format="json",
            HTTP_X_IDEMPOTENCY_KEY="k1",
        )
        # 2
        _add_to_cart(authed_api, product, quantity=1)
        r2 = authed_api.post(
            ORDERS_URL,
            {"address_id": shipping_address.id},
            format="json",
            HTTP_X_IDEMPOTENCY_KEY="k2",
        )
        assert r1.data["id"] != r2.data["id"]
        assert Order.objects.count() == 2


# =============================================================================
# Detail / list
# =============================================================================
class TestOrderDetail:
    def test_user_scoped_list(
        self, authed_api, user, product, shipping_address
    ):
        _add_to_cart(authed_api, product, quantity=1)
        authed_api.post(
            ORDERS_URL, {"address_id": shipping_address.id}, format="json"
        )
        resp = authed_api.get(ORDERS_URL)
        assert resp.data["count"] == 1

    def test_detail_by_number(
        self, authed_api, user, product, shipping_address
    ):
        _add_to_cart(authed_api, product, quantity=1)
        create = authed_api.post(
            ORDERS_URL, {"address_id": shipping_address.id}, format="json"
        )
        number = create.data["number"]
        resp = authed_api.get(f"{ORDERS_URL}{number}/")
        assert resp.status_code == 200
        assert resp.data["number"] == number

    def test_detail_user_isolation(
        self, authed_api, user, product, shipping_address
    ):
        _add_to_cart(authed_api, product, quantity=1)
        create = authed_api.post(
            ORDERS_URL, {"address_id": shipping_address.id}, format="json"
        )
        number = create.data["number"]

        # Boshqa user — shu order'ni ko'rmaydi
        from rest_framework.test import APIClient

        from apps.accounts.tests.factories import UserFactory

        other = UserFactory(email="snooper@example.com", password="x")
        other_api = APIClient()
        other_api.post(
            "/api/v1/auth/login/",
            {"email": other.email, "password": "x"},
            format="json",
        )
        resp = other_api.get(f"{ORDERS_URL}{number}/")
        assert resp.status_code == 404


# =============================================================================
# FSM transitions
# =============================================================================
class TestFSM:
    def test_allowed_pending_to_confirmed(
        self, authed_api, user, product, shipping_address
    ):
        _add_to_cart(authed_api, product, quantity=1)
        r = authed_api.post(
            ORDERS_URL, {"address_id": shipping_address.id}, format="json"
        )
        order = Order.objects.get(number=r.data["number"])
        services.transition(order, Order.Status.CONFIRMED)
        order.refresh_from_db()
        assert order.status == Order.Status.CONFIRMED
        assert order.confirmed_at is not None

    def test_illegal_transition_rejected(self):
        from apps.orders.exceptions import InvalidStatusTransition

        order = Order(status=Order.Status.PENDING)
        with pytest.raises(InvalidStatusTransition):
            services.transition(order, Order.Status.DELIVERED)

    def test_cancel_endpoint(
        self, authed_api, user, product, shipping_address
    ):
        _add_to_cart(authed_api, product, quantity=2)
        r = authed_api.post(
            ORDERS_URL, {"address_id": shipping_address.id}, format="json"
        )
        number = r.data["number"]
        cancel = authed_api.post(
            f"{ORDERS_URL}{number}/cancel/",
            {"reason": "Changed my mind"},
            format="json",
        )
        assert cancel.status_code == 200
        assert cancel.data["status"] == "cancelled"
        assert cancel.data["cancel_reason"] == "Changed my mind"

    def test_cancel_restores_stock(
        self, authed_api, user, product, shipping_address
    ):
        original = product.stock_quantity
        _add_to_cart(authed_api, product, quantity=3)
        r = authed_api.post(
            ORDERS_URL, {"address_id": shipping_address.id}, format="json"
        )
        product.refresh_from_db()
        assert product.stock_quantity == original - 3
        authed_api.post(f"{ORDERS_URL}{r.data['number']}/cancel/", format="json")
        product.refresh_from_db()
        assert product.stock_quantity == original

    def test_cancel_not_cancellable_after_shipped(
        self, authed_api, user, product, shipping_address
    ):
        _add_to_cart(authed_api, product, quantity=1)
        r = authed_api.post(
            ORDERS_URL, {"address_id": shipping_address.id}, format="json"
        )
        order = Order.objects.get(number=r.data["number"])
        services.transition(order, Order.Status.CONFIRMED)
        services.transition(order, Order.Status.SHIPPED)
        resp = authed_api.post(f"{ORDERS_URL}{order.number}/cancel/", format="json")
        assert resp.status_code == 400
