#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Directory Views - Edit Mode Module

Handles file editing functionality.
"""

from __future__ import annotations

import logging
from pathlib import Path

from django.shortcuts import render, redirect
from django.contrib import messages

from .helpers import build_breadcrumbs

logger = logging.getLogger(__name__)


def handle_edit_mode(request, project, username, slug, file_path, full_file_path: Path):
    """
    Handle edit mode - show editor and save changes.

    Args:
        request: Django request object
        project: Project model instance
        username: Project owner username
        slug: Project slug
        file_path: Relative path to file within project
        full_file_path: Full filesystem path to file

    Returns:
        HttpResponse with edit view or redirect
    """
    file_name = full_file_path.name

    # Only owner can edit
    if not (project.owner == request.user):
        messages.error(request, "Only project owner can edit files.")
        return redirect("user_projects:detail", username=username, slug=slug)

    if request.method == "POST":
        # Save edited content
        new_content = request.POST.get("content", "")
        try:
            with open(full_file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            messages.success(request, f"File '{file_name}' saved successfully!")
            return redirect(
                "user_projects:file_view",
                username=username,
                slug=slug,
                file_path=file_path,
            )
        except Exception as e:
            messages.error(request, f"Error saving file: {e}")

    # Read current content for editing
    try:
        with open(full_file_path, "r", encoding="utf-8", errors="ignore") as f:
            file_content = f.read()
    except Exception as e:
        messages.error(request, f"Error reading file: {e}")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Build breadcrumb
    breadcrumbs = build_breadcrumbs(project, username, slug, file_path)

    context = {
        "project": project,
        "file_name": file_name,
        "file_path": file_path,
        "file_content": file_content,
        "breadcrumbs": breadcrumbs,
        "mode": "edit",
    }
    return render(request, "project_app/repository/file_edit.html", context)


# EOF
