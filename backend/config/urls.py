"""
Root URL conf.

`/api/v1/` ostida barcha API endpoint'lar. `/admin/` Django admin. OpenAPI schema +
Swagger UI + ReDoc qulayligi uchun.
"""

from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.core.views import healthcheck

API_PREFIX = "api/v1/"

api_v1_patterns = [
    path("auth/", include("apps.authn.urls")),
    path("i18n/", include("apps.core.urls")),
    path("catalog/", include("apps.catalog.urls")),
    path("cart/", include("apps.cart.urls")),
    path("wishlist/", include("apps.wishlist.urls")),
    path("orders/", include("apps.orders.urls")),
    path("reviews/", include("apps.reviews.urls")),
    # B10+ da:
    # path("accounts/", include("apps.accounts.urls")),
    # path("promotions/", include("apps.promotions.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", healthcheck, name="healthcheck"),
    path(API_PREFIX, include((api_v1_patterns, "api"), namespace="v1")),
    # OpenAPI / Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

# i18n LocaleMiddleware allaqachon "Accept-Language" header / cookie / session'dan
# tilni aniqlaydi — API uchun URL prefix kerak emas. SSR-only sahifalar
# kelajakda kerak bo'lsa, i18n_patterns(...) shu yerga qo'shiladi.

# Dev-only routes (media + debug toolbar)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        import debug_toolbar

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    except ImportError:
        pass
