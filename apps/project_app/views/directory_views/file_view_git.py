#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-29"
# File: /home/ywatanabe/proj/scitex-cloud/apps/project_app/views/directory_views/file_view_git.py
# ----------------------------------------
"""
Directory Views - Git Information Module

Handles git information retrieval for file views including:
- Current branch detection
- Branch listing
- Commit history for specific files
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def get_git_info_for_file(request, project, project_path, file_path):
    """
    Get Git commit information for a specific file.

    Args:
        request: Django request object
        project: Project model instance
        project_path: Path to project directory
        file_path: Relative path to file within project

    Returns:
        dict: Git information including:
            - current_branch: Current branch name
            - branches: List of all branches
            - author_name: Last commit author name
            - author_email: Last commit author email
            - time_ago: Human-readable time since last commit
            - timestamp: Unix timestamp of last commit
            - message: Last commit message
            - short_hash: Short commit hash
            - full_hash: Full commit hash
    """
    git_info = {}

    try:
        # Get current branch from session or repository
        from apps.project_app.api_views_module.api_views import get_current_branch_from_session

        current_branch = get_current_branch_from_session(request, project)
        git_info["current_branch"] = current_branch

        # Get all branches
        all_branches_result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if all_branches_result.returncode == 0:
            branches = []
            for line in all_branches_result.stdout.split("\n"):
                line = line.strip()
                if line and not line.startswith("*"):
                    # Remove 'remotes/origin/' prefix if present
                    branch_name = line.replace("remotes/origin/", "")
                    if branch_name and branch_name not in branches:
                        branches.append(branch_name)
                elif line.startswith("*"):
                    # Current branch
                    branch_name = line[2:].strip()
                    if branch_name not in branches:
                        branches.insert(0, branch_name)
            git_info["branches"] = branches
        else:
            git_info["branches"] = [git_info["current_branch"]]

        # Get last commit info for this specific file
        commit_result = subprocess.run(
            ["git", "log", "-1", "--format=%an|%ae|%ar|%at|%s|%h|%H", "--", file_path],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if commit_result.returncode == 0 and commit_result.stdout.strip():
            parts = commit_result.stdout.strip().split("|", 6)
            git_info.update(
                {
                    "author_name": parts[0],
                    "author_email": parts[1],
                    "time_ago": parts[2],
                    "timestamp": parts[3],
                    "message": parts[4],
                    "short_hash": parts[5],
                    "full_hash": parts[6] if len(parts) > 6 else parts[5],
                }
            )
        else:
            # File might not be committed yet
            git_info.update(
                {
                    "author_name": "",
                    "author_email": "",
                    "time_ago": "Not committed",
                    "timestamp": "",
                    "message": "No commits yet",
                    "short_hash": "",
                    "full_hash": "",
                }
            )
    except Exception as e:
        logger.debug(f"Error getting git info for {file_path}: {e}")
        git_info = {
            "current_branch": "main",
            "branches": ["main"],
            "author_name": "",
            "author_email": "",
            "time_ago": "",
            "timestamp": "",
            "message": "",
            "short_hash": "",
            "full_hash": "",
        }

    return git_info


# EOF
