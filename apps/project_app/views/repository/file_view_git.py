"""
File View Git Info

Git information retrieval for file view.
"""

import logging
import subprocess

logger = logging.getLogger(__name__)


def get_file_git_info(project_path, file_path, request, project):
    """
    Get Git commit information for a file.

    Args:
        project_path: Path to project root
        file_path: Relative file path
        request: HTTP request object
        project: Project model instance

    Returns:
        dict: Git info including branch, commit details
    """
    git_info = {}

    try:
        # Get current branch from session or repository
        from apps.project_app.api_views_module.api_views import get_current_branch_from_session

        current_branch = get_current_branch_from_session(request, project)
        git_info["current_branch"] = current_branch

        # Get all branches
        git_info["branches"] = _get_branches(project_path, current_branch)

        # Get last commit info for this specific file
        commit_info = _get_file_commit_info(project_path, file_path)
        git_info.update(commit_info)

    except Exception as e:
        logger.debug(f"Error getting git info for {file_path}: {e}")
        git_info = _get_default_git_info()

    return git_info


def _get_branches(project_path, current_branch):
    """Get list of all branches."""
    result = subprocess.run(
        ["git", "branch", "-a"],
        cwd=project_path,
        capture_output=True,
        text=True,
        timeout=5,
    )

    if result.returncode != 0:
        return [current_branch]

    branches = []
    for line in result.stdout.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("*"):
            # Current branch
            branch_name = line[2:].strip()
            if branch_name not in branches:
                branches.insert(0, branch_name)
        else:
            # Remove 'remotes/origin/' prefix if present
            branch_name = line.replace("remotes/origin/", "")
            if branch_name and branch_name not in branches:
                branches.append(branch_name)

    return branches if branches else [current_branch]


def _get_file_commit_info(project_path, file_path):
    """Get last commit info for a specific file."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%an|%ae|%ar|%at|%s|%h|%H", "--", file_path],
        cwd=project_path,
        capture_output=True,
        text=True,
        timeout=5,
    )

    if result.returncode == 0 and result.stdout.strip():
        parts = result.stdout.strip().split("|", 6)
        return {
            "author_name": parts[0],
            "author_email": parts[1],
            "time_ago": parts[2],
            "timestamp": parts[3],
            "message": parts[4],
            "short_hash": parts[5],
            "full_hash": parts[6] if len(parts) > 6 else parts[5],
        }

    # File might not be committed yet
    return {
        "author_name": "",
        "author_email": "",
        "time_ago": "Not committed",
        "timestamp": "",
        "message": "No commits yet",
        "short_hash": "",
        "full_hash": "",
    }


def _get_default_git_info():
    """Return default git info when git operations fail."""
    return {
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
