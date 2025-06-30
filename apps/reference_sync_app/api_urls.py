"""
API URL configuration for reference manager synchronization.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import (
    ReferenceManagerAccountViewSet,
    SyncProfileViewSet,
    SyncSessionViewSet,
    ReferenceMappingViewSet,
    ConflictResolutionViewSet,
    SyncStatisticsViewSet,
    BulkImportAPIView,
    BulkExportAPIView,
    SyncStatusAPIView,
    WebhookAPIView,
    OAuthCallbackAPIView
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'accounts', ReferenceManagerAccountViewSet, basename='account')
router.register(r'profiles', SyncProfileViewSet, basename='profile')
router.register(r'sessions', SyncSessionViewSet, basename='session')
router.register(r'mappings', ReferenceMappingViewSet, basename='mapping')
router.register(r'conflicts', ConflictResolutionViewSet, basename='conflict')
router.register(r'statistics', SyncStatisticsViewSet, basename='statistics')

app_name = 'reference_sync_api'

urlpatterns = [
    # Router-generated URLs
    path('', include(router.urls)),
    
    # Custom API endpoints
    path('bulk/import/', BulkImportAPIView.as_view(), name='bulk_import'),
    path('bulk/export/', BulkExportAPIView.as_view(), name='bulk_export'),
    path('sync-status/<uuid:session_id>/', SyncStatusAPIView.as_view(), name='sync_status'),
    path('webhooks/<str:service>/', WebhookAPIView.as_view(), name='webhook'),
    path('oauth/<str:service>/callback/', OAuthCallbackAPIView.as_view(), name='oauth_callback'),
]