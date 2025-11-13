"""
Project-specific views for Viz app.
"""

from django.shortcuts import render, get_object_or_404
from apps.project_app.models import Project


def project_viz(request, project_id):
    """Viz interface for a specific project."""
    project = get_object_or_404(Project, id=project_id)

    context = {
        "project": project,
    }
    return render(request, "viz_app/project_viz.html", context)
