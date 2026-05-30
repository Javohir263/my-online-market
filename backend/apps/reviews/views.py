"""
Reviews API views — 5 endpoint:
    GET    /reviews/products/<slug>/   — product approved reviews (public, paginated)
    POST   /reviews/                   — yangi review  🔒
    PUT    /reviews/<id>/              — tahrir  🔒  (faqat o'zinikini)
    DELETE /reviews/<id>/              — o'chirish  🔒  (faqat o'zinikini)
    POST   /reviews/<id>/helpful/      — foydali ovoz (toggle)  🔒
"""

from __future__ import annotations

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product
from apps.reviews import services
from apps.reviews.models import Review
from apps.reviews.serializers import (
    CreateReviewSerializer,
    ReviewSerializer,
    UpdateReviewSerializer,
)


class ProductReviewsView(ListAPIView):
    """`GET /reviews/products/<slug>/` — public list of approved reviews."""

    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = ReviewSerializer

    def get_queryset(self):
        slug = self.kwargs["slug"]
        product = get_object_or_404(Product, slug=slug, is_active=True)
        return (
            Review.objects.filter(
                product=product, status=Review.Status.APPROVED
            )
            .select_related("user")
            .prefetch_related("images")
            .order_by("-helpful_count", "-created_at")
        )


class ReviewCreateView(APIView):
    """`POST /reviews/` 🔒 — yangi review."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CreateReviewSerializer,
        responses={201: ReviewSerializer, 400: OpenApiResponse(description="Already reviewed or invalid")},
    )
    def post(self, request):
        serializer = CreateReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = get_object_or_404(
            Product,
            pk=serializer.validated_data["product_id"],
            is_active=True,
        )

        # UNIQUE(product, user) — frontend uchun aniq xato
        if Review.objects.filter(product=product, user=request.user).exists():
            return Response(
                {"detail": "Siz bu mahsulot uchun allaqachon sharh qoldirgansiz."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        review = services.create_review(
            user=request.user,
            product=product,
            rating=serializer.validated_data["rating"],
            title=serializer.validated_data.get("title", ""),
            content=serializer.validated_data["content"],
        )
        return Response(
            ReviewSerializer(review).data,
            status=status.HTTP_201_CREATED,
        )


class ReviewDetailView(APIView):
    """`PUT /reviews/<id>/` + `DELETE /reviews/<id>/` 🔒  — faqat o'zinikini."""

    permission_classes = [IsAuthenticated]

    def _get_own_review(self, request, pk) -> Review:
        review = get_object_or_404(Review, pk=pk)
        if review.user_id != request.user.id:
            raise PermissionDenied("O'zga foydalanuvchi sharhini tahrir qilolmaysiz.")
        return review

    @extend_schema(
        request=UpdateReviewSerializer,
        responses={200: ReviewSerializer},
    )
    def put(self, request, pk: int):
        review = self._get_own_review(request, pk)
        serializer = UpdateReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = services.update_review(review, **serializer.validated_data)
        return Response(ReviewSerializer(review).data)

    @extend_schema(responses={204: OpenApiResponse(description="Deleted")})
    def delete(self, request, pk: int):
        review = self._get_own_review(request, pk)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewHelpfulToggleView(APIView):
    """`POST /reviews/<id>/helpful/` 🔒 — toggle helpful vote."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                description="{is_voted: bool, helpful_count: int}"
            )
        },
    )
    def post(self, request, pk: int):
        review = get_object_or_404(Review, pk=pk)
        is_voted, count = services.toggle_helpful(
            user=request.user, review=review
        )
        return Response({"is_voted": is_voted, "helpful_count": count})
