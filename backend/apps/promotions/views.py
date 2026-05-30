"""
Promotions views.

Endpoints:
    GET  /promotions/banners/?position=     — banner ro'yxati
    POST /promotions/coupons/validate/      — kupon validatsiya + chegirma hisob
"""

from __future__ import annotations

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.promotions import services
from apps.promotions.models import Banner
from apps.promotions.serializers import (
    BannerSerializer,
    CouponPublicSerializer,
    ValidateCouponSerializer,
)


class BannerListView(ListAPIView):
    """`GET /promotions/banners/?position=hero`"""

    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = BannerSerializer
    pagination_class = None

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "position",
                description="hero / sidebar / category / footer",
                required=False,
                type=str,
            ),
        ]
    )
    def get_queryset(self):
        qs = Banner.objects.filter(is_active=True).order_by("order", "id")
        position = self.request.query_params.get("position")
        if position:
            qs = qs.filter(position=position)
        # Window-based filtering (DB level — Python isn't worth it)
        from django.db.models import Q
        from django.utils import timezone

        now = timezone.now()
        qs = qs.filter(
            Q(valid_from__isnull=True) | Q(valid_from__lte=now)
        ).filter(Q(valid_to__isnull=True) | Q(valid_to__gte=now))
        return qs


class CouponValidateView(APIView):
    """`POST /promotions/coupons/validate/` — validatsiya + chegirma hisobi."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=ValidateCouponSerializer,
        responses={200: CouponPublicSerializer},
    )
    def post(self, request):
        serializer = ValidateCouponSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        coupon = services.validate_coupon(
            code=serializer.validated_data["code"],
            user=request.user,
            subtotal=serializer.validated_data["subtotal"],
        )
        discount = services.calc_discount(
            coupon, serializer.validated_data["subtotal"]
        )

        data = CouponPublicSerializer(coupon).data
        data["discount_amount"] = str(discount)
        return Response(data)
