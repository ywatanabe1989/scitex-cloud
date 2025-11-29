#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Directory Views - File View Module

Multi-mode file viewer with support for:
- View mode with syntax highlighting
- Edit mode for text files
- Raw/download mode for binary files
- Blame mode showing git authorship per line
- Markdown rendering
- Binary file detection and handling
"""

from __future__ import annotations

import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User

from apps.project_app.models import Project
from apps.project_app.services.project_filesystem import get_project_filesystem_manager

from .helpers import build_breadcrumbs
from .file_view_git import get_git_info_for_file
from .file_view_blame import handle_blame_mode
from .file_view_raw import handle_raw_mode
from .file_view_edit import handle_edit_mode
from .file_view_content import determine_render_type

logger = logging.getLogger(__name__)


def project_file_view(request, username, slug, file_path):
    """
    View/Edit file contents (GitHub-style /blob/).

    Modes (via query parameter):
    - ?mode=view (default) - View with syntax highlighting
    - ?mode=edit - Edit file content
    - ?mode=raw - Serve raw file content
    - ?mode=blame - Show git blame information

    Supports:
    - Markdown (.md) - Rendered as HTML
    - Python (.py) - Syntax highlighted
    - YAML (.yaml, .yml) - Syntax highlighted
    - JSON (.json) - Syntax highlighted
    - Text files - Plain text with line numbers
    - Images - Display inline
    """
    mode = request.GET.get("mode", "view")
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access
    has_access = (
        project.owner == request.user
        or project.collaborators.filter(id=request.user.id).exists()
        or getattr(project, "visibility", None) == "public"
    )

    if not has_access:
        messages.error(request, "You don't have permission to access this file.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Get file path
    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    if not project_path or not project_path.exists():
        messages.error(request, "Project directory not found.")
        return redirect("user_projects:detail", username=username, slug=slug)

    full_file_path = project_path / file_path

    # Security check - prevent path traversal
    try:
        full_file_path = full_file_path.resolve()
        if not str(full_file_path).startswith(str(project_path.resolve())):
            messages.error(request, "Invalid file path.")
            return redirect("user_projects:detail", username=username, slug=slug)
    except Exception:
        messages.error(request, "Invalid file path.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Check if file exists and is a file
    if not full_file_path.exists() or not full_file_path.is_file():
        messages.error(request, "File not found.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Get file metadata
    file_name = full_file_path.name
    file_ext = full_file_path.suffix.lower()
    file_size = full_file_path.stat().st_size

    # Get Git commit information for this file
    git_info = get_git_info_for_file(request, project, project_path, file_path)

    # Handle raw/download mode
    if mode in ("raw", "download"):
        return handle_raw_mode(full_file_path, file_name, file_ext, mode)

    # Handle blame mode
    if mode == "blame":
        return handle_blame_mode(request, project, username, slug, file_path, git_info)

    # Handle edit mode
    if mode == "edit":
        return handle_edit_mode(request, project, username, slug, file_path, full_file_path)

    # View mode - read and render file content
    try:
        render_type, file_content, file_html, language = determine_render_type(
            full_file_path, file_ext
        )
    except Exception as e:
        messages.error(request, f"Error reading file: {e}")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Build breadcrumb
    breadcrumbs = build_breadcrumbs(project, username, slug, file_path)

    context = {
        "project": project,
        "file_name": file_name,
        "file_path": file_path,
        "file_size": file_size,
        "file_ext": file_ext,
        "file_content": file_content,
        "file_html": file_html,
        "render_type": render_type,
        "language": language,
        "breadcrumbs": breadcrumbs,
        "can_edit": project.owner == request.user,
        "git_info": git_info,
    }

    return render(request, "project_app/repository/file_view.html", context)


# EOF
