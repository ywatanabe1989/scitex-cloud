"""
Repository File View

Main file viewing functionality with syntax highlighting.

Modular structure:
- file_view_helpers.py: Access checking, path validation, breadcrumbs
- file_view_git.py: Git info retrieval
- file_view_raw.py: Raw/download mode
- file_view_content.py: Content rendering
"""

from __future__ import annotations

import logging

from django.shortcuts import render, redirect

from .file_view_helpers import (
    check_file_access,
    validate_file_path,
    build_file_breadcrumbs,
)
from .file_view_git import get_file_git_info
from .file_view_raw import serve_raw_file
from .file_view_content import render_file_content

logger = logging.getLogger(__name__)


def project_file_view(request, username, slug, file_path):
    """
    View/Edit file contents (GitHub-style /blob/).

    Modes (via query parameter):
    - ?mode=view (default) - View with syntax highlighting
    - ?mode=edit - Edit file content
    - ?mode=raw - Serve raw file content
    - ?mode=download - Download file

    Supports:
    - Markdown (.md) - Rendered as HTML
    - Python (.py) - Syntax highlighted
    - YAML (.yaml, .yml) - Syntax highlighted
    - JSON (.json) - Syntax highlighted
    - Text files - Plain text with line numbers
    - Images - Display inline
    """
    mode = request.GET.get("mode", "view")

    # Check access and get project
    project, project_path, error = check_file_access(request, username, slug)
    if error:
        return error

    # Validate file path
    full_file_path, error = validate_file_path(
        request, username, slug, project_path, file_path
    )
    if error:
        return error

    # Get file info
    file_name = full_file_path.name
    file_ext = full_file_path.suffix.lower()
    file_size = full_file_path.stat().st_size

    # Handle raw/download mode
    if mode in ("raw", "download"):
        return serve_raw_file(full_file_path, file_name, file_ext, mode)

    # Handle edit mode - redirect to file_edit view
    if mode == "edit":
        from .file_edit import project_file_edit
        return project_file_edit(request, username, slug, file_path)

    # Get git information
    git_info = get_file_git_info(project_path, file_path, request, project)

    # Render content
    content_data = render_file_content(full_file_path, file_ext, file_size)

    # Build breadcrumbs
    breadcrumbs = build_file_breadcrumbs(username, slug, project.name, file_path)

    context = {
        "project": project,
        "file_name": file_name,
        "file_path": file_path,
        "file_size": file_size,
        "file_ext": file_ext,
        "file_content": content_data["file_content"],
        "file_html": content_data["file_html"],
        "render_type": content_data["render_type"],
        "language": content_data["language"],
        "breadcrumbs": breadcrumbs,
        "can_edit": project.owner == request.user,
        "git_info": git_info,
    }

    return render(request, "project_app/repository/file_view.html", context)
