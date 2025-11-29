"""
File History and Commit Detail Views

Views for displaying file history and commit details.

Modular structure:
- history_git.py: Git operations for history/commits
"""

from __future__ import annotations

import logging
from pathlib import Path

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User

from ...models import Project
from .helpers import build_breadcrumbs
from .history_git import (
    get_file_commits,
    get_commit_info,
    get_commit_files,
    get_current_branch,
)

logger = logging.getLogger(__name__)


def file_history_view(request, username, slug, branch, file_path):
    """
    Show commit history for a specific file (GitHub-style /commits/<branch>/<path>).

    URL: /<username>/<project>/commits/<branch>/<file-path>
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
        messages.error(request, "You don't have permission to access this file.")
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
    breadcrumbs = build_breadcrumbs(project, username, slug, file_path)

    # Get filter parameters
    author_filter = request.GET.get("author", "").strip()
    page_number = request.GET.get("page", 1)

    try:
        page_number = int(page_number)
    except (ValueError, TypeError):
        page_number = 1

    # Get file history
    commits = get_file_commits(project_path, file_path, author_filter)

    if not commits and author_filter:
        messages.info(request, f"No commits found for author: {author_filter}")

    # Pagination
    paginator = Paginator(commits, 30)
    commits_page = paginator.get_page(page_number)

    # Get unique authors for filter dropdown
    unique_authors = sorted(set(c["author_name"] for c in commits))

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

    # Get commit info
    commit_info = get_commit_info(project_path, commit_hash)
    if not commit_info:
        messages.error(request, f"Commit {commit_hash} not found.")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Get changed files
    changed_files = get_commit_files(project_path, commit_hash)

    # Get current branch
    commit_info["current_branch"] = get_current_branch(project_path)

    # Calculate totals
    total_additions = sum(
        int(f["additions"]) if str(f["additions"]).isdigit() else 0
        for f in changed_files
    )
    total_deletions = sum(
        int(f["deletions"]) if str(f["deletions"]).isdigit() else 0
        for f in changed_files
    )

    context = {
        "project": project,
        "commit": commit_info,
        "changed_files": changed_files,
        "total_additions": total_additions,
        "total_deletions": total_deletions,
    }

    return render(request, "project_app/repository/commit_detail.html", context)
