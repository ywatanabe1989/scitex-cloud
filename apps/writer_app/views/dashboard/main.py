"""Dashboard views for SciTeX Writer."""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ...services import DocumentService
from apps.project_app.models import Project
import logging

logger = logging.getLogger(__name__)


@login_required
def dashboard_view(request):
    """Writer dashboard showing user's manuscripts and recent activity.

    Shows:
    - Manuscript list
    - Recent compilations
    - Active collaboration sessions
    - Quick actions
    """
    context = {
        'user_projects': [],
        'recent_manuscripts': [],
        'recent_compilations': [],
    }

    try:
        # Get user's projects with writer enabled
        user_projects = Project.objects.filter(owner=request.user).order_by('-updated_at')
        context['user_projects'] = user_projects

        # TODO: Load recent manuscripts and compilations via service

    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")

    return render(request, 'writer_app/dashboard/main.html', context)


@login_required
def manuscript_list(request):
    """List of user's manuscripts across all projects.

    Shows:
    - All manuscripts
    - Project association
    - Status (draft, in progress, completed)
    - Word counts
    - Last modified
    """
    context = {
        'manuscripts': [],
    }

    try:
        # Get user's projects
        user_projects = Project.objects.filter(owner=request.user)

        # TODO: Load manuscripts from each project via service

    except Exception as e:
        logger.error(f"Error loading manuscripts: {e}")

    return render(request, 'writer_app/dashboard/manuscript_list.html', context)
