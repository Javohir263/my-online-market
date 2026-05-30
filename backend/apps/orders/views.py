"""
Orders API views.

4 endpoint (plan'da):
    GET  /orders/                       — joriy user buyurtmalari (paginated)
    POST /orders/                       — checkout (idempotency key via header)
    GET  /orders/<number>/              — detail
    POST /orders/<number>/cancel/       — bekor qilish
"""

from __future__ import annotations

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Address
from apps.cart.services import resolve_cart
from apps.orders import services
from apps.orders.models import Order
from apps.orders.serializers import (
    CancelOrderSerializer,
    CheckoutSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
)

IDEMPOTENCY_HEADER = "HTTP_X_IDEMPOTENCY_KEY"


class OrderListCreateView(ListAPIView):
    """`GET /orders/` (list) + `POST /orders/` (checkout)."""

    permission_classes = [IsAuthenticated]
    serializer_class = OrderListSerializer

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items")
            .order_by("-created_at")
        )

    @extend_schema(
        request=CheckoutSerializer,
        parameters=[
            OpenApiParameter(
                name="X-Idempotency-Key",
                location=OpenApiParameter.HEADER,
                description=(
                    "Bir xil key bilan POST'lar duplikat buyurtma yaratmaydi. "
                    "Frontend UUID yoki nanoid generate qiladi."
                ),
                required=False,
                type=str,
            ),
        ],
        responses={201: OrderDetailSerializer},
    )
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        address = get_object_or_404(
            Address,
            pk=serializer.validated_data["address_id"],
            user=request.user,
        )

        cart = resolve_cart(request)
        idem_key = request.META.get(IDEMPOTENCY_HEADER) or None

        order = services.checkout_cart(
            user=request.user,
            cart=cart,
            shipping_address=address,
            customer_note=serializer.validated_data.get("customer_note", ""),
            idempotency_key=idem_key,
        )
        return Response(
            OrderDetailSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(APIView):
    """`GET /orders/<number>/`"""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OrderDetailSerializer})
    def get(self, request, number: str):
        order = get_object_or_404(
            Order.objects.prefetch_related("items"),
            number=number,
            user=request.user,
        )
        return Response(OrderDetailSerializer(order).data)


class OrderCancelView(APIView):
    """`POST /orders/<number>/cancel/`"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CancelOrderSerializer,
        responses={
            200: OrderDetailSerializer,
            400: OpenApiResponse(description="Not cancellable"),
        },
    )
    def post(self, request, number: str):
        order = get_object_or_404(
            Order, number=number, user=request.user
        )
        serializer = CancelOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = services.cancel_order(
            order, reason=serializer.validated_data.get("reason", "")
        )
        return Response(OrderDetailSerializer(order).data)
