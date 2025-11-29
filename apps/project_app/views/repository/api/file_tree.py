#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-29 (auto-generated)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/project_app/views/repository/api/file_tree.py
# ----------------------------------------
"""
File Tree Navigation API

This module contains API endpoints for navigating project file structure.
"""

from __future__ import annotations
import logging

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from ....models import Project
from .permissions import check_project_read_access

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def api_file_tree(request, username, slug):
    """API endpoint to get project file tree for sidebar navigation"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access
    if not check_project_read_access(request, project):
        return JsonResponse({"success": False, "error": "Permission denied"})

    # Get project directory (works for both local and remote projects)
    from apps.project_app.services.project_service_manager import ProjectServiceManager

    try:
        service_manager = ProjectServiceManager(project)
        project_path = service_manager.get_project_path()
    except Exception as e:
        logger.error(f"Failed to get project path for {username}/{slug}: {e}")
        return JsonResponse({"success": False, "error": f"Failed to access project: {str(e)}"})

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


# EOF
