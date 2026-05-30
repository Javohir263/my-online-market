"""
Authentication views — 9 ta endpoint.

Security highlights:
- Generic errors on register/password-reset to prevent email enumeration.
- IP + UA audit for OTP issuance.
- httpOnly cookie tokens set by helpers; CSRF enforced by CookieJWTAuthentication.
- Refresh rotation + blacklist enabled in settings.
"""

from __future__ import annotations

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import OtpCode

from . import services
from .cookies import clear_auth_cookies, set_auth_cookies
from .serializers import (
    EmailVerifyConfirmSerializer,
    LoginSerializer,
    LogoutSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserSerializer,
)
from .throttles import (
    EmailRateThrottle,
    LoginThrottle,
    OtpSendThrottle,
    OtpVerifyThrottle,
    PasswordResetThrottle,
    RegisterThrottle,
)

User = get_user_model()
logger = logging.getLogger(__name__)


# =============================================================================
# Register
# =============================================================================
class RegisterView(APIView):
    """`POST /auth/register/` — Yangi user yaratadi va email-verify OTP yuboradi."""

    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]
    throttle_scope = "register"

    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserSerializer},
    )
    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        payload = serializer.validated_data.copy()
        payload.pop("password_confirm", None)

        user = services.register_user(**payload)

        try:
            _otp, raw_code = services.issue_otp(
                target=user.email,
                purpose=OtpCode.Purpose.EMAIL_VERIFY,
                ip_address=services.get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
            services.send_otp_email(
                user.email, raw_code, OtpCode.Purpose.EMAIL_VERIFY
            )
        except Exception:  # noqa: BLE001
            logger.exception("OTP send failed for new user %s", user.email)

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


# =============================================================================
# Login
# =============================================================================
class LoginView(APIView):
    """`POST /auth/login/` — Cookie'ga JWT tokenlarni o'rnatadi."""

    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle, EmailRateThrottle]
    throttle_scope = "login"

    @extend_schema(
        request=LoginSerializer,
        responses={200: UserSerializer},
    )
    def post(self, request):
        serializer = LoginSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        user.last_login = timezone.now()
        user.last_login_ip = services.get_client_ip(request)
        user.save(update_fields=["last_login", "last_login_ip"])
        user_logged_in.send(sender=user.__class__, request=request, user=user)

        response = Response(
            UserSerializer(user).data, status=status.HTTP_200_OK
        )
        set_auth_cookies(response, str(access), str(refresh))
        return response


# =============================================================================
# Logout
# =============================================================================
class LogoutView(APIView):
    """`POST /auth/logout/` — Refresh blacklist + cookies clear."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={204: OpenApiResponse(description="Logged out")},
    )
    def post(self, request):
        from django.conf import settings

        refresh_raw = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        if refresh_raw:
            try:
                token = RefreshToken(refresh_raw)
                token.blacklist()
            except TokenError:
                pass

        response = Response(status=status.HTTP_204_NO_CONTENT)
        clear_auth_cookies(response)
        return response


# =============================================================================
# Refresh
# =============================================================================
class RefreshView(APIView):
    """`POST /auth/refresh/` — Refresh cookie → yangi access (+ refresh rotation)."""

    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description="Tokens refreshed")},
    )
    def post(self, request):
        from django.conf import settings

        refresh_raw = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        if not refresh_raw:
            raise InvalidToken(_("Refresh token mavjud emas."))

        try:
            old_refresh = RefreshToken(refresh_raw)
        except TokenError as exc:
            raise InvalidToken(str(exc)) from exc

        try:
            old_refresh.blacklist()
        except AttributeError:
            pass

        user_id = old_refresh.get("user_id")
        user = User.objects.filter(pk=user_id, is_active=True).first()
        if user is None:
            raise InvalidToken(_("User mavjud emas yoki faol emas."))

        new_refresh = RefreshToken.for_user(user)
        new_access = new_refresh.access_token

        response = Response(status=status.HTTP_200_OK)
        set_auth_cookies(response, str(new_access), str(new_refresh))
        return response


# =============================================================================
# Me
# =============================================================================
class MeView(APIView):
    """`GET /auth/me/` — Joriy foydalanuvchi profili."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserSerializer})
    def get(self, request):
        return Response(UserSerializer(request.user).data)


