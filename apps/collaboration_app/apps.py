from django.apps import AppConfig


class CollaborationAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.collaboration_app'
    verbose_name = 'Collaboration Management'
    
    def ready(self):
        """Initialize app signals and configurations"""
        import apps.collaboration_app.signals
