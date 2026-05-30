"""
Vendor model tests.
"""

from __future__ import annotations

import pytest

from apps.vendors.models import Vendor

pytestmark = pytest.mark.django_db


def test_default_vendor_seeded():
    """Migration 0002 DEFAULT_VENDOR'ni yaratganligini tasdiqlash."""
    vendor = Vendor.objects.get_default()
    assert vendor.slug == "my-online-market"
    assert vendor.status == Vendor.Status.ACTIVE


def test_vendor_str():
    from apps.catalog.tests.factories import VendorFactory

    v = VendorFactory(name="ACME Inc")
    assert str(v) == "ACME Inc"
