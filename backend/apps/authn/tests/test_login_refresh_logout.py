"""
Login + refresh + logout flow tests.
"""

from __future__ import annotations

import pytest
from django.conf import settings

from apps.accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

LOGIN_URL = "/api/v1/auth/login/"
REFRESH_URL = "/api/v1/auth/refresh/"
LOGOUT_URL = "/api/v1/auth/logout/"
ME_URL = "/api/v1/auth/me/"


class TestLogin:
    def test_login_sets_cookies(self, api, user, user_password):
        resp = api.post(
            LOGIN_URL,
            data={"email": user.email, "password": user_password},
            format="json",
        )
        assert resp.status_code == 200
        # User data returned
        assert resp.data["email"] == user.email
        # Cookies set
        assert settings.AUTH_COOKIE_ACCESS in resp.cookies
        assert settings.AUTH_COOKIE_REFRESH in resp.cookies
        access = resp.cookies[settings.AUTH_COOKIE_ACCESS]
        assert access["httponly"]
        assert access["samesite"] == settings.AUTH_COOKIE_SAMESITE

    def test_login_case_insensitive_email(self, api, user, user_password):
        resp = api.post(
            LOGIN_URL,
            data={"email": user.email.upper(), "password": user_password},
            format="json",
        )
        assert resp.status_code == 200

    def test_login_wrong_password(self, api, user):
        resp = api.post(
            LOGIN_URL,
            data={"email": user.email, "password": "wrong"},
            format="json",
        )
        assert resp.status_code == 400

    def test_login_unknown_email_generic_error(self, api):
        resp = api.post(
            LOGIN_URL,
            data={"email": "nobody@example.com", "password": "x"},
            format="json",
        )
        assert resp.status_code == 400
        # Same generic message — no enumeration
        assert "noto'g'ri" in str(resp.data).lower() or "invalid" in str(resp.data).lower()

    def test_login_inactive_user(self, api, user_password):
        u = UserFactory(
            email="inactive@example.com",
            password=user_password,
            is_active=False,
        )
        resp = api.post(
            LOGIN_URL,
            data={"email": u.email, "password": user_password},
            format="json",
        )
        assert resp.status_code == 400


class TestRefresh:
    def test_refresh_rotates_tokens(self, authed_api):
        old_refresh = authed_api.cookies[settings.AUTH_COOKIE_REFRESH].value

        resp = authed_api.post(REFRESH_URL)
        assert resp.status_code == 200
        new_refresh = resp.cookies[settings.AUTH_COOKIE_REFRESH].value
        new_access = resp.cookies[settings.AUTH_COOKIE_ACCESS].value

        assert new_refresh != old_refresh, "refresh token must rotate"
        assert new_access  # non-empty

    def test_refresh_without_cookie_fails(self, api):
        resp = api.post(REFRESH_URL)
        assert resp.status_code in (401, 403)

    def test_refresh_old_token_blacklisted(self, authed_api):
        # First rotation — old gets blacklisted
        first_refresh = authed_api.cookies[settings.AUTH_COOKIE_REFRESH].value
        authed_api.post(REFRESH_URL)
        # Reuse old refresh — must fail
        authed_api.cookies[settings.AUTH_COOKIE_REFRESH] = first_refresh
        resp = authed_api.post(REFRESH_URL)
        assert resp.status_code in (401, 403)


class TestLogout:
    def test_logout_clears_cookies(self, authed_api):
        resp = authed_api.post(LOGOUT_URL)
        assert resp.status_code == 204
        # Cookies tagged for deletion (max-age=0 / expires)
        for key in (settings.AUTH_COOKIE_ACCESS, settings.AUTH_COOKIE_REFRESH):
            cookie = resp.cookies.get(key)
            assert cookie is not None
            assert cookie.value == ""

    def test_logout_blacklists_refresh(self, authed_api):
        refresh = authed_api.cookies[settings.AUTH_COOKIE_REFRESH].value
        authed_api.post(LOGOUT_URL)
        # Try to refresh with the now-blacklisted token
        authed_api.cookies[settings.AUTH_COOKIE_REFRESH] = refresh
        resp = authed_api.post(REFRESH_URL)
        assert resp.status_code in (401, 403)

    def test_logout_requires_auth(self, api):
        resp = api.post(LOGOUT_URL)
        assert resp.status_code in (401, 403)
