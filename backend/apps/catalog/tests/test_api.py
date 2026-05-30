"""
Catalog API tests — 10+ endpoint.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.catalog.models import Product
from apps.catalog.tests.factories import (
    BrandFactory,
    CategoryFactory,
    ProductFactory,
    ProductImageFactory,
    ProductTagFactory,
)

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _clear_cache():
    """Category tree cache testlar orasida tozalansin."""
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api():
    return APIClient()


# =============================================================================
# Categories
# =============================================================================
class TestCategoryTree:
    URL = "/api/v1/catalog/categories/"

    def test_returns_root_categories(self, api):
        CategoryFactory(name="Electronics")
        CategoryFactory(name="Fashion")
        resp = api.get(self.URL)
        assert resp.status_code == 200
        assert len(resp.data) == 2

    def test_nested_children_present(self, api):
        root = CategoryFactory(name="Electronics")
        sub = CategoryFactory(name="Phones", parent=root)
        CategoryFactory(name="iPhone", parent=sub)

        resp = api.get(self.URL)
        assert resp.status_code == 200
        root_node = next(n for n in resp.data if n["slug"] == root.slug)
        assert len(root_node["children"]) == 1
        sub_node = root_node["children"][0]
        assert sub_node["slug"] == sub.slug
        assert len(sub_node["children"]) == 1

    def test_inactive_excluded(self, api):
        CategoryFactory(name="Visible")
        CategoryFactory(name="Hidden", is_active=False)
        resp = api.get(self.URL)
        slugs = [n["slug"] for n in resp.data]
        assert len(slugs) == 1


class TestCategoryDetail:
    def test_detail_with_ancestors(self, api):
        root = CategoryFactory(name="Electronics", slug="electronics")
        leaf = CategoryFactory(name="iPhone", slug="iphone", parent=root)
        resp = api.get(f"/api/v1/catalog/categories/{leaf.slug}/")
        assert resp.status_code == 200
        assert resp.data["slug"] == "iphone"
        assert len(resp.data["parents"]) == 1
        assert resp.data["parents"][0]["slug"] == "electronics"

    def test_404_unknown(self, api):
        resp = api.get("/api/v1/catalog/categories/missing/")
        assert resp.status_code == 404


# =============================================================================
# Brands
# =============================================================================
class TestBrandList:
    URL = "/api/v1/catalog/brands/"

    def test_returns_active_brands(self, api):
        BrandFactory(name="Apple")
        BrandFactory(name="Samsung")
        BrandFactory(name="Inactive", is_active=False)
        resp = api.get(self.URL)
        assert resp.status_code == 200
        names = [b["name"] for b in resp.data]
        assert set(names) == {"Apple", "Samsung"}


# =============================================================================
# Products — list / filter / sort / search
# =============================================================================
class TestProductList:
    URL = "/api/v1/catalog/products/"

    def test_list_paginated(self, api):
        for _ in range(3):
            ProductFactory()
        resp = api.get(self.URL)
        assert resp.status_code == 200
        assert resp.data["count"] == 3
        assert "results" in resp.data

    def test_filter_by_category(self, api):
        cat_a = CategoryFactory(slug="cat-a")
        cat_b = CategoryFactory(slug="cat-b")
        ProductFactory(category=cat_a, name="A1")
        ProductFactory(category=cat_a, name="A2")
        ProductFactory(category=cat_b, name="B1")

        resp = api.get(self.URL, {"category": "cat-a"})
        names = [p["name"] for p in resp.data["results"]]
        assert set(names) == {"A1", "A2"}

    def test_filter_by_brand(self, api):
        b1 = BrandFactory(slug="apple")
        b2 = BrandFactory(slug="samsung")
        ProductFactory(brand=b1, name="iPhone")
        ProductFactory(brand=b2, name="Galaxy")
        resp = api.get(self.URL, {"brand": "apple"})
        assert resp.data["count"] == 1

    def test_filter_min_max_price(self, api):
        ProductFactory(base_price=Decimal("100"), name="A")
        ProductFactory(base_price=Decimal("500"), name="B")
        ProductFactory(base_price=Decimal("1000"), name="C")
        resp = api.get(self.URL, {"min_price": 200, "max_price": 800})
        names = [p["name"] for p in resp.data["results"]]
        assert names == ["B"]

    def test_filter_max_price_considers_sale(self, api):
        ProductFactory(
            base_price=Decimal("1000"),
            sale_price=Decimal("500"),
            name="On-sale",
        )
        resp = api.get(self.URL, {"max_price": 600})
        names = [p["name"] for p in resp.data["results"]]
        assert "On-sale" in names

    def test_filter_in_stock(self, api):
        ProductFactory(stock_quantity=5, name="In")
        out = ProductFactory(stock_quantity=0, name="Out")
        out.is_in_stock = False
        out.save(update_fields=["is_in_stock"])
        resp = api.get(self.URL, {"in_stock": True})
        names = [p["name"] for p in resp.data["results"]]
        assert names == ["In"]

    def test_filter_rating_gte(self, api):
        p1 = ProductFactory(name="Hi")
        p1.ratings_avg = Decimal("4.5")
        p1.save(update_fields=["ratings_avg"])
        p2 = ProductFactory(name="Lo")
        p2.ratings_avg = Decimal("3.0")
        p2.save(update_fields=["ratings_avg"])
        resp = api.get(self.URL, {"rating": 4})
        names = [p["name"] for p in resp.data["results"]]
        assert names == ["Hi"]

    def test_sort_alias_price_asc(self, api):
        ProductFactory(name="Cheap", base_price=Decimal("100"))
        ProductFactory(name="Mid", base_price=Decimal("500"))
        ProductFactory(name="Pricey", base_price=Decimal("900"))
        resp = api.get(self.URL, {"sort": "price"})
        names = [p["name"] for p in resp.data["results"]]
        assert names == ["Cheap", "Mid", "Pricey"]

    def test_sort_alias_rating_desc(self, api):
        # "rating" alias = -ratings_avg (yuqori birinchi)
        p1 = ProductFactory(name="A")
        p2 = ProductFactory(name="B")
        Product.objects.filter(pk=p1.pk).update(ratings_avg=Decimal("3.0"))
        Product.objects.filter(pk=p2.pk).update(ratings_avg=Decimal("4.5"))
        resp = api.get(self.URL, {"sort": "rating"})
        names = [p["name"] for p in resp.data["results"]]
        assert names == ["B", "A"]

    def test_search_icontains(self, api):
        ProductFactory(name="iPhone 15 Pro")
        ProductFactory(name="Galaxy S25")
        resp = api.get(self.URL, {"search": "iphone"})
        assert resp.data["count"] == 1


# =============================================================================
# ProductDetail + views_count
# =============================================================================
class TestProductDetail:
    def test_returns_full_payload(self, api):
        p = ProductFactory()
        ProductImageFactory(product=p, is_primary=True)
        resp = api.get(f"/api/v1/catalog/products/{p.slug}/")
        assert resp.status_code == 200
        assert "images" in resp.data
        assert "variants" in resp.data
        assert "attributes" in resp.data
        assert "tags" in resp.data

    def test_views_count_increments(self, api):
        p = ProductFactory()
        api.get(f"/api/v1/catalog/products/{p.slug}/")
        api.get(f"/api/v1/catalog/products/{p.slug}/")
        p.refresh_from_db()
        assert p.views_count == 2

    def test_inactive_404(self, api):
        p = ProductFactory(is_active=False)
        resp = api.get(f"/api/v1/catalog/products/{p.slug}/")
        assert resp.status_code == 404


# =============================================================================
# Curated lists
# =============================================================================
class TestCurated:
    def test_featured(self, api):
        ProductFactory(is_featured=True, name="A")
        ProductFactory(is_featured=False, name="B")
        resp = api.get("/api/v1/catalog/products/featured/")
        assert resp.status_code == 200
        names = [p["name"] for p in resp.data]
        assert names == ["A"]

    def test_new_arrivals(self, api):
        ProductFactory(is_new=True, name="Yangi")
        ProductFactory(is_new=False, name="Eski")
        resp = api.get("/api/v1/catalog/products/new-arrivals/")
        names = [p["name"] for p in resp.data]
        assert names == ["Yangi"]

    def test_bestsellers(self, api):
        ProductFactory(is_bestseller=True, name="Pop")
        ProductFactory(is_bestseller=False, name="Niche")
        resp = api.get("/api/v1/catalog/products/bestsellers/")
        names = [p["name"] for p in resp.data]
        assert names == ["Pop"]

    def test_curated_respects_limit(self, api):
        for i in range(5):
            ProductFactory(is_featured=True, name=f"P{i}")
        resp = api.get("/api/v1/catalog/products/featured/", {"limit": 3})
        assert len(resp.data) == 3


# =============================================================================
# Similar products
# =============================================================================
class TestSimilar:
    def test_same_category_excludes_self(self, api):
        cat = CategoryFactory()
        target = ProductFactory(category=cat, slug="target")
        ProductFactory(category=cat)
        ProductFactory(category=cat)
        ProductFactory(category=CategoryFactory())  # different cat

        resp = api.get(f"/api/v1/catalog/products/{target.slug}/similar/")
        assert resp.status_code == 200
        slugs = [p["slug"] for p in resp.data]
        assert target.slug not in slugs
        assert len(slugs) == 2

    def test_unknown_product_404(self, api):
        resp = api.get("/api/v1/catalog/products/missing/similar/")
        assert resp.status_code == 404


# =============================================================================
# Search + suggest
# =============================================================================
class TestSearch:
    def test_search_empty_q(self, api):
        resp = api.get("/api/v1/catalog/search/")
        assert resp.status_code == 200
        assert resp.data["count"] == 0

    def test_search_matches_name(self, api):
        ProductFactory(name="iPhone 15", slug="iphone-15", sku="IPH-15")
        ProductFactory(name="Galaxy S25")
        resp = api.get("/api/v1/catalog/search/", {"q": "iphone"})
        assert resp.data["count"] == 1

    def test_search_matches_sku(self, api):
        ProductFactory(name="X", sku="UNIQUE-001")
        resp = api.get("/api/v1/catalog/search/", {"q": "UNIQUE-001"})
        assert resp.data["count"] == 1

    def test_suggest_short_q_returns_empty(self, api):
        ProductFactory(name="abcdef")
        resp = api.get("/api/v1/catalog/search/suggest/", {"q": "a"})
        assert resp.status_code == 200
        assert resp.data == []

    def test_suggest_returns_compact(self, api):
        ProductFactory(name="iPhone 15", slug="iphone-15", sku="X")
        resp = api.get(
            "/api/v1/catalog/search/suggest/", {"q": "iphone"}
        )
        assert resp.status_code == 200
        assert len(resp.data) == 1
        # Compact — no images/variants/etc
        keys = set(resp.data[0].keys())
        assert "images" not in keys
        assert "variants" not in keys