# =============================================================================
# Email verification — SEND
# =============================================================================
class EmailVerifySendView(APIView):
    """`POST /auth/email/verify/send/` 🔒 — OTP qayta yuborish."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [OtpSendThrottle]
    throttle_scope = "otp_send"

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description="OTP sent")},
    )
    def post(self, request):
        if request.user.is_email_verified:
            return Response(
                {"detail": _("Email allaqachon tasdiqlangan.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        _otp, raw_code = services.issue_otp(
            target=request.user.email,
            purpose=OtpCode.Purpose.EMAIL_VERIFY,
            ip_address=services.get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        services.send_otp_email(
            request.user.email, raw_code, OtpCode.Purpose.EMAIL_VERIFY
        )
        return Response({"detail": _("Kod yuborildi.")})


# =============================================================================
# Email verification — CONFIRM
# =============================================================================
class EmailVerifyConfirmView(APIView):
    """`POST /auth/email/verify/confirm/` 🔒 — OTP tasdiqlash."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [OtpVerifyThrottle]
    throttle_scope = "otp_verify"

    @extend_schema(
        request=EmailVerifyConfirmSerializer,
        responses={200: UserSerializer},
    )
    def post(self, request):
        serializer = EmailVerifyConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = services.verify_otp(
            target=request.user.email,
            raw_code=serializer.validated_data["code"],
            purpose=OtpCode.Purpose.EMAIL_VERIFY,
        )
        if otp is None:
            return Response(
                {"detail": _("Kod noto'g'ri yoki muddati o'tgan.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.is_email_verified = True
        request.user.save(update_fields=["is_email_verified"])
        return Response(UserSerializer(request.user).data)


# =============================================================================
# Password reset — REQUEST
# =============================================================================
class PasswordResetRequestView(APIView):
    """`POST /auth/password/reset/request/` — Email → OTP.

    Always returns 200 (anti-enumeration). OTP yuboriladi faqat user mavjud bo'lsa.
    """

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetThrottle]
    throttle_scope = "password_reset"

    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={200: OpenApiResponse(description="OTP sent if user exists")},
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email__iexact=email).first()
        if user is not None:
            _otp, raw_code = services.issue_otp(
                target=user.email,
                purpose=OtpCode.Purpose.PASSWORD_RESET,
                ip_address=services.get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
            services.send_otp_email(
                user.email, raw_code, OtpCode.Purpose.PASSWORD_RESET
            )

        return Response(
            {
                "detail": _(
                    "Agar email mavjud bo'lsa, tiklash kodi yuborildi."
                )
            }
        )


# =============================================================================
# Password reset — CONFIRM
# =============================================================================
class PasswordResetConfirmView(APIView):
    """`POST /auth/password/reset/confirm/` — OTP + new password."""

    permission_classes = [AllowAny]
    throttle_classes = [OtpVerifyThrottle]
    throttle_scope = "otp_verify"

    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={
            200: OpenApiResponse(description="Password updated"),
            400: OpenApiResponse(description="Invalid OTP or password"),
        },
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            return Response(
                {"detail": _("Kod noto'g'ri yoki muddati o'tgan.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = services.verify_otp(
            target=user.email,
            raw_code=serializer.validated_data["code"],
            purpose=OtpCode.Purpose.PASSWORD_RESET,
        )
        if otp is None:
            return Response(
                {"detail": _("Kod noto'g'ri yoki muddati o'tgan.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        services.change_password(user, serializer.validated_data["new_password"])
        return Response({"detail": _("Parol o'zgartirildi.")})
