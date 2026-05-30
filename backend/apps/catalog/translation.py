"""
django-modeltranslation — Catalog modelar uchun i18n field'lar.

Har bir TranslationOptions Django'da `<field>_uz`, `<field>_ru`, `<field>_en`
ustunlarini yaratadi (LANGUAGES'da belgilangan).
"""

from __future__ import annotations

from modeltranslation.translator import TranslationOptions, register

from apps.catalog.models import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductImage,
    ProductTag,
)


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Brand)
class BrandTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(ProductTag)
class ProductTagTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ("name", "short_description", "description")


@register(ProductImage)
class ProductImageTranslationOptions(TranslationOptions):
    fields = ("alt_text",)


@register(ProductAttribute)
class ProductAttributeTranslationOptions(TranslationOptions):
    fields = ("name", "value")
