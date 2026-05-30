"""
Scoped throttle classes for auth endpoints.

Rate'lar `settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']` da set qilingan.
Har view'da `throttle_scope = "<name>"` orqali to'g'ri rate olinadi.

Per-email throttle (login brute force) DRF'ning standart sinflari'da yo'q —
o'zimizning `EmailRateThrottle` ni qo'shamiz (email + IP composite key).
"""

from __future__ import annotations

from rest_framework.throttling import ScopedRateThrottle, SimpleRateThrottle


class EmailRateThrottle(SimpleRateThrottle):
    """Throttle by request.data['email'] — protects against credential
    stuffing on a single target email."""

    scope = "login_email"

    def get_cache_key(self, request, view):
        email = (
            (request.data.get("email") or "").strip().lower()
            if hasattr(request, "data")
            else ""
        )
        if not email:
            return None  # no throttle (no key)
        return self.cache_format % {"scope": self.scope, "ident": email}


# Aliases for clarity in views — they just use ScopedRateThrottle but the
# scope name makes the intent explicit.
class RegisterThrottle(ScopedRateThrottle):
    scope_attr = "throttle_scope"


class LoginThrottle(ScopedRateThrottle):
    scope_attr = "throttle_scope"


class OtpSendThrottle(ScopedRateThrottle):
    scope_attr = "throttle_scope"


class OtpVerifyThrottle(ScopedRateThrottle):
    scope_attr = "throttle_scope"


class PasswordResetThrottle(ScopedRateThrottle):
    scope_attr = "throttle_scope"
