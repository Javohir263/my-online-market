"""
Reviews admin — moderation workflow.
"""

from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html

from apps.reviews.models import HelpfulVote, Review, ReviewImage


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0
    fields = ("image", "order")
    readonly_fields = ("created_at",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "user",
        "rating_stars",
        "status_chip",
        "is_verified_purchase",
        "helpful_count",
        "created_at",
    )
    list_filter = ("status", "is_verified_purchase", "rating", "created_at")
    search_fields = ("product__name", "user__email", "title", "content")
    autocomplete_fields = ("product", "user")
    readonly_fields = (
        "is_verified_purchase",
        "helpful_count",
        "created_at",
        "updated_at",
    )
    actions = ("approve_selected", "reject_selected")
    inlines = [ReviewImageInline]

    @admin.display(description="Rating", ordering="rating")
    def rating_stars(self, obj: Review) -> str:
        return "★" * obj.rating + "☆" * (5 - obj.rating)

    @admin.display(description="Status", ordering="status")
    def status_chip(self, obj: Review) -> str:
        colors = {
            Review.Status.PENDING: "#a08967",
            Review.Status.APPROVED: "#2d5016",
            Review.Status.REJECTED: "#9b1c2d",
        }
        return format_html(
            '<span style="display:inline-block;padding:2px 10px;'
            'border-radius:10px;background:{};color:#fff;font-size:11px;">{}</span>',
            colors.get(obj.status, "#888"),
            obj.get_status_display(),
        )

    @admin.action(description="Approve selected reviews")
    def approve_selected(self, request, queryset):
        for review in queryset:
            review.status = Review.Status.APPROVED
            review.save(update_fields=["status"])

    @admin.action(description="Reject selected reviews")
    def reject_selected(self, request, queryset):
        for review in queryset:
            review.status = Review.Status.REJECTED
            review.save(update_fields=["status"])


@admin.register(HelpfulVote)
class HelpfulVoteAdmin(admin.ModelAdmin):
    list_display = ("user", "review", "created_at")
    autocomplete_fields = ("user", "review")
    readonly_fields = ("created_at",)
