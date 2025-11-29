#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-29"
# File: /home/ywatanabe/proj/scitex-cloud/apps/project_app/views/directory_views/file_view_blame.py
# ----------------------------------------
"""
Directory Views - Blame Mode Module

Handles git blame functionality showing authorship per line.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib import messages

logger = logging.getLogger(__name__)


def handle_blame_mode(request, project, username, slug, file_path, git_info):
    """
    Handle blame mode - show git blame information.

    Args:
        request: Django request object
        project: Project model instance
        username: Project owner username
        slug: Project slug
        file_path: Relative path to file within project
        git_info: Git information dict

    Returns:
        HttpResponse with blame view or redirect on error
    """
    blame_lines = []

    # Get git clone path for running git commands
    git_clone_path = None
    if hasattr(project, 'git_clone_path') and project.git_clone_path:
        git_clone_path = Path(project.git_clone_path)
        if not git_clone_path.exists() or not (git_clone_path / ".git").exists():
            git_clone_path = None

    if not git_clone_path:
        messages.error(request, "Git repository not available for blame. Please ensure the project is cloned from Gitea.")
        return redirect("user_projects:file_view", username=username, slug=slug, file_path=file_path)

    try:
        # Run git blame with porcelain format for easier parsing
        blame_result = subprocess.run(
            ["git", "blame", "--porcelain", file_path],
            cwd=git_clone_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if blame_result.returncode == 0:
            # Parse porcelain format blame output
            blame_lines = _parse_blame_output(blame_result.stdout)
        else:
            # Git blame failed, possibly file not in git
            messages.warning(request, "Unable to get blame information. File may not be tracked in git.")
            return redirect("user_projects:file_view", username=username, slug=slug, file_path=file_path)

    except subprocess.TimeoutExpired:
        messages.error(request, "Git blame timed out. File may be too large.")
        return redirect("user_projects:file_view", username=username, slug=slug, file_path=file_path)
    except Exception as e:
        logger.error(f"Error running git blame: {e}")
        messages.error(request, f"Error getting blame information: {e}")
        return redirect("user_projects:file_view", username=username, slug=slug, file_path=file_path)

    # Build breadcrumb
    from .helpers import build_breadcrumbs
    breadcrumbs = build_breadcrumbs(project, username, slug, file_path)

    file_name = Path(file_path).name

    context = {
        "project": project,
        "file_name": file_name,
        "file_path": file_path,
        "blame_lines": blame_lines,
        "breadcrumbs": breadcrumbs,
        "git_info": git_info,
        "can_edit": project.owner == request.user,
        "mode": "blame",
    }
    return render(request, "project_app/repository/file_blame.html", context)


def _parse_blame_output(blame_output):
    """
    Parse git blame porcelain format output.

    Args:
        blame_output: Raw stdout from git blame --porcelain

    Returns:
        list: List of blame info dictionaries, one per line
    """
    blame_lines = []
    lines = blame_output.split("\n")
    i = 0
    line_number = 1

    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue

        # First line: commit hash, original line, final line, group lines
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

        # Parse following lines for this commit
        i += 1
        while i < len(lines) and not lines[i].startswith('\t'):
            if lines[i].startswith('author '):
                blame_info['author'] = lines[i][7:]
            elif lines[i].startswith('author-time '):
                timestamp = int(lines[i][12:])
                blame_info['author_time'] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
                # Calculate time ago
                blame_info['author_time_ago'] = _calculate_time_ago(timestamp)
            elif lines[i].startswith('summary '):
                blame_info['summary'] = lines[i][8:]
            i += 1

        # Next line should be the actual code content (starts with tab)
        if i < len(lines) and lines[i].startswith('\t'):
            blame_info['content'] = lines[i][1:]  # Remove leading tab
            i += 1

        blame_lines.append(blame_info)
        line_number += 1

    return blame_lines


def _calculate_time_ago(timestamp):
    """
    Calculate human-readable time ago from timestamp.

    Args:
        timestamp: Unix timestamp

    Returns:
        str: Human-readable time ago (e.g., "2d ago", "3h ago")
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


# EOF
