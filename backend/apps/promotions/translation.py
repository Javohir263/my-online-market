"""
Banner i18n field'lari — modeltranslation.
"""

from __future__ import annotations

from modeltranslation.translator import TranslationOptions, register

from apps.promotions.models import Banner


@register(Banner)
class BannerTranslationOptions(TranslationOptions):
    fields = ("title", "subtitle")
