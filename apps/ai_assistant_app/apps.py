from django.apps import AppConfig


class AiAssistantAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_assistant_app'
    verbose_name = 'AI Research Assistant'
    
    def ready(self):
        """Initialize app signals and configurations."""
        pass