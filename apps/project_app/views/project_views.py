#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-04"
# File: /home/ywatanabe/proj/scitex-cloud/apps/project_app/views/project_views.py
# ----------------------------------------
"""
Project Views Module

This module contains view functions related to project management:
- Project listing and user profiles
- Project detail and browsing
- Project creation, editing, and deletion
- User overview and project boards
"""
from __future__ import annotations
import os
import json
import logging

# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.utils.text import slugify
from django.utils.safestring import mark_safe

# Local imports
from ..models import Project, ProjectMembership
from apps.organizations_app.models import Organization, ResearchGroup
from ..decorators import project_required, project_access_required

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
    return render(request, "project_app/user_projects.html", context)


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

    return render(request, "project_app/user_bio.html", context)


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
        from .api_views import api_concatenate_directory
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

    # Get branches for branch selector
    branches = []
    current_branch = project.current_branch or 'develop'
    if project_path and project_path.exists():
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'branch', '-a'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line:
                        # Remove * prefix and remotes/origin/ prefix
                        branch = line.replace('*', '').strip()
                        branch = branch.replace('remotes/origin/', '')
                        if branch and branch not in branches:
                            branches.append(branch)
                        # Check if this is the current branch
                        if line.startswith('*'):
                            current_branch = branch
        except Exception as e:
            logger.debug(f"Error getting branches: {e}")

    if not branches:
        branches = [current_branch]

    # Get social interaction counts
    from apps.project_app.models import ProjectWatch, ProjectStar, ProjectFork
    watch_count = ProjectWatch.objects.filter(project=project).count()
    star_count = ProjectStar.objects.filter(project=project).count()
    fork_count = ProjectFork.objects.filter(original_project=project).count()

    # Check if current user has watched/starred the project
    is_watching = False
    is_starred = False
    if request.user.is_authenticated:
        is_watching = ProjectWatch.objects.filter(user=request.user, project=project).exists()
        is_starred = ProjectStar.objects.filter(user=request.user, project=project).exists()

    context = {
        "project": project,
        "user": request.user,
        "directories": dirs,
        "files": files,
        "readme_content": readme_content,
        "readme_html": readme_html,
        "mode": mode,
        "branches": branches,
        "current_branch": current_branch,
        "watch_count": watch_count,
        "star_count": star_count,
        "fork_count": fork_count,
        "is_watching": is_watching,
        "is_starred": is_starred,
    }
    return render(request, "project_app/browse.html", context)


@login_required
def project_create(request):
    """Create new project"""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        init_type = request.POST.get("init_type", "empty")
        template_type = request.POST.get("template_type", "research")
        git_url = request.POST.get("git_url", "").strip()
        init_scitex_writer = request.POST.get("init_scitex_writer") == "true"

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
        base_slug = slugify(name)
        unique_slug = Project.generate_unique_slug(base_slug, owner=request.user)

        # Check if repository exists in Gitea (enforce 1:1 mapping)
        # This is a final safeguard before creation
        try:
            from apps.gitea_app.api_client import GiteaClient, GiteaAPIError
            client = GiteaClient()

            try:
                existing_repo = client.get_repository(
                    owner=request.user.username,
                    repo=unique_slug
                )
                if existing_repo:
                    # Gitea repo exists - this is a critical conflict
                    error_msg = (
                        f'Repository "{unique_slug}" already exists in Gitea. '
                        f'This is likely an orphaned repository from a previous project. '
                        f'Please visit your <a href="/{request.user.username}/settings/repositories/">repository maintenance page</a> to clean it up.'
                    )
                    messages.error(request, mark_safe(error_msg))
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
                    }
                    return render(request, "project_app/create.html", context)
            except GiteaAPIError:
                # Repository doesn't exist in Gitea - this is good, proceed with creation
                pass
        except Exception as e:
            # Log warning but don't fail - Gitea might be temporarily unavailable
            logger.warning(f"Could not verify Gitea repository availability: {e}")
            messages.warning(
                request,
                "Could not verify repository name with Gitea. Proceeding with caution."
            )

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

        # Initialize SciTeX Writer template if requested
        if init_scitex_writer:
            success, writer_path = manager.initialize_scitex_writer_template(project)
            if success:
                messages.success(
                    request,
                    f'SciTeX Writer template initialized at scitex/writer/'
                )
            else:
                messages.warning(
                    request,
                    f'Project created but SciTeX Writer template initialization failed'
                )

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
    return render(request, "project_app/user_overview.html", context)


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
    return render(request, "project_app/user_board.html", context)


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
    return render(request, "project_app/user_stars.html", context)


# EOF
