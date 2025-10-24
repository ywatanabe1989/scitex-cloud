"""
Project App Views
Central export point for all project-related views
"""

# Import from base_views.py (renamed from views.py to avoid conflict with views/ directory)
from ..base_views import (
    project_create,
    project_list,
    user_profile,
    user_project_list,
    user_bio_page,
    project_detail,
    project_create_from_template,
    project_edit,
    project_settings,
    project_delete,
    project_collaborate,
    project_members,
    github_integration,
    api_file_tree,
    api_check_name_availability,
    api_project_list,
    api_project_create,
    api_concatenate_directory,
    api_project_detail,
    project_detail_redirect,
    project_directory_dynamic,
    project_file_view,
    project_directory,
    user_overview,
    user_projects_board,
    user_stars,
    file_history_view,
    commit_detail,
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
    'project_create',
    'project_list',
    'user_profile',
    'user_project_list',
    'user_bio_page',
    'project_detail',
    'project_create_from_template',
    'project_edit',
    'project_settings',
    'project_delete',
    'project_collaborate',
    'project_members',
    'github_integration',
    'api_file_tree',
    'api_check_name_availability',
    'api_project_list',
    'api_project_create',
    'api_concatenate_directory',
    'api_project_detail',
    'project_detail_redirect',
    'project_directory_dynamic',
    'project_file_view',
    'project_directory',
    'user_overview',
    'user_projects_board',
    'user_stars',
    'file_history_view',
    'commit_detail',
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
