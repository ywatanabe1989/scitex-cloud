"""
Issue Comments API endpoint.
"""

from __future__ import annotations

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ...models import Project, Issue, IssueComment


@require_POST
@login_required
def api_issue_comment(request, username, slug, issue_number):
    """
    API: Add a comment to an issue
    POST /<username>/<slug>/api/issues/<issue_number>/comment/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    issue = get_object_or_404(Issue, project=project, number=issue_number)

    # Check permissions
    if not issue.can_comment(request.user):
        return JsonResponse(
            {
                "success": False,
                "error": "You do not have permission to comment on this issue",
            },
            status=403,
        )

    content = request.POST.get("content", "").strip()
    if not content:
        return JsonResponse(
            {"success": False, "error": "Comment content is required"}, status=400
        )

    # Create comment
    comment = IssueComment.objects.create(
        issue=issue, author=request.user, content=content
    )

    return JsonResponse(
        {
            "success": True,
            "message": "Comment added successfully",
            "comment": {
                "id": comment.id,
                "author": comment.author.username,
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
            },
        }
    )
