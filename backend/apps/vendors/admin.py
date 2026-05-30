"""
Vendors admin.
"""

from __future__ import annotations

from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from apps.vendors.models import Vendor


@admin.register(Vendor)
class VendorAdmin(TranslationAdmin):
    list_display = ("name", "slug", "status", "commission_rate", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("owner",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("slug", "name", "description", "logo")}),
        ("Status & owner", {"fields": ("status", "owner", "commission_rate")}),
        ("Audit", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )
