from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .viewsets import DocumentViewSet, ProjectViewSet, UserProfileViewSet

router = DefaultRouter()
router.register(r'modules', views.ModuleViewSet, basename='module')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'profile', UserProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('apps.api.v1.auth.urls')),
    path('engine/', include('apps.api.v1.modules.engine.urls')),
    path('writer/', include('apps.api.v1.modules.writer.urls')),
    path('code/', include('apps.api.v1.modules.code.urls')),
    path('viz/', include('apps.api.v1.modules.viz.urls')),
    path('scholar/', include('apps.api.v1.modules.scholar.urls')),
    path('cloud/', include('apps.api.v1.modules.cloud.urls')),
    
    # Legacy naming scheme redirects
    path('doc/', include('apps.api.v1.modules.writer.urls')),
    path('search/', include('apps.api.v1.modules.scholar.urls')),
    # Previous naming attempts redirects
    path('studio/', include('apps.api.v1.modules.engine.urls')),
    path('analyzer/', include('apps.api.v1.modules.code.urls')),
    path('explorer/', include('apps.api.v1.modules.scholar.urls')),
    path('coder/', include('apps.api.v1.modules.code.urls')),
]