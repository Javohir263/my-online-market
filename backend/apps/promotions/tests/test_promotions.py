"""
Promotions tests — Banner, Coupon validation, discount calc, checkout integration.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Address
from apps.accounts.tests.factories import UserFactory
from apps.catalog.tests.factories import ProductFactory
from apps.orders.models import Order
from apps.promotions import services
from apps.promotions.exceptions import (
    CouponExpired,
    CouponInactive,
    CouponLimitReached,
    CouponMinNotMet,
    CouponNotFound,
    CouponPerUserLimitReached,
)
from apps.promotions.models import Banner, Coupon, CouponUsage

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _clear_cache():
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def password():
    return "TestPass123!"


@pytest.fixture
def user(password):
    return UserFactory(email="promo@example.com", password=password)


@pytest.fixture
def authed_api(user, password):
    api = APIClient()
    api.post(
        "/api/v1/auth/login/",
        {"email": user.email, "password": password},
        format="json",
    )
    return api


# =============================================================================
# Service: validate_coupon
# =============================================================================
class TestValidate:
    def test_not_found(self):
        with pytest.raises(CouponNotFound):
            services.validate_coupon(code="NOPE", user=None, subtotal=Decimal("100"))

    def test_inactive_rejected(self):
        Coupon.objects.create(code="OFF", value=10, is_active=False)
        with pytest.raises(CouponInactive):
            services.validate_coupon(code="OFF", user=None, subtotal=Decimal("100"))

    def test_expired_rejected(self):
        Coupon.objects.create(
            code="OLD",
            value=10,
            valid_to=timezone.now() - timedelta(days=1),
        )
        with pytest.raises(CouponExpired):
            services.validate_coupon(code="OLD", user=None, subtotal=Decimal("100"))

    def test_not_started_rejected(self):
        Coupon.objects.create(
            code="FUTURE",
            value=10,
            valid_from=timezone.now() + timedelta(days=1),
        )
        with pytest.raises(CouponExpired):
            services.validate_coupon(code="FUTURE", user=None, subtotal=Decimal("100"))

    def test_min_order_not_met(self):
        Coupon.objects.create(
            code="MIN", value=10, min_order_amount=Decimal("500")
        )
        with pytest.raises(CouponMinNotMet):
            services.validate_coupon(code="MIN", user=None, subtotal=Decimal("100"))

    def test_global_limit_reached(self):
        Coupon.objects.create(
            code="LIM", value=10, usage_limit=5, used_count=5
        )
        with pytest.raises(CouponLimitReached):
            services.validate_coupon(code="LIM", user=None, subtotal=Decimal("100"))

    def test_per_user_limit(self, user):
        c = Coupon.objects.create(code="PU", value=10, per_user_limit=1)
        # Mock prior usage
        from apps.accounts.models import Address as _Addr
        order = Order.objects.create(
            number="MOM-2026-000999",
            user=user,
            status=Order.Status.PENDING,
            subtotal=Decimal("100"),
            total=Decimal("100"),
            shipping_address={},
        )
        CouponUsage.objects.create(coupon=c, user=user, order=order)

        with pytest.raises(CouponPerUserLimitReached):
            services.validate_coupon(code="PU", user=user, subtotal=Decimal("100"))


# =============================================================================
# Service: calc_discount
# =============================================================================
class TestDiscountCalc:
    def test_percentage(self):
        c = Coupon.objects.create(code="P", type=Coupon.Type.PERCENTAGE, value=20)
        assert services.calc_discount(c, Decimal("100")) == Decimal("20.00")

    def test_percentage_with_cap(self):
        c = Coupon.objects.create(
            code="P",
            type=Coupon.Type.PERCENTAGE,
            value=50,
            max_discount=Decimal("30"),
        )
        # 50% of 100 = 50 → capped at 30
        assert services.calc_discount(c, Decimal("100")) == Decimal("30.00")

    def test_fixed(self):
        c = Coupon.objects.create(
            code="F", type=Coupon.Type.FIXED, value=Decimal("25.00")
        )
        assert services.calc_discount(c, Decimal("100")) == Decimal("25.00")

    def test_capped_at_subtotal(self):
        c = Coupon.objects.create(
            code="OVER", type=Coupon.Type.FIXED, value=Decimal("200")
        )
        # subtotal 50 → discount 50, not 200
        assert services.calc_discount(c, Decimal("50")) == Decimal("50.00")


# =============================================================================
# Banners API
# =============================================================================
class TestBanners:
    def test_filter_by_position(self):
        Banner.objects.create(
            image="x.jpg", title="A", position=Banner.Position.HERO
        )
        Banner.objects.create(
            image="x.jpg", title="B", position=Banner.Position.FOOTER
        )
        api = APIClient()
        resp = api.get("/api/v1/promotions/banners/?position=hero")
        assert resp.status_code == 200
        titles = [b["title"] for b in resp.data]
        assert titles == ["A"]

    def test_inactive_hidden(self):
        Banner.objects.create(
            image="x.jpg", title="A", position=Banner.Position.HERO
        )
        Banner.objects.create(
            image="x.jpg",
            title="B",
            position=Banner.Position.HERO,
            is_active=False,
        )
        resp = APIClient().get("/api/v1/promotions/banners/")
        titles = [b["title"] for b in resp.data]
        assert titles == ["A"]


# =============================================================================
# Coupon validate endpoint
# =============================================================================
class TestCouponValidateEndpoint:
    def test_returns_discount(self):
        Coupon.objects.create(code="VAL", value=10)
        resp = APIClient().post(
            "/api/v1/promotions/coupons/validate/",
            {"code": "VAL", "subtotal": "500"},
            format="json",
        )
        assert resp.status_code == 200
        # 10% of 500 = 50
        assert Decimal(resp.data["discount_amount"]) == Decimal("50.00")


# =============================================================================
# Cart coupon apply / remove
# =============================================================================
class TestCartCoupon:
    def test_apply_sets_coupon(self, authed_api, user):
        Coupon.objects.create(code="HELLO", value=15)
        product = ProductFactory(
            stock_quantity=5, base_price=Decimal("1000")
        )
        authed_api.post(
            "/api/v1/cart/items/",
            {"product_id": str(product.id), "quantity": 2},
            format="json",
        )
        resp = authed_api.post(
            "/api/v1/cart/coupon/apply/",
            {"code": "HELLO"},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.data["coupon"]["code"] == "HELLO"
        # 15% of 2000 = 300
        assert Decimal(resp.data["discount_amount"]) == Decimal("300.00")
        assert Decimal(resp.data["total"]) == Decimal("1700.00")

    def test_remove(self, authed_api):
        c = Coupon.objects.create(code="REM", value=5)
        product = ProductFactory(stock_quantity=5)
        authed_api.post(
            "/api/v1/cart/items/",
            {"product_id": str(product.id), "quantity": 1},
            format="json",
        )
        authed_api.post(
            "/api/v1/cart/coupon/apply/", {"code": "REM"}, format="json"
        )
        resp = authed_api.delete("/api/v1/cart/coupon/")
        assert resp.status_code == 200
        assert resp.data["coupon"] is None


# =============================================================================
# Checkout — coupon snapshot + CouponUsage + used_count
# =============================================================================
class TestCheckoutWithCoupon:
    def test_creates_coupon_usage_and_increments_used_count(
        self, authed_api, user
    ):
        Coupon.objects.create(code="CK", value=10)
        product = ProductFactory(
            stock_quantity=5, base_price=Decimal("1000")
        )
        address = Address.objects.create(
            user=user,
            type=Address.Type.SHIPPING,
            recipient_name="x",
            recipient_phone="+998901234567",
            region="r",
            city="c",
            street="s",
            building="1",
        )

        authed_api.post(
            "/api/v1/cart/items/",
            {"product_id": str(product.id), "quantity": 1},
            format="json",
        )
        authed_api.post(
            "/api/v1/cart/coupon/apply/", {"code": "CK"}, format="json"
        )
        resp = authed_api.post(
            "/api/v1/orders/",
            {"address_id": address.id},
            format="json",
        )
        assert resp.status_code == 201
        # 10% of 1000 = 100
        assert Decimal(resp.data["discount_amount"]) == Decimal("100.00")
        assert Decimal(resp.data["total"]) == Decimal("900.00")

        c = Coupon.objects.get(code="CK")
        assert c.used_count == 1
        assert CouponUsage.objects.filter(coupon=c, user=user).count() == 1
