from django.apps import AppConfig


class MonitoringAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.monitoring_app'
    verbose_name = 'System Monitoring'