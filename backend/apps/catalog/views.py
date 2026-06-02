"""
Catalog API views — 10+ endpoint.

Performance optimizations:
- select_related on FK (vendor, category, brand)
- prefetch_related on M2M / reverse (images, variants, attributes, tags, children)
- F() atomic update for views_count
- Cache (Redis) for category tree (5 min TTL)
"""

from __future__ import annotations

from django.core.cache import cache
from django.db.models import F, Prefetch, Q, QuerySet
from django.shortcuts import get_object_or_404
from django.utils.translation import get_language
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.filters import ProductFilter
from apps.catalog.models import Brand, Category, Product, ProductImage
from apps.catalog.serializers import (
    BrandSerializer,
    CategoryDetailSerializer,
    CategoryNodeSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductSuggestSerializer,
)

CATEGORY_TREE_CACHE_KEY = "catalog:category_tree"
CATEGORY_TREE_TTL = 60 * 5  # 5 min

# Aliasing — frontend "?sort=price" ko'rinishida yuboradi.
SORT_ALIASES = {
    "price": "base_price",
    "-price": "-base_price",
    "rating": "-ratings_avg",  # default: yuqori reyting birinchi
    "-rating": "ratings_avg",
    "new": "-created_at",
    "old": "created_at",
    "popular": "-views_count",
}


def _apply_sort_alias(request, queryset: QuerySet) -> QuerySet:
    raw = request.query_params.get("sort")
    if raw and raw in SORT_ALIASES:
        return queryset.order_by(SORT_ALIASES[raw])
    return queryset


def _product_list_queryset() -> QuerySet[Product]:
    """Common select/prefetch chain — bir marta yozib reuse qilamiz."""
    return (
        Product.objects.filter(is_active=True)
        .select_related("vendor", "category", "brand")
        .prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.order_by(
                    "-is_primary", "order"
                ),
            ),
        )
    )


def _product_detail_queryset() -> QuerySet[Product]:
    return (
        Product.objects.filter(is_active=True)
        .select_related("vendor", "category", "brand")
        .prefetch_related("images", "variants", "attributes", "tags")
    )


