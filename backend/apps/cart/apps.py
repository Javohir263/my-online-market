from django.apps import AppConfig


class CartConfig(AppConfig):
    name = "apps.cart"
    label = "cart"
    verbose_name = "Cart"

    def ready(self) -> None:
        # noqa: F401 — signal handlers import side effect
        from apps.cart import signals  # noqa: F401
