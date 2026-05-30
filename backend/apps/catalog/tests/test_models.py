"""
Catalog model tests — Category tree, Product helpers, constraints,
ProductImage primary uniqueness.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.catalog.models import Category, Product, ProductImage, ProductTag
from apps.catalog.tests.factories import (
    BrandFactory,
    CategoryFactory,
    ProductAttributeFactory,
    ProductFactory,
    ProductImageFactory,
    ProductTagFactory,
    ProductVariantFactory,
)

pytestmark = pytest.mark.django_db


# =============================================================================
# Category
# =============================================================================
class TestCategory:
    def test_str(self):
        c = CategoryFactory(name="Phones")
        assert str(c) == "Phones"

    def test_depth_root(self):
        c = CategoryFactory()
        assert c.depth == 0

    def test_depth_nested(self):
        root = CategoryFactory(name="Electronics")
        sub = CategoryFactory(name="Phones", parent=root)
        sub_sub = CategoryFactory(name="iPhone", parent=sub)
        assert sub.depth == 1
        assert sub_sub.depth == 2

    def test_get_full_path(self):
        root = CategoryFactory(name="Electronics")
        sub = CategoryFactory(name="Phones", parent=root)
        leaf = CategoryFactory(name="iPhone", parent=sub)
        assert leaf.get_full_path() == "Electronics / Phones / iPhone"

    def test_roots_queryset(self):
        root1 = CategoryFactory()
        root2 = CategoryFactory()
        CategoryFactory(parent=root1)  # not a root
        roots = list(Category.objects.roots())
        assert root1 in roots
        assert root2 in roots
        assert len(roots) == 2

    def test_slug_unique(self):
        # factory has django_get_or_create — bypass it via direct create.
        Category.objects.create(name="X", slug="phones")
        with pytest.raises(IntegrityError):
            Category.objects.create(name="Y", slug="phones")


# =============================================================================
# ProductTag
# =============================================================================
class TestProductTag:
    def test_str(self):
        t = ProductTagFactory(name="new")
        assert str(t) == "new"

    def test_color_choices(self):
        for color, _ in ProductTag.ColorChoices.choices:
            t = ProductTagFactory(color=color)
            assert t.color == color


# =============================================================================
# Product
# =============================================================================
class TestProduct:
    def test_uuid_pk(self):
        p = ProductFactory()
        assert len(str(p.id)) == 36

    def test_current_price_no_sale(self):
        p = ProductFactory(base_price=Decimal("100"), sale_price=None)
        assert p.current_price == Decimal("100")
        assert not p.has_discount

    def test_current_price_with_sale(self):
        p = ProductFactory(
            base_price=Decimal("100"), sale_price=Decimal("70")
        )
        assert p.current_price == Decimal("70")
        assert p.has_discount

    def test_current_price_ignores_sale_equal_or_higher(self):
        # sale_price >= base_price ma'nosiz, lekin check_constraint sale <= base
        # ruxsat beradi (teng). current_price faqat strict < uchun discount.
        p = ProductFactory(
            base_price=Decimal("100"), sale_price=Decimal("100")
        )
        assert p.current_price == Decimal("100")
        assert not p.has_discount

    def test_discount_percentage(self):
        p = ProductFactory(
            base_price=Decimal("100"), sale_price=Decimal("75")
        )
        assert p.discount_percentage == 25

    def test_sale_above_base_rejected(self):
        # CheckConstraint: sale_price <= base_price
        with pytest.raises(IntegrityError):
            ProductFactory(
                base_price=Decimal("100"),
                sale_price=Decimal("150"),
            )

    def test_sku_unique(self):
        ProductFactory(sku="DUPE-1")
        with pytest.raises(IntegrityError):
            ProductFactory(sku="DUPE-1")

    def test_sync_stock_flag_falls_to_zero(self):
        p = ProductFactory(stock_quantity=5)
        assert p.is_in_stock is True
        p.stock_quantity = 0
        p.sync_stock_flag()
        p.refresh_from_db()
        assert p.is_in_stock is False

    def test_sync_stock_flag_rises_from_zero(self):
        p = ProductFactory(stock_quantity=0)
        p.sync_stock_flag()
        p.refresh_from_db()
        assert p.is_in_stock is False  # initial sync
        p.stock_quantity = 3
        p.sync_stock_flag()
        p.refresh_from_db()
        assert p.is_in_stock is True

    def test_tags_m2m(self):
        p = ProductFactory()
        t1 = ProductTagFactory()
        t2 = ProductTagFactory()
        p.tags.add(t1, t2)
        assert p.tags.count() == 2


# =============================================================================
# ProductImage
# =============================================================================
class TestProductImage:
    def test_only_one_primary_per_product(self, monkeypatch):
        p = ProductFactory()
        a = ProductImageFactory(product=p, is_primary=True)
        b = ProductImageFactory(product=p, is_primary=True)
        a.refresh_from_db()
        assert b.is_primary is True
        assert a.is_primary is False

    def test_many_non_primary_allowed(self):
        p = ProductFactory()
        ProductImageFactory(product=p, is_primary=False)
        ProductImageFactory(product=p, is_primary=False)
        assert ProductImage.objects.filter(product=p).count() == 2


# =============================================================================
# ProductVariant
# =============================================================================
class TestProductVariant:
    def test_sku_unique(self):
        p = ProductFactory()
        ProductVariantFactory(product=p, sku="V-1")
        with pytest.raises(IntegrityError):
            ProductVariantFactory(product=p, sku="V-1")

    def test_final_price_with_additional(self):
        p = ProductFactory(base_price=Decimal("100"))
        v = ProductVariantFactory(
            product=p, additional_price=Decimal("20")
        )
        assert v.final_price == Decimal("120")

    def test_final_price_with_product_sale(self):
        p = ProductFactory(
            base_price=Decimal("100"), sale_price=Decimal("80")
        )
        v = ProductVariantFactory(
            product=p, additional_price=Decimal("5")
        )
        assert v.final_price == Decimal("85")


# =============================================================================
# ProductAttribute
# =============================================================================
class TestProductAttribute:
    def test_str(self):
        a = ProductAttributeFactory(name="Color", value="Red")
        assert str(a) == "Color: Red"
