from django.apps import AppConfig


class RegulationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "regulations"

    def ready(self):
        from . import signals  # noqa: F401
