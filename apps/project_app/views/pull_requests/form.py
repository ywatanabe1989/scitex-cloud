"""
Pull Request Form Views

Handles PR creation and branch comparison.

Modular structure:
- helpers.py: get_project_branches, compare_branches
- form_git.py: sync_pr_commits, check_pr_conflicts
"""

from __future__ import annotations

import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404

from apps.project_app.models import (
    Project,
    PullRequest,
    PullRequestEvent,
)
from .helpers import get_project_branches, compare_branches
from .form_git import sync_pr_commits, check_pr_conflicts

logger = logging.getLogger(__name__)


@login_required
def pr_create(request, username, slug):
    """
    Form to create new PR from branch comparison.

    URL: /<username>/<slug>/pull/new/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)

    # Check permissions
    if not project.can_edit(request.user):
        messages.error(request, "You don't have permission to create pull requests")
        return redirect("user_projects:detail", username=username, slug=slug)

    # Get compare parameters (base and head branches)
    base_branch = request.GET.get("base", project.current_branch or "main")
    head_branch = request.GET.get("head", "")

    # Get list of branches
    branches = get_project_branches(project)

    if request.method == "POST":
        return _handle_pr_create_post(
            request, project, username, slug, base_branch, head_branch
        )

    # Get comparison data if both branches are selected
    comparison = None
    if head_branch and base_branch:
        comparison = compare_branches(project, base_branch, head_branch)

    # Get potential reviewers (collaborators)
    potential_reviewers = project.collaborators.exclude(id=request.user.id)

    context = {
        "project": project,
        "base_branch": base_branch,
        "head_branch": head_branch,
        "branches": branches,
        "comparison": comparison,
        "potential_reviewers": potential_reviewers,
    }

    return render(request, "project_app/pull_requests/form.html", context)


def _handle_pr_create_post(request, project, username, slug, base_branch, head_branch):
    """Handle POST request for PR creation."""
    title = request.POST.get("title", "").strip()
    description = request.POST.get("description", "").strip()
    base = request.POST.get("base", base_branch)
    head = request.POST.get("head", head_branch)
    is_draft = request.POST.get("is_draft") == "on"
    reviewers = request.POST.getlist("reviewers")

    # Validation
    if not title:
        messages.error(request, "PR title is required")
        return redirect(request.path)
    if not head:
        messages.error(request, "Source branch is required")
        return redirect(request.path)
    if base == head:
        messages.error(request, "Source and target branches must be different")
        return redirect(request.path)

    try:
        # Create PR
        pr = PullRequest.objects.create(
            project=project,
            title=title,
            description=description,
            author=request.user,
            source_branch=head,
            target_branch=base,
            state="draft" if is_draft else "open",
            is_draft=is_draft,
        )

        # Add reviewers
        if reviewers:
            from django.contrib.auth.models import User
            reviewer_users = User.objects.filter(username__in=reviewers)
            pr.reviewers.set(reviewer_users)

        # Sync commits from git
        sync_pr_commits(pr)

        # Check for conflicts
        check_pr_conflicts(pr)

        # Create event
        PullRequestEvent.objects.create(
            pull_request=pr,
            event_type="opened",
            actor=request.user,
        )

        messages.success(request, f"Pull request #{pr.number} created successfully")
        return redirect(
            "user_projects:pr_detail",
            username=username,
            slug=slug,
            pr_number=pr.number,
        )

    except Exception as e:
        logger.error(f"Failed to create PR: {e}")
        messages.error(request, f"Failed to create pull request: {str(e)}")
        return redirect(request.path)


def pr_compare(request, username, slug):
    """
    Branch comparison for creating PR.

    URL: /<username>/<slug>/compare/<base>...<head>/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)

    # Check permissions
    if not project.can_view(request.user):
        raise Http404("Project not found")

    # Get compare parameters
    compare_str = request.GET.get("compare", "")
    if "..." in compare_str:
        base, head = compare_str.split("...")
    else:
        base = project.current_branch or "main"
        head = ""

    # Get list of branches
    branches = get_project_branches(project)

    # Get comparison data
    comparison = None
    if head and base:
        comparison = compare_branches(project, base, head)

    context = {
        "project": project,
        "base_branch": base,
        "head_branch": head,
        "branches": branches,
        "comparison": comparison,
        "can_create": project.can_edit(request.user),
    }

    return render(request, "project_app/pull_requests/form.html", context)
