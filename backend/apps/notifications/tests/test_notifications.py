"""
Notification + Celery tests.

Test settings'da `CELERY_TASK_ALWAYS_EAGER=True` → tasks sync ishlaydi.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.core import mail
from rest_framework.test import APIClient

from apps.accounts.models import Address
from apps.accounts.tests.factories import UserFactory
from apps.catalog.tests.factories import ProductFactory
from apps.notifications.models import EmailLog, Notification

pytestmark = pytest.mark.django_db

LIST_URL = "/api/v1/notifications/"
READ_ALL_URL = "/api/v1/notifications/read-all/"


@pytest.fixture(autouse=True)
def _clear():
    from django.core.cache import cache
    cache.clear()
    mail.outbox = []
    yield
    cache.clear()


@pytest.fixture
def password():
    return "TestPass123!"


@pytest.fixture
def user(password):
    return UserFactory(email="notif@example.com", password=password)


@pytest.fixture
def authed_api(user, password):
    api = APIClient()
    api.post(
        "/api/v1/auth/login/",
        {"email": user.email, "password": password},
        format="json",
    )
    return api


# =============================================================================
# Notification creation via checkout
# =============================================================================
class TestCheckoutNotification:
    def test_creates_notification_and_sends_email(self, authed_api, user):
        product = ProductFactory(stock_quantity=5, base_price=Decimal("100"))
        address = Address.objects.create(
            user=user,
            type=Address.Type.SHIPPING,
            recipient_name="x",
            recipient_phone="+998901234567",
            region="r", city="c", street="s", building="1",
        )
        authed_api.post(
            "/api/v1/cart/items/",
            {"product_id": str(product.id), "quantity": 1},
            format="json",
        )
        resp = authed_api.post(
            "/api/v1/orders/",
            {"address_id": address.id},
            format="json",
        )
        assert resp.status_code == 201, resp.data
        # Notification yaratildi
        notif = Notification.objects.filter(
            user=user, type=Notification.Type.ORDER_CREATED
        ).first()
        assert notif is not None
        assert notif.data["order_number"] == resp.data["number"]
        # EmailLog yozildi
        log = EmailLog.objects.filter(recipient=user.email).first()
        assert log is not None
        assert log.status == EmailLog.Status.SENT
        # Console backend — mail.outbox'ga ham tushadi
        assert len(mail.outbox) >= 1


# =============================================================================
# Register — OTP async
# =============================================================================
class TestRegisterOtpAsync:
    def test_otp_email_via_celery_eager(self):
        api = APIClient()
        resp = api.post(
            "/api/v1/auth/register/",
            {
                "email": "newonly@example.com",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
                "full_name": "X",
            },
            format="json",
        )
        assert resp.status_code == 201
        # EmailLog must exist (task ran eager)
        assert EmailLog.objects.filter(
            recipient="newonly@example.com", template="otp"
        ).exists()
        assert len(mail.outbox) >= 1


# =============================================================================
# List / Read API
# =============================================================================
class TestNotificationAPI:
    def test_anon_forbidden(self):
        api = APIClient()
        resp = api.get(LIST_URL)
        assert resp.status_code in (401, 403)

    def test_list_user_scoped(self, authed_api, user):
        Notification.objects.create(
            user=user, type=Notification.Type.SYSTEM,
            title="A", message="m1",
        )
        other = UserFactory(email="other-notif@example.com")
        Notification.objects.create(
            user=other, type=Notification.Type.SYSTEM,
            title="other", message="m2",
        )
        resp = authed_api.get(LIST_URL)
        assert resp.status_code == 200
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["title"] == "A"

    def test_filter_is_read(self, authed_api, user):
        Notification.objects.create(
            user=user, type=Notification.Type.SYSTEM,
            title="read", message="m", is_read=True,
        )
        Notification.objects.create(
            user=user, type=Notification.Type.SYSTEM,
            title="unread", message="m",
        )
        resp = authed_api.get(LIST_URL + "?is_read=false")
        titles = [n["title"] for n in resp.data["results"]]
        assert titles == ["unread"]

    def test_mark_read(self, authed_api, user):
        n = Notification.objects.create(
            user=user, type=Notification.Type.SYSTEM,
            title="t", message="m",
        )
        resp = authed_api.patch(f"{LIST_URL}{n.pk}/read/")
        assert resp.status_code == 200
        assert resp.data["is_read"] is True
        n.refresh_from_db()
        assert n.read_at is not None

    def test_mark_read_only_own(self, authed_api):
        other = UserFactory(email="o2@example.com")
        n = Notification.objects.create(
            user=other, type=Notification.Type.SYSTEM,
            title="t", message="m",
        )
        resp = authed_api.patch(f"{LIST_URL}{n.pk}/read/")
        assert resp.status_code == 404

    def test_read_all(self, authed_api, user):
        for i in range(3):
            Notification.objects.create(
                user=user, type=Notification.Type.SYSTEM,
                title=f"t{i}", message="m",
            )
        resp = authed_api.post(READ_ALL_URL)
        assert resp.status_code == 200
        assert resp.data["marked"] == 3
        assert Notification.objects.filter(
            user=user, is_read=False
        ).count() == 0


# =============================================================================
# Cleanup expired OTPs
# =============================================================================
class TestOtpCleanup:
    def test_cleanup_task_deletes_old(self):
        from datetime import timedelta

        from django.utils import timezone

        from apps.accounts.models import OtpCode
        from apps.notifications.tasks import cleanup_expired_otps_task

        # 25 hours expired — eligible
        old = OtpCode(
            target="x@x.com",
            purpose=OtpCode.Purpose.EMAIL_VERIFY,
            expires_at=timezone.now() - timedelta(hours=25),
        )
        old.set_code("123456")
        old.save()
        # 1 hour expired — also eligible (cutoff is 24h)
        recent_expired = OtpCode(
            target="y@y.com",
            purpose=OtpCode.Purpose.EMAIL_VERIFY,
            expires_at=timezone.now() - timedelta(hours=1),
        )
        recent_expired.set_code("123456")
        recent_expired.save()
        # Future expiry — keep
        future = OtpCode(
            target="z@z.com",
            purpose=OtpCode.Purpose.EMAIL_VERIFY,
            expires_at=timezone.now() + timedelta(hours=2),
        )
        future.set_code("123456")
        future.save()

        deleted = cleanup_expired_otps_task()
        # cutoff: now - 24h → only "old" (25h ago) below cutoff
        assert deleted == 1
        assert OtpCode.objects.filter(target="x@x.com").count() == 0
        assert OtpCode.objects.filter(target="y@y.com").count() == 1
        assert OtpCode.objects.filter(target="z@z.com").count() == 1
