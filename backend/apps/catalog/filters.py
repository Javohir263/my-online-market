"""
django-filter ProductFilter — list endpoint uchun.

Query parameters:
    ?category=slug                     — bitta yoki bir nechta (vergul bilan)
    ?brand=slug                        — bitta yoki bir nechta
    ?min_price=10000&max_price=200000
    ?rating=4                          — ratings_avg >= rating
    ?in_stock=true
    ?tags=hit,sale                     — vergul bilan ajratilgan slug'lar
    ?sort=price | -price | rating | -rating | new | popular
    ?search=qidiruv so'zi
"""

from __future__ import annotations

import django_filters as df
from django.db.models import Q

from apps.catalog.models import Category, Product


class CommaSeparatedSlugFilter(df.BaseInFilter, df.CharFilter):
    """`?brand=apple,samsung` → brand__slug__in=['apple', 'samsung']."""


class ProductFilter(df.FilterSet):
    category = CommaSeparatedSlugFilter(method="filter_category")
    brand = CommaSeparatedSlugFilter(field_name="brand__slug", lookup_expr="in")
    tags = CommaSeparatedSlugFilter(field_name="tags__slug", lookup_expr="in")

    min_price = df.NumberFilter(method="filter_min_price")
    max_price = df.NumberFilter(method="filter_max_price")
    rating = df.NumberFilter(field_name="ratings_avg", lookup_expr="gte")
    in_stock = df.BooleanFilter(field_name="is_in_stock")

    is_featured = df.BooleanFilter()
    is_new = df.BooleanFilter()
    is_bestseller = df.BooleanFilter()

    class Meta:
        model = Product
        fields: list[str] = []  # methods + custom only

    # ------------------------------------------------------------------
    # Custom filters
    # ------------------------------------------------------------------
    def filter_category(self, queryset, name, value):
        """`category=phones` agar bu root bo'lsa, descendant'larni ham
        qamrab oladi. Tree-aware filtering."""
        if not value:
            return queryset
        slugs = list(value) if isinstance(value, (list, tuple)) else [value]
        categories = list(Category.objects.filter(slug__in=slugs))
        if not categories:
            return queryset.none()

        # Collect category + descendants ID'lari
        all_ids: set[int] = set()
        for cat in categories:
            all_ids.add(cat.id)
            all_ids.update(self._descendant_ids(cat))
        return queryset.filter(category_id__in=all_ids)

    @staticmethod
    def _descendant_ids(cat: Category) -> set[int]:
        ids: set[int] = set()
        stack = list(cat.children.all())
        while stack:
            node = stack.pop()
            ids.add(node.id)
            stack.extend(list(node.children.all()))
        return ids

    def filter_min_price(self, queryset, name, value):
        """current_price >= value — sale_price'ni hisobga oladi."""
        return queryset.filter(
            Q(sale_price__isnull=True, base_price__gte=value)
            | Q(sale_price__isnull=False, sale_price__gte=value)
        )

    def filter_max_price(self, queryset, name, value):
        return queryset.filter(
            Q(sale_price__isnull=True, base_price__lte=value)
            | Q(sale_price__isnull=False, sale_price__lte=value)
        )
