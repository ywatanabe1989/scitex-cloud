from django.urls import path
from . import views

app_name = 'user_projects'

urlpatterns = [
    # GitHub-style username/project URLs - these don't need username in the pattern
    # since the username is already captured by the parent URL pattern
    path('', views.user_project_list, name='user_projects'),
    path('<slug:slug>/', views.project_detail, name='detail'),
    path('<slug:slug>/edit/', views.project_edit, name='edit'),
    path('<slug:slug>/delete/', views.project_delete, name='delete'),
    
    # File manager URLs
    path('<slug:slug>/files/', views.project_files, name='files'),
    path('<slug:slug>/files/upload/', views.file_upload, name='file_upload'),
    path('<slug:slug>/files/download/', views.file_download, name='file_download'),
    
    # Collaboration URLs
    path('<slug:slug>/collaborate/', views.project_collaborate, name='collaborate'),
    path('<slug:slug>/members/', views.project_members, name='members'),
    
    # Integration URLs
    path('<slug:slug>/github/', views.github_integration, name='github'),
    path('<slug:slug>/sync/', views.project_sync, name='sync'),
    
    # Module integration URLs
    path('<slug:slug>/scholar/', views.project_scholar, name='scholar'),
    path('<slug:slug>/writer/', views.project_writer, name='writer'),
    path('<slug:slug>/code/', views.project_code, name='code'),
    path('<slug:slug>/viz/', views.project_viz, name='viz'),
    
    # Scientific workflow directory URLs
    path('<slug:slug>/scripts/', views.project_directory, {'directory': 'scripts'}, name='scripts'),
    path('<slug:slug>/scripts/<path:subpath>/', views.project_directory, {'directory': 'scripts'}, name='scripts_subpath'),
    path('<slug:slug>/data/', views.project_directory, {'directory': 'data'}, name='data'),
    path('<slug:slug>/data/<path:subpath>/', views.project_directory, {'directory': 'data'}, name='data_subpath'),
    path('<slug:slug>/docs/', views.project_directory, {'directory': 'docs'}, name='docs'),
    path('<slug:slug>/docs/<path:subpath>/', views.project_directory, {'directory': 'docs'}, name='docs_subpath'),
    path('<slug:slug>/results/', views.project_directory, {'directory': 'results'}, name='results'),
    path('<slug:slug>/results/<path:subpath>/', views.project_directory, {'directory': 'results'}, name='results_subpath'),
    path('<slug:slug>/config/', views.project_directory, {'directory': 'config'}, name='config'),
    path('<slug:slug>/config/<path:subpath>/', views.project_directory, {'directory': 'config'}, name='config_subpath'),
    path('<slug:slug>/temp/', views.project_directory, {'directory': 'temp'}, name='temp'),
    path('<slug:slug>/temp/<path:subpath>/', views.project_directory, {'directory': 'temp'}, name='temp_subpath'),
]