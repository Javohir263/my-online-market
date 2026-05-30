"""
Cart serializers.
"""

from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

from apps.cart.models import Cart, CartItem
from apps.catalog.models import Product, ProductVariant


class ProductMiniSerializer(serializers.ModelSerializer):
    """Cart/wishlist'da ko'rsatish uchun mahsulot mini-card."""

    primary_image = serializers.SerializerMethodField()
    current_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "slug",
            "name",
            "currency",
            "base_price",
            "sale_price",
            "current_price",
            "is_in_stock",
            "stock_quantity",
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


class VariantMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ("id", "sku", "color", "size", "additional_price", "stock_quantity")
        read_only_fields = fields


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductMiniSerializer(read_only=True)
    variant = VariantMiniSerializer(read_only=True)
    line_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    available_stock = serializers.IntegerField(read_only=True)

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product",
            "variant",
            "quantity",
            "price_snapshot",
            "line_total",
            "available_stock",
            "created_at",
        )
        read_only_fields = fields


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )

    class Meta:
        model = Cart
        fields = ("id", "items", "items_count", "subtotal", "updated_at")
        read_only_fields = fields


# =============================================================================
# Write serializers (mutations)
# =============================================================================
class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
