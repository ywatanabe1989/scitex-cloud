#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-31 19:51:27 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/writer_app/urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./apps/writer_app/urls.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""
Simplified Writer URLs - REST API focused.

Routes are organized as:
1. Essential views (index, workspace, initialize)
2. New REST API endpoints (all Writer operations via /api/project/<id>/...)
3. Stub routes for backward compatibility (return 410 Gone)
"""

from django.urls import path
from . import views
from .views import api_views

app_name = "writer"

urlpatterns = [
    # ===== ESSENTIAL VIEWS =====
    path("", views.index, name="index"),  # Main writer home at /writer/
    path(
        "workspace/",
        views.user_default_workspace,
        name="user_default_workspace",
    ),
    path(
        "project/<int:project_id>/",
        views.project_writer,
        name="project-writer",
    ),
    # ===== NEW REST API (scitex.writer.Writer delegation) =====
    # Section CRUD operations
    path(
        "api/project/<int:project_id>/section/<str:section_name>/",
        api_views.section_view,
        name="api-section",
    ),
    # Git operations (history, diff, checkout)
    path(
        "api/project/<int:project_id>/section/<str:section_name>/history/",
        api_views.section_history_view,
        name="api-section-history",
    ),
    path(
        "api/project/<int:project_id>/section/<str:section_name>/diff/",
        api_views.section_diff_view,
        name="api-section-diff",
    ),
    path(
        "api/project/<int:project_id>/section/<str:section_name>/checkout/",
        api_views.section_checkout_view,
        name="api-section-checkout",
    ),
    # Compilation & PDF
    path(
        "api/project/<int:project_id>/compile_preview/",
        api_views.compile_preview_view,
        name="api-compile-preview",
    ),
    path(
        "api/project/<int:project_id>/compile_full/",
        api_views.compile_full_view,
        name="api-compile-full",
    ),
    path(
        "api/project/<int:project_id>/compile/",
        api_views.compile_view,
        name="api-compile",  # DEPRECATED: backward compatibility
    ),
    path(
        "api/project/<int:project_id>/pdf/", api_views.pdf_view, name="api-pdf"
    ),
    path(
        "api/project/<int:project_id>/preview-pdf/",
        api_views.preview_pdf_view,
        name="api-preview-pdf",
    ),
    # Metadata
    path(
        "api/project/<int:project_id>/sections/",
        api_views.available_sections_view,
        name="api-available-sections",
    ),
    path(
        "api/sections-config/",
        api_views.sections_config_view,
        name="api-sections-config",
    ),
    # Bulk save sections
    path(
        "api/project/<int:project_id>/save-sections/",
        api_views.save_sections_view,
        name="api-save-sections",
    ),
    # File tree
    path(
        "api/project/<int:project_id>/file-tree/",
        api_views.file_tree_view,
        name="api-file-tree",
    ),
    # Read .tex file
    path(
        "api/project/<int:project_id>/read-tex-file/",
        api_views.read_tex_file_view,
        name="api-read-tex-file",
    ),
    # Initialization
    path(
        "api/initialize-workspace/",
        views.initialize_workspace,
        name="initialize-workspace",
    ),
    # ===== BACKWARD COMPATIBILITY STUBS (410 Gone) =====
    # Old project-specific routes redirect to API
    path(
        "project/<int:project_id>/save-section/",
        views.save_section,
        name="save-section",
    ),
    path(
        "project/<int:project_id>/load-latex/",
        views.load_latex_section,
        name="load-latex",
    ),
    path(
        "project/<int:project_id>/save-latex/",
        views.save_latex_section,
        name="save-latex",
    ),
    path(
        "project/<int:project_id>/list-tex-files/",
        views.list_tex_files,
        name="list-tex-files",
    ),
    path(
        "project/<int:project_id>/compile/",
        views.compile_modular_manuscript,
        name="compile-modular",
    ),
    path(
        "project/<int:project_id>/stats/",
        views.get_manuscript_stats,
        name="manuscript-stats",
    ),
    path(
        "project/<int:project_id>/toggle-mode/",
        views.toggle_editing_mode,
        name="toggle-mode",
    ),
    path(
        "project/<int:project_id>/cloud-compile/",
        views.cloud_compile_sections,
        name="cloud-compile-sections",
    ),
    path(
        "project/<int:project_id>/download-paper/",
        views.download_paper_zip,
        name="download-paper-zip",
    ),
    path(
        "project/<int:project_id>/pdf/",
        views.download_compiled_pdf,
        name="compiled-pdf",
    ),
    # Old editor interfaces redirect to main index
    path("modular/", views.modular_editor, name="modular-editor"),
    path("simple/", views.simple_editor, name="simple-editor"),
    path("advanced/", views.latex_editor_view, name="latex-editor"),
    path("features/", views.features, name="features"),
    path("pricing/", views.pricing, name="pricing"),
    # Old API endpoints (deprecated)
    path("api/compile/", views.quick_compile, name="real-compile"),
    path(
        "api/status/<uuid:job_id>/",
        views.compilation_status,
        name="compilation-status",
    ),
    path("api/save/", views.mock_save, name="mock-save"),
    # Collaborative editing (WebSocket, stubs for backward compat)
    path(
        "api/collaborate/manuscript/<int:manuscript_id>/sessions/",
        views.collaborative_sessions,
        name="collaborative-sessions",
    ),
    path(
        "api/collaborate/manuscript/<int:manuscript_id>/join/",
        views.join_collaboration,
        name="join-collaboration",
    ),
    path(
        "api/collaborate/manuscript/<int:manuscript_id>/leave/",
        views.leave_collaboration,
        name="leave-collaboration",
    ),
    path(
        "api/collaborate/section/<int:section_id>/lock/",
        views.lock_section,
        name="lock-section",
    ),
    path(
        "api/collaborate/section/<int:section_id>/unlock/",
        views.unlock_section,
        name="unlock-section",
    ),
    path(
        "collaborative/<int:manuscript_id>/",
        views.collaborative_editor,
        name="collaborative-editor",
    ),
    # Version control (stubs, not yet implemented)
    path(
        "api/version/<int:manuscript_id>/history/",
        views.version_history,
        name="version-history",
    ),
    path(
        "api/version/<int:manuscript_id>/create/",
        views.create_version,
        name="create-version",
    ),
    path(
        "api/version/<int:manuscript_id>/diff/<uuid:from_version_id>/<uuid:to_version_id>/",
        views.view_diff,
        name="view-diff",
    ),
    path(
        "api/version/<int:manuscript_id>/rollback/<uuid:version_id>/",
        views.rollback_version,
        name="rollback-version",
    ),
    path(
        "api/branch/<int:manuscript_id>/list/",
        views.branch_list,
        name="branch-list",
    ),
    path(
        "api/branch/<int:manuscript_id>/create/",
        views.create_branch,
        name="create-branch",
    ),
    path(
        "api/merge/<int:manuscript_id>/create/",
        views.create_merge_request,
        name="create-merge-request",
    ),
    path(
        "version-control/<int:manuscript_id>/",
        views.version_control_dashboard,
        name="version-control-dashboard",
    ),
    # Advanced dashboards (stubs)
    path(
        "advanced/dashboard/",
        views.writer_dashboard_view,
        name="writer-dashboard",
    ),
    path(
        "advanced/manuscripts/", views.manuscript_list, name="manuscript-list"
    ),
    path("advanced/compile/", views.quick_compile, name="quick-compile"),
    # arXiv Integration (stubs, to be removed)
    path("arxiv/", views.ArxivDashboardView.as_view(), name="arxiv-dashboard"),
    path(
        "arxiv/account/setup/",
        views.arxiv_account_setup,
        name="arxiv-account-setup",
    ),
    path(
        "arxiv/submissions/",
        views.SubmissionListView.as_view(),
        name="arxiv-submission-list",
    ),
    path(
        "arxiv/submit/<int:manuscript_id>/",
        views.manuscript_submission_form,
        name="arxiv-submit-manuscript",
    ),
    path(
        "arxiv/submission/<str:submission_id>/",
        views.submission_detail,
        name="arxiv-submission-detail",
    ),
    path(
        "arxiv/submission/<str:submission_id>/validate/",
        views.validate_submission,
        name="arxiv-validate-submission",
    ),
    path(
        "arxiv/submission/<str:submission_id>/prepare-files/",
        views.prepare_submission_files,
        name="arxiv-prepare-files",
    ),
    path(
        "arxiv/submission/<str:submission_id>/submit/",
        views.submit_to_arxiv,
        name="arxiv-submit-to-arxiv",
    ),
    path(
        "arxiv/submission/<str:submission_id>/check-status/",
        views.check_submission_status,
        name="arxiv-check-status",
    ),
    path(
        "arxiv/submission/<str:submission_id>/withdraw/",
        views.withdraw_submission,
        name="arxiv-withdraw-submission",
    ),
    path(
        "arxiv/submission/<str:submission_id>/replace/",
        views.create_replacement,
        name="arxiv-create-replacement",
    ),
    path(
        "arxiv/submission/<str:submission_id>/history/",
        views.submission_history_api,
        name="arxiv-submission-history",
    ),
    path(
        "arxiv/api/categories/",
        views.categories_api,
        name="arxiv-categories-api",
    ),
    path(
        "arxiv/api/suggest-categories/<int:manuscript_id>/",
        views.suggest_categories_api,
        name="arxiv-suggest-categories",
    ),
    path(
        "arxiv/api/status/",
        views.arxiv_status_check,
        name="arxiv-status-check",
    ),
    path(
        "arxiv/api/initialize-categories/",
        views.initialize_categories,
        name="arxiv-initialize-categories",
    ),
]


    # Presence & Collaboration
    path(
        "api/project/<int:project_id>/presence/update/",
        views.presence_update_view,
        name="presence-update",
    ),
    path(
        "api/project/<int:project_id>/presence/list/",
        views.presence_list_view,
        name="presence-list",
    ),
]

# EOF
