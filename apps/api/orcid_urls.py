from django.urls import path
from . import orcid_views

app_name = 'api_orcid'

urlpatterns = [
    # Authentication endpoints
    path('auth/status/', orcid_views.auth_status, name='auth_status'),
    path('auth/connect/', orcid_views.connect, name='connect'),
    path('auth/disconnect/', orcid_views.disconnect, name='disconnect'),
    
    # Profile endpoints
    path('profile/', orcid_views.profile_detail, name='profile_detail'),
    path('profile/sync/', orcid_views.sync_profile, name='sync_profile'),
    
    # Publications endpoints
    path('publications/', orcid_views.publications_list, name='publications_list'),
    path('publications/sync/', orcid_views.sync_publications, name='sync_publications'),
    path('publications/<uuid:publication_id>/', orcid_views.publication_detail, name='publication_detail'),
    path('publications/<uuid:publication_id>/import/', orcid_views.import_publication, name='import_publication'),
    path('publications/bulk-import/', orcid_views.bulk_import_publications, name='bulk_import_publications'),
    
    # Works endpoints
    path('works/', orcid_views.works_list, name='works_list'),
    path('works/<uuid:work_id>/', orcid_views.work_detail, name='work_detail'),
    
    # Sync logs
    path('logs/', orcid_views.sync_logs, name='sync_logs'),
    path('logs/<uuid:log_id>/', orcid_views.sync_log_detail, name='sync_log_detail'),
    
    # Full sync
    path('sync/full/', orcid_views.full_sync, name='full_sync'),
]