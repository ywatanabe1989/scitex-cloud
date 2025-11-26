#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-04 (auto-generated)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/project_app/views/api_views.py
# ----------------------------------------
"""
REST API Views for Project App

This module contains all REST API endpoints for the project application,
including file tree, name availability checking, project CRUD operations,
and repository health management.
"""

from __future__ import annotations
import json
import logging

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from ..models import Project

logger = logging.getLogger(__name__)


# ============================================================================
# File Tree API
# ============================================================================


@require_http_methods(["GET"])
def api_file_tree(request, username, slug):
    """API endpoint to get project file tree for sidebar navigation"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access (allow public access for public projects)
    if request.user.is_authenticated:
        has_access = (
            project.owner == request.user
            or project.collaborators.filter(id=request.user.id).exists()
            or project.visibility == "public"
        )
    else:
        # For anonymous users, check if this is their allocated visitor project
        visitor_project_id = request.session.get("visitor_project_id")
        has_access = (
            project.visibility == "public"
            or (visitor_project_id and project.id == visitor_project_id)
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
        return JsonResponse({"success": False, "error": "Project directory not found"})

    def build_tree(path, max_depth=5, current_depth=0):
        """Build file tree recursively (deeper for full navigation)"""
        items = []
        try:
            for item in sorted(
                path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())
            ):
                # Skip hidden files except .git directory, .gitignore, and .gitkeep
                if item.name.startswith(".") and item.name not in [
                    ".git",
                    ".gitignore",
                    ".gitkeep",
                ]:
                    continue
                # Skip common non-essential directories
                if item.name in [
                    "__pycache__",
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


# ============================================================================
# Name Availability API
# ============================================================================


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
        return JsonResponse({"available": False, "message": "Project name is required"})

    # Validate name using scitex.project validator
    try:
        from scitex.project import validate_name

        is_valid, error = validate_name(name)
        if not is_valid:
            return JsonResponse({"available": False, "message": error})
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
                owner=request.user.username, repo=slug
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

    return JsonResponse({"available": True, "message": f'"{name}" is available'})


# ============================================================================
# Project CRUD APIs
# ============================================================================


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
            return JsonResponse({"success": False, "error": "Project name is required"})

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


# ============================================================================
# Directory Concatenation API
# ============================================================================


@login_required
def api_concatenate_directory(request, username, slug, directory_path=""):
    """
    API endpoint to concatenate all files in a directory (like view_repo.sh).
    Returns markdown-formatted content with tree + file contents.
    """
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
        return JsonResponse({"success": False, "error": "Project directory not found"})

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
        except Exception:
            continue

    concatenated_content = "\n".join(output)

    return JsonResponse(
        {
            "success": True,
            "content": concatenated_content,
            "file_count": len([l for l in output if l.startswith("###")]),
        }
    )


# ============================================================================
# Repository Health Management APIs
# ============================================================================


@login_required
def api_repository_health(request, username):
    """
    API endpoint to check repository health for a user.

    GET: Returns list of all repository health issues and statistics
    """
    if request.method != "GET":
        return JsonResponse(
            {"success": False, "error": "Method not allowed"}, status=405
        )

    # Only allow users to check their own repository health
    user = get_object_or_404(User, username=username)
    if user != request.user and not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Access denied"}, status=403)

    try:
        from apps.project_app.services.repository_health_service import (
            RepositoryHealthChecker,
        )

        checker = RepositoryHealthChecker(user)
        issues, stats = checker.check_all_repositories()

        return JsonResponse(
            {
                "success": True,
                "stats": stats,
                "issues": [issue.to_dict() for issue in issues],
            }
        )

    except Exception as e:
        logger.error(f"Error checking repository health: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def api_repository_cleanup(request, username):
    """
    API endpoint to cleanup orphaned Gitea repositories.

    POST: Delete an orphaned repository (requires confirmation)
    """
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Method not allowed"}, status=405
        )

    # Only allow users to manage their own repositories
    user = get_object_or_404(User, username=username)
    if user != request.user and not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Access denied"}, status=403)

    try:
        data = json.loads(request.body)
        gitea_name = data.get("gitea_name", "").strip()

        if not gitea_name:
            return JsonResponse(
                {"success": False, "error": "Repository name required"}, status=400
            )

        from apps.project_app.services.repository_health_service import (
            RepositoryHealthChecker,
        )

        checker = RepositoryHealthChecker(user)
        success, message = checker.delete_orphaned_repository(gitea_name)

        return JsonResponse(
            {
                "success": success,
                "message": message,
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error during repository cleanup: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def api_repository_sync(request, username):
    """
    API endpoint to sync a repository.

    POST: Sync project with Gitea (re-clone if needed)
    """
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Method not allowed"}, status=405
        )

    # Only allow users to manage their own repositories
    user = get_object_or_404(User, username=username)
    if user != request.user and not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Access denied"}, status=403)

    try:
        data = json.loads(request.body)
        project_slug = data.get("project_slug", "").strip()

        if not project_slug:
            return JsonResponse(
                {"success": False, "error": "Project slug required"}, status=400
            )

        from apps.project_app.services.repository_health_service import (
            RepositoryHealthChecker,
        )

        checker = RepositoryHealthChecker(user)
        success, message = checker.sync_repository(project_slug)

        return JsonResponse(
            {
                "success": success,
                "message": message,
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error during repository sync: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def api_repository_restore(request, username):
    """
    API endpoint to restore an orphaned Gitea repository.

    Recovers a project by creating a Django project linked to an orphaned
    Gitea repository. This restores the full 1:1:1 mapping.

    POST: Restore orphaned repository as a new project
    """
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Method not allowed"}, status=405
        )

    # Only allow users to manage their own repositories
    user = get_object_or_404(User, username=username)
    if user != request.user and not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Access denied"}, status=403)

    try:
        data = json.loads(request.body)
        gitea_name = data.get("gitea_name", "").strip()
        project_name = data.get("project_name", "").strip()

        if not gitea_name:
            return JsonResponse(
                {"success": False, "error": "Repository name required"}, status=400
            )

        # If no project name provided, use the gitea_name
        if not project_name:
            project_name = gitea_name

        from apps.project_app.services.repository_health_service import (
            RepositoryHealthChecker,
        )

        checker = RepositoryHealthChecker(user)
        success, message, project_id = checker.restore_orphaned_repository(
            gitea_name, project_name
        )

        return JsonResponse(
            {
                "success": success,
                "message": message,
                "project_id": project_id,  # Return project ID for redirect
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error during repository restore: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# EOF
