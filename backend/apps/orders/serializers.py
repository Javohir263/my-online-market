"""
Order serializers — Checkout (write), List/Detail (read), Cancel.
"""

from __future__ import annotations

from rest_framework import serializers

from apps.orders.models import Order, OrderItem


# =============================================================================
# OrderItem (read)
# =============================================================================
class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "variant",
            "vendor",
            "quantity",
            "price_at_purchase",
            "line_total",
            "product_name_snapshot",
            "product_sku_snapshot",
            "variant_label_snapshot",
            "product_image_snapshot",
        )
        read_only_fields = fields


# =============================================================================
# Order (read)
# =============================================================================
class OrderListSerializer(serializers.ModelSerializer):
    """Compact list — buyurtmalar ro'yxati uchun."""

    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "number",
            "status",
            "currency",
            "total",
            "items_count",
            "created_at",
        )
        read_only_fields = fields

    def get_items_count(self, obj: Order) -> int:
        return sum(i.quantity for i in obj.items.all())


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "number",
            "status",
            "currency",
            "subtotal",
            "shipping_cost",
            "discount_amount",
            "total",
            "shipping_address",
            "customer_note",
            "items",
            "confirmed_at",
            "shipped_at",
            "delivered_at",
            "cancelled_at",
            "cancel_reason",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


# =============================================================================
# Checkout (write)
# =============================================================================
class CheckoutSerializer(serializers.Serializer):
    """Checkout payload.

    address_id — User'ning mavjud manzilidan biri (UUID emas, BigInt FK).
    Yoki frontend inline `address` dict yuborishi mumkin (kelajak), hozir
    faqat address_id supported.
    """

    address_id = serializers.IntegerField()
    customer_note = serializers.CharField(
        max_length=1000, required=False, allow_blank=True, default=""
    )
    coupon_code = serializers.CharField(
        max_length=64, required=False, allow_blank=True
    )


class CancelOrderSerializer(serializers.Serializer):
    reason = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )
