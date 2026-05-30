"""
Seed the single DEFAULT_VENDOR — MVP marketplace owner.

Plan'da: "MVP'da bitta DEFAULT_VENDOR seed".
"""

from __future__ import annotations

from django.conf import settings
from django.db import migrations

DEFAULT_NAME = "My Online Market"
DEFAULT_DESC = "Premium e-commerce marketplace — Uzum.uz uslubida."


def seed(apps, schema_editor) -> None:
    Vendor = apps.get_model("vendors", "Vendor")
    slug = getattr(settings, "DEFAULT_VENDOR_SLUG", "my-online-market")
    Vendor.objects.update_or_create(
        slug=slug,
        defaults={
            "name": DEFAULT_NAME,
            "name_uz": DEFAULT_NAME,
            "name_ru": DEFAULT_NAME,
            "name_en": DEFAULT_NAME,
            "description": DEFAULT_DESC,
            "description_uz": DEFAULT_DESC,
            "description_ru": (
                "Премиум маркетплейс — в стиле Uzum.uz."
            ),
            "description_en": DEFAULT_DESC,
            "status": "active",
            "commission_rate": 0,
        },
    )


def reverse(apps, schema_editor) -> None:
    Vendor = apps.get_model("vendors", "Vendor")
    slug = getattr(settings, "DEFAULT_VENDOR_SLUG", "my-online-market")
    Vendor.objects.filter(slug=slug).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("vendors", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, reverse),
    ]
