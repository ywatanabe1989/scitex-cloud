from django.apps import AppConfig


class ReferenceSyncAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reference_sync_app'
    verbose_name = 'Reference Manager Sync'
    
    def ready(self):
        """Import signal handlers when app is ready."""
        try:
            import apps.reference_sync_app.signals
        except ImportError:
            pass