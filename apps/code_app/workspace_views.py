"""
Code Workspace Views - Simple file editor with project tree.

Provides IDE-like interface for editing and running scripts.
Gets project from header dropdown (like Scholar/Writer).
"""

import logging
from django.shortcuts import render
from django.http import HttpResponse
from apps.project_app.services import get_current_project

logger = logging.getLogger(__name__)


def code_workspace(request):
    """
    Main code workspace view - IDE interface.
    
    URL: /code/ (replaces index redirect)
    Gets project from header dropdown via get_current_project()
    """
    context = {
        "is_anonymous": not request.user.is_authenticated,
        "module_name": "Code",
        "module_icon": "fa-code",
    }
    
    if request.user.is_authenticated:
        # Get current project from header dropdown
        current_project = get_current_project(request, user=request.user)
        
        if current_project:
            # Check permissions (user must be owner or collaborator)
            if not (
                request.user == current_project.owner
                or request.user in current_project.collaborators.all()
            ):
                return HttpResponse("Unauthorized", status=403)
            
            context["current_project"] = current_project
            context["project"] = current_project
        else:
            # User authenticated but no project selected
            context["needs_project_creation"] = True
    else:
        # Anonymous user - allocate from visitor pool
        from apps.project_app.services.visitor_pool import VisitorPool
        
        try:
            visitor_project, visitor_user = VisitorPool.allocate_visitor(
                request.session
            )
        except Exception as e:
            logger.error(f"[Code] Visitor pool allocation failed: {e}", exc_info=True)
            context["pool_error"] = True
            context["pool_error_message"] = (
                "Visitor pool not initialized. Please run: python manage.py create_visitor_pool"
            )
            context["is_demo"] = True
            return render(request, "code_app/workspace.html", context)
        
        if not visitor_project:
            # Pool exhausted
            logger.warning("[Code] Visitor pool exhausted - all slots in use")
            context["pool_exhausted"] = True
            context["is_demo"] = True
            return render(request, "code_app/workspace.html", context)
        
        context["is_demo"] = True
        context["project"] = visitor_project
        context["current_project"] = visitor_project
        context["visitor_username"] = visitor_user.username if visitor_user else None
    
    return render(request, "code_app/workspace.html", context)
