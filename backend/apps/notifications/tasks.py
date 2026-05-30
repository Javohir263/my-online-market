"""
Celery tasks — async email + notification.

Bu yerdagi `@shared_task`'lar Redis broker orqali yuboriladi
(production) yoki test settings'da `CELERY_TASK_ALWAYS_EAGER=True`
bilan inline ishlaydi.
"""

from __future__ import annotations

import logging

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from apps.notifications.models import EmailLog

logger = logging.getLogger(__name__)


@shared_task(name="notifications.send_email", autoretry_for=(Exception,), max_retries=3, default_retry_delay=30)
def send_email_task(
    *,
    recipient: str,
    subject: str,
    body: str,
    template: str = "",
) -> int:
    """Asosiy email yuborish task'i. EmailLog yozadi."""
    log = EmailLog.objects.create(
        recipient=recipient,
        subject=subject,
        body=body,
        template=template,
        status=EmailLog.Status.QUEUED,
    )
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=None,  # DEFAULT_FROM_EMAIL
            recipient_list=[recipient],
            fail_silently=False,
        )
        log.status = EmailLog.Status.SENT
        log.sent_at = timezone.now()
        log.save(update_fields=["status", "sent_at"])
        return log.id
    except Exception as exc:
        log.status = EmailLog.Status.FAILED
        log.error_message = str(exc)[:1000]
        log.save(update_fields=["status", "error_message"])
        raise


@shared_task(name="notifications.send_otp")
def send_otp_email_task(target: str, raw_code: str, purpose: str) -> None:
    """OTP email — B3'dagi sync `services.send_otp_email`'ning async versiyasi."""
    from django.utils.translation import gettext as _

    from apps.accounts.models import OtpCode

    subject_by_purpose = {
        OtpCode.Purpose.EMAIL_VERIFY: _("Email tasdiqlash kodi"),
        OtpCode.Purpose.PASSWORD_RESET: _("Parolni tiklash kodi"),
        OtpCode.Purpose.LOGIN: _("Tizimga kirish kodi"),
    }
    subject = str(subject_by_purpose.get(purpose, _("Tasdiqlash kodi")))
    body = str(
        _(
            "Sizning bir martalik kodingiz: %(code)s\n\n"
            "Kod %(minutes)d daqiqa amal qiladi."
        )
        % {"code": raw_code, "minutes": OtpCode.DEFAULT_TTL_MINUTES}
    )

    send_email_task(
        recipient=target,
        subject=subject,
        body=body,
        template="otp",
    )


@shared_task(name="notifications.send_order_confirmation")
def send_order_confirmation_task(order_id: str) -> None:
    """Buyurtma tasdig'i emaili. order_id — Order.id (UUID string)."""
    from django.utils.translation import activate

    from apps.orders.models import Order

    order = Order.objects.filter(pk=order_id).first()
    if order is None:
        logger.warning("send_order_confirmation: order not found %s", order_id)
        return

    activate(order.user.language)
    from django.utils.translation import gettext as _

    subject = str(_("Buyurtmangiz qabul qilindi: %(number)s") % {"number": order.number})
    items_text = "\n".join(
        f"• {it.product_name_snapshot} × {it.quantity} = {it.line_total} {order.currency}"
        for it in order.items.all()
    )
    body = str(
        _(
            "Hurmatli mijoz,\n\n"
            "Sizning %(number)s raqamli buyurtmangiz muvaffaqiyatli qabul qilindi.\n\n"
            "Mahsulotlar:\n%(items)s\n\n"
            "Jami: %(total)s %(currency)s\n\n"
            "My Online Market"
        )
        % {
            "number": order.number,
            "items": items_text,
            "total": order.total,
            "currency": order.currency,
        }
    )

    send_email_task(
        recipient=order.user.email,
        subject=subject,
        body=body,
        template="order_confirmation",
    )


@shared_task(name="notifications.cleanup_expired_otps")
def cleanup_expired_otps_task() -> int:
    """24 soatdan eski muddati o'tgan OTP'larni o'chiradi.

    Celery beat schedule orqali kuniga 1 marta chaqiriladi.
    """
    from datetime import timedelta

    from apps.accounts.models import OtpCode

    cutoff = timezone.now() - timedelta(hours=24)
    deleted, _ = OtpCode.objects.filter(expires_at__lt=cutoff).delete()
    logger.info("Cleaned up %d expired OTPs", deleted)
    return deleted
