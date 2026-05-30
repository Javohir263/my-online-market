"""
Wishlist serializers.
"""

from __future__ import annotations

from rest_framework import serializers

from apps.cart.serializers import ProductMiniSerializer
from apps.wishlist.models import WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductMiniSerializer(read_only=True)

    class Meta:
        model = WishlistItem
        fields = ("id", "product", "created_at")
        read_only_fields = fields


class AddWishlistItemSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
