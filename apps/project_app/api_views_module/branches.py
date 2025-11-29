"""
Branch Switching API endpoint and helper functions.
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
import subprocess
import json
import logging

from apps.project_app.models import Project

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def api_switch_branch(request, username, slug):
    """
    API endpoint to switch the current branch for file browsing.

    This does NOT actually run `git checkout` - it only updates the session
    to read files from the selected branch using `git show branch:path`.

    POST /username/project/api/switch-branch/
    Body: {"branch": "branch-name"}

    Returns:
        JSON: {"success": True, "branch": "branch-name"} or error
    """
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access
    has_access = (
        project.owner == request.user
        or project.collaborators.filter(id=request.user.id).exists()
        or getattr(project, "visibility", None) == "public"
    )

    if not has_access:
        return JsonResponse(
            {"success": False, "error": "Permission denied"}, status=403
        )

    try:
        data = json.loads(request.body)
        branch_name = data.get("branch", "").strip()

        if not branch_name:
            return JsonResponse(
                {"success": False, "error": "Branch name is required"}, status=400
            )

        # Verify branch exists in the repository
        from apps.project_app.services.project_filesystem import (
            get_project_filesystem_manager,
        )

        manager = get_project_filesystem_manager(project.owner)
        project_path = manager.get_project_root_path(project)

        if not project_path or not project_path.exists():
            return JsonResponse(
                {"success": False, "error": "Project directory not found"}, status=404
            )

        # Verify branch exists
        result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            return JsonResponse(
                {"success": False, "error": "Failed to list branches"}, status=500
            )

        # Parse branch list and check if requested branch exists
        branches = []
        for line in result.stdout.split("\n"):
            line = line.strip()
            if line:
                # Remove * prefix and remotes/origin/ prefix
                branch = line.replace("*", "").strip()
                branch = branch.replace("remotes/origin/", "")
                if branch and branch not in branches:
                    branches.append(branch)

        if branch_name not in branches:
            return JsonResponse(
                {
                    "success": False,
                    "error": f"Branch '{branch_name}' not found. Available branches: {', '.join(branches)}",
                },
                status=404,
            )

        # Store branch in session (scoped by project)
        session_key = f"project_{project.id}_branch"
        request.session[session_key] = branch_name

        logger.info(
            f"Switched branch for project {project.slug} to {branch_name} (user: {request.user.username})"
        )

        return JsonResponse(
            {
                "success": True,
                "branch": branch_name,
                "message": f"Switched to branch '{branch_name}'",
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON in request body"}, status=400
        )
    except subprocess.TimeoutExpired:
        return JsonResponse(
            {"success": False, "error": "Git command timed out"}, status=500
        )
    except Exception as e:
        logger.error(f"Error switching branch: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def get_current_branch_from_session(request, project):
    """
    Helper function to get the current branch from session.

    Returns the session-stored branch for this project, or the repository's
    current branch if not set in session.

    Args:
        request: Django request object
        project: Project model instance

    Returns:
        str: Branch name (e.g., "develop", "main")
    """
    session_key = f"project_{project.id}_branch"

    # Check session first
    if session_key in request.session:
        return request.session[session_key]

    # Fall back to repository's current branch
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    if not project_path or not project_path.exists():
        return "main"  # Default fallback

    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0 and result.stdout.strip():
            branch = result.stdout.strip()
            # Store in session for next time
            request.session[session_key] = branch
            return branch

    except Exception as e:
        logger.debug(f"Error getting current branch: {e}")

    return "main"  # Final fallback
