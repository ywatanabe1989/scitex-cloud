"""
Writer App Views - Feature-based Organization

This module exports views organized by feature domains:
- Editor: Main manuscript editing interface
- Compilation: PDF compilation and status
- Version Control: Git integration and history
- arXiv: Submission to arXiv.org
- Collaboration: Real-time collaborative editing
- Dashboard: User dashboard and manuscript list
"""

# Editor views
from .editor import (
    editor_view,
    save_section_api,
    load_section_api,
    compile_api,
    compilation_status_api,
)

# Compilation views
from .compilation import (
    compilation_view,
    compilation_api,
    status_api,
)

# Version control views
from .version_control import (
    version_control_dashboard,
    history_api,
    create_version_api,
    rollback_api,
)

# arXiv views
from .arxiv import (
    submission_form,
    submission_list,
    submission_detail,
    submit_api,
    status_check_api,
    validate_api,
)

# Collaboration views
from .collaboration import (
    collaboration_session,
    session_list,
    join_api,
    leave_api,
    lock_section_api,
    unlock_section_api,
)

# Dashboard views
from .dashboard import (
    dashboard_view,
    manuscript_list,
)

# Keep legacy views for backward compatibility (from old views files)
# These will be gradually migrated to the new structure
from .main_views import (
    index,
    initialize_workspace,
    user_default_workspace,
    project_writer,
)

__all__ = [
    # Editor
    'editor_view',
    'save_section_api',
    'load_section_api',
    'compile_api',
    'compilation_status_api',

    # Compilation
    'compilation_view',
    'compilation_api',
    'status_api',

    # Version Control
    'version_control_dashboard',
    'history_api',
    'create_version_api',
    'rollback_api',

    # arXiv
    'submission_form',
    'submission_list',
    'submission_detail',
    'submit_api',
    'status_check_api',
    'validate_api',

    # Collaboration
    'collaboration_session',
    'session_list',
    'join_api',
    'leave_api',
    'lock_section_api',
    'unlock_section_api',

    # Dashboard
    'dashboard_view',
    'manuscript_list',

    # Legacy (backward compatibility)
    'index',
    'initialize_workspace',
    'user_default_workspace',
    'project_writer',
]
