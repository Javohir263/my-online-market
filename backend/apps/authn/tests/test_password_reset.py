"""
Password reset flow tests — generic responses + enumeration protection.
"""

from __future__ import annotations

import pytest

from apps.accounts.models import OtpCode
from apps.authn import services

pytestmark = pytest.mark.django_db

REQUEST_URL = "/api/v1/auth/password/reset/request/"
CONFIRM_URL = "/api/v1/auth/password/reset/confirm/"


class TestRequest:
    def test_request_existing_user_sends_otp(self, api, user, mailoutbox):
        resp = api.post(
            REQUEST_URL, {"email": user.email}, format="json"
        )
        assert resp.status_code == 200
        assert OtpCode.objects.filter(
            target=user.email, purpose=OtpCode.Purpose.PASSWORD_RESET
        ).exists()
        assert len(mailoutbox) == 1

    def test_request_unknown_user_returns_200_anti_enumeration(
        self, api, mailoutbox
    ):
        resp = api.post(
            REQUEST_URL, {"email": "nobody@example.com"}, format="json"
        )
        assert resp.status_code == 200, resp.data
        assert len(mailoutbox) == 0


class TestConfirm:
    def test_confirm_success_changes_password(self, api, user):
        _, raw = services.issue_otp(
            target=user.email, purpose=OtpCode.Purpose.PASSWORD_RESET
        )
        new_pwd = "BrandNewPass456!"
        resp = api.post(
            CONFIRM_URL,
            {
                "email": user.email,
                "code": raw,
                "new_password": new_pwd,
                "new_password_confirm": new_pwd,
            },
            format="json",
        )
        assert resp.status_code == 200, resp.data
        user.refresh_from_db()
        assert user.check_password(new_pwd)

    def test_confirm_wrong_code(self, api, user):
        services.issue_otp(
            target=user.email, purpose=OtpCode.Purpose.PASSWORD_RESET
        )
        resp = api.post(
            CONFIRM_URL,
            {
                "email": user.email,
                "code": "000000",
                "new_password": "OtherPass789!",
                "new_password_confirm": "OtherPass789!",
            },
            format="json",
        )
        assert resp.status_code == 400

    def test_confirm_unknown_user_generic_error(self, api):
        resp = api.post(
            CONFIRM_URL,
            {
                "email": "nobody@example.com",
                "code": "123456",
                "new_password": "AnotherPass456!",
                "new_password_confirm": "AnotherPass456!",
            },
            format="json",
        )
        assert resp.status_code == 400

    def test_confirm_password_mismatch(self, api, user):
        _, raw = services.issue_otp(
            target=user.email, purpose=OtpCode.Purpose.PASSWORD_RESET
        )
        resp = api.post(
            CONFIRM_URL,
            {
                "email": user.email,
                "code": raw,
                "new_password": "SamePass123!",
                "new_password_confirm": "Different456!",
            },
            format="json",
        )
        assert resp.status_code == 400
