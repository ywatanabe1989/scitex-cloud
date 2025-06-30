from django.apps import AppConfig


class MendeleyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.mendeley_app'
    verbose_name = 'Mendeley Integration'
    
    def ready(self):
        """
        Import signals when the app is ready.
        """
        try:
            from . import signals
        except ImportError:
            pass