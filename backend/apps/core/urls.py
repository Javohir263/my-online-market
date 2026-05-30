"""
core app — i18n endpoints. `/api/v1/i18n/...` ostiga ulanadi.
"""

from __future__ import annotations

from django.urls import path

from apps.core.views import LanguageListView, LanguagePreferenceView

app_name = "core"

urlpatterns = [
    path("languages/", LanguageListView.as_view(), name="languages"),
    path("preference/", LanguagePreferenceView.as_view(), name="preference"),
]
