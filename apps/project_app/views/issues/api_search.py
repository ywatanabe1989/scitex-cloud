"""
Issue Search API endpoint.
"""

from __future__ import annotations

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from ...models import Project


@require_http_methods(["GET"])
def api_issue_search(request, username, slug):
    """
    API: Search issues
    GET /<username>/<slug>/api/issues/search/?q=<query>&state=<state>
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)

    # Check permissions
    if not project.can_view(request.user):
        return JsonResponse(
            {
                "success": False,
                "error": "You do not have permission to view this project",
            },
            status=403,
        )

    query = request.GET.get("q", "").strip()
    state = request.GET.get("state", "open")

    issues = project.issues.select_related("author")

    if state != "all":
        issues = issues.filter(state=state)

    if query:
        from django.db.models import Q

        issues = issues.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Limit to 10 results
    issues = issues[:10]

    return JsonResponse(
        {
            "success": True,
            "issues": [
                {
                    "number": issue.number,
                    "title": issue.title,
                    "state": issue.state,
                    "author": issue.author.username,
                    "created_at": issue.created_at.isoformat(),
                    "url": issue.get_absolute_url(),
                }
                for issue in issues
            ],
        }
    )
