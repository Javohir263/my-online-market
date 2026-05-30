"""
Promotion serializers.
"""

from __future__ import annotations

from rest_framework import serializers

from apps.promotions.models import Banner, Coupon


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = (
            "id",
            "title",
            "subtitle",
            "image",
            "link",
            "position",
            "order",
        )
        read_only_fields = fields


class CouponPublicSerializer(serializers.ModelSerializer):
    """Validate javobi — chegirma hisoblangan."""

    discount_amount = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )

    class Meta:
        model = Coupon
        fields = (
            "id",
            "code",
            "type",
            "value",
            "min_order_amount",
            "max_discount",
            "discount_amount",
        )
        read_only_fields = fields


class ValidateCouponSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=64)
    subtotal = serializers.DecimalField(
        max_digits=14, decimal_places=2, min_value=0
    )
