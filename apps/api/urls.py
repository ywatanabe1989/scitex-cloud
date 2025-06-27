from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('v1/', include('apps.api.v1.urls')),
    
    # Direct module endpoints (for backwards compatibility)
    path('engine/', include('apps.api.engine_urls')),
    path('doc/', include('apps.api.doc_urls')),
    path('code/', include('apps.api.code_urls')),
    path('viz/', include('apps.api.viz_urls')),
    path('search/', include('apps.api.search_urls')),
    path('cloud/', include('apps.api.cloud_urls')),
]