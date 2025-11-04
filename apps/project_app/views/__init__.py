"""
Project App Views
Central export point for all project-related views

Organized by feature following Django best practices:
- project_views: CRUD operations, user profiles
- directory_views: File browser, directory listing
- api_views: REST API endpoints
- integration_views: GitHub/Gitea integration
- collaboration_views: Invitations, members
- settings_views: Project settings
"""

# Project CRUD and user profile views
from .project_views import (
    project_list,
    user_profile,
    user_project_list,
    user_bio_page,
    project_detail,
    project_create,
    project_create_from_template,
    project_edit,
    project_delete,
    project_detail_redirect,
    user_overview,
    user_projects_board,
    user_stars,
)

# Directory and file browser views
from .directory_views import (
    project_directory_dynamic,
    project_file_view,
    project_directory,
    file_history_view,
    commit_detail,
)

# REST API views
from .api_views import (
    api_file_tree,
    api_check_name_availability,
    api_project_list,
    api_project_create,
    api_concatenate_directory,
    api_project_detail,
    api_repository_health,
    api_repository_cleanup,
    api_repository_sync,
    api_repository_restore,
)

# GitHub/Gitea integration views
from .integration_views import (
    github_integration,
    repository_maintenance,
)

# Collaboration views
from .collaboration_views import (
    project_collaborate,
    project_members,
    accept_invitation,
    decline_invitation,
)

# Settings views
from .settings_views import (
    project_settings,
)

# Import actions views
# TODO: Uncomment when workflow models are available
# from .actions_views import (
#     actions_list,
#     workflow_detail,
#     workflow_run_detail,
#     workflow_create,
#     workflow_trigger,
#     workflow_edit,
#     workflow_delete,
#     workflow_enable_disable,
# )

__all__ = [
    # Project views (CRUD, user profiles)
    'project_list',
    'user_profile',
    'user_project_list',
    'user_bio_page',
    'project_detail',
    'project_create',
    'project_create_from_template',
    'project_edit',
    'project_delete',
    'project_detail_redirect',
    'user_overview',
    'user_projects_board',
    'user_stars',
    # Directory views (file browser)
    'project_directory_dynamic',
    'project_file_view',
    'project_directory',
    'file_history_view',
    'commit_detail',
    # API views (REST endpoints)
    'api_file_tree',
    'api_check_name_availability',
    'api_project_list',
    'api_project_create',
    'api_concatenate_directory',
    'api_project_detail',
    'api_repository_health',
    'api_repository_cleanup',
    'api_repository_sync',
    'api_repository_restore',
    # Integration views (GitHub/Gitea)
    'github_integration',
    'repository_maintenance',
    # Collaboration views
    'project_collaborate',
    'project_members',
    'accept_invitation',
    'decline_invitation',
    # Settings views
    'project_settings',
    # CI/CD Actions views - commented out until models are available
    # 'actions_list',
    # 'workflow_detail',
    # 'workflow_run_detail',
    # 'workflow_create',
    # 'workflow_trigger',
    # 'workflow_edit',
    # 'workflow_delete',
    # 'workflow_enable_disable',
]

# EOF
