#!/usr/bin/env python3
"""
Views package for SciTeX-Code application.
Exports all views for backward compatibility.
"""

from .main_views import (
    index,
    features,
    pricing,
    editor,
    jobs,
    job_detail,
    execute_code,
    job_status,
    notebooks,
    notebook_detail,
    analysis,
    templates,
    run_analysis,
    get_job_progress,
    environments,
    create_environment,
    setup_environment,
    environment_detail,
    execute_in_environment,
    workflows,
    create_workflow,
    execute_workflow,
    workflow_detail,
    create_notebook,
    execute_notebook,
    visualizations,
    generate_visualization,
    process_data_visualization,
    create_research_report,
)

from .workspace_views import (
    guest_session_view,
    user_default_workspace,
)

from .project_views import (
    project_code,
)

__all__ = [
    # Main views
    'index',
    'features',
    'pricing',
    'editor',
    'jobs',
    'job_detail',
    'execute_code',
    'job_status',
    'notebooks',
    'notebook_detail',
    'analysis',
    'templates',
    'run_analysis',
    'get_job_progress',
    'environments',
    'create_environment',
    'setup_environment',
    'environment_detail',
    'execute_in_environment',
    'workflows',
    'create_workflow',
    'execute_workflow',
    'workflow_detail',
    'create_notebook',
    'execute_notebook',
    'visualizations',
    'generate_visualization',
    'process_data_visualization',
    'create_research_report',
    # Workspace views
    'guest_session_view',
    'user_default_workspace',
    # Project views
    'project_code',
]
