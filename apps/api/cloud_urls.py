from django.urls import path
from apps.api import cloud_views

urlpatterns = [
    # SciTeX-Cloud API endpoints
    path('subscription/status/', cloud_views.subscription_status, name='cloud-subscription-status'),
    path('usage/', cloud_views.resource_usage, name='cloud-resource-usage'),
    path('usage/track/', cloud_views.track_usage, name='cloud-track-usage'),
    path('api-keys/', cloud_views.manage_api_keys, name='cloud-api-keys'),
    path('api-keys/<int:key_id>/', cloud_views.delete_api_key, name='cloud-delete-api-key'),
    path('integrations/', cloud_views.manage_integrations, name='cloud-integrations'),
    path('integrations/<int:integration_id>/', cloud_views.delete_integration, name='cloud-delete-integration'),
    path('plans/', cloud_views.available_plans, name='cloud-available-plans'),
]