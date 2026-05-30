"""
Wishlist API views — 3 endpoint:
    GET    /wishlist/                         — list (paginated)
    POST   /wishlist/items/                   — add
    DELETE /wishlist/items/<product_id>/      — remove
Hammasi 🔒 (authenticated only).
"""

from __future__ import annotations

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product
from apps.wishlist.models import WishlistItem
from apps.wishlist.serializers import (
    AddWishlistItemSerializer,
    WishlistItemSerializer,
)


class WishlistListView(ListAPIView):
    """`GET /wishlist/` 🔒"""

    permission_classes = [IsAuthenticated]
    serializer_class = WishlistItemSerializer

    def get_queryset(self):
        return (
            WishlistItem.objects.filter(user=self.request.user)
            .select_related("product", "product__category", "product__brand")
            .prefetch_related("product__images")
        )


class WishlistAddView(APIView):
    """`POST /wishlist/items/` 🔒 — idempotent."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AddWishlistItemSerializer,
        responses={201: WishlistItemSerializer},
    )
    def post(self, request):
        serializer = AddWishlistItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = get_object_or_404(
            Product, pk=serializer.validated_data["product_id"], is_active=True
        )
        item, created = WishlistItem.objects.get_or_create(
            user=request.user, product=product
        )
        return Response(
            WishlistItemSerializer(item, context={"request": request}).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class WishlistRemoveView(APIView):
    """`DELETE /wishlist/items/<product_id>/` 🔒"""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={204: OpenApiResponse(description="Removed")})
    def delete(self, request, product_id):
        deleted, _ = WishlistItem.objects.filter(
            user=request.user, product_id=product_id
        ).delete()
        if deleted == 0:
            return Response(
                {"detail": "Not in wishlist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
