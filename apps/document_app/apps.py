from django.apps import AppConfig


class DocumentAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.document_app'
    verbose_name = 'Document Management'
    
    def ready(self):
        """Initialize the app when Django starts."""
        pass