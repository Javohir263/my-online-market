"""
factory-boy fixtures for catalog + vendor models.
"""

from __future__ import annotations

from decimal import Decimal

import factory
from factory.django import DjangoModelFactory

from apps.catalog.models import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductImage,
    ProductTag,
    ProductVariant,
)
from apps.vendors.models import Vendor


class VendorFactory(DjangoModelFactory):
    class Meta:
        model = Vendor
        django_get_or_create = ("slug",)

    slug = factory.Sequence(lambda n: f"vendor-{n}")
    name = factory.Faker("company")
    status = Vendor.Status.ACTIVE


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ("slug",)

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")
    is_active = True


class BrandFactory(DjangoModelFactory):
    class Meta:
        model = Brand
        django_get_or_create = ("slug",)

    name = factory.Sequence(lambda n: f"Brand {n}")
    slug = factory.Sequence(lambda n: f"brand-{n}")
    is_active = True


class ProductTagFactory(DjangoModelFactory):
    class Meta:
        model = ProductTag
        django_get_or_create = ("slug",)

    name = factory.Sequence(lambda n: f"tag-{n}")
    slug = factory.Sequence(lambda n: f"tag-{n}")
    color = ProductTag.ColorChoices.PRIMARY


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    vendor = factory.SubFactory(VendorFactory)
    category = factory.SubFactory(CategoryFactory)
    brand = factory.SubFactory(BrandFactory)
    name = factory.Sequence(lambda n: f"Product {n}")
    slug = factory.Sequence(lambda n: f"product-{n}")
    sku = factory.Sequence(lambda n: f"SKU-{n:06d}")
    base_price = Decimal("100000.00")
    stock_quantity = 10
    is_active = True


class ProductImageFactory(DjangoModelFactory):
    class Meta:
        model = ProductImage

    product = factory.SubFactory(ProductFactory)
    image = factory.django.ImageField(filename="test.jpg")
    alt_text = factory.Faker("sentence", nb_words=3)
    order = 0
    is_primary = False


class ProductVariantFactory(DjangoModelFactory):
    class Meta:
        model = ProductVariant

    product = factory.SubFactory(ProductFactory)
    sku = factory.Sequence(lambda n: f"VAR-{n:06d}")
    color = "red"
    size = "M"
    additional_price = Decimal("0.00")
    stock_quantity = 5


class ProductAttributeFactory(DjangoModelFactory):
    class Meta:
        model = ProductAttribute

    product = factory.SubFactory(ProductFactory)
    name = "Material"
    value = "Cotton"
    order = 0
