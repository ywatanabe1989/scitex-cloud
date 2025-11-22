from django.urls import path
from . import views, api_views, default_workspace_views, workspace_views, workspace_api_views

app_name = "code"

urlpatterns = [
    # Default workspace for logged-in users without project
    path(
        "workspace/",
        default_workspace_views.user_default_workspace,
        name="user_default_workspace",
    ),
    # Main workspace - simple file editor (replaces redirect)
    path("", workspace_views.code_workspace, name="index"),
    # Workspace API endpoints
    path("api/file-content/<path:file_path>", workspace_api_views.api_get_file_content, name="api_file_content"),
    path("api/save/", workspace_api_views.api_save_file, name="api_save_file"),
    path("api/execute/", workspace_api_views.api_execute_script, name="api_execute_script"),
    path("api/command/", workspace_api_views.api_execute_command, name="api_execute_command"),
    path("api/create-file/", workspace_api_views.api_create_file, name="api_create_file"),
    path("api/delete/", workspace_api_views.api_delete_file, name="api_delete_file"),
    # Git status and diff endpoints
    path("api/git-status/", workspace_api_views.api_get_git_status, name="api_git_status"),
    path("api/file-diff/<path:file_path>", workspace_api_views.api_get_file_diff, name="api_file_diff"),
    path("api/git-commit/", workspace_api_views.api_git_commit, name="api_git_commit"),
    # Landing pages
    path("features/", views.features, name="features"),
    path("pricing/", views.pricing, name="pricing"),
    # Legacy index redirect (if needed)
    # path("old/", views.index, name="old_index"),
    path("features/", views.features, name="features"),
    path("pricing/", views.pricing, name="pricing"),
    # Core functionality
    path("editor/", views.editor, name="editor"),
    path("execute/", views.execute_code, name="execute_code"),
    path("analysis/", views.analysis, name="analysis"),
    path("analysis/run/", views.run_analysis, name="run_analysis"),
    path("templates/", views.templates, name="templates"),
    # Job management
    path("jobs/", views.jobs, name="jobs"),
    path("jobs/<uuid:job_id>/", views.job_detail, name="job_detail"),
    path("jobs/<uuid:job_id>/status/", views.job_status, name="job_status"),
    # Notebook management (views)
    path("notebooks/", views.notebooks, name="notebooks"),
    path(
        "notebooks/<uuid:notebook_id>/", views.notebook_detail, name="notebook_detail"
    ),
    path("notebooks/create/", views.create_notebook, name="create_notebook"),
    path(
        "notebooks/<uuid:notebook_id>/execute/",
        views.execute_notebook,
        name="execute_notebook",
    ),
    # Environment management
    path("environments/", views.environments, name="environments"),
    path("environments/create/", views.create_environment, name="create_environment"),
    path(
        "environments/<str:env_id>/",
        views.environment_detail,
        name="environment_detail",
    ),
    path(
        "environments/<str:env_id>/setup/",
        views.setup_environment,
        name="setup_environment",
    ),
    path(
        "environments/<str:env_id>/execute/",
        views.execute_in_environment,
        name="execute_in_environment",
    ),
    # Workflow management
    path("workflows/", views.workflows, name="workflows"),
    path("workflows/create/", views.create_workflow, name="create_workflow"),
    path("workflows/<str:workflow_id>/", views.workflow_detail, name="workflow_detail"),
    path(
        "workflows/<str:workflow_id>/execute/",
        views.execute_workflow,
        name="execute_workflow",
    ),
    # Data visualization pipeline
    path("visualizations/", views.visualizations, name="visualizations"),
    path(
        "visualizations/generate/",
        views.generate_visualization,
        name="generate_visualization",
    ),
    path(
        "visualizations/process/",
        views.process_data_visualization,
        name="process_data_visualization",
    ),
    path(
        "reports/create/", views.create_research_report, name="create_research_report"
    ),
    # Jupyter Notebook API endpoints
    path("api/notebooks/", api_views.NotebookListAPI.as_view(), name="api_notebooks"),
    path(
        "api/notebooks/<uuid:notebook_id>/",
        api_views.NotebookDetailAPI.as_view(),
        name="api_notebook_detail",
    ),
    path(
        "api/notebooks/<uuid:notebook_id>/execute/",
        api_views.NotebookExecutionAPI.as_view(),
        name="api_notebook_execute",
    ),
    path(
        "api/notebooks/<uuid:notebook_id>/convert/<str:format_type>/",
        api_views.NotebookConversionAPI.as_view(),
        name="api_notebook_convert",
    ),
    path(
        "api/notebooks/<uuid:notebook_id>/share/",
        api_views.NotebookSharingAPI.as_view(),
        name="api_notebook_share",
    ),
    path(
        "api/notebooks/<uuid:notebook_id>/duplicate/",
        api_views.duplicate_notebook_api,
        name="api_notebook_duplicate",
    ),
    path(
        "api/templates/",
        api_views.NotebookTemplatesAPI.as_view(),
        name="api_notebook_templates",
    ),
    path(
        "api/jobs/<uuid:job_id>/status/",
        api_views.notebook_status_api,
        name="api_job_status",
    ),
]