# =============================================================================
# Categories
# =============================================================================
class CategoryTreeView(APIView):
    """`GET /catalog/categories/` — to'liq daraxt (cache 5 min)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        responses={200: CategoryNodeSerializer(many=True)},
        description="Faollashtirilgan kategoriyalarning to'liq daraxti.",
    )
    def get(self, request):
        # Cache key must include language — kategoriya nomlari uz/ru/en farqli.
        lang = (get_language() or "uz")[:2]
        cache_key = f"{CATEGORY_TREE_CACHE_KEY}:{lang}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        roots = (
            Category.objects.filter(parent__isnull=True, is_active=True)
            .prefetch_related("children__children__children")
            .order_by("order", "name")
        )
        data = CategoryNodeSerializer(
            roots, many=True, context={"request": request}
        ).data
        cache.set(cache_key, data, CATEGORY_TREE_TTL)
        return Response(data)


class CategoryDetailView(RetrieveAPIView):
    """`GET /catalog/categories/<slug>/`"""

    queryset = Category.objects.filter(is_active=True).select_related("parent")
    serializer_class = CategoryDetailSerializer
    lookup_field = "slug"
    permission_classes = [AllowAny]
    authentication_classes = []


# =============================================================================
# Brands
# =============================================================================
class BrandListView(ListAPIView):
    """`GET /catalog/brands/`"""

    queryset = Brand.objects.filter(is_active=True).order_by("name")
    serializer_class = BrandSerializer
    pagination_class = None
    permission_classes = [AllowAny]
    authentication_classes = []
    filter_backends = [SearchFilter]
    search_fields = ["name", "slug"]


# =============================================================================
# Products — list with filters / sort / search
# =============================================================================
class ProductListView(ListAPIView):
    """`GET /catalog/products/` — to'liq mahsulot ro'yxati, filter+sort+search."""

    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "sku", "short_description"]
    # NOTE: `?sort=` alias via `_apply_sort_alias` — OrderingFilter is
    # intentionally NOT included to avoid conflicting with the alias.
    # Default ordering comes from Product.Meta.ordering = ("-created_at",).

    def get_queryset(self):
        return _apply_sort_alias(self.request, _product_list_queryset())


class ProductDetailView(RetrieveAPIView):
    """`GET /catalog/products/<slug>/` — atomic views++."""

    queryset = _product_detail_queryset()
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"
    permission_classes = [AllowAny]
    authentication_classes = []

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Atomic increment — duplikat fetch yo'q
        Product.objects.filter(pk=instance.pk).update(
            views_count=F("views_count") + 1
        )
        instance.views_count += 1  # serializer'da to'g'ri ko'rinish uchun
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# =============================================================================
# Products — curated lists
# =============================================================================
class _BaseCuratedList(ListAPIView):
    """Featured/new/bestsellers uchun umumiy skeleton (paginatsiyasiz, top-N)."""

    serializer_class = ProductListSerializer
    pagination_class = None
    permission_classes = [AllowAny]
    authentication_classes = []
    DEFAULT_LIMIT = 12
    flag_field: str = ""

    def get_queryset(self):
        limit = int(self.request.query_params.get("limit", self.DEFAULT_LIMIT))
        limit = min(max(limit, 1), 50)
        return _product_list_queryset().filter(
            **{self.flag_field: True}
        ).order_by("-created_at")[:limit]


class FeaturedProductsView(_BaseCuratedList):
    """`GET /catalog/products/featured/`"""

    flag_field = "is_featured"


class NewArrivalsView(_BaseCuratedList):
    """`GET /catalog/products/new-arrivals/`"""

    flag_field = "is_new"


class BestsellersView(_BaseCuratedList):
    """`GET /catalog/products/bestsellers/`"""

    flag_field = "is_bestseller"


class SimilarProductsView(ListAPIView):
    """`GET /catalog/products/<slug>/similar/` — same category, exclude self."""

    serializer_class = ProductListSerializer
    pagination_class = None
    permission_classes = [AllowAny]
    authentication_classes = []
    DEFAULT_LIMIT = 8

    def get_queryset(self):
        slug = self.kwargs["slug"]
        product = get_object_or_404(Product, slug=slug, is_active=True)
        limit = int(self.request.query_params.get("limit", self.DEFAULT_LIMIT))
        limit = min(max(limit, 1), 24)
        return (
            _product_list_queryset()
            .filter(category=product.category)
            .exclude(pk=product.pk)
            .order_by("-ratings_avg", "-views_count")[:limit]
        )


# =============================================================================
# Search
# =============================================================================
class ProductSearchView(ListAPIView):
    """`GET /catalog/search/?q=...` — icontains across name + short_description + sku.

    pg_trgm bilan optimallashtirish kelajak (B6.5 ixtiyoriy yoki keyingi
    bosqichda — extension huquqi kerak).
    """

    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "q", description="Search query", required=True, type=str
            ),
        ]
    )
    def get_queryset(self):
        q = (self.request.query_params.get("q") or "").strip()
        if not q:
            return Product.objects.none()
        return (
            _product_list_queryset()
            .filter(
                Q(name__icontains=q)
                | Q(short_description__icontains=q)
                | Q(sku__icontains=q)
            )
            .order_by("-ratings_avg")
        )


class SearchSuggestView(APIView):
    """`GET /catalog/search/suggest/?q=...` — dropdown uchun engil ro'yxat (top 8)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        parameters=[
            OpenApiParameter("q", type=str, required=True),
        ],
        responses={200: ProductSuggestSerializer(many=True)},
    )
    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        if len(q) < 2:
            return Response([])
        qs = (
            Product.objects.filter(is_active=True)
            .filter(Q(name__icontains=q) | Q(sku__icontains=q))
            .order_by("-ratings_avg")[:8]
        )
        data = ProductSuggestSerializer(
            qs, many=True, context={"request": request}
        ).data
        return Response(data)
