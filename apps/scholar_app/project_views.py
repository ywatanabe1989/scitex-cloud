"""
Project-specific views for Scholar app.
"""

from django.shortcuts import render, get_object_or_404
from apps.project_app.models import Project


def project_search(request, project_id):
    """Scholar search interface for a specific project."""
    project = get_object_or_404(Project, id=project_id)

    context = {
        'project': project,
    }
    return render(request, 'scholar_app/project_search.html', context)
