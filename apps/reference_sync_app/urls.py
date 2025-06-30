"""
URL configuration for reference manager synchronization app.
"""

from django.urls import path, include
from . import views

app_name = 'reference_sync'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Account management
    path('accounts/', views.AccountListView.as_view(), name='accounts'),
    path('accounts/<uuid:pk>/', views.AccountDetailView.as_view(), name='account_detail'),
    path('accounts/connect/<str:service>/', views.ConnectAccountView.as_view(), name='connect_account'),
    path('accounts/disconnect/<uuid:pk>/', views.DisconnectAccountView.as_view(), name='disconnect_account'),
    
    # OAuth callbacks
    path('oauth/<str:service>/callback/', views.oauth_callback, name='oauth_callback'),
    
    # Sync profiles
    path('profiles/', views.SyncProfileListView.as_view(), name='profiles'),
    path('profiles/create/', views.SyncProfileCreateView.as_view(), name='profile_create'),
    path('profiles/<uuid:pk>/', views.SyncProfileDetailView.as_view(), name='profile_detail'),
    path('profiles/<uuid:pk>/edit/', views.SyncProfileUpdateView.as_view(), name='profile_update'),
    path('profiles/<uuid:pk>/delete/', views.SyncProfileDeleteView.as_view(), name='profile_delete'),
    path('profiles/<uuid:pk>/sync/', views.StartSyncView.as_view(), name='start_sync'),
    
    # Sync sessions
    path('sessions/', views.SyncSessionListView.as_view(), name='sessions'),
    path('sessions/<uuid:pk>/', views.SyncSessionDetailView.as_view(), name='session_detail'),
    
    # Conflict resolution
    path('conflicts/', views.ConflictResolutionListView.as_view(), name='conflicts'),
    path('conflicts/<uuid:pk>/', views.ConflictResolutionDetailView.as_view(), name='conflict_detail'),
    
    # Bulk operations
    path('bulk/import/', views.BulkImportView.as_view(), name='bulk_import'),
    path('bulk/export/', views.BulkExportView.as_view(), name='bulk_export'),
    
    # API endpoints
    path('api/sync-status/<uuid:pk>/', views.SyncStatusAPIView.as_view(), name='api_sync_status'),
    path('api/webhooks/<str:service>/', views.WebhookEndpointView.as_view(), name='webhook'),
]