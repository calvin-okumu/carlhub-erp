from django.apps import AppConfig


class SalesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sales"

    def ready(self):
        # Import signals here to ensure they're registered
        pass
