#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-04"
# File: /home/ywatanabe/proj/scitex-cloud/apps/project_app/views/directory_views.py
# ----------------------------------------
"""
Directory and File Browser Views Module

This module contains all views related to browsing and navigating project
directories and files, including:
- Dynamic directory browser
- File viewing with syntax highlighting
- File editing
- File history and commit details
- Git integration for file/directory information
"""
from __future__ import annotations

import os
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User

from ..models import Project, ProjectMembership
from ..decorators import project_required, project_access_required

logger = logging.getLogger(__name__)


def _detect_language(file_ext, file_name):
    """
    Detect language for syntax highlighting based on file extension.
    Returns language identifier for highlight.js.
    """
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'bash',
        '.fish': 'bash',
        '.c': 'c',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.java': 'java',
        '.rb': 'ruby',
        '.php': 'php',
        '.go': 'go',
        '.rs': 'rust',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.r': 'r',
        '.R': 'r',
        '.sql': 'sql',
        '.tex': 'latex',
        '.bib': 'bibtex',
        '.dockerfile': 'dockerfile',
        '.makefile': 'makefile',
        '.txt': 'plaintext',
        '.log': 'plaintext',
        '.csv': 'plaintext',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'ini',
    }

    # Check by extension first
    if file_ext.lower() in language_map:
        return language_map[file_ext.lower()]

    # Check by filename patterns
    filename_lower = file_name.lower()
    if filename_lower in ['dockerfile', 'makefile', 'rakefile', 'gemfile']:
        return language_map.get(f'.{filename_lower}', 'plaintext')

    # Default to plaintext
    return 'plaintext'


