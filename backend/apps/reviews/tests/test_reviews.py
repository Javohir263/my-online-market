"""
Reviews API + services tests.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Address
from apps.accounts.tests.factories import UserFactory
from apps.catalog.models import Product
from apps.catalog.tests.factories import ProductFactory
from apps.orders.models import Order, OrderItem
from apps.orders.services import generate_order_number
from apps.reviews import services
from apps.reviews.models import HelpfulVote, Review

pytestmark = pytest.mark.django_db

PRODUCT_REVIEWS_URL = "/api/v1/reviews/products/{slug}/"
CREATE_URL = "/api/v1/reviews/"
DETAIL_URL = "/api/v1/reviews/{pk}/"
HELPFUL_URL = "/api/v1/reviews/{pk}/helpful/"


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
    return UserFactory(email="reviewer@example.com", password=password)


@pytest.fixture
def authed_api(user, password):
    api = APIClient()
    api.post(
        "/api/v1/auth/login/",
        {"email": user.email, "password": password},
        format="json",
    )
    return api


@pytest.fixture
def product():
    return ProductFactory(stock_quantity=10)


def _completed_order(user, product, quantity=1):
    """Tezkor helper: confirmed buyurtma yaratish (verified-purchase uchun)."""
    order = Order.objects.create(
        number=generate_order_number(year=2026),
        user=user,
        status=Order.Status.CONFIRMED,
        currency="UZS",
        subtotal=product.current_price * quantity,
        total=product.current_price * quantity,
        shipping_address={"city": "Toshkent"},
    )
    from apps.vendors.models import Vendor

    OrderItem.objects.create(
        order=order,
        product=product,
        vendor=Vendor.objects.get_default(),
        quantity=quantity,
        price_at_purchase=product.current_price,
        product_name_snapshot=product.name,
        product_sku_snapshot=product.sku,
    )
    return order


# =============================================================================
# Service: verified-purchase detection
# =============================================================================
class TestVerifiedPurchase:
    def test_no_order_returns_false(self, user, product):
        assert services.detect_verified_purchase(user, product) is False

    def test_with_completed_order_returns_true(self, user, product):
        _completed_order(user, product)
        assert services.detect_verified_purchase(user, product) is True

    def test_pending_order_does_not_count(self, user, product):
        Order.objects.create(
            number=generate_order_number(year=2026),
            user=user,
            status=Order.Status.PENDING,
            currency="UZS",
            subtotal=Decimal("100"),
            total=Decimal("100"),
            shipping_address={},
        )
        assert services.detect_verified_purchase(user, product) is False


# =============================================================================
# Create
# =============================================================================
class TestCreateReview:
    def test_create_pending_by_default(self, authed_api, user, product):
        resp = authed_api.post(
            CREATE_URL,
            {
                "product_id": str(product.id),
                "rating": 5,
                "title": "Great",
                "content": "Loved it",
            },
            format="json",
        )
        assert resp.status_code == 201, resp.data
        assert resp.data["status"] == "pending"
        assert resp.data["rating"] == 5

    def test_verified_purchase_auto_set(self, authed_api, user, product):
        _completed_order(user, product)
        resp = authed_api.post(
            CREATE_URL,
            {"product_id": str(product.id), "rating": 4, "content": "ok"},
            format="json",
        )
        assert resp.status_code == 201
        assert resp.data["is_verified_purchase"] is True

    def test_unique_per_user_product(self, authed_api, user, product):
        authed_api.post(
            CREATE_URL,
            {"product_id": str(product.id), "rating": 5, "content": "a"},
            format="json",
        )
        resp = authed_api.post(
            CREATE_URL,
            {"product_id": str(product.id), "rating": 4, "content": "b"},
            format="json",
        )
        assert resp.status_code == 400

    def test_anon_forbidden(self, product):
        api = APIClient()
        resp = api.post(
            CREATE_URL,
            {"product_id": str(product.id), "rating": 5, "content": "x"},
            format="json",
        )
        assert resp.status_code in (401, 403)


# =============================================================================
# List (product reviews) — public, only approved
# =============================================================================
class TestProductReviews:
    def test_only_approved_visible(self, user, product):
        Review.objects.create(
            user=user, product=product, rating=5, content="visible",
            status=Review.Status.APPROVED,
        )
        Review.objects.create(
            user=UserFactory(email="b@x.com"), product=product, rating=4,
            content="pending", status=Review.Status.PENDING,
        )
        api = APIClient()
        resp = api.get(PRODUCT_REVIEWS_URL.format(slug=product.slug))
        assert resp.status_code == 200
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["content"] == "visible"


# =============================================================================
# Update / delete (own only)
# =============================================================================
class TestReviewOwnership:
    def test_update_own_resets_status_to_pending(self, authed_api, user, product):
        review = Review.objects.create(
            user=user, product=product, rating=4, content="ok",
            status=Review.Status.APPROVED,
        )
        resp = authed_api.put(
            DETAIL_URL.format(pk=review.pk),
            {"rating": 5, "content": "edited"},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.data["rating"] == 5
        assert resp.data["status"] == "pending"  # qaytadan moderatsiyaga

    def test_cannot_edit_others(self, authed_api, user, product):
        other = UserFactory(email="other-rev@example.com")
        review = Review.objects.create(
            user=other, product=product, rating=4, content="theirs",
        )
        resp = authed_api.put(
            DETAIL_URL.format(pk=review.pk),
            {"rating": 1},
            format="json",
        )
        assert resp.status_code in (403, 404)

    def test_delete_own(self, authed_api, user, product):
        review = Review.objects.create(
            user=user, product=product, rating=5, content="x"
        )
        resp = authed_api.delete(DETAIL_URL.format(pk=review.pk))
        assert resp.status_code == 204
        assert not Review.objects.filter(pk=review.pk).exists()


# =============================================================================
# Helpful toggle
# =============================================================================
class TestHelpful:
    def test_first_vote_increments(self, authed_api, user, product):
        other = UserFactory(email="auth-rev@example.com")
        review = Review.objects.create(
            user=other, product=product, rating=5, content="x",
            status=Review.Status.APPROVED,
        )
        resp = authed_api.post(HELPFUL_URL.format(pk=review.pk))
        assert resp.status_code == 200
        assert resp.data == {"is_voted": True, "helpful_count": 1}

    def test_second_vote_toggles_off(self, authed_api, user, product):
        other = UserFactory(email="auth-rev2@example.com")
        review = Review.objects.create(
            user=other, product=product, rating=5, content="x",
            status=Review.Status.APPROVED,
        )
        authed_api.post(HELPFUL_URL.format(pk=review.pk))
        resp = authed_api.post(HELPFUL_URL.format(pk=review.pk))
        assert resp.data == {"is_voted": False, "helpful_count": 0}
        assert HelpfulVote.objects.filter(user=user, review=review).count() == 0


# =============================================================================
# Signal: Product.ratings_avg/count recompute
# =============================================================================
class TestRatingRecompute:
    def test_approved_review_updates_product_rating(self, user, product):
        Review.objects.create(
            user=user, product=product, rating=5, content="a",
            status=Review.Status.APPROVED,
        )
        product.refresh_from_db()
        assert product.ratings_count == 1
        assert product.ratings_avg == Decimal("5.00")

    def test_pending_review_does_not_count(self, user, product):
        Review.objects.create(
            user=user, product=product, rating=5, content="x",
            status=Review.Status.PENDING,
        )
        product.refresh_from_db()
        assert product.ratings_count == 0
        assert product.ratings_avg == Decimal("0.00")

    def test_avg_across_multiple_approved(self, product):
        u1 = UserFactory(email="r1@x.com")
        u2 = UserFactory(email="r2@x.com")
        Review.objects.create(
            user=u1, product=product, rating=4, content="a",
            status=Review.Status.APPROVED,
        )
        Review.objects.create(
            user=u2, product=product, rating=5, content="b",
            status=Review.Status.APPROVED,
        )
        product.refresh_from_db()
        assert product.ratings_count == 2
        assert product.ratings_avg == Decimal("4.50")

    def test_delete_review_recomputes(self, user, product):
        r = Review.objects.create(
            user=user, product=product, rating=5, content="x",
            status=Review.Status.APPROVED,
        )
        product.refresh_from_db()
        assert product.ratings_count == 1
        r.delete()
        product.refresh_from_db()
        assert product.ratings_count == 0
        assert product.ratings_avg == Decimal("0.00")
