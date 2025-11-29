"""
Scientific Figure Editor Views
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from ..models import ScientificFigure, JournalPreset
from apps.project_app.services.project_utils import get_current_project


def figure_editor(request):
    """Main figure editor view - Sigma (SigmaPlot-inspired)"""
    # Allow visitor access with limited functionality
    if request.user.is_authenticated:
        figures = ScientificFigure.objects.filter(owner=request.user).order_by("-updated_at")
        current_project = get_current_project(request, user=request.user)
    else:
        figures = []
        current_project = None

    context = {
        "figures": figures,
        "journal_presets": JournalPreset.objects.filter(is_active=True),
        "current_project": current_project,
    }

    return render(request, "vis_app/editor.html", context)


@login_required
def figure_editor_legacy(request):
    """Legacy canvas-based figure editor (deprecated)"""
    # Get user's figures
    figures = ScientificFigure.objects.filter(owner=request.user).order_by("-updated_at")

    context = {
        "figures": figures,
        "journal_presets": JournalPreset.objects.filter(is_active=True),
    }

    return render(request, "vis_app/legacy/editor.html", context)


@login_required
@require_http_methods(["POST"])
def create_figure(request):
    """Create a new scientific figure"""
    title = request.POST.get("title", "Untitled Figure")
    layout = request.POST.get("layout", "1x1")

    figure = ScientificFigure.objects.create(
        owner=request.user,
        title=title,
        layout=layout,
    )

    messages.success(request, f"Figure '{title}' created successfully!")
    return redirect("vis:figure_detail", figure_id=figure.id)


@login_required
def figure_detail(request, figure_id):
    """Edit a specific figure"""
    figure = get_object_or_404(ScientificFigure, id=figure_id, owner=request.user)
    current_project = get_current_project(request, user=request.user)

    context = {
        "figure": figure,
        "figures": ScientificFigure.objects.filter(owner=request.user).order_by("-updated_at"),
        "journal_presets": JournalPreset.objects.filter(is_active=True),
        "current_project": current_project,
    }

    return render(request, "vis_app/editor.html", context)


@login_required
def figure_list(request):
    """List all figures for user"""
    figures = ScientificFigure.objects.filter(owner=request.user).order_by(
        "-updated_at"
    )

    context = {
        "figures": figures,
    }

    return render(request, "vis_app/figure_list.html", context)


# Export all view functions for backward compatibility
__all__ = [
    'figure_editor',
    'figure_editor_legacy',
    'create_figure',
    'figure_detail',
    'figure_list',
]


# EOF
