"""
File View Helpers

Common utilities for file view operations.
"""

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User

from apps.project_app.models import Project
from apps.project_app.services.project_filesystem import (
    get_project_filesystem_manager,
)


def check_file_access(request, username, slug):
    """
    Check file access and return project, manager, project_path.

    Returns:
        tuple: (project, project_path, error_redirect) where error_redirect is None on success
    """
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
        return project, None, redirect("user_projects:detail", username=username, slug=slug)

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    if not project_path or not project_path.exists():
        messages.error(request, "Project directory not found.")
        return project, None, redirect("user_projects:detail", username=username, slug=slug)

    return project, project_path, None


def validate_file_path(request, username, slug, project_path, file_path):
    """
    Validate file path and return full path.

    Returns:
        tuple: (full_file_path, error_redirect) where error_redirect is None on success
    """
    full_file_path = project_path / file_path

    # Security check
    try:
        full_file_path = full_file_path.resolve()
        if not str(full_file_path).startswith(str(project_path.resolve())):
            messages.error(request, "Invalid file path.")
            return None, redirect("user_projects:detail", username=username, slug=slug)
    except Exception:
        messages.error(request, "Invalid file path.")
        return None, redirect("user_projects:detail", username=username, slug=slug)

    # Check if file exists and is a file
    if not full_file_path.exists() or not full_file_path.is_file():
        messages.error(request, "File not found.")
        return None, redirect("user_projects:detail", username=username, slug=slug)

    return full_file_path, None


def build_file_breadcrumbs(username, slug, project_name, file_path):
    """
    Build breadcrumb navigation for file view.

    Args:
        username: Project owner username
        slug: Project slug
        project_name: Project display name
        file_path: Relative file path

    Returns:
        list: Breadcrumb items with name and url
    """
    breadcrumbs = [{"name": project_name, "url": f"/{username}/{slug}/"}]

    path_parts = file_path.split("/")
    current_path = ""
    for i, part in enumerate(path_parts):
        current_path += part
        if i < len(path_parts) - 1:  # Directory
            current_path += "/"
            breadcrumbs.append(
                {"name": part, "url": f"/{username}/{slug}/{current_path}"}
            )
        else:  # File
            breadcrumbs.append({"name": part, "url": None})

    return breadcrumbs
