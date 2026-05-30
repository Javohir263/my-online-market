"""
Custom admin dashboard widget injection — KPI tiles for admin/index/.

Approach: override AdminSite.index_template via custom template loader,
serving extra context (today's orders, low-stock products, pending reviews).
We monkey-patch `admin.site.index` to inject extra_context.
"""

from __future__ import annotations

from datetime import timedelta

from django.contrib import admin
from django.db.models import Sum
from django.template.response import TemplateResponse
from django.utils import timezone


def _today_kpis() -> dict:
    """Compute KPI metrics for dashboard tiles (lazy-imported models)."""
    from apps.catalog.models import Product
    from apps.orders.models import Order
    from apps.reviews.models import Review

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    today_orders = Order.objects.filter(created_at__gte=today_start)
    week_orders = Order.objects.filter(
        created_at__gte=week_ago,
        status__in=(
            Order.Status.CONFIRMED,
            Order.Status.SHIPPED,
            Order.Status.DELIVERED,
        ),
    )
    revenue = (
        week_orders.aggregate(total=Sum("total"))["total"] or 0
    )

    return {
        "orders_today": today_orders.count(),
        "orders_pending": Order.objects.filter(
            status=Order.Status.PENDING
        ).count(),
        "revenue_7d": revenue,
        "low_stock_count": Product.objects.filter(
            is_active=True, stock_quantity__lte=5
        ).count(),
        "pending_reviews": Review.objects.filter(
            status=Review.Status.PENDING
        ).count(),
        "recent_orders": list(
            Order.objects.order_by("-created_at")[:5]
        ),
    }


_original_index = admin.site.index


def patched_index(request, extra_context=None):
    """Wrap default admin index with KPI tiles."""
    extra_context = extra_context or {}
    try:
        extra_context["mom_dashboard"] = _today_kpis()
    except Exception:
        # Migration phase yoki testlar — model'lar mavjud bo'lmasligi mumkin
        extra_context["mom_dashboard"] = None

    response = _original_index(request, extra_context=extra_context)
    if isinstance(response, TemplateResponse):
        response.template_name = "admin/mom_index.html"
    return response


def install_dashboard() -> None:
    """One-time install — called from AppConfig.ready()."""
    admin.site.index = patched_index  # type: ignore[assignment]
    admin.site.site_header = "My Online Market"
    admin.site.site_title = "My Online Market Admin"
    admin.site.index_title = "Dashboard"
