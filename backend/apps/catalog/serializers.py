"""
Catalog serializers — Category tree, Brand, Tag, Product list/detail.

Senior approach:
- ListSerializer (lightweight, faqat card uchun kerakli field'lar)
- DetailSerializer (nested images/variants/attributes/tags)
- Recursive CategoryNodeSerializer (tree response uchun, prefetch optimized)
- read_only field'lar — denorm counters va computed property'lar
"""

from __future__ import annotations

from rest_framework import serializers

from apps.catalog.models import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductImage,
    ProductTag,
    ProductVariant,
)


# =============================================================================
# Brand
# =============================================================================
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "slug", "name", "description", "logo", "is_active")


# =============================================================================
# ProductTag
# =============================================================================
class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        fields = ("id", "slug", "name", "color")


# =============================================================================
# Category — tree (recursive)
# =============================================================================
class CategoryNodeSerializer(serializers.ModelSerializer):
    """Recursive tree serializer. View `prefetch_related('children')` qiladi."""

    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "slug",
            "name",
            "icon",
            "image",
            "products_count",
            "order",
            "children",
        )
        read_only_fields = fields

    def get_children(self, obj: Category) -> list[dict]:
        kids = [c for c in obj.children.all() if c.is_active]
        kids.sort(key=lambda c: (c.order, c.name))
        return CategoryNodeSerializer(kids, many=True, context=self.context).data


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Bitta category to'liq ma'lumoti (parents zanjiri bilan)."""

    parents = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "slug",
            "name",
            "description",
            "image",
            "icon",
            "products_count",
            "parents",
        )
        read_only_fields = fields

    def get_parents(self, obj: Category) -> list[dict]:
        return [
            {"id": c.id, "slug": c.slug, "name": c.name}
            for c in obj.get_ancestors()
        ]


# =============================================================================
# Product — nested resources
# =============================================================================
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "image", "alt_text", "order", "is_primary")


class ProductVariantSerializer(serializers.ModelSerializer):
    final_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "sku",
            "color",
            "size",
            "additional_price",
            "final_price",
            "stock_quantity",
            "image",
            "is_active",
        )


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ("id", "name", "value", "order")


# =============================================================================
# Product — list (compact card)
# =============================================================================
class ProductListSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    current_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    has_discount = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "slug",
            "sku",
            "name",
            "short_description",
            "currency",
            "base_price",
            "sale_price",
            "current_price",
            "has_discount",
            "discount_percentage",
            "stock_quantity",
            "is_in_stock",
            "ratings_avg",
            "ratings_count",
            "is_featured",
            "is_new",
            "is_bestseller",
            "brand",
            "category",
            "primary_image",
        )
        read_only_fields = fields

    def get_primary_image(self, obj: Product) -> str | None:
        primary = next(
            (i for i in obj.images.all() if i.is_primary), None
        ) or (obj.images.all()[0] if obj.images.all() else None)
        if not primary or not primary.image:
            return None
        request = self.context.get("request")
        url = primary.image.url
        return request.build_absolute_uri(url) if request else url

    def get_brand(self, obj: Product) -> dict | None:
        if obj.brand is None:
            return None
        return {"id": obj.brand.id, "slug": obj.brand.slug, "name": obj.brand.name}

    def get_category(self, obj: Product) -> dict:
        return {
            "id": obj.category.id,
            "slug": obj.category.slug,
            "name": obj.category.name,
        }


# =============================================================================
# Product — detail (full)
# =============================================================================
class ProductDetailSerializer(ProductListSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    attributes = ProductAttributeSerializer(many=True, read_only=True)
    tags = ProductTagSerializer(many=True, read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = (
            *ProductListSerializer.Meta.fields,
            "description",
            "views_count",
            "images",
            "variants",
            "attributes",
            "tags",
        )
        read_only_fields = fields


# =============================================================================
# Search suggest (lightweight)
# =============================================================================
class ProductSuggestSerializer(serializers.ModelSerializer):
    """Search dropdown — eng kerakli minimum."""

    class Meta:
        model = Product
        fields = ("id", "slug", "name", "current_price", "currency")
        read_only_fields = fields

    current_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
