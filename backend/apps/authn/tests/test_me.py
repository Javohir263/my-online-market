"""
/auth/me/ tests.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.django_db

URL = "/api/v1/auth/me/"


def test_me_anonymous_unauthorized(api):
    resp = api.get(URL)
    assert resp.status_code in (401, 403)


def test_me_returns_current_user(authed_api, user):
    resp = authed_api.get(URL)
    assert resp.status_code == 200
    assert resp.data["email"] == user.email
    assert "password" not in resp.data
    # UUID id present
    assert str(resp.data["id"]) == str(user.id)
