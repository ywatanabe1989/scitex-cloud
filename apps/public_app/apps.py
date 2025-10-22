from django.apps import AppConfig


class CloudAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cloud_app'
    verbose_name = 'Cloud'