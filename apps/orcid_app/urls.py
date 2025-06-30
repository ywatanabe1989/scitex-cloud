from django.urls import path
from . import views

app_name = 'orcid_app'

urlpatterns = [
    # Main dashboard
    path('', views.orcid_dashboard, name='dashboard'),
    
    # Authentication
    path('connect/', views.orcid_connect, name='connect'),
    path('callback/', views.orcid_callback, name='callback'),
    path('disconnect/', views.orcid_disconnect, name='disconnect'),
    
    # Profile and sync
    path('sync/profile/', views.sync_profile, name='sync_profile'),
    path('sync/publications/', views.sync_publications, name='sync_publications'),
    path('sync/full/', views.full_sync, name='full_sync'),
    path('settings/', views.profile_settings, name='profile_settings'),
    
    # Publications
    path('publications/', views.publications_list, name='publications'),
    path('publications/<uuid:publication_id>/', views.publication_detail, name='publication_detail'),
    path('publications/<uuid:publication_id>/import/', views.import_to_scholar, name='import_to_scholar'),
    path('publications/bulk-import/', views.bulk_import_to_scholar, name='bulk_import_to_scholar'),
    
    # Logs
    path('logs/', views.sync_logs, name='sync_logs'),
    
    # API endpoints
    path('api/status/', views.api_profile_status, name='api_profile_status'),
    path('api/sync/profile/', views.api_sync_profile, name='api_sync_profile'),
    path('api/sync/publications/', views.api_sync_publications, name='api_sync_publications'),
    path('api/publications/', views.api_publications_list, name='api_publications_list'),
    path('api/logs/', views.api_sync_logs, name='api_sync_logs'),
]