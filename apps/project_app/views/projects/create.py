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
        init_scitex = request.POST.get("init_scitex") == "true"

        # Project type (local or remote)
        project_type = request.POST.get("project_type", "local")

        # Remote project fields
        remote_credential_id = request.POST.get("remote_credential_id")
        remote_path = request.POST.get("remote_path", "").strip()

        # Handle remote project creation separately
        if project_type == "remote":
            return _create_remote_project(
                request, name, description, remote_credential_id, remote_path
            )

        # Initialize directory manager for all init types (local projects only)
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
                    owner=request.user.username, repo=unique_slug
                )
                if existing_repo:
                    # Gitea repo exists - this is a critical conflict
                    error_msg = (
                        f'Repository "{unique_slug}" already exists in Gitea. '
                        f"This is likely an orphaned repository from a previous project. "
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
                "Could not verify repository name with Gitea. Proceeding with caution.",
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
                # Path must match signal handler: /data/users/{username}/proj/{slug}/
                project_dir = (
                    Path(settings.BASE_DIR)
                    / "data"
                    / "users"
                    / project.owner.username
                    / "proj"
                    / project.slug
                )

                if not project_dir.exists() or not (project_dir / ".git").exists():
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
                    return render(request, "project_app/projects/create.html", context)

            except Exception as e:
                error_msg = str(e)
                if "already exists" in error_msg.lower() or "409" in error_msg:
                    messages.error(
                        request,
                        f'Repository "{name}" already exists in Gitea. Please choose a different name.',
                    )
                else:
                    messages.error(request, f"Failed to create repository: {error_msg}")
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
                return render(request, "project_app/projects/create.html", context)

        elif init_type == "github":
            # Import from GitHub/GitLab - Use direct Git clone instead of Gitea
            if not git_url:
                messages.error(request, "Repository URL is required for importing")
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
                return render(request, "project_app/projects/create.html", context)

            try:
                # Clone from Git repository directly (no Gitea needed)
                success, error_msg = manager.clone_from_git(project, git_url)

                if not success:
                    messages.error(request, f"Failed to clone repository: {error_msg}")
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
                messages.error(request, f"Failed to create project with template")
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

        # Initialize SciTeX ecosystem if requested
        if init_scitex:
            try:
                import shutil
                from pathlib import Path as PathLib

                project_path = manager.get_project_root_path(project)
                if project_path:
                    # Use master template copy (fast, offline, reliable)
                    # Same approach as visitor pool initialization
                    template_master = PathLib(getattr(
                        settings,
                        "VISITOR_TEMPLATE_PATH",
                        "/app/templates/research-master"
                    ))

                    if not template_master.exists():
                        logger.warning(f"[ProjectCreate] Master template not found at {template_master}")
                        messages.warning(
                            request,
                            f'Project "{project.name}" created but template not found. Creating basic directory structure.'
                        )
                        success = False
                    else:
                        logger.info(f"[ProjectCreate] Copying template from {template_master} to {project_path}")

                        # Copy entire template to project directory
                        # This will overwrite existing files if any
                        try:
                            # Remove existing contents if any
                            for item in project_path.iterdir():
                                if item.is_dir() and item.name != '.git':
                                    shutil.rmtree(item)
                                elif item.is_file():
                                    item.unlink()

                            # Copy template contents (not the directory itself)
                            for item in template_master.iterdir():
                                if item.name == '.git':
                                    continue  # Skip .git from template

                                dest = project_path / item.name
                                if item.is_dir():
                                    shutil.copytree(item, dest, symlinks=True)
                                else:
                                    shutil.copy2(item, dest)

                            success = True
                            messages.success(
                                request,
                                f'Project "{project.name}" created successfully with SciTeX ecosystem initialized!',
                            )
                        except Exception as copy_err:
                            logger.error(f"[ProjectCreate] Failed to copy template: {copy_err}")
                            success = False
                            messages.warning(
                                request,
                                f'Project "{project.name}" created but template copy failed: {str(copy_err)}'
                            )
                else:
                    messages.warning(
                        request,
                        f'Project "{project.name}" created but could not find project directory for SciTeX initialization.'
                    )
            except Exception as e:
                logger.error(f"Failed to initialize SciTeX ecosystem: {e}")
                messages.warning(
                    request,
                    f'Project "{project.name}" created but SciTeX initialization failed: {str(e)}'
                )
        else:
            messages.success(request, f'Project "{project.name}" created successfully!')

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

    # Get user's remote credentials for remote project option
    from apps.project_app.models import RemoteCredential

    remote_credentials = RemoteCredential.objects.filter(
        user=request.user, is_active=True
    ).order_by("name")

    context = {
        "available_templates": available_templates,
        "remote_credentials": remote_credentials,
    }
    return render(request, "project_app/projects/create.html", context)


@login_required
def project_create_from_template(request, username, slug):
    """Create template structure for an existing empty project"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Only project owner can create template
    if project.owner != request.user:
        messages.error(request, "Only project owner can create template structure.")
        return redirect("user_projects:detail", username=username, slug=slug)

    if request.method == "POST":
        # Create template structure
        from apps.project_app.services.project_filesystem import (
            get_project_filesystem_manager,
        )

        manager = get_project_filesystem_manager(project.owner)

        try:
            success, path = manager.create_project_from_template(project)

            if success:
                messages.success(
                    request,
                    f'Template structure created successfully for "{project.name}"!',
                )
            else:
                messages.error(request, "Failed to create template structure.")
        except Exception as e:
            messages.error(request, f"Failed to create template structure: {str(e)}")

        return redirect("user_projects:detail", username=username, slug=slug)

    # GET request - show confirmation page or redirect
    return redirect("user_projects:detail", username=username, slug=slug)


def _create_remote_project(request, name, description, remote_credential_id, remote_path):
    """
    Create a remote project (SSHFS mount, no Git).

    Args:
        request: HTTP request
        name: Project name
        description: Project description
        remote_credential_id: ID of RemoteCredential to use
        remote_path: Absolute path on remote system

    Returns:
        HTTP response (redirect or render)
    """
    from apps.project_app.models import RemoteCredential, RemoteProjectConfig

    # Validate inputs
    if not all([name, remote_credential_id, remote_path]):
        messages.error(request, "All fields are required for remote projects")
        return redirect("project_app:create")

    # Get remote credential
    try:
        credential = RemoteCredential.objects.get(
            id=remote_credential_id, user=request.user
        )
    except RemoteCredential.DoesNotExist:
        messages.error(request, "Invalid remote credential selected")
        return redirect("project_app:create")

    # Validate repository name
    is_valid, error_message = Project.validate_repository_name(name)
    if not is_valid:
        messages.error(request, error_message)
        return redirect("project_app:create")

    # Check if name already exists for this user
    if Project.objects.filter(name=name, owner=request.user).exists():
        messages.error(
            request,
            f'You already have a project named "{name}". Please choose a different name.',
        )
        return redirect("project_app:create")

    # Generate slug
    slug = Project.generate_unique_slug(name, owner=request.user)

    # Test SSH connection before creating project
    from apps.project_app.services.remote_project_manager import RemoteProjectManager
    import subprocess

    logger.info(f"Testing SSH connection for remote project: {name}")

    ssh_key_path = credential.private_key_path
    cmd = [
        "ssh",
        "-p",
        str(credential.ssh_port),
        "-i",
        ssh_key_path,
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        "ConnectTimeout=10",
        f"{credential.ssh_username}@{credential.ssh_host}",
        f"test -d {remote_path} && echo 'OK' || echo 'NOT_FOUND'",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

        if result.returncode != 0:
            messages.error(
                request,
                mark_safe(
                    f"SSH connection failed: {result.stderr}<br>"
                    f"Please verify your credentials and try again."
                ),
            )
            return redirect("project_app:create")

        if "NOT_FOUND" in result.stdout:
            messages.warning(
                request,
                mark_safe(
                    f"⚠️  Remote directory not found: {remote_path}<br>"
                    f"The directory will be created when you access the project."
                ),
            )

    except subprocess.TimeoutExpired:
        messages.error(request, "SSH connection timeout. Please check your network and try again.")
        return redirect("project_app:create")
    except Exception as e:
        messages.error(request, f"Connection test failed: {str(e)}")
        return redirect("project_app:create")

    # Create remote project
    try:
        project = Project.objects.create(
            name=name,
            slug=slug,
            description=description,
            owner=request.user,
            project_type="remote",  # ✅ Remote project
            visibility="private",  # Remote projects default to private
        )

        # Create remote configuration
        remote_config = RemoteProjectConfig.objects.create(
            project=project,
            ssh_host=credential.ssh_host,
            ssh_port=credential.ssh_port,
            ssh_username=credential.ssh_username,
            remote_credential=credential,
            remote_path=remote_path,
            is_mounted=False,  # Not mounted yet
        )

        project.remote_config = remote_config
        project.save()

        # Update credential last used timestamp
        from django.utils import timezone

        credential.last_used_at = timezone.now()
        credential.save()

        logger.info(
            f"✅ Remote project created: {request.user.username}/{slug} "
            f"→ {credential.ssh_username}@{credential.ssh_host}:{remote_path}"
        )

        messages.success(
            request,
            mark_safe(
                f'✅ Remote project "{name}" created successfully!<br>'
                f"Files will be accessed from: {credential.ssh_username}@{credential.ssh_host}:{remote_path}"
            ),
        )

        return redirect("user_projects:detail", username=request.user.username, slug=slug)

    except Exception as e:
        logger.error(f"Failed to create remote project: {e}")
        messages.error(request, f"Failed to create remote project: {str(e)}")
        return redirect("project_app:create")


# EOF
