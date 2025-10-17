"""
Decorators for project-based access control.
"""

from functools import wraps
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Project


def project_required(view_func):
    """
    Decorator to ensure user has at least one project.

    If user has no projects, redirects to project creation page with helpful message.
    Must be used with @login_required.

    Usage:
        @login_required
        @project_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user has any projects
        user_projects = Project.objects.filter(owner=request.user)

        if not user_projects.exists():
            messages.warning(
                request,
                'You need to create a project first. Projects help organize your research work across Scholar, Writer, Code, and Viz modules.'
            )
            return redirect('project_app:create')

        return view_func(request, *args, **kwargs)

    return wrapper


def project_access_required(view_func):
    """
    Decorator to check if user has access to a specific project.

    Expects username and slug in kwargs.
    Checks if user is owner or collaborator.

    Usage:
        @login_required
        @project_access_required
        def my_view(request, username, slug):
            project = request.project  # Available in request
            ...
    """
    @wraps(view_func)
    def wrapper(request, username, slug, *args, **kwargs):
        from django.contrib.auth.models import User

        # Get user and project
        user = get_object_or_404(User, username=username)
        project = get_object_or_404(Project, slug=slug, owner=user)

        # Check access
        has_access = (
            project.owner == request.user or
            project.collaborators.filter(id=request.user.id).exists() or
            request.user.is_staff
        )

        if not has_access:
            messages.error(request, "You don't have permission to access this project.")
            return redirect('project_app:user_projects', username=request.user.username)

        # Attach project to request for convenience
        request.project = project

        return view_func(request, username, slug, *args, **kwargs)

    return wrapper
