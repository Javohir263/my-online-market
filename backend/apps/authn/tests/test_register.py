"""
Register endpoint tests.
"""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import OtpCode

User = get_user_model()
pytestmark = pytest.mark.django_db

URL = "/api/v1/auth/register/"


def _payload(**overrides):
    base = {
        "email": "newuser@example.com",
        "password": "StrongPass123!",
        "password_confirm": "StrongPass123!",
        "full_name": "New User",
    }
    base.update(overrides)
    return base


class TestRegister:
    def test_register_success_creates_user_and_otp(self, api, mailoutbox):
        resp = api.post(URL, _payload(), format="json")
        assert resp.status_code == 201, resp.data
        assert resp.data["email"] == "newuser@example.com"
        assert resp.data["is_email_verified"] is False
        # UUID, no password leaked
        assert "password" not in resp.data
        assert User.objects.filter(email="newuser@example.com").exists()
        # OTP issued + email sent
        assert OtpCode.objects.filter(
            target="newuser@example.com",
            purpose=OtpCode.Purpose.EMAIL_VERIFY,
        ).exists()
        assert len(mailoutbox) == 1

    def test_register_duplicate_email(self, api, user):
        resp = api.post(URL, _payload(email=user.email), format="json")
        assert resp.status_code == 400

    def test_register_duplicate_case_insensitive(self, api, user):
        resp = api.post(
            URL, _payload(email=user.email.upper()), format="json"
        )
        assert resp.status_code == 400

    def test_register_password_mismatch(self, api):
        resp = api.post(
            URL, _payload(password_confirm="Different123!"), format="json"
        )
        assert resp.status_code == 400

    def test_register_weak_password(self, api):
        resp = api.post(URL, _payload(password="short", password_confirm="short"), format="json")
        assert resp.status_code == 400

    def test_register_normalizes_email(self, api):
        resp = api.post(URL, _payload(email="MiXeD@Example.COM"), format="json")
        assert resp.status_code == 201
        assert User.objects.filter(email="mixed@example.com").exists()
