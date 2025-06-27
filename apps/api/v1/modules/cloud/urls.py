from django.urls import path, include

urlpatterns = [
    # Include the cloud API endpoints
    path('', include('apps.api.cloud_urls')),
]