"""
Project-specific views for Scholar app.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.project_app.models import Project
from .models import BibTeXEnrichmentJob


def project_search(request, project_id):
    """Scholar search interface for a specific project."""
    project = get_object_or_404(Project, id=project_id)

    # Get user's projects for the selector (in case they want to switch)
    user_projects = []
    if request.user.is_authenticated:
        user_projects = Project.objects.filter(owner=request.user).order_by('-created_at')

    # Get recent enrichment jobs for this project
    recent_jobs = BibTeXEnrichmentJob.objects.filter(
        project=project
    ).select_related('project').order_by('-created_at')[:5]

    context = {
        'project': project,
        'user_projects': user_projects,
        'recent_jobs': recent_jobs,
        'current_project': project,  # Pre-select this project
    }
    return render(request, 'scholar_app/project_search.html', context)
