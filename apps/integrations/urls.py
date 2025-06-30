from django.urls import path
from . import views

app_name = 'integrations'

urlpatterns = [
    # Integrations profile
    path('', views.integrations_profile, name='profile'),
    
    # ORCID OAuth2 flow
    path('orcid/connect/', views.orcid_connect, name='orcid_connect'),
    path('orcid/callback/', views.orcid_callback, name='orcid_callback'),
    path('orcid/disconnect/', views.orcid_disconnect, name='orcid_disconnect'),
    path('orcid/sync/', views.sync_orcid_profile, name='orcid_sync'),
    
    # API endpoints
    path('api/connections/', views.api_connection_status, name='api_connections'),
]