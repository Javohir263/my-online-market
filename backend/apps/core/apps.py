from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "apps.core"
    label = "core"
    verbose_name = "Core"

    def ready(self) -> None:
        # Install custom admin dashboard hook
        from apps.core.dashboard import install_dashboard

        install_dashboard()
