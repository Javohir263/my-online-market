"""
Signal handlers — auto-merge anon cart with user cart on login.
"""

from __future__ import annotations

import logging

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from apps.cart.services import merge_on_login

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def auto_merge_cart_on_login(sender, request, user, **kwargs) -> None:
    """Login muvaffaqiyatli bo'lganda anon cart user cart'ga ko'chiriladi."""
    try:
        merge_on_login(request, user)
    except Exception:  # noqa: BLE001
        # Merge muvaffaqiyatsizligi login'ni to'xtatmaydi
        logger.exception("Cart merge on login failed for user %s", user.email)
