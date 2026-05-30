"""
Orders admin — buyurtma boshqaruvi.
"""

from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html

from apps.orders.models import Order, OrderItem, OrderNumberSequence


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    fields = (
        "product_name_snapshot",
        "product_sku_snapshot",
        "variant_label_snapshot",
        "quantity",
        "price_at_purchase",
        "line_total_display",
    )
    readonly_fields = (
        "product",
        "variant",
        "vendor",
        "product_name_snapshot",
        "product_sku_snapshot",
        "variant_label_snapshot",
        "product_image_snapshot",
        "quantity",
        "price_at_purchase",
        "line_total_display",
    )

    def line_total_display(self, obj: OrderItem) -> str:
        return f"{obj.line_total}"

    line_total_display.short_description = "Line total"

    def has_add_permission(self, request, obj=None) -> bool:
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "user",
        "status_chip",
        "total",
        "currency",
        "items_count",
        "created_at",
    )
    list_filter = ("status", "currency", "created_at")
    search_fields = (
        "number",
        "user__email",
        "user__full_name",
        "customer_note",
    )
    autocomplete_fields = ("user",)  # `coupon` autocomplete B10'da yoqiladi
    readonly_fields = (
        "id",
        "number",
        "user",
        "subtotal",
        "shipping_cost",
        "discount_amount",
        "total",
        "currency",
        "shipping_address",
        "idempotency_key",
        "confirmed_at",
        "shipped_at",
        "delivered_at",
        "cancelled_at",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "number",
                    "user",
                    "status",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "currency",
                    "subtotal",
                    "shipping_cost",
                    "discount_amount",
                    "total",
                )
            },
        ),
        (
            "Delivery",
            {
                "fields": (
                    "shipping_address",
                    "customer_note",
                )
            },
        ),
        (
            "Promotions",
            {
                "fields": ("coupon",),
                "classes": ("collapse",),
            },
        ),
        (
            "Lifecycle",
            {
                "fields": (
                    "confirmed_at",
                    "shipped_at",
                    "delivered_at",
                    "cancelled_at",
                    "cancel_reason",
                ),
            },
        ),
        (
            "Audit",
            {
                "classes": ("collapse",),
                "fields": (
                    "idempotency_key",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )
    inlines = [OrderItemInline]
    ordering = ("-created_at",)

    STATUS_COLORS = {
        Order.Status.PENDING: "#a08967",     # neutral / khaki
        Order.Status.CONFIRMED: "#2563eb",   # blue
        Order.Status.SHIPPED: "#c9a227",     # gold
        Order.Status.DELIVERED: "#2d5016",   # accent green
        Order.Status.CANCELLED: "#9b1c2d",   # primary bordoviy
    }

    @admin.display(description="Status", ordering="status")
    def status_chip(self, obj: Order) -> str:
        color = self.STATUS_COLORS.get(obj.status, "#888")
        return format_html(
            '<span style="display:inline-block;padding:2px 10px;border-radius:10px;'
            'background:{};color:#fff;font-size:11px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.display(description="Items")
    def items_count(self, obj: Order) -> int:
        return sum(i.quantity for i in obj.items.all())


@admin.register(OrderNumberSequence)
class OrderNumberSequenceAdmin(admin.ModelAdmin):
    list_display = ("year", "last_number")
    readonly_fields = ("year", "last_number")

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
