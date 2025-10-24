#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-24 00:23:02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/project_app/views.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./apps/project_app/views.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from apps.project_app.models import Project
from apps.project_app.models import ProjectMembership
from .models import Organization, ResearchGroup
from .decorators import project_required
from .decorators import project_access_required
from django.contrib.auth.models import User
import json
import logging

logger = logging.getLogger(__name__)


@login_required
def project_list(request):
    """Redirect to user's personal project page (GitHub-style)"""
    return redirect(f"/{request.user.username}/?tab=repositories")


def user_profile(request, username):
    """
    User profile page (GitHub-style /<username>/)

    Public view - no login required (like GitHub)

    Supports tabs via query parameter:
    - /<username>/ or /<username>?tab=overview - Overview
    - /<username>?tab=repositories - Projects list
    - /<username>?tab=projects - Project boards (future)
    - /<username>?tab=stars - Starred projects
    """
    # Check if username is a reserved path
    from config.urls import RESERVED_PATHS
    if username.lower() in [path.lower() for path in RESERVED_PATHS]:
        from django.http import Http404
        raise Http404("This path is reserved and not a valid username")

    user = get_object_or_404(User, username=username)
    tab = request.GET.get("tab", "repositories")  # Default to repositories

    if tab == "repositories":
        return user_project_list(request, username)
    elif tab == "overview":
        return user_overview(request, username)
    elif tab == "projects":
        return user_projects_board(request, username)
    elif tab == "stars":
        return user_stars(request, username)
    else:
        # Invalid tab - redirect to repositories
        return user_project_list(request, username)


def user_project_list(request, username):
    """List a specific user's projects (called from user_profile with tab=repositories)"""
    user = get_object_or_404(User, username=username)

    # Filter projects based on visibility and access
    user_projects = Project.objects.filter(owner=user)

    # If not the owner, only show public projects or projects where user is a collaborator
    if not (request.user.is_authenticated and request.user == user):
        if request.user.is_authenticated:
            # Show public projects + projects where user is a collaborator
            user_projects = user_projects.filter(
                models.Q(visibility="public")
                | models.Q(memberships__user=request.user)
            ).distinct()
        else:
            # Anonymous users only see public projects
            user_projects = user_projects.filter(visibility="public")

    user_projects = user_projects.order_by("-updated_at")

    # Check if this is the current user viewing their own projects
    is_own_projects = request.user.is_authenticated and request.user == user

    # Add pagination
    paginator = Paginator(user_projects, 12)
    page_number = request.GET.get("page")
    projects = paginator.get_page(page_number)

    # Get social stats
    from apps.social_app.models import UserFollow, RepositoryStar

    followers_count = UserFollow.get_followers_count(user)
    following_count = UserFollow.get_following_count(user)
    is_following = (
        UserFollow.is_following(request.user, user)
        if request.user.is_authenticated
        else False
    )

    context = {
        "projects": projects,
        "profile_user": user,  # The user whose profile we're viewing
        "is_own_projects": is_own_projects,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "active_tab": "repositories",
        # Note: 'user' is automatically available as request.user in templates
        # Don't override it here - it should always be the logged-in user
    }
    return render(request, "project_app/users/projects.html", context)


def user_bio_page(request, username):
    """User bio/profile README page (GitHub-style /<username>/<username>/)"""
    user = get_object_or_404(User, username=username)

    # Get or create user profile
    from apps.accounts_app.models import UserProfile

    profile, created = UserProfile.objects.get_or_create(user=user)

    # Get user's projects
    projects = Project.objects.filter(owner=user).order_by("-updated_at")[
        :6
    ]  # Show top 6

    # Check if this is the user viewing their own profile
    is_own_profile = request.user.is_authenticated and request.user == user

    context = {
        "profile_user": user,
        "profile": profile,
        "projects": projects,
        "is_own_profile": is_own_profile,
        "total_projects": Project.objects.filter(owner=user).count(),
    }

    return render(request, "project_app/users/bio.html", context)


