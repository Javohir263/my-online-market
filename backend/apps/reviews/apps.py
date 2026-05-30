from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    name = "apps.reviews"
    label = "reviews"
    verbose_name = "Reviews"

    def ready(self) -> None:
        # Signal handlers — Product rating denorm
        from apps.reviews import signals  # noqa: F401
