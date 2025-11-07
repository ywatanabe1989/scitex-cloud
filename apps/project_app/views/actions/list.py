#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actions List View

Display workflow actions for a project (GitHub Actions-style).
"""
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.db.models import Count, Avg
import logging

from apps.project_app.models import Project
# TODO: Uncomment when workflow models are available
# from apps.project_app.models import Workflow, WorkflowRun

logger = logging.getLogger(__name__)


def actions_list(request, username, slug):
    """
    List all workflows for a project

    URL: /<username>/<slug>/actions/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)

    # Check permissions
    if not project.can_view(request.user):
        return HttpResponseForbidden("You don't have permission to view this project")

    # Get all workflows for this project
    workflows = Workflow.objects.filter(project=project).annotate(
        total_runs_count=Count('runs'),
        avg_duration=Avg('runs__duration_seconds')
    ).order_by('-updated_at')

    # Get recent workflow runs (last 10)
    recent_runs = WorkflowRun.objects.filter(
        workflow__project=project
    ).select_related('workflow', 'trigger_user').order_by('-created_at')[:10]

    # Calculate statistics
    total_workflows = workflows.count()
    enabled_workflows = workflows.filter(enabled=True).count()
    total_runs = WorkflowRun.objects.filter(workflow__project=project).count()
    successful_runs = WorkflowRun.objects.filter(
        workflow__project=project,
        conclusion='success'
    ).count()

    success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0

    context = {
        'project': project,
        'workflows': workflows,
        'recent_runs': recent_runs,
        'stats': {
            'total_workflows': total_workflows,
            'enabled_workflows': enabled_workflows,
            'total_runs': total_runs,
            'success_rate': round(success_rate, 1),
        },
    }

    return render(request, 'project_app/actions/list.html', context)


# EOF
