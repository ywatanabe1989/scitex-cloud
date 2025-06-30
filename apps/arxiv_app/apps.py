from django.apps import AppConfig


class ArxivAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.arxiv_app'
    verbose_name = 'arXiv Integration'
    
    def ready(self):
        """Import signals when app is ready."""
        import apps.arxiv_app.signals