"""
Orders URLs — mounted at `/api/v1/orders/`.
"""

from __future__ import annotations

from django.urls import path

from apps.orders.views import (
    OrderCancelView,
    OrderDetailView,
    OrderListCreateView,
)

app_name = "orders"

urlpatterns = [
    path("", OrderListCreateView.as_view(), name="list-create"),
    path("<str:number>/", OrderDetailView.as_view(), name="detail"),
    path("<str:number>/cancel/", OrderCancelView.as_view(), name="cancel"),
]
