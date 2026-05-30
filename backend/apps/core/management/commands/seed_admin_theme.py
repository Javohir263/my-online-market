"""
`python manage.py seed_admin_theme` — My Online Market brand theme
(bordoviy + bej + to'q yashil) for django-admin-interface.

Idempotent: re-running updates colors without duplicating themes.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed (or update) the My Online Market admin theme."

    THEME_NAME = "My Online Market"

    def handle(self, *args, **options):
        from admin_interface.models import Theme

        defaults = {
            # Title bar — bordoviy (brand primary)
            "title": "My Online Market Admin",
            "title_visible": True,
            "title_color": "#FFFFFF",
            "logo_visible": True,
            # Env banner — dev'da yashil, prod'da qizil
            "env_name": "Development",
            "env_color": "#2D5016",
            "env_visible_in_header": True,
            "env_visible_in_favicon": True,
            # Header colors (bordoviy)
            "css_header_background_color": "#9B1C2D",
            "css_header_text_color": "#F5F0E8",
            "css_header_link_color": "#FCE7EB",
            "css_header_link_hover_color": "#FFFFFF",
            # Module / app headers (to'q yashil accent)
            "css_module_background_color": "#1B4332",
            "css_module_background_selected_color": "#2D5016",
            "css_module_text_color": "#FFFFFF",
            "css_module_link_color": "#F5F0E8",
            "css_module_link_selected_color": "#FFFFFF",
            "css_module_link_hover_color": "#FCE7EB",
            "css_module_rounded_corners": True,
            # Buttons (bordoviy)
            "css_save_button_background_color": "#9B1C2D",
            "css_save_button_background_hover_color": "#7A142A",
            "css_save_button_text_color": "#FFFFFF",
            "css_delete_button_background_color": "#DC2626",
            "css_delete_button_background_hover_color": "#B91C1C",
            "css_delete_button_text_color": "#FFFFFF",
            # Generic links (khaki)
            "css_generic_link_color": "#6B5D3F",
            "css_generic_link_hover_color": "#9B1C2D",
            # Behaviour
            "list_filter_dropdown": True,
            "list_filter_highlight": True,
            "list_filter_sticky": True,
            "form_pagination_sticky": True,
            "form_submit_sticky": True,
            "form_actions_sticky": True,
            "recent_actions_visible": True,
            "related_modal_active": True,
            "show_fieldsets_as_tabs": False,
            "collapsible_stacked_inlines_collapsed": False,
            "language_chooser_active": True,
            "language_chooser_display": "code",
        }

        theme, created = Theme.objects.update_or_create(
            name=self.THEME_NAME, defaults=defaults
        )
        Theme.objects.exclude(pk=theme.pk).update(active=False)
        theme.active = True
        theme.save(update_fields=["active"])

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} brand theme '{self.THEME_NAME}' (active=True)."
            )
        )