@project_access_required
def project_detail(request, username, slug):
    """
    Project detail page (GitHub-style /<username>/<project>/)

    Supports mode via query parameter:
    - /<username>/<project>/ or ?mode=overview - Project dashboard
    - /<username>/<project>?mode=writer - Writer module (legacy, use /writer/)
    - /<username>/<project>?mode=code - Code module (legacy, use /code/)
    - /<username>/<project>?mode=viz - Viz module (legacy, use /viz/)

    Note: Scholar module now only accessible via /scholar/
    """
    # Special case: if slug matches username, this is a bio/profile README page
    if slug == username:
        return user_bio_page(request, username)

    # project available in request.project from decorator
    project = request.project
    mode = request.GET.get("mode", "overview")
    view = request.GET.get("view", "default")

    # Track last active repository for this user
    if request.user.is_authenticated and hasattr(request.user, "profile"):
        if request.user.profile.last_active_repository != project:
            request.user.profile.last_active_repository = project
            request.user.profile.save(update_fields=["last_active_repository"])

    # Handle concatenated view
    if view == "concatenated":
        return api_concatenate_directory(request, username, slug, "")

    # Route to appropriate module based on mode
    if mode == "writer":
        from apps.writer_app import views as writer_views

        return writer_views.project_writer(request, project.id)
    elif mode == "code":
        from apps.code_app import views as code_views

        return code_views.project_code(request, project.id)
    elif mode == "viz":
        from apps.viz_app import views as viz_views

        return viz_views.project_viz(request, project.id)

    # Default mode: overview - GitHub-style file browser with README
    # Get project directory and file list
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    # Get root directory files (like GitHub)
    files = []
    dirs = []
    readme_content = None
    readme_html = None

    if project_path and project_path.exists():
        try:
            # Helper function to get git commit info for a file/folder
            def get_git_info(path):
                """Get last commit message, author, hash, and time for a file/folder"""
                try:
                    import subprocess
                    from datetime import datetime

                    # Get last commit for this file (including hash)
                    result = subprocess.run(
                        ['git', 'log', '-1', '--format=%an|%ar|%s|%h', '--', str(path.name)],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                    if result.returncode == 0 and result.stdout.strip():
                        author, time_ago, message, commit_hash = result.stdout.strip().split('|', 3)
                        return {
                            'author': author,
                            'time_ago': time_ago,
                            'message': message[:80],  # Truncate to 80 chars
                            'hash': commit_hash
                        }
                except Exception as e:
                    logger.debug(f"Error getting git info for {path}: {e}")

                return {
                    'author': '',
                    'time_ago': '',
                    'message': '',
                    'hash': ''
                }

            for item in project_path.iterdir():
                # Show all files including dotfiles
                git_info = get_git_info(item)

                if item.is_file():
                    files.append(
                        {
                            "name": item.name,
                            "path": str(item.relative_to(project_path)),
                            "size": item.stat().st_size,
                            "modified": item.stat().st_mtime,
                            "author": git_info.get('author', ''),
                            "time_ago": git_info.get('time_ago', ''),
                            "message": git_info.get('message', ''),
                            "hash": git_info.get('hash', ''),
                        }
                    )
                elif item.is_dir():
                    dirs.append(
                        {
                            "name": item.name,
                            "path": str(item.relative_to(project_path)),
                            "author": git_info.get('author', ''),
                            "time_ago": git_info.get('time_ago', ''),
                            "message": git_info.get('message', ''),
                            "hash": git_info.get('hash', ''),
                        }
                    )

            # Read README.md if exists and convert to HTML
            readme_path = project_path / "README.md"
            if readme_path.exists():
                readme_content = readme_path.read_text(encoding="utf-8")
                # Convert markdown to HTML
                import markdown

                readme_html = markdown.markdown(
                    readme_content,
                    extensions=["fenced_code", "tables", "nl2br"],
                )
        except Exception as e:
            pass

    # Sort: directories first, then files
    dirs.sort(key=lambda x: x["name"].lower())
    files.sort(key=lambda x: x["name"].lower())

    context = {
        "project": project,
        "user": request.user,
        "directories": dirs,
        "files": files,
        "readme_content": readme_content,
        "readme_html": readme_html,
        "mode": mode,
    }
    return render(request, "project_app/index.html", context)


@login_required
def project_create(request):
    """Create new project"""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        init_type = request.POST.get("init_type", "empty")
        template_type = request.POST.get("template_type", "research")
        git_url = request.POST.get("git_url", "").strip()

        # Initialize directory manager for all init types
        from apps.project_app.services.project_filesystem import (
            get_project_filesystem_manager,
        )

        manager = get_project_filesystem_manager(request.user)

        # If importing from Git and no name provided, extract from URL
        if not name and git_url and init_type in ["github", "git"]:
            name = Project.extract_repo_name_from_url(git_url)

        if not name:
            messages.error(request, "Project name is required")
            # Get templates for re-rendering form
            try:
                from scitex.template import get_available_templates_info

                available_templates = get_available_templates_info()
            except ImportError:
                available_templates = []
            context = {"available_templates": available_templates}
            return render(request, "project_app/create.html", context)

        # Validate repository name
        is_valid, error_message = Project.validate_repository_name(name)
        if not is_valid:
            messages.error(request, error_message)
            # Get templates for re-rendering form
            try:
                from scitex.template import get_available_templates_info

                available_templates = get_available_templates_info()
            except ImportError:
                available_templates = []
            context = {
                "available_templates": available_templates,
                "name": name,
                "description": description,
                "init_type": init_type,
                "git_url": git_url,
            }
            return render(request, "project_app/create.html", context)

        # Check if name already exists for this user
        if Project.objects.filter(name=name, owner=request.user).exists():
            messages.error(
                request,
                f'You already have a project named "{name}". Please choose a different name.',
            )
            # Get templates for re-rendering form
            try:
                from scitex.template import get_available_templates_info

                available_templates = get_available_templates_info()
            except ImportError:
                available_templates = []
            context = {
                "available_templates": available_templates,
                "name": name,
                "description": description,
            }
            return render(request, "project_app/create.html", context)

        # Generate slug from name
        from django.utils.text import slugify

        base_slug = slugify(name)
        unique_slug = Project.generate_unique_slug(base_slug)

        try:
            project = Project.objects.create(
                name=name,
                slug=unique_slug,
                description=description,
                owner=request.user,
            )
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            messages.error(request, f"Failed to create project: {str(e)}")
            return redirect("project_app:list")

        # Handle different initialization types
        if init_type == "gitea":
            # Create with Gitea + template
            try:
                # Signal already created Gitea repo, just verify it worked
                if not project.gitea_enabled or not project.gitea_repo_id:
                    # If signal failed, try manual creation
                    repo = project.create_gitea_repository()

                # Refresh from DB to get latest signal updates
                project.refresh_from_db()

                # Check if clone already succeeded (done by signal)
                from pathlib import Path
                from django.conf import settings
                project_dir = Path(settings.BASE_DIR) / 'data' / 'users' / project.owner.username / project.slug

                if not project_dir.exists() or not (project_dir / '.git').exists():
                    # Clone to local directory if not done by signal
                    success, result = project.clone_gitea_to_local()
                else:
                    # Already cloned by signal
                    success = True
                    result = str(project_dir)

                if success:
                    messages.success(
                        request,
                        f'Project "{project.name}" created successfully!',
                    )
                else:
                    messages.error(
                        request,
                        f"Gitea repository created but clone failed: {result}",
                    )
                    logger.error(f"Clone failed for {project.slug}: {result}")
                    project.delete()
                    # Get templates for re-rendering form
                    try:
                        from scitex.template import (
                            get_available_templates_info,
                        )

                        available_templates = get_available_templates_info()
                    except ImportError:
                        available_templates = []
                    context = {
                        "available_templates": available_templates,
                        "error": f"Clone failed: {result}",
                    }
                    return render(
                        request, "project_app/create.html", context
                    )

            except Exception as e:
                error_msg = str(e)
                if "already exists" in error_msg.lower() or "409" in error_msg:
                    messages.error(
                        request,
                        f'Repository "{name}" already exists in Gitea. Please choose a different name.',
                    )
                else:
                    messages.error(
                        request, f"Failed to create repository: {error_msg}"
                    )
                logger.error(f"Gitea creation failed for {project.slug}: {e}")
                project.delete()
                # Get templates for re-rendering form
                try:
                    from scitex.template import get_available_templates_info

                    available_templates = get_available_templates_info()
                except ImportError:
                    available_templates = []
                context = {
                    "available_templates": available_templates,
                    "name": name,
                    "description": description,
                    "error": error_msg,
                }
                return render(
                    request, "project_app/create.html", context
                )

        elif init_type == "github":
            # Import from GitHub/GitLab - Use direct Git clone instead of Gitea
            if not git_url:
                messages.error(
                    request, "Repository URL is required for importing"
                )
                project.delete()
                # Get templates for re-rendering form
                try:
                    from scitex.template import get_available_templates_info

                    available_templates = get_available_templates_info()
                except ImportError:
                    available_templates = []
                context = {
                    "available_templates": available_templates,
                    "name": name,
                    "description": description,
                    "init_type": "github",
                    "git_url": git_url,
                }
                return render(
                    request, "project_app/create.html", context
                )

            try:
                # Clone from Git repository directly (no Gitea needed)
                success, error_msg = manager.clone_from_git(project, git_url)

                if success:
                    messages.success(
                        request,
                        f'Project "{project.name}" imported from Git repository successfully',
                    )
                else:
                    messages.error(
                        request, f"Failed to clone repository: {error_msg}"
                    )
                    project.delete()
                    return redirect("new")

            except Exception as e:
                messages.error(request, f"Failed to import from Git: {str(e)}")
                project.delete()
                return redirect("new")

        elif init_type == "template":
            # Create with template (no Gitea)
            success, path = manager.create_project_directory(
                project, use_template=True, template_type=template_type
            )
            if success:
                messages.success(
                    request,
                    f'Project "{project.name}" created with {template_type} template',
                )
            else:
                messages.error(
                    request, f"Failed to create project with template"
                )
                project.delete()
                return redirect("project_app:list")

        elif init_type == "git":
            # Validate Git URL
            if not git_url:
                messages.error(
                    request, "Repository URL is required for cloning from Git"
                )
                project.delete()
                return redirect("new")

            # Create empty directory first
            success, path = manager.create_project_directory(
                project, use_template=False
            )
            if not success:
                messages.error(request, "Failed to create project directory")
                project.delete()
                return redirect("project_app:list")

            # Clone from Git repository
            success, error_msg = manager.clone_from_git(project, git_url)
            if success:
                messages.success(
                    request,
                    f'Project "{project.name}" created and cloned from Git repository',
                )
            else:
                messages.error(
                    request, f"Project created but cloning failed: {error_msg}"
                )

        else:
            # Create empty project
            success, path = manager.create_project_directory(
                project, use_template=False
            )
            if success:
                messages.success(
                    request, f'Project "{project.name}" created successfully'
                )
            else:
                messages.error(request, f"Failed to create project directory")
                project.delete()
                return redirect("project_app:list")

        return redirect(
            "user_projects:detail",
            username=request.user.username,
            slug=project.slug,
        )

    # GET request - get available templates from scitex
    try:
        from scitex.template import get_available_templates_info

        available_templates = get_available_templates_info()
    except ImportError:
        # Fallback if scitex not available
        available_templates = [
            {
                "id": "research",
                "name": "Research Project",
                "description": "Full scientific workflow structure",
            },
            {
                "id": "pip_project",
                "name": "Python Package",
                "description": "Pip-installable package template",
            },
            {
                "id": "singularity",
                "name": "Singularity Container",
                "description": "Container-based project",
            },
        ]

    context = {"available_templates": available_templates}
    return render(request, "project_app/create.html", context)


@login_required
def project_create_from_template(request, username, slug):
    """Create template structure for an existing empty project"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Only project owner can create template
    if project.owner != request.user:
        messages.error(
            request, "Only project owner can create template structure."
        )
        return redirect("user_projects:detail", username=username, slug=slug)

    if request.method == "POST":
        # Create template structure
        from apps.project_app.services.project_filesystem import (
            get_project_filesystem_manager,
        )

        manager = get_project_filesystem_manager(project.owner)

        success, path = manager.create_project_from_template(project)

        if success:
            messages.success(
                request,
                f'Template structure created successfully for "{project.name}"!',
            )
        else:
            messages.error(request, "Failed to create template structure.")

        return redirect("user_projects:detail", username=username, slug=slug)

    # GET request - show confirmation page or redirect
    return redirect("user_projects:detail", username=username, slug=slug)


@login_required
def project_edit(request, username, slug):
    """Edit project"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Only project owner can edit
    if project.owner != request.user:
        messages.error(
            request, "You don't have permission to edit this project."
        )
        return redirect("project_app:detail", username=username, slug=slug)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        if name:
            project.name = name
        if description:
            project.description = description

        project.save()
        messages.success(request, "Project updated successfully")
        return redirect(
            "project_app:detail", username=username, slug=project.slug
        )

    context = {"project": project}
    return render(request, "project_app/edit.html", context)


@login_required
def project_settings(request, username, slug):
    """GitHub-style repository settings page"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Only project owner can access settings
    if project.owner != request.user:
        messages.error(
            request, "You don't have permission to access settings."
        )
        return redirect("user_projects:detail", username=username, slug=slug)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_general":
            # Update basic project info
            project.name = request.POST.get("name", "").strip()
            project.description = request.POST.get("description", "").strip()
            project.save()
            messages.success(request, "General settings updated successfully")

        elif action == "update_visibility":
            # Update visibility
            new_visibility = request.POST.get("visibility")
            if new_visibility in ["public", "private"]:
                project.visibility = new_visibility
                project.save()
                messages.success(
                    request,
                    f"Repository visibility updated to {new_visibility}",
                )

        elif action == "add_collaborator":
            # Add collaborator
            collaborator_username = request.POST.get(
                "collaborator_username", ""
            ).strip()
            collaborator_role = request.POST.get(
                "collaborator_role", "collaborator"
            )

            if collaborator_username:
                try:
                    collaborator = User.objects.get(
                        username=collaborator_username
                    )

                    # Check if already a collaborator
                    if ProjectMembership.objects.filter(
                        project=project, user=collaborator
                    ).exists():
                        messages.warning(
                            request,
                            f"{collaborator_username} is already a collaborator",
                        )
                    elif collaborator == project.owner:
                        messages.warning(
                            request,
                            "Repository owner is already a collaborator",
                        )
                    else:
                        # Add collaborator
                        ProjectMembership.objects.create(
                            project=project,
                            user=collaborator,
                            role=collaborator_role,
                        )
                        messages.success(
                            request,
                            f"{collaborator_username} added as {collaborator_role}",
                        )
                except User.DoesNotExist:
                    messages.error(
                        request, f'User "{collaborator_username}" not found'
                    )
            else:
                messages.error(request, "Please enter a username")

        elif action == "delete_repository":
            # Delete repository
            project_name = project.name
            project.delete()
            messages.success(
                request, f'Repository "{project_name}" has been deleted'
            )
            return redirect(f"/{request.user.username}/")

        return redirect("user_projects:settings", username=username, slug=slug)

    context = {
        "project": project,
    }
    return render(request, "project_app/settings.html", context)


@login_required
def project_delete(request, username, slug):
    """Delete project"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Only project owner can delete
    if project.owner != request.user:
        messages.error(
            request, "You don't have permission to delete this project."
        )
        return redirect("project_app:detail", username=username, slug=slug)

    if request.method == "POST":
        # Verify confirmation text matches "username/slug"
        confirmation = request.POST.get("confirmation", "").strip()
        expected_confirmation = f"{username}/{slug}"

        if confirmation != expected_confirmation:
            messages.error(
                request,
                f'Confirmation text does not match. Please type "{expected_confirmation}" exactly.',
            )
            return render(
                request,
                "project_app/delete.html",
                {"project": project},
            )

        project_name = project.name
        project.delete()
        messages.success(
            request, f'Project "{project_name}" deleted successfully'
        )
        return redirect("project_app:list")

    context = {"project": project}
    return render(request, "project_app/delete.html", context)


@login_required
def project_collaborate(request, username, slug):
    """Project collaboration management"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Only project owner can manage collaborators
    if project.owner != request.user:
        messages.error(
            request,
            "You don't have permission to manage collaborators for this project.",
        )
        return redirect("project_app:detail", username=username, slug=slug)

    context = {
        "project": project,
        "memberships": project.memberships.all(),
    }
    return render(request, "project_app/project_collaborate.html", context)


@login_required
def project_members(request, username, slug):
    """Project members management"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Only project owner can manage members
    if project.owner != request.user:
        messages.error(
            request,
            "You don't have permission to manage members for this project.",
        )
        return redirect("project_app:detail", username=username, slug=slug)

    context = {
        "project": project,
        "members": project.memberships.all(),
    }
    return render(request, "project_app/project_members.html", context)


@login_required
def github_integration(request, username, slug):
    """GitHub integration for project"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Only project owner can manage GitHub integration
    if project.owner != request.user:
        messages.error(
            request,
            "You don't have permission to manage GitHub integration for this project.",
        )
        return redirect("project_app:detail", username=username, slug=slug)

    context = {
        "project": project,
    }
    return render(request, "project_app/github_integration.html", context)


# API Views
@login_required
@require_http_methods(["GET"])
def api_file_tree(request, username, slug):
    """API endpoint to get project file tree for sidebar navigation"""
    from pathlib import Path

    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access
    has_access = (
        project.owner == request.user
        or project.collaborators.filter(id=request.user.id).exists()
    )

    if not has_access:
        return JsonResponse({"success": False, "error": "Permission denied"})

    # Get project directory
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    if not project_path or not project_path.exists():
        return JsonResponse(
            {"success": False, "error": "Project directory not found"}
        )

    def build_tree(path, max_depth=5, current_depth=0):
        """Build file tree recursively (deeper for full navigation)"""
        items = []
        try:
            for item in sorted(
                path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())
            ):
                if item.name.startswith(".") and item.name not in [
                    ".gitignore"
                ]:
                    continue
                # Skip common non-essential directories
                if item.name in [
                    "__pycache__",
                    ".git",
                    "node_modules",
                    ".venv",
                    "venv",
                ]:
                    continue

                rel_path = item.relative_to(project_path)
                item_data = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "path": str(rel_path),
                }

                # Add children for directories (deeper depth for full tree)
                if item.is_dir() and current_depth < max_depth:
                    item_data["children"] = build_tree(
                        item, max_depth, current_depth + 1
                    )

                items.append(item_data)
        except PermissionError:
            pass

        return items

    tree = build_tree(project_path)

    return JsonResponse({"success": True, "tree": tree})


@login_required
@require_http_methods(["GET"])
def api_check_name_availability(request):
    """
    API endpoint to check if project name is available.

    Enforces strict 1:1 mapping: Local ↔ Django ↔ Gitea
    A name is only available if it's free in BOTH Django AND Gitea.
    """
    name = request.GET.get("name", "").strip()

    if not name:
        return JsonResponse(
            {"available": False, "message": "Project name is required"}
        )

    # Validate name using scitex.project validator
    try:
        from scitex.project import validate_name
        is_valid, error = validate_name(name)
        if not is_valid:
            return JsonResponse(
                {"available": False, "message": error}
            )
    except ImportError:
        # Fallback to basic validation if scitex.project not available
        pass

    # Check 1: Django database (name must be unique per user)
    exists_in_django = Project.objects.filter(name=name, owner=request.user).exists()
    if exists_in_django:
        return JsonResponse(
            {
                "available": False,
                "message": f'You already have a project named "{name}"',
            }
        )

    # Check 2: Gitea repository (enforce 1:1 mapping)
    # Generate slug to check in Gitea
    from django.utils.text import slugify
    slug = slugify(name)

    try:
        from apps.gitea_app.api_client import GiteaClient, GiteaAPIError
        client = GiteaClient()

        try:
            existing_repo = client.get_repository(
                owner=request.user.username,
                repo=slug
            )
            if existing_repo:
                # Gitea repo exists - check if it's orphaned (no Django project)
                # This is the problem: orphaned Gitea repo blocks creation
                return JsonResponse(
                    {
                        "available": False,
                        "message": f'Repository "{name}" already exists in Gitea. If this is an old project, please contact support to clean it up.',
                    }
                )
        except GiteaAPIError as e:
            # 404 means repository doesn't exist in Gitea - that's good
            if "404" in str(e) or "not found" in str(e).lower():
                pass  # Continue, name is available
            else:
                # Some other Gitea error - log it but don't block
                logger.warning(f"Gitea check failed for {name}: {e}")
                pass  # Continue, assume available
    except Exception as e:
        # If Gitea check fails entirely, log but don't block
        logger.warning(f"Gitea availability check failed: {e}")
        pass  # Continue, assume available

    return JsonResponse(
        {"available": True, "message": f'"{name}" is available'}
    )


@login_required
@require_http_methods(["GET"])
def api_project_list(request):
    """API endpoint for project list"""
    projects = Project.objects.filter(owner=request.user).values(
        "id", "name", "description", "created_at", "updated_at"
    )
    return JsonResponse({"projects": list(projects)})


@login_required
@require_http_methods(["POST"])
def api_project_create(request):
    """API endpoint for project creation"""
    try:
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        description = data.get("description", "").strip()

        if not name:
            return JsonResponse(
                {"success": False, "error": "Project name is required"}
            )

        # Ensure unique name
        unique_name = Project.generate_unique_name(name, request.user)

        project = Project.objects.create(
            name=unique_name,
            description=description,
            owner=request.user,
        )

        return JsonResponse(
            {
                "success": True,
                "project_id": project.pk,
                "message": f'Project "{project.name}" created successfully',
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def api_concatenate_directory(request, username, slug, directory_path=""):
    """
    API endpoint to concatenate all files in a directory (like view_repo.sh).
    Returns markdown-formatted content with tree + file contents.
    """
    from pathlib import Path

    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access
    has_access = (
        project.owner == request.user
        or project.collaborators.filter(id=request.user.id).exists()
    )

    if not has_access:
        return JsonResponse({"success": False, "error": "Permission denied"})

    # Get directory path
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    if not project_path or not project_path.exists():
        return JsonResponse(
            {"success": False, "error": "Project directory not found"}
        )

    dir_path = project_path / directory_path

    # Security check
    try:
        dir_path = dir_path.resolve()
        if not str(dir_path).startswith(str(project_path.resolve())):
            return JsonResponse({"success": False, "error": "Invalid path"})
    except (ValueError, OSError, RuntimeError) as e:
        logger.warning(f"Path resolution failed: {e}")
        return JsonResponse({"success": False, "error": "Invalid path"})

    if not dir_path.exists() or not dir_path.is_dir():
        return JsonResponse({"success": False, "error": "Directory not found"})

    # Whitelist extensions
    WHITELIST_EXTS = {
        ".txt",
        ".md",
        ".org",
        ".sh",
        ".py",
        ".yaml",
        ".yml",
        ".json",
        ".tex",
        ".bib",
    }
    MAX_FILE_SIZE = 100000  # 100KB

    output = []
    output.append(
        f"# Directory View: {directory_path if directory_path else 'Project Root'}"
    )
    output.append(f"Project: {project.name}")
    output.append(f"Owner: {project.owner.username}")
    output.append(f"")
    output.append(f"## File Contents")
    output.append(f"")

    # Recursively get all files
    for file_path in sorted(dir_path.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.name.startswith(".") and file_path.name not in [
            ".gitignore",
            ".gitkeep",
        ]:
            continue
        if file_path.suffix.lower() not in WHITELIST_EXTS:
            continue
        if file_path.stat().st_size > MAX_FILE_SIZE:
            continue

        try:
            rel_path = file_path.relative_to(dir_path)
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            # Get language for syntax highlighting
            lang_map = {
                ".py": "python",
                ".sh": "bash",
                ".yaml": "yaml",
                ".yml": "yaml",
                ".json": "json",
                ".md": "markdown",
                ".tex": "latex",
            }
            lang = lang_map.get(file_path.suffix.lower(), "plaintext")

            output.append(f"### `{rel_path}`")
            output.append(f"")
            output.append(f"```{lang}")
            output.append(content[:5000])  # First 5000 chars
            if len(content) > 5000:
                output.append("...")
            output.append("```")
            output.append(f"")
        except Exception as e:
            continue

    concatenated_content = "\n".join(output)

    return JsonResponse(
        {
            "success": True,
            "content": concatenated_content,
            "file_count": len([l for l in output if l.startswith("###")]),
        }
    )


@login_required
@require_http_methods(["GET"])
def api_project_detail(request, pk):
    """API endpoint for project detail"""
    try:
        project = get_object_or_404(Project, pk=pk, owner=request.user)
        data = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "progress": project.progress,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
        }
        return JsonResponse({"success": True, "project": data})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def project_detail_redirect(request, pk=None, slug=None):
    """Redirect old URLs to new username/project URLs for backward compatibility"""
    if pk:
        # Redirect from /projects/id/123/ to /username/project-name/
        project = get_object_or_404(Project, pk=pk, owner=request.user)
        return redirect(
            "project_app:detail",
            username=project.owner.username,
            slug=project.slug,
            permanent=True,
        )
    elif slug:
        # Redirect from /projects/project-name/ to /username/project-name/
        project = get_object_or_404(Project, slug=slug, owner=request.user)
        return redirect(
            "project_app:detail",
            username=project.owner.username,
            slug=project.slug,
            permanent=True,
        )
    else:
        return redirect("project_app:list")


def project_directory_dynamic(request, username, slug, directory_path):
    """
    Dynamic directory browser - handles ANY directory path.

    URLs like:
    - /username/project/scripts/
    - /username/project/scripts/mnist/
    - /username/project/paper/manuscript/
    - /username/project/data/raw/images/
    """
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access permissions
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
            messages.error(
                request, "You don't have permission to access this project."
            )
            return redirect(
                "user_projects:detail", username=username, slug=slug
            )

    # Get project path
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    if not project_path or not project_path.exists():
        messages.error(request, "Project directory not found.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Construct full directory path
    from pathlib import Path

    full_directory_path = project_path / directory_path

    # Security check: ensure path is within project directory
    try:
        full_directory_path = full_directory_path.resolve()
        if not str(full_directory_path).startswith(
            str(project_path.resolve())
        ):
            messages.error(request, "Invalid directory path.")
            return redirect(
                "user_projects:detail", username=username, slug=slug
            )
    except Exception:
        messages.error(request, "Invalid directory path.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Check if directory exists
    if not full_directory_path.exists():
        messages.error(request, f"Directory '{directory_path}' not found.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Get directory contents
    contents = []
    try:
        for item in full_directory_path.iterdir():
            # Show all files and directories including hidden files
            # Skip only special directories like .git
            if item.is_dir() and item.name in [
                ".git",
                "__pycache__",
                "node_modules",
                ".venv",
                "venv",
            ]:
                continue

            if item.is_file():
                contents.append(
                    {
                        "name": item.name,
                        "type": "file",
                        "size": item.stat().st_size,
                        "modified": item.stat().st_mtime,
                        "path": str(item.relative_to(project_path)),
                    }
                )
            elif item.is_dir():
                contents.append(
                    {
                        "name": item.name,
                        "type": "directory",
                        "path": str(item.relative_to(project_path)),
                    }
                )
    except PermissionError:
        messages.error(request, "Permission denied accessing directory.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Sort: directories first, then files, alphabetically
    contents.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))

    # Build breadcrumb navigation
    breadcrumbs = [{"name": project.name, "url": f"/{username}/{slug}/"}]

    # Add each path component to breadcrumbs
    path_parts = directory_path.split("/")
    current_path = ""
    for part in path_parts:
        if part:
            current_path += part + "/"
            breadcrumbs.append(
                {"name": part, "url": f"/{username}/{slug}/{current_path}"}
            )

    context = {
        "project": project,
        "directory": path_parts[0] if path_parts else directory_path,
        "subpath": "/".join(path_parts[1:]) if len(path_parts) > 1 else None,
        "breadcrumb_path": directory_path,
        "contents": contents,
        "breadcrumbs": breadcrumbs,
        "can_edit": project.owner == request.user
        or project.collaborators.filter(id=request.user.id).exists(),
    }

    return render(request, "project_app/filer/directory.html", context)


def _detect_language(file_ext, file_name):
    """
    Detect language for syntax highlighting based on file extension.
    Returns language identifier for highlight.js.
    """
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'bash',
        '.fish': 'bash',
        '.c': 'c',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.java': 'java',
        '.rb': 'ruby',
        '.php': 'php',
        '.go': 'go',
        '.rs': 'rust',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.r': 'r',
        '.R': 'r',
        '.sql': 'sql',
        '.tex': 'latex',
        '.bib': 'bibtex',
        '.dockerfile': 'dockerfile',
        '.makefile': 'makefile',
        '.txt': 'plaintext',
        '.log': 'plaintext',
        '.csv': 'plaintext',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'ini',
    }

    # Check by extension first
    if file_ext.lower() in language_map:
        return language_map[file_ext.lower()]

    # Check by filename patterns
    filename_lower = file_name.lower()
    if filename_lower in ['dockerfile', 'makefile', 'rakefile', 'gemfile']:
        return language_map.get(f'.{filename_lower}', 'plaintext')

    # Default to plaintext
    return 'plaintext'


def project_file_view(request, username, slug, file_path):
    """
    View/Edit file contents (GitHub-style /blob/).

    Modes (via query parameter):
    - ?mode=view (default) - View with syntax highlighting
    - ?mode=edit - Edit file content
    - ?mode=raw - Serve raw file content

    Supports:
    - Markdown (.md) - Rendered as HTML
    - Python (.py) - Syntax highlighted
    - YAML (.yaml, .yml) - Syntax highlighted
    - JSON (.json) - Syntax highlighted
    - Text files - Plain text with line numbers
    - Images - Display inline
    """
    from pathlib import Path
    import subprocess
    from datetime import datetime

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
        messages.error(
            request, "You don't have permission to access this file."
        )
        return redirect("user_projects:detail", username=username, slug=slug)

    # Get file path
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    if not project_path or not project_path.exists():
        messages.error(request, "Project directory not found.")
        return redirect("user_projects:detail", username=username, slug=slug)

    full_file_path = project_path / file_path

    # Security check
    try:
        full_file_path = full_file_path.resolve()
        if not str(full_file_path).startswith(str(project_path.resolve())):
            messages.error(request, "Invalid file path.")
            return redirect(
                "user_projects:detail", username=username, slug=slug
            )
    except Exception:
        messages.error(request, "Invalid file path.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Check if file exists and is a file
    if not full_file_path.exists() or not full_file_path.is_file():
        messages.error(request, "File not found.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Get Git commit information for this file
    git_info = {}
    try:
        # Get current branch from session or repository
        from apps.project_app.views.api_views import get_current_branch_from_session
        current_branch = get_current_branch_from_session(request, project)
        git_info['current_branch'] = current_branch

        # Get all branches
        all_branches_result = subprocess.run(
            ['git', 'branch', '-a'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if all_branches_result.returncode == 0:
            branches = []
            for line in all_branches_result.stdout.split('\n'):
                line = line.strip()
                if line and not line.startswith('*'):
                    # Remove 'remotes/origin/' prefix if present
                    branch_name = line.replace('remotes/origin/', '')
                    if branch_name and branch_name not in branches:
                        branches.append(branch_name)
                elif line.startswith('*'):
                    # Current branch
                    branch_name = line[2:].strip()
                    if branch_name not in branches:
                        branches.insert(0, branch_name)
            git_info['branches'] = branches
        else:
            git_info['branches'] = [git_info['current_branch']]

        # Get last commit info for this specific file
        commit_result = subprocess.run(
            ['git', 'log', '-1', '--format=%an|%ae|%ar|%at|%s|%h|%H', '--', file_path],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )

        if commit_result.returncode == 0 and commit_result.stdout.strip():
            parts = commit_result.stdout.strip().split('|', 6)
            git_info.update({
                'author_name': parts[0],
                'author_email': parts[1],
                'time_ago': parts[2],
                'timestamp': parts[3],
                'message': parts[4],
                'short_hash': parts[5],
                'full_hash': parts[6] if len(parts) > 6 else parts[5],
            })
        else:
            # File might not be committed yet
            git_info.update({
                'author_name': '',
                'author_email': '',
                'time_ago': 'Not committed',
                'timestamp': '',
                'message': 'No commits yet',
                'short_hash': '',
                'full_hash': '',
            })
    except Exception as e:
        logger.debug(f"Error getting git info for {file_path}: {e}")
        git_info = {
            'current_branch': 'main',
            'branches': ['main'],
            'author_name': '',
            'author_email': '',
            'time_ago': '',
            'timestamp': '',
            'message': '',
            'short_hash': '',
            'full_hash': '',
        }

    # Determine file type and rendering method
    file_name = full_file_path.name
    file_ext = full_file_path.suffix.lower()
    file_size = full_file_path.stat().st_size

    # Handle raw mode - serve file directly
    if mode == "raw" or mode == "download":
        # Determine content type based on file extension
        content_type = "text/plain; charset=utf-8"
        if file_ext == ".pdf":
            content_type = "application/pdf"
        elif file_ext in [".png"]:
            content_type = "image/png"
        elif file_ext in [".jpg", ".jpeg"]:
            content_type = "image/jpeg"
        elif file_ext in [".gif"]:
            content_type = "image/gif"

        with open(full_file_path, "rb") as f:
            response = HttpResponse(f.read(), content_type=content_type)
            # For download mode, force download instead of inline display
            disposition = "attachment" if mode == "download" else "inline"
            response["Content-Disposition"] = f'{disposition}; filename="{file_name}"'
            return response

    # Handle edit mode - show editor
    if mode == "edit":
        if not (project.owner == request.user):
            messages.error(request, "Only project owner can edit files.")
            return redirect(
                "user_projects:detail", username=username, slug=slug
            )

        if request.method == "POST":
            # Save edited content
            new_content = request.POST.get("content", "")
            try:
                with open(full_file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                messages.success(
                    request, f"File '{file_name}' saved successfully!"
                )
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
            with open(
                full_file_path, "r", encoding="utf-8", errors="ignore"
            ) as f:
                file_content = f.read()
        except Exception as e:
            messages.error(request, f"Error reading file: {e}")
            return redirect(
                "user_projects:detail", username=username, slug=slug
            )

        # Build breadcrumb
        breadcrumbs = [{"name": project.name, "url": f"/{username}/{slug}/"}]
        path_parts = file_path.split("/")
        current_path = ""
        for i, part in enumerate(path_parts):
            current_path += part
            if i < len(path_parts) - 1:
                current_path += "/"
                breadcrumbs.append(
                    {"name": part, "url": f"/{username}/{slug}/{current_path}"}
                )
            else:
                breadcrumbs.append({"name": part, "url": None})

        context = {
            "project": project,
            "file_name": file_name,
            "file_path": file_path,
            "file_content": file_content,
            "breadcrumbs": breadcrumbs,
            "mode": "edit",
        }
        return render(request, "project_app/filer/edit.html", context)

    # Read file content
    try:
        # Check if binary file
        # File size limit: 1MB for display
        MAX_DISPLAY_SIZE = 1024 * 1024  # 1MB
        if file_size > MAX_DISPLAY_SIZE:
            render_type = "binary"
            file_content = f"File too large to display ({file_size:,} bytes). Maximum size: {MAX_DISPLAY_SIZE:,} bytes."
            file_html = None
            language = None
        else:
            # Check if file is binary by extension first
            is_binary = file_ext in [
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".pdf",
                ".zip",
                ".tar",
                ".gz",
                ".ico",
                ".woff",
                ".woff2",
                ".ttf",
                ".eot",
            ]

            if is_binary:
                # For images, show inline
                if file_ext in [".png", ".jpg", ".jpeg", ".gif"]:
                    render_type = "image"
                    file_content = None
                    file_html = None
                    language = None
                # For PDFs, use PDF.js viewer
                elif file_ext == ".pdf":
                    render_type = "pdf"
                    file_content = None
                    file_html = None
                    language = None
                else:
                    render_type = "binary"
                    file_content = f"Binary file ({file_size:,} bytes)"
                    file_html = None
                    language = None
            else:
                # Try to read as text file
                try:
                    with open(
                        full_file_path, "r", encoding="utf-8"
                    ) as f:
                        file_content = f.read()

                    # Detect language for syntax highlighting
                    language = _detect_language(file_ext, file_name)

                    # Render based on file type
                    if file_ext == ".md":
                        import markdown

                        file_html = markdown.markdown(
                            file_content,
                            extensions=[
                                "fenced_code",
                                "tables",
                                "nl2br",
                                "codehilite",
                            ],
                        )
                        render_type = "markdown"
                    elif language:
                        # Use highlight.js on frontend
                        render_type = "code"
                        file_html = None
                    else:
                        file_html = None
                        render_type = "text"

                except UnicodeDecodeError:
                    # File is binary but wasn't caught by extension check
                    render_type = "binary"
                    file_content = f"Binary file ({file_size:,} bytes)"
                    file_html = None
                    language = None

    except Exception as e:
        messages.error(request, f"Error reading file: {e}")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Build breadcrumb
    breadcrumbs = [{"name": project.name, "url": f"/{username}/{slug}/"}]

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

    context = {
        "project": project,
        "file_name": file_name,
        "file_path": file_path,
        "file_size": file_size,
        "file_ext": file_ext,
        "file_content": file_content,
        "file_html": file_html,
        "render_type": render_type,
        "language": language if 'language' in locals() else None,
        "breadcrumbs": breadcrumbs,
        "can_edit": project.owner == request.user,
        "git_info": git_info,
    }

    return render(request, "project_app/filer/view.html", context)


def project_directory(request, username, slug, directory, subpath=None):
    """
    Browse scientific workflow directories within a project.

    URLs like:
    - /username/project-name/scripts/
    - /username/project-name/scripts/analysis/
    - /username/project-name/data/raw/
    """
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access permissions
    has_access = (
        project.owner == request.user
        or project.collaborators.filter(id=request.user.id).exists()
        or project.visibility == "public"
    )

    if not has_access:
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(request.get_full_path())
        else:
            messages.error(
                request, "You don't have permission to access this project."
            )
            return redirect("project_app:detail", username=username, slug=slug)

    # Get the project directory manager
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    if not project_path or not project_path.exists():
        messages.error(request, "Project directory not found.")
        return redirect("project_app:detail", username=username, slug=slug)

    # Construct the full directory path
    if subpath:
        directory_path = project_path / directory / subpath
        breadcrumb_path = f"{directory}/{subpath}"
    else:
        directory_path = project_path / directory
        breadcrumb_path = directory

    # Security check: ensure path is within project directory
    try:
        directory_path = directory_path.resolve()
        if not str(directory_path).startswith(str(project_path.resolve())):
            messages.error(request, "Invalid directory path.")
            return redirect("project_app:detail", username=username, slug=slug)
    except Exception:
        messages.error(request, "Invalid directory path.")
        return redirect("project_app:detail", username=username, slug=slug)

    # Check if directory exists
    if not directory_path.exists():
        messages.error(request, f"Directory '{breadcrumb_path}' not found.")
        return redirect("project_app:detail", username=username, slug=slug)

    # Get directory contents
    contents = []
    try:
        # Helper function to get git commit info for a file/folder
        def get_git_info(path):
            """Get last commit message, author, hash, and time for a file/folder"""
            try:
                import subprocess

                # Get last commit for this file (including hash)
                result = subprocess.run(
                    ['git', 'log', '-1', '--format=%an|%ar|%s|%h', '--', str(path.name)],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0 and result.stdout.strip():
                    author, time_ago, message, commit_hash = result.stdout.strip().split('|', 3)
                    return {
                        'author': author,
                        'time_ago': time_ago,
                        'message': message[:80],  # Truncate to 80 chars
                        'hash': commit_hash
                    }
            except Exception as e:
                logger.debug(f"Error getting git info for {path}: {e}")

            return {
                'author': '',
                'time_ago': '',
                'message': '',
                'hash': ''
            }

        for item in directory_path.iterdir():
            # Show all files and directories including dotfiles
            git_info = get_git_info(item)

            if item.is_file():
                contents.append(
                    {
                        "name": item.name,
                        "type": "file",
                        "size": item.stat().st_size,
                        "modified": item.stat().st_mtime,
                        "path": str(item.relative_to(project_path)),
                        "author": git_info.get('author', ''),
                        "time_ago": git_info.get('time_ago', ''),
                        "message": git_info.get('message', ''),
                        "hash": git_info.get('hash', ''),
                    }
                )
            elif item.is_dir():
                contents.append(
                    {
                        "name": item.name,
                        "type": "directory",
                        "path": str(item.relative_to(project_path)),
                        "author": git_info.get('author', ''),
                        "time_ago": git_info.get('time_ago', ''),
                        "message": git_info.get('message', ''),
                        "hash": git_info.get('hash', ''),
                    }
                )
    except PermissionError:
        messages.error(request, "Permission denied accessing directory.")
        return redirect("project_app:detail", username=username, slug=slug)

    # Sort contents: directories first, then files, both alphabetically
    contents.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))

    # Build breadcrumb navigation
    breadcrumbs = [
        {"name": project.name, "url": project.get_absolute_url()},
        {
            "name": directory,
            "url": f"{project.get_absolute_url()}{directory}/",
        },
    ]

    if subpath:
        path_parts = subpath.split("/")
        current_path = directory
        for part in path_parts:
            current_path += f"/{part}"
            breadcrumbs.append(
                {
                    "name": part,
                    "url": f"{project.get_absolute_url()}{current_path}/",
                }
            )

    context = {
        "project": project,
        "directory": directory,
        "subpath": subpath,
        "breadcrumb_path": breadcrumb_path,
        "contents": contents,
        "breadcrumbs": breadcrumbs,
        "can_edit": project.owner == request.user
        or project.collaborators.filter(id=request.user.id).exists(),
    }

    return render(request, "project_app/filer/directory.html", context)


def user_overview(request, username):
    """User profile overview tab"""
    user = get_object_or_404(User, username=username)
    is_own_profile = request.user.is_authenticated and request.user == user

    # Get recent activity
    recent_projects = Project.objects.filter(owner=user)
    if not is_own_profile:
        recent_projects = recent_projects.filter(visibility="public")
    recent_projects = recent_projects.order_by("-updated_at")[:6]

    # Get social stats
    from apps.social_app.models import UserFollow, RepositoryStar

    followers_count = UserFollow.get_followers_count(user)
    following_count = UserFollow.get_following_count(user)
    is_following = (
        UserFollow.is_following(request.user, user)
        if request.user.is_authenticated
        else False
    )

    context = {
        "profile_user": user,
        "is_own_profile": is_own_profile,
        "recent_projects": recent_projects,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "active_tab": "overview",
    }
    return render(request, "project_app/users/overview.html", context)


def user_projects_board(request, username):
    """User project boards tab (placeholder for future implementation)"""
    user = get_object_or_404(User, username=username)
    is_own_profile = request.user.is_authenticated and request.user == user

    # Get social stats
    from apps.social_app.models import UserFollow

    followers_count = UserFollow.get_followers_count(user)
    following_count = UserFollow.get_following_count(user)
    is_following = (
        UserFollow.is_following(request.user, user)
        if request.user.is_authenticated
        else False
    )

    context = {
        "profile_user": user,
        "is_own_profile": is_own_profile,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "active_tab": "projects",
    }
    return render(request, "project_app/users/board.html", context)


def user_stars(request, username):
    """User starred repositories tab"""
    user = get_object_or_404(User, username=username)
    is_own_profile = request.user.is_authenticated and request.user == user

    # Get starred repositories
    from apps.social_app.models import RepositoryStar, UserFollow

    starred_repos = (
        RepositoryStar.objects.filter(user=user)
        .select_related("repository")
        .order_by("-created_at")
    )

    # Pagination
    paginator = Paginator(starred_repos, 12)
    page_number = request.GET.get("page")
    stars = paginator.get_page(page_number)

    # Get social stats
    followers_count = UserFollow.get_followers_count(user)
    following_count = UserFollow.get_following_count(user)
    is_following = (
        UserFollow.is_following(request.user, user)
        if request.user.is_authenticated
        else False
    )

    context = {
        "profile_user": user,
        "is_own_profile": is_own_profile,
        "stars": stars,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "active_tab": "stars",
    }
    return render(request, "project_app/users/stars.html", context)


def file_history_view(request, username, slug, branch, file_path):
    """
    Show commit history for a specific file (GitHub-style /commits/<branch>/<path>).

    Displays all commits that modified this file with:
    - Commit message, author, date, hash
    - File-specific stats (+/- lines)
    - Pagination (30 commits per page)
    - Filter by author or date range

    URLs:
    - /<username>/<project>/commits/<branch>/<file-path>
    """
    from pathlib import Path
    import subprocess
    from datetime import datetime

    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access
    has_access = (
        project.owner == request.user
        or project.collaborators.filter(id=request.user.id).exists()
        or getattr(project, "visibility", None) == "public"
    )

    if not has_access:
        messages.error(
            request, "You don't have permission to access this file."
        )
        return redirect("user_projects:detail", username=username, slug=slug)

    # Get project path
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    if not project_path or not project_path.exists():
        messages.error(request, "Project directory not found.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Build breadcrumb
    breadcrumbs = [{"name": project.name, "url": f"/{username}/{slug}/"}]

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
            breadcrumbs.append({"name": part, "url": f"/{username}/{slug}/blob/{file_path}"})

    # Get filter parameters
    author_filter = request.GET.get("author", "").strip()
    page_number = request.GET.get("page", 1)

    try:
        page_number = int(page_number)
    except (ValueError, TypeError):
        page_number = 1

    # Get file history using git log --follow
    commits = []
    try:
        # Build git log command
        # Format: hash|author_name|author_email|timestamp|relative_time|subject
        git_cmd = [
            'git', 'log', '--follow',
            '--format=%H|%an|%ae|%at|%ar|%s',
            '--', file_path
        ]

        # Add author filter if specified
        if author_filter:
            git_cmd.insert(3, f'--author={author_filter}')

        result = subprocess.run(
            git_cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = line.split('|', 5)
                if len(parts) < 6:
                    continue

                commit_hash, author_name, author_email, timestamp, relative_time, subject = parts

                # Get file-specific stats for this commit
                stats_result = subprocess.run(
                    ['git', 'show', '--numstat', '--format=', commit_hash, '--', file_path],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                additions = 0
                deletions = 0
                if stats_result.returncode == 0 and stats_result.stdout.strip():
                    stat_line = stats_result.stdout.strip().split('\n')[0]
                    stat_parts = stat_line.split('\t')
                    if len(stat_parts) >= 2:
                        try:
                            additions = int(stat_parts[0]) if stat_parts[0] != '-' else 0
                            deletions = int(stat_parts[1]) if stat_parts[1] != '-' else 0
                        except ValueError:
                            pass

                commits.append({
                    'hash': commit_hash,
                    'short_hash': commit_hash[:7],
                    'author_name': author_name,
                    'author_email': author_email,
                    'timestamp': int(timestamp),
                    'relative_time': relative_time,
                    'subject': subject,
                    'additions': additions,
                    'deletions': deletions,
                })

    except subprocess.TimeoutExpired:
        logger.error(f"Git log timeout for {file_path} in {project.slug}")
        messages.error(request, "Timeout while fetching file history.")
    except Exception as e:
        logger.error(f"Error getting file history for {file_path}: {e}")
        messages.error(request, f"Error fetching file history: {str(e)}")

    # Pagination
    paginator = Paginator(commits, 30)
    commits_page = paginator.get_page(page_number)

    # Get unique authors for filter dropdown
    unique_authors = sorted(set(c['author_name'] for c in commits))

    context = {
        "project": project,
        "file_path": file_path,
        "file_name": Path(file_path).name,
        "branch": branch,
        "breadcrumbs": breadcrumbs,
        "commits": commits_page,
        "unique_authors": unique_authors,
        "author_filter": author_filter,
        "total_commits": len(commits),
    }

    return render(request, "project_app/filer/history.html", context)

# EOF


def commit_detail(request, username, slug, commit_hash):
    """
    GitHub-style commit detail page showing diff and metadata.

    URL: /<username>/<slug>/commit/<commit_hash>/

    Shows:
    - Commit metadata (author, date, message)
    - Changed files with stats
    - Unified diffs for each file
    """
    import subprocess
    from pathlib import Path
    from datetime import datetime

    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access permissions
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

    # Get project path
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    if not project_path or not project_path.exists():
        messages.error(request, "Project directory not found.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Fetch commit information using git
    commit_info = {}
    changed_files = []

    try:
        # Get commit metadata: author, email, date, message
        result = subprocess.run(
            ['git', 'show', '--no-patch', '--format=%an|%ae|%aI|%s|%b|%P|%H', commit_hash],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            messages.error(request, f"Commit {commit_hash} not found.")
            return redirect("user_projects:detail", username=username, slug=slug)

        parts = result.stdout.strip().split('|', 6)
        commit_info = {
            'author_name': parts[0],
            'author_email': parts[1],
            'date': datetime.fromisoformat(parts[2].replace('Z', '+00:00')),
            'subject': parts[3],  # First line of commit message
            'body': parts[4] if len(parts) > 4 else '',  # Full commit message body
            'parent_hash': parts[5].split()[0] if len(parts) > 5 and parts[5] else None,  # First parent
            'full_hash': parts[6] if len(parts) > 6 else commit_hash,
            'short_hash': commit_hash[:7],
        }

        # Get list of changed files with stats
        stats_result = subprocess.run(
            ['git', 'diff-tree', '--no-commit-id', '--numstat', '-r', commit_hash],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        if stats_result.returncode == 0:
            for line in stats_result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('\t')
                if len(parts) >= 3:
                    added = parts[0]
                    deleted = parts[1]
                    filepath = parts[2]

                    # Get the actual diff for this file
                    diff_result = subprocess.run(
                        ['git', 'show', '--format=', commit_hash, '--', filepath],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    # Parse unified diff to get line-by-line changes
                    diff_lines = []
                    if diff_result.returncode == 0 and diff_result.stdout:
                        for diff_line in diff_result.stdout.split('\n'):
                            line_type = 'context'
                            if diff_line.startswith('+++') or diff_line.startswith('---'):
                                line_type = 'header'
                            elif diff_line.startswith('@@'):
                                line_type = 'hunk'
                            elif diff_line.startswith('+'):
                                line_type = 'addition'
                            elif diff_line.startswith('-'):
                                line_type = 'deletion'

                            diff_lines.append({
                                'content': diff_line,
                                'type': line_type
                            })

                    # Determine file extension for syntax highlighting hint
                    file_ext = Path(filepath).suffix.lower()

                    changed_files.append({
                        'path': filepath,
                        'additions': added if added != '-' else 0,
                        'deletions': deleted if deleted != '-' else 0,
                        'diff': diff_lines,
                        'extension': file_ext,
                    })

        # Get current branch
        branch_result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if branch_result.returncode == 0:
            commit_info['current_branch'] = branch_result.stdout.strip() or 'main'
        else:
            commit_info['current_branch'] = 'main'

    except subprocess.TimeoutExpired:
        messages.error(request, "Git command timed out.")
        return redirect("user_projects:detail", username=username, slug=slug)
    except Exception as e:
        logger.error(f"Error fetching commit details: {e}")
        messages.error(request, f"Error fetching commit details: {e}")
        return redirect("user_projects:detail", username=username, slug=slug)

    context = {
        'project': project,
        'commit': commit_info,
        'changed_files': changed_files,
        'total_additions': sum(int(f['additions']) if isinstance(f['additions'], (int, str)) and str(f['additions']).isdigit() else 0 for f in changed_files),
        'total_deletions': sum(int(f['deletions']) if isinstance(f['deletions'], (int, str)) and str(f['deletions']).isdigit() else 0 for f in changed_files),
    }

    return render(request, 'project_app/commits/detail.html', context)
