"""
i18n endpoint + UserLanguageMiddleware tests.
"""

from __future__ import annotations

import pytest
from django.conf import settings
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _clear_cache():
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def user_password():
    return "TestPass123!"


@pytest.fixture
def user(user_password):
    return UserFactory(email="lang@example.com", password=user_password)


@pytest.fixture
def authed_api(api, user, user_password):
    resp = api.post(
        "/api/v1/auth/login/",
        data={"email": user.email, "password": user_password},
        format="json",
    )
    assert resp.status_code == 200
    return api


# =============================================================================
# GET /i18n/languages/
# =============================================================================
class TestLanguageList:
    URL = "/api/v1/i18n/languages/"

    def test_list_returns_supported_languages(self, api):
        resp = api.get(self.URL)
        assert resp.status_code == 200
        codes = [lang["code"] for lang in resp.data["languages"]]
        assert set(codes) == {"uz", "ru", "en"}

    def test_default_language_is_uz(self, api):
        resp = api.get(self.URL)
        assert resp.data["default"] == "uz"

    def test_accept_language_changes_current(self, api):
        resp = api.get(self.URL, HTTP_ACCEPT_LANGUAGE="ru")
        assert resp.status_code == 200
        assert resp.data["current"] == "ru"

    def test_accept_language_unsupported_falls_back(self, api):
        resp = api.get(self.URL, HTTP_ACCEPT_LANGUAGE="fr")
        assert resp.data["current"] == "uz"  # default


# =============================================================================
# PATCH /i18n/preference/
# =============================================================================
class TestLanguagePreference:
    URL = "/api/v1/i18n/preference/"

    def test_anonymous_sets_cookie(self, api):
        resp = api.patch(self.URL, {"language": "ru"}, format="json")
        assert resp.status_code == 200
        assert resp.data["language"] == "ru"
        assert settings.LANGUAGE_COOKIE_NAME in resp.cookies
        assert resp.cookies[settings.LANGUAGE_COOKIE_NAME].value == "ru"

    def test_authenticated_updates_user_language(self, authed_api, user):
        resp = authed_api.patch(self.URL, {"language": "en"}, format="json")
        assert resp.status_code == 200
        user.refresh_from_db()
        assert user.language == "en"

    def test_unsupported_language_rejected(self, api):
        resp = api.patch(self.URL, {"language": "fr"}, format="json")
        assert resp.status_code == 400


# =============================================================================
# UserLanguageMiddleware — user.language > Accept-Language
# =============================================================================
class TestUserLanguageMiddleware:
    URL = "/api/v1/i18n/languages/"

    def test_authed_user_language_overrides_header(self, authed_api, user):
        # User language = "uz" (default)
        user.language = "en"
        user.save(update_fields=["language"])

        # Re-login to refresh session
        resp = authed_api.get(
            self.URL, HTTP_ACCEPT_LANGUAGE="ru"
        )  # header says ru
        assert resp.data["current"] == "en"  # but user.language wins

    def test_anon_user_uses_accept_language(self, api):
        resp = api.get(self.URL, HTTP_ACCEPT_LANGUAGE="en")
        assert resp.data["current"] == "en"
