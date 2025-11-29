"""
Git Helpers

Functions for retrieving and parsing git information.
"""

from __future__ import annotations

import logging
import subprocess
from datetime import datetime

logger = logging.getLogger(__name__)


def get_git_file_info(project_path, file_path, request, project):
    """
    Get git metadata for a file including commit info and branches.

    Args:
        project_path: Path to project root
        file_path: Relative file path
        request: Django request object
        project: Project instance

    Returns:
        dict: Git information including branches, commits, author, etc.
    """
    git_info = {}
    try:
        from apps.project_app.api_views_module.api_views import get_current_branch_from_session

        current_branch = get_current_branch_from_session(request, project)
        git_info["current_branch"] = current_branch

        # Get all branches
        git_info["branches"] = _get_all_branches(project_path, current_branch)

        # Get last commit info for this specific file
        commit_info = _get_file_commit_info(project_path, file_path)
        git_info.update(commit_info)

    except Exception as e:
        logger.debug(f"Error getting git info for {file_path}: {e}")
        git_info = _get_default_git_info()

    return git_info


def _get_all_branches(project_path, current_branch):
    """Get all branches from repository."""
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
        if line and not line.startswith("*"):
            branch_name = line.replace("remotes/origin/", "")
            if branch_name and branch_name not in branches:
                branches.append(branch_name)
        elif line.startswith("*"):
            branch_name = line[2:].strip()
            if branch_name not in branches:
                branches.insert(0, branch_name)

    return branches if branches else [current_branch]


def _get_file_commit_info(project_path, file_path):
    """Get last commit info for a file."""
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
    """Return default git info on error."""
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


def calculate_time_ago(timestamp):
    """
    Calculate human-readable time ago from Unix timestamp.

    Args:
        timestamp: Unix timestamp integer

    Returns:
        str: Human-readable time string (e.g., "2d ago", "3h ago")
    """
    delta = datetime.now() - datetime.fromtimestamp(timestamp)
    if delta.days > 365:
        return f"{delta.days // 365}y ago"
    elif delta.days > 30:
        return f"{delta.days // 30}mo ago"
    elif delta.days > 0:
        return f"{delta.days}d ago"
    elif delta.seconds > 3600:
        return f"{delta.seconds // 3600}h ago"
    elif delta.seconds > 60:
        return f"{delta.seconds // 60}m ago"
    else:
        return "just now"


def parse_git_blame_porcelain(blame_stdout):
    """
    Parse git blame porcelain format output into structured data.

    Args:
        blame_stdout: Output from git blame --porcelain command

    Returns:
        list: Blame information dicts with commit, author, time, content
    """
    blame_lines = []
    lines = blame_stdout.split("\n")
    i = 0
    line_number = 1

    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue

        parts = lines[i].split()
        if len(parts) < 3:
            i += 1
            continue

        commit_hash = parts[0]
        blame_info = {
            'commit_hash': commit_hash,
            'short_hash': commit_hash[:7],
            'line_number': line_number,
            'author': '',
            'author_time': '',
            'author_time_ago': '',
            'summary': '',
            'content': '',
        }

        i += 1
        while i < len(lines) and not lines[i].startswith('\t'):
            if lines[i].startswith('author '):
                blame_info['author'] = lines[i][7:]
            elif lines[i].startswith('author-time '):
                timestamp = int(lines[i][12:])
                blame_info['author_time'] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
                blame_info['author_time_ago'] = calculate_time_ago(timestamp)
            elif lines[i].startswith('summary '):
                blame_info['summary'] = lines[i][8:]
            i += 1

        if i < len(lines) and lines[i].startswith('\t'):
            blame_info['content'] = lines[i][1:]
            i += 1

        blame_lines.append(blame_info)
        line_number += 1

    return blame_lines


def parse_unified_diff(diff_stdout):
    """
    Parse unified diff format into structured line-by-line data.

    Args:
        diff_stdout: Output from git show/diff command

    Returns:
        list: Diff lines with content and type (header/hunk/addition/deletion/context)
    """
    diff_lines = []
    for diff_line in diff_stdout.split("\n"):
        line_type = "context"
        if diff_line.startswith("+++") or diff_line.startswith("---"):
            line_type = "header"
        elif diff_line.startswith("@@"):
            line_type = "hunk"
        elif diff_line.startswith("+"):
            line_type = "addition"
        elif diff_line.startswith("-"):
            line_type = "deletion"

        diff_lines.append({"content": diff_line, "type": line_type})

    return diff_lines
