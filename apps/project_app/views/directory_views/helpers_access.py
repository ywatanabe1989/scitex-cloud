"""
Access Control Helpers

Validation functions for project and file access.
"""

from __future__ import annotations

from django.shortcuts import redirect
from django.contrib import messages


def check_project_access(request, project, username, slug):
    """
    Validate user access to project and redirect if unauthorized.

    Args:
        request: Django request object
        project: Project instance
        username: Project owner username
        slug: Project slug

    Returns:
        HttpResponse redirect if no access, None if access granted
    """
    has_access = (
        project.owner == request.user
        or project.collaborators.filter(id=request.user.id).exists()
        or getattr(project, "visibility", None) == "public"
    )

    if not has_access:
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        else:
            messages.error(request, "You don't have permission to access this project.")
            return redirect("user_projects:detail", username=username, slug=slug)

    return None


def get_project_filesystem(project, username, slug):
    """
    Get project filesystem manager and validate project path exists.

    Args:
        project: Project instance
        username: Project owner username
        slug: Project slug

    Returns:
        tuple: (manager, project_path) or (None, redirect_response)
    """
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    if not project_path or not project_path.exists():
        messages.error(None, "Project directory not found.")
        return None, redirect("user_projects:detail", username=username, slug=slug)

    return manager, project_path


def validate_path_security(full_path, project_path, username, slug):
    """
    Ensure path is within project directory (prevent path traversal).

    Args:
        full_path: Full path to validate
        project_path: Project root path
        username: Project owner username
        slug: Project slug

    Returns:
        Path object if valid, redirect response if invalid
    """
    try:
        resolved_path = full_path.resolve()
        if not str(resolved_path).startswith(str(project_path.resolve())):
            messages.error(None, "Invalid directory path.")
            return redirect("user_projects:detail", username=username, slug=slug)
        return resolved_path
    except Exception:
        messages.error(None, "Invalid directory path.")
        return redirect("user_projects:detail", username=username, slug=slug)
