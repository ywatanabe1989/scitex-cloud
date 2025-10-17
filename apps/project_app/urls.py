from django.urls import path
from . import views

app_name = 'project_app'

urlpatterns = [
    # Legacy routes for backward compatibility - redirect to user_projects namespace
    # These are accessed via /project/ prefix (configured in config/urls.py)
    path('', views.project_list, name='list'),

    # API endpoints (keep numeric IDs for API)
    path('api/list/', views.api_project_list, name='api_list'),
    path('api/create/', views.api_project_create, name='api_create'),
    path('api/<int:pk>/', views.api_project_detail, name='api_detail'),

    # Backward compatibility redirects
    path('project/<slug:slug>/', views.project_detail_redirect, name='slug_redirect'),
    path('id/<int:pk>/', views.project_detail_redirect, name='detail_redirect'),
]