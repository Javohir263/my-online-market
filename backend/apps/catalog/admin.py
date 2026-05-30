"""
Catalog admin — Category tree, Brand, Tag, Product (tabbed translation +
inlines for image/variant/attribute).
"""

from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline

from apps.catalog.models import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductImage,
    ProductTag,
    ProductVariant,
)
from apps.core.admin_helpers import image_thumb_html


# =============================================================================
# Category — tree-aware
# =============================================================================
@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = (
        "image_thumb",
        "indented_name",
        "slug",
        "parent",
        "products_count",
        "order",
        "is_active",
    )

    @admin.display(description="Img")
    def image_thumb(self, obj):
        url = obj.image.url if obj.image else ""
        return image_thumb_html(url, size=40)

    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("parent",)
    readonly_fields = ("products_count", "created_at", "updated_at")

    @admin.display(description="Name")
    def indented_name(self, obj: Category) -> str:
        prefix = "— " * obj.depth
        return f"{prefix}{obj.name}"


# =============================================================================
# Brand
# =============================================================================
@admin.register(Brand)
class BrandAdmin(TranslationAdmin):
    list_display = ("logo_thumb", "name", "slug", "is_active", "created_at")

    @admin.display(description="Logo")
    def logo_thumb(self, obj):
        url = obj.logo.url if obj.logo else ""
        return image_thumb_html(url, size=40)

    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    list_editable = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


# =============================================================================
# ProductTag
# =============================================================================
@admin.register(ProductTag)
class ProductTagAdmin(TranslationAdmin):
    list_display = ("name", "slug", "color_chip", "is_active")
    list_filter = ("color", "is_active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Color")
    def color_chip(self, obj: ProductTag) -> str:
        palette = {
            "primary": "#9b1c2d",
            "accent": "#2d5016",
            "warning": "#c9a227",
            "sale": "#dc2626",
            "new": "#2563eb",
            "neutral": "#6b5d3f",
        }
        c = palette.get(obj.color, "#888")
        return format_html(
            '<span style="display:inline-block;width:14px;height:14px;'
            'border-radius:50%;background:{};margin-right:6px;"></span>{}',
            c,
            obj.get_color_display(),
        )


# =============================================================================
# Product inlines
# =============================================================================
class ProductImageInline(TranslationStackedInline):
    model = ProductImage
    extra = 0
    fields = ("image", "image_preview", "alt_text", "order", "is_primary")
    readonly_fields = ("image_preview",)

    @admin.display(description="Preview")
    def image_preview(self, obj):
        url = obj.image.url if obj.image else ""
        return image_thumb_html(url, size=80)



class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = (
        "sku", "color", "size", "additional_price",
        "stock_quantity", "is_active",
    )


class ProductAttributeInline(TranslationStackedInline):
    model = ProductAttribute
    extra = 0
    fields = ("name", "value", "order")


# =============================================================================
# Product
# =============================================================================
@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "brand",
        "current_price_display",
        "stock_quantity",
        "is_in_stock",
        "is_active",
        "is_featured",
    )
    list_filter = (
        "is_active",
        "is_featured",
        "is_new",
        "is_bestseller",
        "is_in_stock",
        "category",
        "brand",
        "vendor",
    )
    search_fields = ("name", "sku", "slug")
    list_editable = ("is_active", "is_featured")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("vendor", "category", "brand", "tags")
    readonly_fields = (
        "id",
        "ratings_avg",
        "ratings_count",
        "views_count",
        "is_in_stock",
        "created_at",
        "updated_at",
    )
    inlines = [
        ProductImageInline,
        ProductVariantInline,
        ProductAttributeInline,
    ]

    fieldsets = (
        (None, {"fields": ("id", "slug", "sku", "vendor", "category", "brand", "tags")}),
        ("Content", {"fields": ("name", "short_description", "description")}),
        ("Pricing", {"fields": ("currency", "base_price", "sale_price")}),
        ("Inventory", {"fields": ("stock_quantity", "is_in_stock")}),
        (
            "Flags",
            {
                "fields": (
                    "is_active",
                    "is_featured",
                    "is_new",
                    "is_bestseller",
                )
            },
        ),
        (
            "Stats (denormalized)",
            {
                "classes": ("collapse",),
                "fields": ("ratings_avg", "ratings_count", "views_count"),
            },
        ),
        ("Audit", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Price", ordering="base_price")
    def current_price_display(self, obj: Product) -> str:
        if obj.has_discount:
            return format_html(
                '<span style="text-decoration:line-through;color:#888;'
                'margin-right:6px;">{} {}</span><b>{} {}</b>',
                obj.base_price,
                obj.currency,
                obj.sale_price,
                obj.currency,
            )
        return f"{obj.base_price} {obj.currency}"


# =============================================================================
# ProductImage / Variant / Attribute (stand-alone)
# =============================================================================
@admin.register(ProductImage)
class ProductImageAdmin(TranslationAdmin):
    list_display = ("product", "alt_text", "order", "is_primary")
    list_filter = ("is_primary",)
    autocomplete_fields = ("product",)
    search_fields = ("product__name",)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "sku", "product", "color", "size",
        "additional_price", "stock_quantity", "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("sku", "product__name", "color", "size")
    autocomplete_fields = ("product",)


@admin.register(ProductAttribute)
class ProductAttributeAdmin(TranslationAdmin):
    list_display = ("product", "name", "value", "order")
    autocomplete_fields = ("product",)
    search_fields = ("product__name", "name", "value")
