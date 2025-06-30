from django.apps import AppConfig


class BillingAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.billing_app'
    verbose_name = 'SciTeX Billing & Monetization'
    
    def ready(self):
        # Import signals after migrations
        try:
            import apps.billing_app.signals
        except ImportError:
            # Skip during initial migrations
            pass