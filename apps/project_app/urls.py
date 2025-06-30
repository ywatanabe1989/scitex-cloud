from django.urls import path
from . import views

app_name = 'project_app'

urlpatterns = [
    # User's project list (when accessed via projects/ without username)
    path('', views.project_list, name='list'),
    path('create/', views.project_create, name='create'),
    
    # GitHub-style username/project URLs
    path('<str:username>/', views.user_project_list, name='user_projects'),
    path('<str:username>/<slug:slug>/', views.project_detail, name='detail'),
    path('<str:username>/<slug:slug>/edit/', views.project_edit, name='edit'),
    path('<str:username>/<slug:slug>/delete/', views.project_delete, name='delete'),
    
    # File manager URLs
    path('<str:username>/<slug:slug>/files/', views.project_files, name='files'),
    path('<str:username>/<slug:slug>/files/upload/', views.file_upload, name='file_upload'),
    path('<str:username>/<slug:slug>/files/download/', views.file_download, name='file_download'),
    
    # Collaboration URLs
    path('<str:username>/<slug:slug>/collaborate/', views.project_collaborate, name='collaborate'),
    path('<str:username>/<slug:slug>/members/', views.project_members, name='members'),
    
    # Integration URLs
    path('<str:username>/<slug:slug>/github/', views.github_integration, name='github'),
    path('<str:username>/<slug:slug>/sync/', views.project_sync, name='sync'),
    
    # Module integration URLs
    path('<str:username>/<slug:slug>/scholar/', views.project_scholar, name='scholar'),
    path('<str:username>/<slug:slug>/writer/', views.project_writer, name='writer'),
    path('<str:username>/<slug:slug>/code/', views.project_code, name='code'),
    path('<str:username>/<slug:slug>/viz/', views.project_viz, name='viz'),
    
    # Backward compatibility for old slug URLs (redirect to username/slug)
    path('project/<slug:slug>/', views.project_detail_redirect, name='slug_redirect'),
    path('id/<int:pk>/', views.project_detail_redirect, name='detail_redirect'),
    
    # API endpoints (keep numeric IDs for API)
    path('api/list/', views.api_project_list, name='api_list'),
    path('api/create/', views.api_project_create, name='api_create'),
    path('api/<int:pk>/', views.api_project_detail, name='api_detail'),
]