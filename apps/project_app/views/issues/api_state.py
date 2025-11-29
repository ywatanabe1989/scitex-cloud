"""
Issue State API endpoints - Close and reopen issues.
"""

from __future__ import annotations

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ...models import Project, Issue, IssueEvent


@require_POST
@login_required
def api_issue_close(request, username, slug, issue_number):
    """
    API: Close an issue
    POST /<username>/<slug>/api/issues/<issue_number>/close/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    issue = get_object_or_404(Issue, project=project, number=issue_number)

    # Check permissions
    if not issue.can_edit(request.user):
        return JsonResponse(
            {
                "success": False,
                "error": "You do not have permission to close this issue",
            },
            status=403,
        )

    if issue.state == "closed":
        return JsonResponse(
            {"success": False, "error": "Issue is already closed"}, status=400
        )

    # Close issue
    issue.close(request.user)

    # Create event
    IssueEvent.objects.create(issue=issue, event_type="closed", actor=request.user)

    return JsonResponse(
        {
            "success": True,
            "message": "Issue closed successfully",
            "issue": {
                "number": issue.number,
                "state": issue.state,
                "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
            },
        }
    )


@require_POST
@login_required
def api_issue_reopen(request, username, slug, issue_number):
    """
    API: Reopen a closed issue
    POST /<username>/<slug>/api/issues/<issue_number>/reopen/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    issue = get_object_or_404(Issue, project=project, number=issue_number)

    # Check permissions
    if not issue.can_edit(request.user):
        return JsonResponse(
            {
                "success": False,
                "error": "You do not have permission to reopen this issue",
            },
            status=403,
        )

    if issue.state == "open":
        return JsonResponse(
            {"success": False, "error": "Issue is already open"}, status=400
        )

    # Reopen issue
    issue.reopen()

    # Create event
    IssueEvent.objects.create(issue=issue, event_type="reopened", actor=request.user)

    return JsonResponse(
        {
            "success": True,
            "message": "Issue reopened successfully",
            "issue": {
                "number": issue.number,
                "state": issue.state,
            },
        }
    )
