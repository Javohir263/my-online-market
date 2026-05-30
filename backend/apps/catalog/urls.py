"""
Catalog URLs — mounted at `/api/v1/catalog/`.
"""

from __future__ import annotations

from django.urls import path

from apps.catalog.views import (
    BestsellersView,
    BrandListView,
    CategoryDetailView,
    CategoryTreeView,
    FeaturedProductsView,
    NewArrivalsView,
    ProductDetailView,
    ProductListView,
    ProductSearchView,
    SearchSuggestView,
    SimilarProductsView,
)

app_name = "catalog"

urlpatterns = [
    # Categories
    path("categories/", CategoryTreeView.as_view(), name="category-tree"),
    path(
        "categories/<slug:slug>/",
        CategoryDetailView.as_view(),
        name="category-detail",
    ),
    # Brands
    path("brands/", BrandListView.as_view(), name="brand-list"),
    # Products — curated lists (avval, slug bilan to'qnashmasligi uchun)
    path(
        "products/featured/",
        FeaturedProductsView.as_view(),
        name="product-featured",
    ),
    path(
        "products/new-arrivals/",
        NewArrivalsView.as_view(),
        name="product-new-arrivals",
    ),
    path(
        "products/bestsellers/",
        BestsellersView.as_view(),
        name="product-bestsellers",
    ),
    # Products — main list + detail + similar
    path("products/", ProductListView.as_view(), name="product-list"),
    path(
        "products/<slug:slug>/",
        ProductDetailView.as_view(),
        name="product-detail",
    ),
    path(
        "products/<slug:slug>/similar/",
        SimilarProductsView.as_view(),
        name="product-similar",
    ),
    # Search
    path("search/", ProductSearchView.as_view(), name="search"),
    path(
        "search/suggest/",
        SearchSuggestView.as_view(),
        name="search-suggest",
    ),
]
