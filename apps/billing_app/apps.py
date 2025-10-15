from django.apps import AppConfig


class BillingAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.billing_app'
    verbose_name = 'Billing and Subscriptions'
