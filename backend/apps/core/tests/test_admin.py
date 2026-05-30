"""
Admin smoke tests — B12 dashboard, theme, image previews.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import SuperUserFactory
from apps.catalog.tests.factories import (
    BrandFactory,
    CategoryFactory,
    ProductFactory,
)
from apps.orders.models import Order
from apps.orders.services import generate_order_number

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _seed_theme(db):
    """Test DB toza — admin theme'ni seed qilamiz (B12'dagi management command logikasi)."""
    from django.core.management import call_command

    call_command("seed_admin_theme", verbosity=0)


@pytest.fixture
def admin_user():
    return SuperUserFactory(
        email="adm@example.com", password="AdmPass123!"
    )


@pytest.fixture
def admin_client(admin_user):
    """Django session-based admin login."""
    from django.test import Client

    c = Client()
    assert c.login(email="adm@example.com", password="AdmPass123!")
    return c


# =============================================================================
# Dashboard
# =============================================================================
class TestAdminDashboard:
    def test_index_renders_200(self, admin_client):
        resp = admin_client.get("/admin/")
        assert resp.status_code == 200

    def test_kpi_data_available_on_request(self, rf, admin_user):
        """Direct unit test of `_today_kpis()` so we don't depend on
        admin template rendering details."""
        from apps.core.dashboard import _today_kpis

        Order.objects.create(
            number=generate_order_number(year=2026),
            user=admin_user,
            status=Order.Status.PENDING,
            subtotal=Decimal("100"),
            total=Decimal("100"),
            shipping_address={},
        )
        kpis = _today_kpis()
        assert kpis["orders_today"] >= 1
        assert kpis["orders_pending"] >= 1
        assert "low_stock_count" in kpis
        assert "pending_reviews" in kpis
        assert isinstance(kpis["recent_orders"], list)


# =============================================================================
# Theme (admin_interface.Theme exists)
# =============================================================================
class TestThemeSeeded:
    def test_theme_exists(self):
        from admin_interface.models import Theme

        themes = Theme.objects.all()
        assert themes.count() >= 1


# =============================================================================
# Model admin list views — smoke (200 responses)
# =============================================================================
class TestAdminListViews:
    @pytest.mark.parametrize(
        "path",
        [
            "/admin/accounts/user/",
            "/admin/catalog/product/",
            "/admin/catalog/category/",
            "/admin/catalog/brand/",
            "/admin/orders/order/",
            "/admin/promotions/banner/",
            "/admin/promotions/coupon/",
            "/admin/reviews/review/",
            "/admin/notifications/notification/",
            "/admin/notifications/emaillog/",
            "/admin/vendors/vendor/",
        ],
    )
    def test_admin_list_renders(self, admin_client, path):
        # Seed minimal data — catalogue empty also fine
        BrandFactory()
        CategoryFactory()
        ProductFactory(stock_quantity=2)
        resp = admin_client.get(path)
        assert resp.status_code == 200, f"{path} → {resp.status_code}"
