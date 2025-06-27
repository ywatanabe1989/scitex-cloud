from django.apps import AppConfig


class CoreAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core_app'
    verbose_name = 'SciTeX Core Application'

    def ready(self):
        # Import signals to ensure they are connected
        import apps.core_app.signals