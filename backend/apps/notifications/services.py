"""
Notification creation service — bir marta call'da Notification + email task.
"""

from __future__ import annotations

from django.utils.translation import activate, gettext as _

from apps.notifications.models import Notification
from apps.notifications.tasks import send_order_confirmation_task


def notify_order_created(order) -> Notification:
    """Buyurtma yaratilganda chaqiriladi. Notification + email async."""
    activate(order.user.language)
    title = str(_("Buyurtmangiz qabul qilindi"))
    message = str(
        _("№ %(number)s — kutib oling, tez orada tasdiqlanadi.")
        % {"number": order.number}
    )

    notif = Notification.objects.create(
        user=order.user,
        type=Notification.Type.ORDER_CREATED,
        title=title,
        message=message,
        data={
            "order_number": order.number,
            "order_id": str(order.id),
            "total": str(order.total),
            "currency": order.currency,
        },
    )
    # Async email
    send_order_confirmation_task.delay(str(order.id))
    return notif
