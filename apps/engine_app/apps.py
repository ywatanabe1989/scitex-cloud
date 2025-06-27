from django.apps import AppConfig


class EngineAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.engine_app'
    verbose_name = 'Engine'