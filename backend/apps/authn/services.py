"""
authn service layer — view'lar shu yerdagi funksiyalarni chaqiradi
(business logic view'lardan tashqarida).
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.accounts.models import OtpCode

User = get_user_model()
logger = logging.getLogger(__name__)


# =============================================================================
# Registration
# =============================================================================
@transaction.atomic
def register_user(
    *,
    email: str,
    password: str,
    full_name: str,
    language: str = User.Language.UZ,
    phone: str = "",
) -> User:
    """User yaratadi va email-verify OTP yuboradi.

    Atomik — agar email yuborish ham xato bo'lsa, user ham yaratilmaydi
    (lekin biz email-yuborishni atomic blockdan keyin chaqiramiz, chunki
    transaction ichida side-effect tavsiya etilmaydi).
    """
    user = User.objects.create_user(
        email=email,
        password=password,
        full_name=full_name,
        language=language,
        phone=phone,
    )
    return user


# =============================================================================
# OTP
# =============================================================================
def issue_otp(
    *,
    target: str,
    purpose: str,
    ttl_minutes: int = OtpCode.DEFAULT_TTL_MINUTES,
    ip_address: str | None = None,
    user_agent: str = "",
) -> tuple[OtpCode, str]:
    """Yangi OTP yaratadi va RAW kodni qaytaradi (yuborish uchun).

    Raw kod faqat shu funksiyadan qaytadi — DB'da faqat hash saqlanadi.
    Eski active OTP'larni invalidate qilish ham shu yerda.
    """
    # Eski OTP'larni mark used qilish (bitta target+purpose uchun aktiv 1 ta)
    OtpCode.objects.filter(
        target=target,
        purpose=purpose,
        used_at__isnull=True,
    ).update(used_at=timezone.now())

    raw_code = OtpCode.generate_code()
    otp = OtpCode(
        target=target,
        purpose=purpose,
        expires_at=timezone.now() + timedelta(minutes=ttl_minutes),
        ip_address=ip_address,
        user_agent=user_agent[:500],
    )
    otp.set_code(raw_code)
    otp.save()
    return otp, raw_code


def verify_otp(
    *, target: str, raw_code: str, purpose: str
) -> OtpCode | None:
    """Eng oxirgi active OTP'ni tekshiradi va used qiladi.

    Returns:
        OtpCode if successful, None otherwise.
    """
    otp = (
        OtpCode.objects.filter(
            target=target, purpose=purpose, used_at__isnull=True
        )
        .order_by("-created_at")
        .first()
    )
    if otp is None or not otp.is_valid:
        return None

    if not otp.verify(raw_code):
        otp.increment_attempt()
        return None

    otp.mark_used()
    return otp


# =============================================================================
# Email sender (B11'da Celery task'ga delegate qilindi)
# =============================================================================
def send_otp_email(target: str, raw_code: str, purpose: str) -> None:
    """OTP'ni asinxron Celery task orqali yuboradi.

    Test settings'da `CELERY_TASK_ALWAYS_EAGER=True` — sync ishlaydi.
    Production'da Redis broker orqali worker'ga uzatiladi.
    """
    from apps.notifications.tasks import send_otp_email_task

    send_otp_email_task.delay(target, raw_code, purpose)
    logger.info("OTP email enqueued: target=%s purpose=%s", target, purpose)


# =============================================================================
# Password change — invalidates all sessions
# =============================================================================
@transaction.atomic
def change_password(user: User, new_password: str) -> None:
    """Parolni o'zgartiradi va barcha outstanding refresh tokenlarni
    blacklist qiladi (boshqa qurilmalardan chiqadi)."""
    from rest_framework_simplejwt.token_blacklist.models import (
        OutstandingToken,
    )

    user.set_password(new_password)
    user.save(update_fields=["password"])

    # Barcha outstanding refresh tokenlarni blacklist
    tokens = OutstandingToken.objects.filter(user=user)
    for tok in tokens:
        try:
            tok.blacklistedtoken  # already blacklisted?
        except Exception:  # noqa: BLE001
            from rest_framework_simplejwt.token_blacklist.models import (
                BlacklistedToken,
            )

            BlacklistedToken.objects.create(token=tok)


# =============================================================================
# Request helpers
# =============================================================================
def get_client_ip(request: Any) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "") or "0.0.0.0"
