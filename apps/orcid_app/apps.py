from django.apps import AppConfig


class OrcidAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orcid_app'
    verbose_name = 'ORCID Integration'
    
    def ready(self):
        import apps.orcid_app.signals