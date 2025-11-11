#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-04 20:52:01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/writer_app/urls/api.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./apps/writer_app/urls/api.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""
Writer App API URLs

REST API endpoints for writer operations:
- Section read/write
- Compilation (preview & full)
- Git operations
- Presence tracking
- File operations
"""

from django.urls import path
from ..views.editor import api as api_views
from ..views.editor import ai2_prompt
from ..views.index import main as index_views

urlpatterns = [
    # Workspace initialization
    path('initialize-workspace/', index_views.initialize_workspace, name='api-initialize-workspace'),
    # Sections config (no project_id needed)
    path('sections-config/', api_views.sections_config_view, name='api-sections-config'),
    # Section management operations (MUST come BEFORE general section pattern)
    path(
        "project/<int:project_id>/section/create/",
        api_views.section_create_view,
        name="api-section-create",
    ),
    path(
        "project/<int:project_id>/section/<path:section_name>/delete/",
        api_views.section_delete_view,
        name="api-section-delete",
    ),
    path(
        "project/<int:project_id>/section/<path:section_name>/toggle-exclude/",
        api_views.section_toggle_exclude_view,
        name="api-section-toggle-exclude",
    ),
    path(
        "project/<int:project_id>/section/<path:section_name>/move-up/",
        api_views.section_move_up_view,
        name="api-section-move-up",
    ),
    path(
        "project/<int:project_id>/section/<path:section_name>/move-down/",
        api_views.section_move_down_view,
        name="api-section-move-down",
    ),
    # Section CRUD operations (supports hierarchical IDs like "shared/authors")
    # This MUST come AFTER specific endpoints to avoid catching their URLs
    path(
        "project/<int:project_id>/section/<path:section_name>/",
        api_views.section_view,
        name="api-section",
    ),
    # Compilation
    path(
        "project/<int:project_id>/compile_preview/",
        api_views.compile_preview_view,
        name="api-compile-preview",
    ),
    path(
        "project/<int:project_id>/compile_full/",
        api_views.compile_full_view,
        name="api-compile-full",
    ),
    path(
        "project/<int:project_id>/compilation/status/<str:job_id>/",
        api_views.compilation_job_status,
        name="api-compilation-status",
    ),
    path(
        "project/<int:project_id>/compile/",
        api_views.compile_view,
        name="api-compile",
    ),
    # Git operations
    path(
        "project/<int:project_id>/section/<str:section_name>/history/",
        api_views.section_history_view,
        name="api-section-history",
    ),
    path(
        "project/<int:project_id>/section/<str:section_name>/diff/",
        api_views.section_diff_view,
        name="api-section-diff",
    ),
    path(
        "project/<int:project_id>/section/<str:section_name>/checkout/",
        api_views.section_checkout_view,
        name="api-section-checkout",
    ),
    path(
        "project/<int:project_id>/section/<str:section_name>/commit/",
        api_views.section_commit_view,
        name="api-section-commit",
    ),
    # PDF and file operations (accept optional trailing slash)
    path("project/<int:project_id>/pdf/<str:pdf_filename>/", api_views.pdf_view, name="api-pdf-file-slash"),
    path("project/<int:project_id>/pdf/<str:pdf_filename>", api_views.pdf_view, name="api-pdf-file"),
    path("project/<int:project_id>/pdf/", api_views.pdf_view, name="api-pdf"),
    path(
        "project/<int:project_id>/preview-pdf/",
        api_views.preview_pdf_view,
        name="api-preview-pdf",
    ),
    path(
        "project/<int:project_id>/file-tree/",
        api_views.file_tree_view,
        name="api-file-tree",
    ),
    path(
        "project/<int:project_id>/read-tex-file/",
        api_views.read_tex_file_view,
        name="api-read-tex-file",
    ),
    # Section management
    path(
        "project/<int:project_id>/available-sections/",
        api_views.available_sections_view,
        name="api-available-sections",
    ),
    path(
        "project/<int:project_id>/save-sections/",
        api_views.save_sections_view,
        name="api-save-sections",
    ),
    # Presence tracking
    path(
        "project/<int:project_id>/presence/update/",
        api_views.presence_update_view,
        name="api-presence-update",
    ),
    path(
        "project/<int:project_id>/presence/list/",
        api_views.presence_list_view,
        name="api-presence-list",
    ),
    # Citations (for autocomplete)
    path(
        "project/<int:project_id>/citations/",
        api_views.citations_api,
        name="api-citations",
    ),
    # Bibliography regeneration
    path(
        "project/<int:project_id>/regenerate-bibliography/",
        api_views.regenerate_bibliography_api,
        name="api-regenerate-bibliography",
    ),
    # AI2 Asta prompt generation
    path(
        "project/<int:project_id>/generate-ai2-prompt/",
        ai2_prompt.generate_ai2_prompt_view,
        name="api-generate-ai2-prompt",
    ),
]

# EOF
