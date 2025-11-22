#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-04 (auto-generated)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/project_app/views/repository/api.py
# ----------------------------------------
"""
Repository-related REST API endpoints

This module contains API endpoints for:
- File tree navigation
- Directory concatenation
- Repository health management
- Repository cleanup, sync, and restore
"""

from __future__ import annotations
import json
import logging

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from ...models import Project

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
        has_access = project.visibility == "public"

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
                # Skip hidden files except .git directory and .gitignore
                if item.name.startswith(".") and item.name not in [
                    ".git",
                    ".gitignore",
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

                # Detect symlinks
                is_symlink = item.is_symlink()
                symlink_target = None
                if is_symlink:
                    try:
                        # Get symlink target relative to the symlink location
                        target = item.readlink()
                        symlink_target = str(target)
                    except (OSError, ValueError):
                        symlink_target = None

                item_data = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "path": str(rel_path),
                    "is_symlink": is_symlink,
                }

                # Add symlink target if available
                if symlink_target:
                    item_data["symlink_target"] = symlink_target

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


# ============================================================================
# Git Status API
# ============================================================================


@require_http_methods(["GET"])
def api_git_status(request, username, slug):
    """
    API endpoint to get git status for all files in the project.
    Returns status of modified, added, deleted, and untracked files.
    """
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access
    if request.user.is_authenticated:
        has_access = (
            project.owner == request.user
            or project.collaborators.filter(id=request.user.id).exists()
            or project.visibility == "public"
        )
    else:
        has_access = project.visibility == "public"

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

    try:
        import subprocess
        from pathlib import Path

        # Get current branch
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        current_branch = (
            branch_result.stdout.strip()
            if branch_result.returncode == 0
            else "unknown"
        )

        # Get ahead/behind count
        ahead = 0
        behind = 0
        try:
            ahead_behind_result = subprocess.run(
                [
                    "git",
                    "rev-list",
                    "--left-right",
                    "--count",
                    f"HEAD...origin/{current_branch}",
                ],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if ahead_behind_result.returncode == 0:
                parts = ahead_behind_result.stdout.strip().split()
                if len(parts) == 2:
                    ahead = int(parts[0])
                    behind = int(parts[1])
        except (subprocess.TimeoutExpired, ValueError):
            pass

        # Get git status (porcelain format for easy parsing)
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Failed to get git status",
                    "branch": current_branch,
                }
            )

        # Parse git status output
        files = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            # Git status porcelain format:
            # XY filename
            # X = index status, Y = working tree status
            status_code = line[:2]
            filepath = line[3:].strip()

            # Remove quotes if present
            if filepath.startswith('"') and filepath.endswith('"'):
                filepath = filepath[1:-1]

            # Determine status
            index_status = status_code[0]
            worktree_status = status_code[1]

            status = "modified"
            staged = False

            if index_status == "?" or worktree_status == "?":
                status = "untracked"
            elif index_status == "A" or worktree_status == "A":
                status = "added"
                staged = index_status == "A"
            elif index_status == "D" or worktree_status == "D":
                status = "deleted"
                staged = index_status == "D"
            elif index_status == "R":
                status = "renamed"
                staged = True
            elif index_status == "C":
                status = "copied"
                staged = True
            elif index_status == "M" or worktree_status == "M":
                status = "modified"
                staged = index_status == "M"

            # Get number of changes for this file (if it's a text file)
            changes = 0
            try:
                diff_result = subprocess.run(
                    ["git", "diff", "--numstat", "--", filepath],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if diff_result.returncode == 0 and diff_result.stdout.strip():
                    parts = diff_result.stdout.strip().split("\t")
                    if len(parts) >= 2:
                        try:
                            additions = int(parts[0]) if parts[0] != "-" else 0
                            deletions = int(parts[1]) if parts[1] != "-" else 0
                            changes = additions + deletions
                        except ValueError:
                            pass
            except subprocess.TimeoutExpired:
                pass

            files.append(
                {"path": filepath, "status": status, "staged": staged, "changes": changes}
            )

        return JsonResponse(
            {
                "success": True,
                "files": files,
                "branch": current_branch,
                "ahead": ahead,
                "behind": behind,
            }
        )

    except subprocess.TimeoutExpired:
        return JsonResponse({"success": False, "error": "Git command timed out"})
    except Exception as e:
        logger.error(f"Error getting git status: {e}")
        return JsonResponse({"success": False, "error": str(e)})


# EOF
