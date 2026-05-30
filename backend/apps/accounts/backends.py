"""
Case-insensitive email authentication backend.

Login formada `User@Example.COM` yoki `user@example.com` — ikkalasi ham
bir xil foydalanuvchini topadi (DB'da lowercase saqlanadi UserManager
tomonidan).
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class EmailBackend(ModelBackend):
    """`ModelBackend` ni email `iexact` lookup bilan kengaytirgan variant."""

    def authenticate(
        self,
        request,
        username: str | None = None,
        password: str | None = None,
        **kwargs,
    ):
        email = (username or kwargs.get("email") or "").strip()
        if not email or not password:
            return None
        try:
            user = UserModel.objects.get(email__iexact=email)
        except UserModel.DoesNotExist:
            # Default behavior: run hasher to mitigate timing attacks
            UserModel().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
