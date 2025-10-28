"""
Writer App Views

Organized by feature for maintainability.
All views are imported here for backward compatibility with urls.py
"""

# Main views (project-based, manuscript management, compilation)
from .main_views import (
    # Main pages
    features,
    pricing,
    dashboard,
    templates,

    # Manuscript management
    manuscript_list,
    manuscript_create,
    manuscript_edit,

    # Project-based writer
    project_writer,
    project_writer_compilation,
    save_section,
    load_latex_section,
    save_latex_section,
    list_tex_files,
    get_manuscript_stats,
    toggle_editing_mode,

    # Compilation
    compile_modular_manuscript,
    cloud_compile_sections,
    quick_compile,
    compilation_status,
    manuscript_compile,
    download_compiled_pdf,
    download_paper_zip,
    test_compilation,

    # LaTeX Editor
    latex_editor_view,
    writer_dashboard_view,

    # Export
    export_manuscript,
    ai_assist,

    # Collaboration
    collaborative_sessions,
    join_collaboration,
    leave_collaboration,
    lock_section,
    unlock_section,
    collaborative_editor,
    add_collaborator,
    remove_collaborator,

    # Version Control
    version_history,
    create_version,
    view_diff,
    branch_list,
    create_branch,
    rollback_version,
    create_merge_request,
    version_control_dashboard,

    # AI Features
    ai_improve_text,
    ai_generate_section,
    ai_suggest_citations,
)

# Editor views (simple/modular editors, workspace initialization)
from .editor_views import (
    index,  # Project-based editor with workspace initialization
    get_or_create_guest_user,
    ensure_writer_directory,
    simple_editor,
    modular_editor,
    mock_compile,
    mock_save,
    initialize_workspace,
)

# Use centralized project getter from project_app
from apps.project_app.services import get_or_create_default_project

# Workspace views (default workspace for users)
from .workspace_views import (
    guest_session_view,
    user_default_workspace,
)

# arXiv views (arXiv submission and integration)
from .arxiv_views import (
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
    categories_api,
    suggest_categories_api,
    submission_history_api,
    arxiv_status_check,
    initialize_categories,
)

__all__ = [
    # Main views
    'index',
    'features',
    'pricing',
    'dashboard',
    'templates',
    'manuscript_list',
    'manuscript_create',
    'manuscript_edit',
    'project_writer',
    'project_writer_compilation',
    'save_section',
    'load_latex_section',
    'save_latex_section',
    'list_tex_files',
    'get_manuscript_stats',
    'toggle_editing_mode',
    'compile_modular_manuscript',
    'cloud_compile_sections',
    'quick_compile',
    'compilation_status',
    'manuscript_compile',
    'download_compiled_pdf',
    'download_paper_zip',
    'test_compilation',
    'latex_editor_view',
    'writer_dashboard_view',
    'export_manuscript',
    'ai_assist',
    'collaborative_sessions',
    'join_collaboration',
    'leave_collaboration',
    'lock_section',
    'unlock_section',
    'collaborative_editor',
    'add_collaborator',
    'remove_collaborator',
    'version_history',
    'create_version',
    'view_diff',
    'branch_list',
    'create_branch',
    'rollback_version',
    'create_merge_request',
    'version_control_dashboard',
    'ai_improve_text',
    'ai_generate_section',
    'ai_suggest_citations',

    # Editor views
    'get_or_create_guest_user',
    'get_or_create_default_project',
    'ensure_writer_directory',
    'simple_editor',
    'modular_editor',
    'mock_compile',
    'mock_save',
    'initialize_workspace',

    # Workspace views
    'guest_session_view',
    'user_default_workspace',

    # arXiv views
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
    'categories_api',
    'suggest_categories_api',
    'submission_history_api',
    'arxiv_status_check',
    'initialize_categories',
]
