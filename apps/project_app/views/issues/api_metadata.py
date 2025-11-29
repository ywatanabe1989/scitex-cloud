"""
Issue Metadata API endpoints - Assignments, Labels, and Milestones.
"""

from __future__ import annotations
import json

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ...models import (
    Project,
    Issue,
    IssueLabel,
    IssueMilestone,
    IssueAssignment,
    IssueEvent,
)


@require_POST
@login_required
def api_issue_assign(request, username, slug, issue_number):
    """
    API: Assign/unassign a user to/from an issue
    POST /<username>/<slug>/api/issues/<issue_number>/assign/
    Body: { "user_id": 123, "action": "add" | "remove" }
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    issue = get_object_or_404(Issue, project=project, number=issue_number)

    # Check permissions
    if not project.can_edit(request.user):
        return JsonResponse(
            {"success": False, "error": "You do not have permission to assign users"},
            status=403,
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    user_id = data.get("user_id")
    action = data.get("action", "add")

    if not user_id:
        return JsonResponse(
            {"success": False, "error": "User ID is required"}, status=400
        )

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"success": False, "error": "User not found"}, status=404)

    if action == "add":
        # Add assignment
        assignment, created = IssueAssignment.objects.get_or_create(
            issue=issue, user=user, defaults={"assigned_by": request.user}
        )

        if created:
            # Create event
            IssueEvent.objects.create(
                issue=issue,
                event_type="assigned",
                actor=request.user,
                metadata={"assignee": user.username},
            )
            message = f"{user.username} assigned successfully"
        else:
            message = f"{user.username} is already assigned"

    elif action == "remove":
        # Remove assignment
        deleted_count, _ = IssueAssignment.objects.filter(
            issue=issue, user=user
        ).delete()

        if deleted_count > 0:
            # Create event
            IssueEvent.objects.create(
                issue=issue,
                event_type="unassigned",
                actor=request.user,
                metadata={"assignee": user.username},
            )
            message = f"{user.username} unassigned successfully"
        else:
            message = f"{user.username} was not assigned"

    else:
        return JsonResponse(
            {"success": False, "error": 'Invalid action. Use "add" or "remove"'},
            status=400,
        )

    return JsonResponse(
        {
            "success": True,
            "message": message,
            "assignees": [
                {"id": a.id, "username": a.username} for a in issue.assignees.all()
            ],
        }
    )


@require_POST
@login_required
def api_issue_label(request, username, slug, issue_number):
    """
    API: Add/remove a label to/from an issue
    POST /<username>/<slug>/api/issues/<issue_number>/label/
    Body: { "label_id": 123, "action": "add" | "remove" }
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    issue = get_object_or_404(Issue, project=project, number=issue_number)

    # Check permissions
    if not project.can_edit(request.user):
        return JsonResponse(
            {"success": False, "error": "You do not have permission to modify labels"},
            status=403,
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    label_id = data.get("label_id")
    action = data.get("action", "add")

    if not label_id:
        return JsonResponse(
            {"success": False, "error": "Label ID is required"}, status=400
        )

    try:
        label = IssueLabel.objects.get(id=label_id, project=project)
    except IssueLabel.DoesNotExist:
        return JsonResponse({"success": False, "error": "Label not found"}, status=404)

    if action == "add":
        # Add label
        issue.labels.add(label)
        # Create event
        IssueEvent.objects.create(
            issue=issue,
            event_type="labeled",
            actor=request.user,
            metadata={"label": label.name, "color": label.color},
        )
        message = f'Label "{label.name}" added successfully'

    elif action == "remove":
        # Remove label
        issue.labels.remove(label)
        # Create event
        IssueEvent.objects.create(
            issue=issue,
            event_type="unlabeled",
            actor=request.user,
            metadata={"label": label.name, "color": label.color},
        )
        message = f'Label "{label.name}" removed successfully'

    else:
        return JsonResponse(
            {"success": False, "error": 'Invalid action. Use "add" or "remove"'},
            status=400,
        )

    return JsonResponse(
        {
            "success": True,
            "message": message,
            "labels": [
                {"id": l.id, "name": l.name, "color": l.color}
                for l in issue.labels.all()
            ],
        }
    )


@require_POST
@login_required
def api_issue_milestone(request, username, slug, issue_number):
    """
    API: Set or remove milestone for an issue
    POST /<username>/<slug>/api/issues/<issue_number>/milestone/
    Body: { "milestone_id": 123 } or { "milestone_id": null }
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    issue = get_object_or_404(Issue, project=project, number=issue_number)

    # Check permissions
    if not project.can_edit(request.user):
        return JsonResponse(
            {
                "success": False,
                "error": "You do not have permission to modify milestones",
            },
            status=403,
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    milestone_id = data.get("milestone_id")

    if milestone_id:
        # Set milestone
        try:
            milestone = IssueMilestone.objects.get(id=milestone_id, project=project)
            old_milestone = issue.milestone
            issue.milestone = milestone
            issue.save()

            # Create event
            IssueEvent.objects.create(
                issue=issue,
                event_type="milestoned",
                actor=request.user,
                metadata={"milestone": milestone.title},
            )

            message = f'Milestone "{milestone.title}" set successfully'
        except IssueMilestone.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Milestone not found"}, status=404
            )
    else:
        # Remove milestone
        old_milestone = issue.milestone
        if old_milestone:
            issue.milestone = None
            issue.save()

            # Create event
            IssueEvent.objects.create(
                issue=issue,
                event_type="demilestoned",
                actor=request.user,
                metadata={"milestone": old_milestone.title},
            )

            message = "Milestone removed successfully"
        else:
            message = "Issue has no milestone"

    return JsonResponse(
        {
            "success": True,
            "message": message,
            "milestone": {"id": issue.milestone.id, "title": issue.milestone.title}
            if issue.milestone
            else None,
        }
    )
