"""
SciTeX Cloud - Directory Management URLs

URL patterns for project directory management and file operations.
"""

from django.urls import path
from .views import directory_views

app_name = 'directory'

urlpatterns = [
    # Project directory structure
    path('projects/<int:project_id>/structure/', 
         directory_views.project_structure, 
         name='project_structure'),
    
    # File management
    path('projects/<int:project_id>/files/', 
         directory_views.project_files, 
         name='project_files'),
    
    path('projects/<int:project_id>/upload/', 
         directory_views.upload_file, 
         name='upload_file'),
    
    path('projects/<int:project_id>/download/', 
         directory_views.download_file, 
         name='download_file'),
    
    path('projects/<int:project_id>/delete-file/', 
         directory_views.delete_file, 
         name='delete_file'),
    
    # Directory management
    path('projects/<int:project_id>/create-directory/', 
         directory_views.create_directory, 
         name='create_directory'),
    
    path('projects/<int:project_id>/initialize/', 
         directory_views.initialize_project_directory, 
         name='initialize_project_directory'),
    
    # README management
    path('projects/<int:project_id>/readme/', 
         directory_views.project_readme, 
         name='project_readme'),
    
    path('projects/<int:project_id>/readme/update/', 
         directory_views.update_project_readme, 
         name='update_project_readme'),
    
    # User storage
    path('storage/', 
         directory_views.user_storage_usage, 
         name='user_storage_usage'),
    
    # GitHub integration
    path('projects/<int:project_id>/github/sync/', 
         directory_views.sync_with_github, 
         name='sync_with_github'),
    
    # Script execution
    path('projects/<int:project_id>/scripts/executions/', 
         directory_views.get_script_executions, 
         name='get_script_executions'),
    
    path('projects/<int:project_id>/scripts/execute/', 
         directory_views.execute_script, 
         name='execute_script'),
]