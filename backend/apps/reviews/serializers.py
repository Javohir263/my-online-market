"""
Review serializers.
"""

from __future__ import annotations

from rest_framework import serializers

from apps.reviews.models import Review, ReviewImage


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ("id", "image", "order")
        read_only_fields = fields


class ReviewUserMiniSerializer(serializers.Serializer):
    """User'ning ozgina ma'lumotini ko'rsatish (privacy)."""

    id = serializers.UUIDField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    initial = serializers.SerializerMethodField()

    def get_initial(self, obj) -> str:
        return (obj.full_name or obj.email)[:1].upper()


class ReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserMiniSerializer(read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = (
            "id",
            "user",
            "rating",
            "title",
            "content",
            "is_verified_purchase",
            "helpful_count",
            "status",
            "images",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CreateReviewSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    title = serializers.CharField(max_length=140, required=False, allow_blank=True, default="")
    content = serializers.CharField()


class UpdateReviewSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
    title = serializers.CharField(max_length=140, required=False, allow_blank=True)
    content = serializers.CharField(required=False)
