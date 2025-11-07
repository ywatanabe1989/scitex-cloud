#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Create Views

Handle project creation with various initialization options.
"""
from __future__ import annotations
import logging
from pathlib import Path

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django.conf import settings

from ...models import Project

logger = logging.getLogger(__name__)


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
        init_scitex_scholar = request.POST.get("init_scitex_scholar") == "true"

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
            return render(request, "project_app/projects/create.html", context)

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
            return render(request, "project_app/projects/create.html", context)

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
            return render(request, "project_app/projects/create.html", context)

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
                    return render(request, "project_app/projects/create.html", context)
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
                project_dir = Path(settings.BASE_DIR) / 'data' / 'users' / project.owner.username / project.slug

                if not project_dir.exists() or not (project_dir / '.git').exists():
                    # Clone to local directory if not done by signal
                    success, result = project.clone_gitea_to_local()
                else:
                    # Already cloned by signal
                    success = True
                    result = str(project_dir)

                if not success:
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
                        request, "project_app/projects/create.html", context
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
                    request, "project_app/projects/create.html", context
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
                    request, "project_app/projects/create.html", context
                )

            try:
                # Clone from Git repository directly (no Gitea needed)
                success, error_msg = manager.clone_from_git(project, git_url)

                if not success:
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
            if not success:
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
            if not success:
                messages.error(
                    request, f"Project created but cloning failed: {error_msg}"
                )

        else:
            # Create empty project
            success, path = manager.create_project_directory(
                project, use_template=False
            )
            if not success:
                messages.error(request, f"Failed to create project directory")
                project.delete()
                return redirect("project_app:list")

        # Initialize SciTeX templates if requested
        writer_initialized = False
        scholar_initialized = False

        if init_scitex_writer:
            success, writer_path = manager.initialize_scitex_writer_template(project)
            if success:
                writer_initialized = True
            else:
                messages.warning(
                    request,
                    f'SciTeX Writer template initialization failed'
                )

        if init_scitex_scholar:
            # Initialize Scholar structure
            from apps.project_app.services.bibliography_manager import ensure_bibliography_structure

            try:
                project_path = manager.get_project_root_path(project)
                if project_path:
                    ensure_bibliography_structure(project_path)
                    scholar_initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize Scholar structure: {e}")
                messages.warning(
                    request,
                    f'SciTeX Scholar template initialization failed'
                )

        # Show consolidated success message
        templates_msg = []
        if writer_initialized:
            templates_msg.append("Writer")
        if scholar_initialized:
            templates_msg.append("Scholar")

        if templates_msg:
            templates_str = " and ".join(templates_msg)
            messages.success(
                request,
                f'Project "{project.name}" created successfully with SciTeX {templates_str} initialized!'
            )
        else:
            messages.success(
                request,
                f'Project "{project.name}" created successfully!'
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
    return render(request, "project_app/projects/create.html", context)


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


# EOF
