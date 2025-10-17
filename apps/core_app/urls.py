from django.urls import path, include
from . import views
from . import api_views
from . import github_views

app_name = 'core_app'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.index, name='index'),
    path('dashboard/file-manager/', views.dashboard_react_tree, name='dashboard_react_tree'),
    path('documents/', views.document_list, name='document_list'),
    path('projects/', views.project_list, name='project_list'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/profile/', views.profile_edit, name='profile_edit'),
    path('settings/appearance/', views.appearance_settings, name='appearance'),
    path('monitoring/', views.monitoring, name='monitoring'),
    path('monitoring/data/', views.monitoring_data, name='monitoring_data'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms_of_use, name='terms'),
    path('cookies/', views.cookie_policy, name='cookies'),
]

# API URLs
api_urlpatterns = [
    # Document management
    path("api/v1/documents/", api_views.document_api, name="api-documents"),
    path("api/v1/documents/<int:document_id>/", api_views.document_api, name="api-document-detail"),
    
    # Project management
    path("api/v1/projects/", api_views.project_api, name="api-projects"),
    path("api/v1/projects/<int:project_id>/", api_views.project_api, name="api-project-detail"),
    
    # User statistics and profile
    path("api/v1/stats/", api_views.user_stats_api, name="api-user-stats"),
    path("api/v1/profile/", api_views.user_profile_api, name="api-user-profile"),
    
    # Example project creation
    path("api/v1/projects/examples/", views.create_example_project, name="api-create-example-project"),
    path("api/v1/projects/<int:project_id>/copy/", views.copy_project, name="api-copy-project"),
    
    # GitHub Integration APIs
    path("api/v1/github/oauth/initiate/", github_views.github_oauth_initiate, name="api-github-oauth-initiate"),
    path("api/v1/github/oauth/callback/", github_views.github_oauth_callback, name="api-github-oauth-callback"),
    path("api/v1/github/create-repo/", github_views.github_create_repository, name="api-github-create-repo"),
    path("api/v1/github/link-repo/", github_views.github_link_repository, name="api-github-link-repo"),
    path("api/v1/github/projects/<int:project_id>/status/", github_views.github_get_status, name="api-github-status"),
    path("api/v1/github/projects/<int:project_id>/sync/", github_views.github_sync_status, name="api-github-sync"),
    path("api/v1/github/projects/<int:project_id>/commit/", github_views.github_commit_files, name="api-github-commit"),
    path("api/v1/github/projects/<int:project_id>/push/", github_views.github_push_changes, name="api-github-push"),
    path("api/v1/github/repositories/", github_views.github_list_repositories, name="api-github-repos"),
    
    # File System APIs for React Complex Tree Dashboard
    path("api/v1/filesystem/tree/", api_views.file_tree_api_wrapper, name="api-file-tree"),
    path("api/v1/filesystem/content/<str:file_id>/", api_views.file_content_api_wrapper, name="api-file-content"),
    
    # Debug endpoint
    path("api/v1/debug/projects/", api_views.debug_user_projects, name="api-debug-projects"),
]

# Directory management URLs
directory_urlpatterns = [
    path('directory/', include('apps.core_app.directory_urls')),
]

# Combine regular, API, and directory URLs
urlpatterns += api_urlpatterns + directory_urlpatterns