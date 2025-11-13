from django.apps import AppConfig


class AccountsAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts_app"
    verbose_name = "User Accounts"

    def ready(self):
        """Import signals when app is ready"""
        import apps.accounts_app.signals  # noqa
