"""
Promotions admin — Banner + Coupon + CouponUsage.
"""

from __future__ import annotations

from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from apps.promotions.models import Banner, Coupon, CouponUsage


@admin.register(Banner)
class BannerAdmin(TranslationAdmin):
    list_display = (
        "id",
        "position",
        "title",
        "order",
        "is_active",
        "valid_from",
        "valid_to",
    )
    list_filter = ("position", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("title", "subtitle")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "type",
        "value",
        "min_order_amount",
        "max_discount",
        "used_count",
        "usage_limit",
        "per_user_limit",
        "is_active",
        "valid_to",
    )
    list_filter = ("type", "is_active")
    search_fields = ("code",)
    readonly_fields = ("used_count", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("code", "type", "value", "is_active")}),
        (
            "Constraints",
            {"fields": ("min_order_amount", "max_discount")},
        ),
        (
            "Usage limits",
            {
                "fields": (
                    "usage_limit",
                    "per_user_limit",
                    "used_count",
                )
            },
        ),
        (
            "Validity",
            {"fields": ("valid_from", "valid_to")},
        ),
        (
            "Audit",
            {"classes": ("collapse",), "fields": ("created_at", "updated_at")},
        ),
    )


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ("coupon", "user", "order", "discount_applied", "used_at")
    list_filter = ("coupon",)
    search_fields = ("coupon__code", "user__email", "order__number")
    autocomplete_fields = ("coupon", "user")
    readonly_fields = ("used_at",)

    def has_add_permission(self, request) -> bool:
        return False  # faqat checkout orqali yaratiladi