def project_directory_dynamic(request, username, slug, directory_path):
    """
    Dynamic directory browser - handles ANY directory path.

    URLs like:
    - /username/project/scripts/
    - /username/project/scripts/mnist/
    - /username/project/paper/manuscript/
    - /username/project/data/raw/images/
    """
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access permissions
    has_access = (
        project.owner == request.user
        or project.collaborators.filter(id=request.user.id).exists()
        or getattr(project, "visibility", None) == "public"
    )

    if not has_access:
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(request.get_full_path())
        else:
            messages.error(
                request, "You don't have permission to access this project."
            )
            return redirect(
                "user_projects:detail", username=username, slug=slug
            )

    # Get project path
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    if not project_path or not project_path.exists():
        messages.error(request, "Project directory not found.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Construct full directory path
    full_directory_path = project_path / directory_path

    # Security check: ensure path is within project directory
    try:
        full_directory_path = full_directory_path.resolve()
        if not str(full_directory_path).startswith(
            str(project_path.resolve())
        ):
            messages.error(request, "Invalid directory path.")
            return redirect(
                "user_projects:detail", username=username, slug=slug
            )
    except Exception:
        messages.error(request, "Invalid directory path.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Check if directory exists
    if not full_directory_path.exists():
        messages.error(request, f"Directory '{directory_path}' not found.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Get directory contents
    contents = []
    try:
        for item in full_directory_path.iterdir():
            # Show all files and directories including hidden files
            # Skip only special directories like .git
            if item.is_dir() and item.name in [
                ".git",
                "__pycache__",
                "node_modules",
                ".venv",
                "venv",
            ]:
                continue

            if item.is_file():
                contents.append(
                    {
                        "name": item.name,
                        "type": "file",
                        "size": item.stat().st_size,
                        "modified": item.stat().st_mtime,
                        "path": str(item.relative_to(project_path)),
                    }
                )
            elif item.is_dir():
                contents.append(
                    {
                        "name": item.name,
                        "type": "directory",
                        "path": str(item.relative_to(project_path)),
                    }
                )
    except PermissionError:
        messages.error(request, "Permission denied accessing directory.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Sort: directories first, then files, alphabetically
    contents.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))

    # Build breadcrumb navigation
    breadcrumbs = [{"name": project.name, "url": f"/{username}/{slug}/", "is_last": False}]

    # Add each path component to breadcrumbs
    path_parts = [p for p in directory_path.split("/") if p]  # Filter empty strings
    current_path = ""
    for idx, part in enumerate(path_parts):
        current_path += part + "/"
        is_last = (idx == len(path_parts) - 1)  # Last item in the path
        breadcrumbs.append(
            {"name": part, "url": f"/{username}/{slug}/{current_path}", "is_last": is_last}
        )

    context = {
        "project": project,
        "directory": path_parts[0] if path_parts else directory_path,
        "subpath": "/".join(path_parts[1:]) if len(path_parts) > 1 else None,
        "breadcrumb_path": directory_path,
        "contents": contents,
        "breadcrumbs": breadcrumbs,
        "can_edit": project.owner == request.user
        or project.collaborators.filter(id=request.user.id).exists(),
    }

    return render(request, "project_app/repository/directory_browser.html", context)


def project_file_view(request, username, slug, file_path):
    """
    View/Edit file contents (GitHub-style /blob/).

    Modes (via query parameter):
    - ?mode=view (default) - View with syntax highlighting
    - ?mode=edit - Edit file content
    - ?mode=raw - Serve raw file content

    Supports:
    - Markdown (.md) - Rendered as HTML
    - Python (.py) - Syntax highlighted
    - YAML (.yaml, .yml) - Syntax highlighted
    - JSON (.json) - Syntax highlighted
    - Text files - Plain text with line numbers
    - Images - Display inline
    """
    mode = request.GET.get("mode", "view")
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access
    has_access = (
        project.owner == request.user
        or project.collaborators.filter(id=request.user.id).exists()
        or getattr(project, "visibility", None) == "public"
    )

    if not has_access:
        messages.error(
            request, "You don't have permission to access this file."
        )
        return redirect("user_projects:detail", username=username, slug=slug)

    # Get file path
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    if not project_path or not project_path.exists():
        messages.error(request, "Project directory not found.")
        return redirect("user_projects:detail", username=username, slug=slug)

    full_file_path = project_path / file_path

    # Security check
    try:
        full_file_path = full_file_path.resolve()
        if not str(full_file_path).startswith(str(project_path.resolve())):
            messages.error(request, "Invalid file path.")
            return redirect(
                "user_projects:detail", username=username, slug=slug
            )
    except Exception:
        messages.error(request, "Invalid file path.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Check if file exists and is a file
    if not full_file_path.exists() or not full_file_path.is_file():
        messages.error(request, "File not found.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Get Git commit information for this file
    git_info = {}
    try:
        # Get current branch from session or repository
        from apps.project_app.views.api_views import get_current_branch_from_session
        current_branch = get_current_branch_from_session(request, project)
        git_info['current_branch'] = current_branch

        # Get all branches
        all_branches_result = subprocess.run(
            ['git', 'branch', '-a'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if all_branches_result.returncode == 0:
            branches = []
            for line in all_branches_result.stdout.split('\n'):
                line = line.strip()
                if line and not line.startswith('*'):
                    # Remove 'remotes/origin/' prefix if present
                    branch_name = line.replace('remotes/origin/', '')
                    if branch_name and branch_name not in branches:
                        branches.append(branch_name)
                elif line.startswith('*'):
                    # Current branch
                    branch_name = line[2:].strip()
                    if branch_name not in branches:
                        branches.insert(0, branch_name)
            git_info['branches'] = branches
        else:
            git_info['branches'] = [git_info['current_branch']]

        # Get last commit info for this specific file
        commit_result = subprocess.run(
            ['git', 'log', '-1', '--format=%an|%ae|%ar|%at|%s|%h|%H', '--', file_path],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )

        if commit_result.returncode == 0 and commit_result.stdout.strip():
            parts = commit_result.stdout.strip().split('|', 6)
            git_info.update({
                'author_name': parts[0],
                'author_email': parts[1],
                'time_ago': parts[2],
                'timestamp': parts[3],
                'message': parts[4],
                'short_hash': parts[5],
                'full_hash': parts[6] if len(parts) > 6 else parts[5],
            })
        else:
            # File might not be committed yet
            git_info.update({
                'author_name': '',
                'author_email': '',
                'time_ago': 'Not committed',
                'timestamp': '',
                'message': 'No commits yet',
                'short_hash': '',
                'full_hash': '',
            })
    except Exception as e:
        logger.debug(f"Error getting git info for {file_path}: {e}")
        git_info = {
            'current_branch': 'main',
            'branches': ['main'],
            'author_name': '',
            'author_email': '',
            'time_ago': '',
            'timestamp': '',
            'message': '',
            'short_hash': '',
            'full_hash': '',
        }

    # Determine file type and rendering method
    file_name = full_file_path.name
    file_ext = full_file_path.suffix.lower()
    file_size = full_file_path.stat().st_size

    # Handle raw mode - serve file directly
    if mode == "raw" or mode == "download":
        # Determine content type based on file extension
        content_type = "text/plain; charset=utf-8"
        if file_ext == ".pdf":
            content_type = "application/pdf"
        elif file_ext in [".png"]:
            content_type = "image/png"
        elif file_ext in [".jpg", ".jpeg"]:
            content_type = "image/jpeg"
        elif file_ext in [".gif"]:
            content_type = "image/gif"

        with open(full_file_path, "rb") as f:
            response = HttpResponse(f.read(), content_type=content_type)
            # For download mode, force download instead of inline display
            disposition = "attachment" if mode == "download" else "inline"
            response["Content-Disposition"] = f'{disposition}; filename="{file_name}"'
            return response

    # Handle edit mode - show editor
    if mode == "edit":
        if not (project.owner == request.user):
            messages.error(request, "Only project owner can edit files.")
            return redirect(
                "user_projects:detail", username=username, slug=slug
            )

        if request.method == "POST":
            # Save edited content
            new_content = request.POST.get("content", "")
            try:
                with open(full_file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                messages.success(
                    request, f"File '{file_name}' saved successfully!"
                )
                return redirect(
                    "user_projects:file_view",
                    username=username,
                    slug=slug,
                    file_path=file_path,
                )
            except Exception as e:
                messages.error(request, f"Error saving file: {e}")

        # Read current content for editing
        try:
            with open(
                full_file_path, "r", encoding="utf-8", errors="ignore"
            ) as f:
                file_content = f.read()
        except Exception as e:
            messages.error(request, f"Error reading file: {e}")
            return redirect(
                "user_projects:detail", username=username, slug=slug
            )

        # Build breadcrumb
        breadcrumbs = [{"name": project.name, "url": f"/{username}/{slug}/"}]
        path_parts = file_path.split("/")
        current_path = ""
        for i, part in enumerate(path_parts):
            current_path += part
            if i < len(path_parts) - 1:
                current_path += "/"
                breadcrumbs.append(
                    {"name": part, "url": f"/{username}/{slug}/{current_path}"}
                )
            else:
                breadcrumbs.append({"name": part, "url": None})

        context = {
            "project": project,
            "file_name": file_name,
            "file_path": file_path,
            "file_content": file_content,
            "breadcrumbs": breadcrumbs,
            "mode": "edit",
        }
        return render(request, "project_app/repository/file_edit.html", context)

    # Read file content
    try:
        # Check if binary file
        # File size limit: 1MB for display
        MAX_DISPLAY_SIZE = 1024 * 1024  # 1MB
        if file_size > MAX_DISPLAY_SIZE:
            render_type = "binary"
            file_content = f"File too large to display ({file_size:,} bytes). Maximum size: {MAX_DISPLAY_SIZE:,} bytes."
            file_html = None
            language = None
        else:
            # Check if file is binary by extension first
            is_binary = file_ext in [
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".pdf",
                ".zip",
                ".tar",
                ".gz",
                ".ico",
                ".woff",
                ".woff2",
                ".ttf",
                ".eot",
            ]

            if is_binary:
                # For images, show inline
                if file_ext in [".png", ".jpg", ".jpeg", ".gif"]:
                    render_type = "image"
                    file_content = None
                    file_html = None
                    language = None
                # For PDFs, use PDF.js viewer
                elif file_ext == ".pdf":
                    render_type = "pdf"
                    file_content = None
                    file_html = None
                    language = None
                else:
                    render_type = "binary"
                    file_content = f"Binary file ({file_size:,} bytes)"
                    file_html = None
                    language = None
            else:
                # Try to read as text file
                try:
                    with open(
                        full_file_path, "r", encoding="utf-8"
                    ) as f:
                        file_content = f.read()

                    # Detect language for syntax highlighting
                    language = _detect_language(file_ext, file_name)

                    # Render based on file type
                    if file_ext == ".md":
                        import markdown

                        file_html = markdown.markdown(
                            file_content,
                            extensions=[
                                "fenced_code",
                                "tables",
                                "nl2br",
                                "codehilite",
                            ],
                        )
                        render_type = "markdown"
                    elif language:
                        # Use highlight.js on frontend
                        render_type = "code"
                        file_html = None
                    else:
                        file_html = None
                        render_type = "text"

                except UnicodeDecodeError:
                    # File is binary but wasn't caught by extension check
                    render_type = "binary"
                    file_content = f"Binary file ({file_size:,} bytes)"
                    file_html = None
                    language = None

    except Exception as e:
        messages.error(request, f"Error reading file: {e}")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Build breadcrumb
    breadcrumbs = [{"name": project.name, "url": f"/{username}/{slug}/"}]

    path_parts = file_path.split("/")
    current_path = ""
    for i, part in enumerate(path_parts):
        current_path += part
        if i < len(path_parts) - 1:  # Directory
            current_path += "/"
            breadcrumbs.append(
                {"name": part, "url": f"/{username}/{slug}/{current_path}"}
            )
        else:  # File
            breadcrumbs.append({"name": part, "url": None})

    context = {
        "project": project,
        "file_name": file_name,
        "file_path": file_path,
        "file_size": file_size,
        "file_ext": file_ext,
        "file_content": file_content,
        "file_html": file_html,
        "render_type": render_type,
        "language": language if 'language' in locals() else None,
        "breadcrumbs": breadcrumbs,
        "can_edit": project.owner == request.user,
        "git_info": git_info,
    }

    return render(request, "project_app/repository/file_view.html", context)


def project_directory(request, username, slug, directory, subpath=None):
    """
    Browse scientific workflow directories within a project.

    URLs like:
    - /username/project-name/scripts/
    - /username/project-name/scripts/analysis/
    - /username/project-name/data/raw/
    """
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access permissions
    has_access = (
        project.owner == request.user
        or project.collaborators.filter(id=request.user.id).exists()
        or project.visibility == "public"
    )

    if not has_access:
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(request.get_full_path())
        else:
            messages.error(
                request, "You don't have permission to access this project."
            )
            return redirect("project_app:detail", username=username, slug=slug)

    # Get the project directory manager
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    if not project_path or not project_path.exists():
        messages.error(request, "Project directory not found.")
        return redirect("project_app:detail", username=username, slug=slug)

    # Construct the full directory path
    if subpath:
        directory_path = project_path / directory / subpath
        breadcrumb_path = f"{directory}/{subpath}"
    else:
        directory_path = project_path / directory
        breadcrumb_path = directory

    # Security check: ensure path is within project directory
    try:
        directory_path = directory_path.resolve()
        if not str(directory_path).startswith(str(project_path.resolve())):
            messages.error(request, "Invalid directory path.")
            return redirect("project_app:detail", username=username, slug=slug)
    except Exception:
        messages.error(request, "Invalid directory path.")
        return redirect("project_app:detail", username=username, slug=slug)

    # Check if directory exists
    if not directory_path.exists():
        messages.error(request, f"Directory '{breadcrumb_path}' not found.")
        return redirect("project_app:detail", username=username, slug=slug)

    # Get directory contents
    contents = []
    try:
        # Helper function to get git commit info for a file/folder
        def get_git_info(path):
            """Get last commit message, author, hash, and time for a file/folder"""
            try:
                # Get last commit for this file (including hash)
                result = subprocess.run(
                    ['git', 'log', '-1', '--format=%an|%ar|%s|%h', '--', str(path.name)],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0 and result.stdout.strip():
                    author, time_ago, message, commit_hash = result.stdout.strip().split('|', 3)
                    return {
                        'author': author,
                        'time_ago': time_ago,
                        'message': message[:80],  # Truncate to 80 chars
                        'hash': commit_hash
                    }
            except Exception as e:
                logger.debug(f"Error getting git info for {path}: {e}")

            return {
                'author': '',
                'time_ago': '',
                'message': '',
                'hash': ''
            }

        for item in directory_path.iterdir():
            # Show all files and directories including dotfiles
            git_info = get_git_info(item)

            if item.is_file():
                contents.append(
                    {
                        "name": item.name,
                        "type": "file",
                        "size": item.stat().st_size,
                        "modified": item.stat().st_mtime,
                        "path": str(item.relative_to(project_path)),
                        "author": git_info.get('author', ''),
                        "time_ago": git_info.get('time_ago', ''),
                        "message": git_info.get('message', ''),
                        "hash": git_info.get('hash', ''),
                    }
                )
            elif item.is_dir():
                contents.append(
                    {
                        "name": item.name,
                        "type": "directory",
                        "path": str(item.relative_to(project_path)),
                        "author": git_info.get('author', ''),
                        "time_ago": git_info.get('time_ago', ''),
                        "message": git_info.get('message', ''),
                        "hash": git_info.get('hash', ''),
                    }
                )
    except PermissionError:
        messages.error(request, "Permission denied accessing directory.")
        return redirect("project_app:detail", username=username, slug=slug)

    # Sort contents: directories first, then files, both alphabetically
    contents.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))

    # Build breadcrumb navigation
    breadcrumbs = [
        {"name": project.name, "url": project.get_absolute_url()},
        {
            "name": directory,
            "url": f"{project.get_absolute_url()}{directory}/",
        },
    ]

    if subpath:
        path_parts = subpath.split("/")
        current_path = directory
        for part in path_parts:
            current_path += f"/{part}"
            breadcrumbs.append(
                {
                    "name": part,
                    "url": f"{project.get_absolute_url()}{current_path}/",
                }
            )

    context = {
        "project": project,
        "directory": directory,
        "subpath": subpath,
        "breadcrumb_path": breadcrumb_path,
        "contents": contents,
        "breadcrumbs": breadcrumbs,
        "can_edit": project.owner == request.user
        or project.collaborators.filter(id=request.user.id).exists(),
    }

    return render(request, "project_app/repository/directory_browser.html", context)


def file_history_view(request, username, slug, branch, file_path):
    """
    Show commit history for a specific file (GitHub-style /commits/<branch>/<path>).

    Displays all commits that modified this file with:
    - Commit message, author, date, hash
    - File-specific stats (+/- lines)
    - Pagination (30 commits per page)
    - Filter by author or date range

    URLs:
    - /<username>/<project>/commits/<branch>/<file-path>
    """
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access
    has_access = (
        project.owner == request.user
        or project.collaborators.filter(id=request.user.id).exists()
        or getattr(project, "visibility", None) == "public"
    )

    if not has_access:
        messages.error(
            request, "You don't have permission to access this file."
        )
        return redirect("user_projects:detail", username=username, slug=slug)

    # Get project path
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    if not project_path or not project_path.exists():
        messages.error(request, "Project directory not found.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Build breadcrumb
    breadcrumbs = [{"name": project.name, "url": f"/{username}/{slug}/"}]

    path_parts = file_path.split("/")
    current_path = ""
    for i, part in enumerate(path_parts):
        current_path += part
        if i < len(path_parts) - 1:  # Directory
            current_path += "/"
            breadcrumbs.append(
                {"name": part, "url": f"/{username}/{slug}/{current_path}"}
            )
        else:  # File
            breadcrumbs.append({"name": part, "url": f"/{username}/{slug}/blob/{file_path}"})

    # Get filter parameters
    author_filter = request.GET.get("author", "").strip()
    page_number = request.GET.get("page", 1)

    try:
        page_number = int(page_number)
    except (ValueError, TypeError):
        page_number = 1

    # Get file history using git log --follow
    commits = []
    try:
        # Build git log command
        # Format: hash|author_name|author_email|timestamp|relative_time|subject
        git_cmd = [
            'git', 'log', '--follow',
            '--format=%H|%an|%ae|%at|%ar|%s',
            '--', file_path
        ]

        # Add author filter if specified
        if author_filter:
            git_cmd.insert(3, f'--author={author_filter}')

        result = subprocess.run(
            git_cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = line.split('|', 5)
                if len(parts) < 6:
                    continue

                commit_hash, author_name, author_email, timestamp, relative_time, subject = parts

                # Get file-specific stats for this commit
                stats_result = subprocess.run(
                    ['git', 'show', '--numstat', '--format=', commit_hash, '--', file_path],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                additions = 0
                deletions = 0
                if stats_result.returncode == 0 and stats_result.stdout.strip():
                    stat_line = stats_result.stdout.strip().split('\n')[0]
                    stat_parts = stat_line.split('\t')
                    if len(stat_parts) >= 2:
                        try:
                            additions = int(stat_parts[0]) if stat_parts[0] != '-' else 0
                            deletions = int(stat_parts[1]) if stat_parts[1] != '-' else 0
                        except ValueError:
                            pass

                commits.append({
                    'hash': commit_hash,
                    'short_hash': commit_hash[:7],
                    'author_name': author_name,
                    'author_email': author_email,
                    'timestamp': int(timestamp),
                    'relative_time': relative_time,
                    'subject': subject,
                    'additions': additions,
                    'deletions': deletions,
                })

    except subprocess.TimeoutExpired:
        logger.error(f"Git log timeout for {file_path} in {project.slug}")
        messages.error(request, "Timeout while fetching file history.")
    except Exception as e:
        logger.error(f"Error getting file history for {file_path}: {e}")
        messages.error(request, f"Error fetching file history: {str(e)}")

    # Pagination
    paginator = Paginator(commits, 30)
    commits_page = paginator.get_page(page_number)

    # Get unique authors for filter dropdown
    unique_authors = sorted(set(c['author_name'] for c in commits))

    context = {
        "project": project,
        "file_path": file_path,
        "file_name": Path(file_path).name,
        "branch": branch,
        "breadcrumbs": breadcrumbs,
        "commits": commits_page,
        "unique_authors": unique_authors,
        "author_filter": author_filter,
        "total_commits": len(commits),
    }

    return render(request, "project_app/repository/file_history.html", context)


def commit_detail(request, username, slug, commit_hash):
    """
    GitHub-style commit detail page showing diff and metadata.

    URL: /<username>/<slug>/commit/<commit_hash>/

    Shows:
    - Commit metadata (author, date, message)
    - Changed files with stats
    - Unified diffs for each file
    """
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access permissions
    has_access = (
        project.owner == request.user
        or project.collaborators.filter(id=request.user.id).exists()
        or getattr(project, "visibility", None) == "public"
    )

    if not has_access:
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        else:
            messages.error(request, "You don't have permission to access this project.")
            return redirect("user_projects:detail", username=username, slug=slug)

    # Get project path
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    if not project_path or not project_path.exists():
        messages.error(request, "Project directory not found.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Fetch commit information using git
    commit_info = {}
    changed_files = []

    try:
        # Get commit metadata: author, email, date, message
        result = subprocess.run(
            ['git', 'show', '--no-patch', '--format=%an|%ae|%aI|%s|%b|%P|%H', commit_hash],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            messages.error(request, f"Commit {commit_hash} not found.")
            return redirect("user_projects:detail", username=username, slug=slug)

        parts = result.stdout.strip().split('|', 6)
        commit_info = {
            'author_name': parts[0],
            'author_email': parts[1],
            'date': datetime.fromisoformat(parts[2].replace('Z', '+00:00')),
            'subject': parts[3],  # First line of commit message
            'body': parts[4] if len(parts) > 4 else '',  # Full commit message body
            'parent_hash': parts[5].split()[0] if len(parts) > 5 and parts[5] else None,  # First parent
            'full_hash': parts[6] if len(parts) > 6 else commit_hash,
            'short_hash': commit_hash[:7],
        }

        # Get list of changed files with stats
        stats_result = subprocess.run(
            ['git', 'diff-tree', '--no-commit-id', '--numstat', '-r', commit_hash],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        if stats_result.returncode == 0:
            for line in stats_result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('\t')
                if len(parts) >= 3:
                    added = parts[0]
                    deleted = parts[1]
                    filepath = parts[2]

                    # Get the actual diff for this file
                    diff_result = subprocess.run(
                        ['git', 'show', '--format=', commit_hash, '--', filepath],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    # Parse unified diff to get line-by-line changes
                    diff_lines = []
                    if diff_result.returncode == 0 and diff_result.stdout:
                        for diff_line in diff_result.stdout.split('\n'):
                            line_type = 'context'
                            if diff_line.startswith('+++') or diff_line.startswith('---'):
                                line_type = 'header'
                            elif diff_line.startswith('@@'):
                                line_type = 'hunk'
                            elif diff_line.startswith('+'):
                                line_type = 'addition'
                            elif diff_line.startswith('-'):
                                line_type = 'deletion'

                            diff_lines.append({
                                'content': diff_line,
                                'type': line_type
                            })

                    # Determine file extension for syntax highlighting hint
                    file_ext = Path(filepath).suffix.lower()

                    changed_files.append({
                        'path': filepath,
                        'additions': added if added != '-' else 0,
                        'deletions': deleted if deleted != '-' else 0,
                        'diff': diff_lines,
                        'extension': file_ext,
                    })

        # Get current branch
        branch_result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if branch_result.returncode == 0:
            commit_info['current_branch'] = branch_result.stdout.strip() or 'main'
        else:
            commit_info['current_branch'] = 'main'

    except subprocess.TimeoutExpired:
        messages.error(request, "Git command timed out.")
        return redirect("user_projects:detail", username=username, slug=slug)
    except Exception as e:
        logger.error(f"Error fetching commit details: {e}")
        messages.error(request, f"Error fetching commit details: {e}")
        return redirect("user_projects:detail", username=username, slug=slug)

    context = {
        'project': project,
        'commit': commit_info,
        'changed_files': changed_files,
        'total_additions': sum(int(f['additions']) if isinstance(f['additions'], (int, str)) and str(f['additions']).isdigit() else 0 for f in changed_files),
        'total_deletions': sum(int(f['deletions']) if isinstance(f['deletions'], (int, str)) and str(f['deletions']).isdigit() else 0 for f in changed_files),
    }

    return render(request, 'project_app/commit_detail.html', context)


# EOF
