"""
django-modeltranslation — Vendor uchun i18n field'lar.
"""

from __future__ import annotations

from modeltranslation.translator import TranslationOptions, register

from apps.vendors.models import Vendor


@register(Vendor)
class VendorTranslationOptions(TranslationOptions):
    fields = ("name", "description")
