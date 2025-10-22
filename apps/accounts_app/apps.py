from django.apps import AppConfig


class ProfileAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.profile_app'
    verbose_name = 'User Profiles'

    def ready(self):
        """Import signals when app is ready"""
        import apps.profile_app.signals  # noqa
