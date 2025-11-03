"""
Writer App Views - Minimal Interface

Main views delegating to REST API:
- index: Home page
- initialize_workspace: Initialize Writer project
- Workspace views for user defaults
- API stubs for backward compatibility
"""

# API views
from .api_views import (
    presence_update_view,
    presence_list_view,
)

# Main views
from .main_views import (
    index,
    initialize_workspace,
    user_default_workspace,
    project_writer,
    
    # API stubs (return JSON with deprecation notice)
    save_section,
    load_latex_section,
    save_latex_section,
    list_tex_files,
    compile_modular_manuscript,
    cloud_compile_sections,
    quick_compile,
    compilation_status,
    download_compiled_pdf,
    download_paper_zip,
    
    # Editor stubs
    collaborative_editor,
    features,
    pricing,
    modular_editor,
    simple_editor,
    latex_editor_view,
    writer_dashboard_view,
    manuscript_list,
    
    # Collaboration stubs
    collaborative_sessions,
    join_collaboration,
    leave_collaboration,
    lock_section,
    unlock_section,
    
    # Version control stubs
    version_history,
    create_version,
    view_diff,
    rollback_version,
    branch_list,
    create_branch,
    create_merge_request,
    version_control_dashboard,
    
    # arXiv stubs
    ArxivDashboardView,
    SubmissionListView,
    arxiv_account_setup,
    manuscript_submission_form,
    submission_detail,
    validate_submission,
    prepare_submission_files,
    submit_to_arxiv,
    check_submission_status,
    withdraw_submission,
    create_replacement,
    submission_history_api,
    categories_api,
    suggest_categories_api,
    arxiv_status_check,
    initialize_categories,
    
    # Old stubs
    mock_save,
    get_manuscript_stats,
    toggle_editing_mode,
)

__all__ = [
    # Main
    'index',
    'initialize_workspace',
    'user_default_workspace',
    'project_writer',

    # Presence
    'presence_update_view',
    'presence_list_view',

    # API stubs
    'save_section',
    'load_latex_section',
    'save_latex_section',
    'list_tex_files',
    'compile_modular_manuscript',
    'cloud_compile_sections',
    'quick_compile',
    'compilation_status',
    'download_compiled_pdf',
    'download_paper_zip',
    'get_manuscript_stats',
    'toggle_editing_mode',
    
    # Editors
    'collaborative_editor',
    'features',
    'pricing',
    'modular_editor',
    'simple_editor',
    'latex_editor_view',
    'writer_dashboard_view',
    'manuscript_list',
    'mock_save',
    
    # Collaboration
    'collaborative_sessions',
    'join_collaboration',
    'leave_collaboration',
    'lock_section',
    'unlock_section',
    
    # Version control
    'version_history',
    'create_version',
    'view_diff',
    'rollback_version',
    'branch_list',
    'create_branch',
    'create_merge_request',
    'version_control_dashboard',
    
    # arXiv
    'ArxivDashboardView',
    'SubmissionListView',
    'arxiv_account_setup',
    'manuscript_submission_form',
    'submission_detail',
    'validate_submission',
    'prepare_submission_files',
    'submit_to_arxiv',
    'check_submission_status',
    'withdraw_submission',
    'create_replacement',
    'submission_history_api',
    'categories_api',
    'suggest_categories_api',
    'arxiv_status_check',
    'initialize_categories',
]
