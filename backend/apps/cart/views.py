"""
Cart API views — 6 endpoint:
    GET    /cart/                       — current cart (anon yoki auth)
    POST   /cart/items/                 — add item
    PATCH  /cart/items/<id>/            — update quantity
    DELETE /cart/items/<id>/            — remove
    DELETE /cart/                       — clear
    POST   /cart/merge/  🔒             — manual merge (idempotent)
"""

from __future__ import annotations

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cart import services
from apps.cart.exceptions import CartItemNotFound
from apps.cart.models import CartItem
from apps.cart.serializers import (
    AddCartItemSerializer,
    ApplyCouponSerializer,
    CartItemSerializer,
    CartSerializer,
    UpdateCartItemSerializer,
)
from apps.promotions import services as promo_services


class CartDetailView(APIView):
    """`GET /cart/` va `DELETE /cart/` (clear)."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: CartSerializer})
    def get(self, request):
        cart = services.resolve_cart(request)
        return Response(
            CartSerializer(cart, context={"request": request}).data
        )

    @extend_schema(responses={204: OpenApiResponse(description="Cart cleared")})
    def delete(self, request):
        cart = services.resolve_cart(request)
        services.clear_cart(cart)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemListView(APIView):
    """`POST /cart/items/` — add (idempotent)."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=AddCartItemSerializer,
        responses={201: CartItemSerializer},
    )
    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = services.resolve_cart(request)
        item = services.add_item(cart, **serializer.validated_data)
        return Response(
            CartItemSerializer(item, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class CartItemDetailView(APIView):
    """`PATCH /cart/items/<id>/`, `DELETE /cart/items/<id>/`."""

    permission_classes = [AllowAny]

    def _get_item(self, request, pk) -> CartItem:
        cart = services.resolve_cart(request)
        item = cart.items.filter(pk=pk).first()
        if item is None:
            raise CartItemNotFound()
        return item

    @extend_schema(
        request=UpdateCartItemSerializer,
        responses={200: CartItemSerializer},
    )
    def patch(self, request, pk: int):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = self._get_item(request, pk)
        item = services.update_quantity(item, serializer.validated_data["quantity"])
        return Response(
            CartItemSerializer(item, context={"request": request}).data
        )

    @extend_schema(responses={204: OpenApiResponse(description="Item removed")})
    def delete(self, request, pk: int):
        item = self._get_item(request, pk)
        services.remove_item(item)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartCouponView(APIView):
    """`POST /cart/coupon/apply/` + `DELETE /cart/coupon/`.

    POST — kupon kodini cart'ga ulaydi. DELETE — uzadi.
    Anonim ham, auth ham ishlatishi mumkin.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        request=ApplyCouponSerializer,
        responses={200: CartSerializer},
    )
    def post(self, request):
        serializer = ApplyCouponSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = services.resolve_cart(request)
        coupon = promo_services.validate_coupon(
            code=serializer.validated_data["code"],
            user=request.user if request.user.is_authenticated else None,
            subtotal=cart.subtotal,
        )
        cart.coupon = coupon
        cart.save(update_fields=["coupon"])
        return Response(
            CartSerializer(cart, context={"request": request}).data
        )

    @extend_schema(responses={200: CartSerializer})
    def delete(self, request):
        cart = services.resolve_cart(request)
        if cart.coupon_id is not None:
            cart.coupon = None
            cart.save(update_fields=["coupon"])
        return Response(
            CartSerializer(cart, context={"request": request}).data
        )


class CartMergeView(APIView):
    """`POST /cart/merge/` 🔒 — anon cart'ni user cart'ga merge qiladi.

    Odatda login paytida signal orqali avtomatik chaqiriladi, lekin frontend
    explicit merge ham talab qilishi mumkin (multi-tab edge case).
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={200: CartSerializer},
    )
    def post(self, request):
        cart = services.merge_on_login(request, request.user)
        if cart is None:
            cart = services.resolve_cart(request)
        return Response(
            CartSerializer(cart, context={"request": request}).data
        )
