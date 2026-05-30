"""
Email verification flow tests.
"""

from __future__ import annotations

import pytest

from apps.accounts.models import OtpCode
from apps.authn import services

pytestmark = pytest.mark.django_db

SEND_URL = "/api/v1/auth/email/verify/send/"
CONFIRM_URL = "/api/v1/auth/email/verify/confirm/"


def test_send_otp_authenticated(authed_api, user, mailoutbox):
    resp = authed_api.post(SEND_URL)
    assert resp.status_code == 200
    assert OtpCode.objects.filter(
        target=user.email, purpose=OtpCode.Purpose.EMAIL_VERIFY
    ).exists()
    assert len(mailoutbox) == 1


def test_send_otp_already_verified(authed_api, user):
    user.is_email_verified = True
    user.save(update_fields=["is_email_verified"])
    resp = authed_api.post(SEND_URL)
    assert resp.status_code == 400


def test_confirm_otp_success(authed_api, user):
    _, raw = services.issue_otp(
        target=user.email, purpose=OtpCode.Purpose.EMAIL_VERIFY
    )
    resp = authed_api.post(CONFIRM_URL, {"code": raw}, format="json")
    assert resp.status_code == 200
    user.refresh_from_db()
    assert user.is_email_verified is True


def test_confirm_otp_wrong_code(authed_api, user):
    services.issue_otp(target=user.email, purpose=OtpCode.Purpose.EMAIL_VERIFY)
    resp = authed_api.post(CONFIRM_URL, {"code": "000000"}, format="json")
    assert resp.status_code == 400


def test_confirm_otp_unauthenticated(api):
    resp = api.post(CONFIRM_URL, {"code": "123456"}, format="json")
    assert resp.status_code in (401, 403)
