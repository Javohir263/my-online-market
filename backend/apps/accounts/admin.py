"""
accounts admin.

`UserAdmin` ni custom qilamiz — username yo'q, email login. Address inline.
OtpCode read-only (raw kod hech qachon ko'rinmaydi — hash saqlanadi).
"""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import Address, OtpCode, User


# =============================================================================
# Custom forms — email-based, no username
# =============================================================================
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "full_name")


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


# =============================================================================
# AddressInline
# =============================================================================
class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = (
        "type", "recipient_name", "recipient_phone",
        "city", "street", "building", "is_default",
    )
    show_change_link = True


# =============================================================================
# UserAdmin
# =============================================================================
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Email-based admin — no username field anywhere."""

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        "email", "full_name", "phone",
        "role", "language",
        "is_active", "is_email_verified", "is_phone_verified",
        "created_at",
    )
    list_filter = (
        "role", "language",
        "is_active", "is_staff", "is_superuser",
        "is_email_verified", "is_phone_verified",
    )
    search_fields = ("email", "full_name", "phone")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "last_login", "last_login_ip")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {"fields": ("full_name", "phone", "language")},
        ),
        (
            _("Role & status"),
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_email_verified",
                    "is_phone_verified",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "classes": ("collapse",),
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Audit"),
            {
                "classes": ("collapse",),
                "fields": (
                    "last_login",
                    "last_login_ip",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "full_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    inlines = [AddressInline]


# =============================================================================
# AddressAdmin (stand-alone)
# =============================================================================
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "user", "type", "recipient_name",
        "city", "street", "building",
        "is_default", "created_at",
    )
    list_filter = ("type", "is_default", "region")
    search_fields = (
        "recipient_name", "recipient_phone",
        "city", "street", "user__email",
    )
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")


# =============================================================================
# OtpCodeAdmin — read-only debugging view (no raw code visible)
# =============================================================================
@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display = (
        "target", "purpose",
        "expires_at", "used_at",
        "attempts", "max_attempts",
        "is_valid_display", "created_at",
    )
    list_filter = ("purpose",)
    search_fields = ("target",)
    ordering = ("-created_at",)
    readonly_fields = (
        "id", "target", "purpose",
        "code_hash", "expires_at", "used_at",
        "attempts", "max_attempts",
        "ip_address", "user_agent",
        "created_at", "updated_at",
    )

    def has_add_permission(self, request) -> bool:
        return False  # only created via service layer

    @admin.display(boolean=True, description=_("valid"))
    def is_valid_display(self, obj: OtpCode) -> bool:
        return obj.is_valid
