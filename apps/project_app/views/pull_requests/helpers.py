"""
Pull Request Helper Functions

Shared utilities for PR views.
"""

from __future__ import annotations

import logging
import subprocess
from itertools import chain
from operator import attrgetter

logger = logging.getLogger(__name__)


def get_pr_diff(project, pr):
    """
    Get diff for a PR.

    Returns:
        tuple: (diff_data: str, changed_files: list)
    """
    try:
        from apps.project_app.services.project_filesystem import (
            get_project_filesystem_manager,
        )

        manager = get_project_filesystem_manager(project.owner)
        project_path = manager.get_project_root_path(project)

        if not project_path or not project_path.exists():
            return None, []

        # Get full diff
        result = subprocess.run(
            ["git", "diff", f"{pr.target_branch}...{pr.source_branch}"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return None, []

        diff_data = result.stdout

        # Get changed files
        files_result = subprocess.run(
            [
                "git",
                "diff",
                "--name-status",
                f"{pr.target_branch}...{pr.source_branch}",
            ],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        changed_files = []
        if files_result.returncode == 0:
            for line in files_result.stdout.split("\n"):
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        changed_files.append(
                            {
                                "status": parts[0],
                                "path": parts[1],
                            }
                        )

        return diff_data, changed_files

    except Exception as e:
        logger.error(f"Failed to get PR diff: {e}")
        return None, []


def get_pr_checks(project, pr):
    """
    Get CI/CD checks status for a PR.

    Returns:
        list: Check results
    """
    # TODO: Implement integration with CI/CD system (GitHub Actions equivalent)
    # For now, return empty list
    return []


def get_pr_timeline(pr):
    """
    Get merged timeline of comments and events.

    Returns:
        list: Timeline items sorted chronologically
    """
    # Get comments and events
    comments = list(
        pr.comments.filter(parent_comment__isnull=True).select_related("author")
    )
    events = list(pr.events.select_related("actor"))

    # Merge and sort by created_at
    timeline = sorted(chain(comments, events), key=attrgetter("created_at"))

    return timeline


def get_project_branches(project):
    """
    Get list of branches for a project.

    Returns:
        list: Branch names
    """
    try:
        from apps.project_app.services.project_filesystem import (
            get_project_filesystem_manager,
        )

        manager = get_project_filesystem_manager(project.owner)
        project_path = manager.get_project_root_path(project)

        if not project_path or not project_path.exists():
            return []

        # Get branches from git
        result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return []

        # Parse branch names
        branches = []
        for line in result.stdout.split("\n"):
            line = line.strip()
            if line and not line.startswith("*"):
                # Remove remote prefix
                branch = line.replace("remotes/origin/", "")
                if branch not in branches:
                    branches.append(branch)

        return sorted(branches)

    except Exception as e:
        logger.error(f"Failed to get branches: {e}")
        return []


def compare_branches(project, base, head):
    """
    Compare two branches.

    Returns:
        dict: Comparison data (commits, files changed, diff)
    """
    try:
        from apps.project_app.services.project_filesystem import (
            get_project_filesystem_manager,
        )

        manager = get_project_filesystem_manager(project.owner)
        project_path = manager.get_project_root_path(project)

        if not project_path or not project_path.exists():
            return None

        # Get diff between branches
        result = subprocess.run(
            ["git", "diff", f"{base}...{head}", "--stat"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return None

        # Get commit count
        commit_result = subprocess.run(
            ["git", "rev-list", "--count", f"{base}..{head}"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        commit_count = (
            int(commit_result.stdout.strip()) if commit_result.returncode == 0 else 0
        )

        return {
            "base": base,
            "head": head,
            "commit_count": commit_count,
            "diff_stat": result.stdout,
        }

    except Exception as e:
        logger.error(f"Failed to compare branches: {e}")
        return None
