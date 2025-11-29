"""
Project Social Interaction APIs - Watch, Star, Fork, Stats
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.db import transaction
import logging

from apps.project_app.models import (
    Project,
    ProjectWatch,
    ProjectStar,
    ProjectFork,
)

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def api_project_watch(request, username, slug):
    """
    Toggle watch status for a project

    Returns:
        JSON with success status and new watch state
    """
    try:
        user = get_object_or_404(User, username=username)
        project = get_object_or_404(Project, slug=slug, owner=user)

        # Check if user has access to watch
        has_access = (
            project.owner == request.user
            or project.collaborators.filter(id=request.user.id).exists()
            or project.visibility == "public"
        )

        if not has_access:
            return JsonResponse(
                {"success": False, "error": "Permission denied"}, status=403
            )

        # Toggle watch
        watch, created = ProjectWatch.objects.get_or_create(
            user=request.user,
            project=project,
            defaults={"notification_settings": "all"},
        )

        if not created:
            # Already watching, so unwatch
            watch.delete()
            is_watching = False
        else:
            is_watching = True

        # Get updated count
        watch_count = project.project_watchers.count()

        return JsonResponse(
            {
                "success": True,
                "is_watching": is_watching,
                "watch_count": watch_count,
                "message": "Watching" if is_watching else "Unwatched",
            }
        )

    except Exception as e:
        logger.error(f"Error toggling watch for project {slug}: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_project_star(request, username, slug):
    """
    Toggle star status for a project

    Returns:
        JSON with success status and new star state
    """
    try:
        user = get_object_or_404(User, username=username)
        project = get_object_or_404(Project, slug=slug, owner=user)

        # Check if user has access to star
        has_access = (
            project.owner == request.user
            or project.collaborators.filter(id=request.user.id).exists()
            or project.visibility == "public"
        )

        if not has_access:
            return JsonResponse(
                {"success": False, "error": "Permission denied"}, status=403
            )

        # Toggle star
        star, created = ProjectStar.objects.get_or_create(
            user=request.user, project=project
        )

        if not created:
            # Already starred, so unstar
            star.delete()
            is_starred = False
        else:
            is_starred = True

        # Get updated count
        star_count = project.project_stars_set.count()

        return JsonResponse(
            {
                "success": True,
                "is_starred": is_starred,
                "star_count": star_count,
                "message": "Starred" if is_starred else "Unstarred",
            }
        )

    except Exception as e:
        logger.error(f"Error toggling star for project {slug}: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_project_fork(request, username, slug):
    """
    Fork a project (create a copy under the current user's account)

    Returns:
        JSON with success status and forked project details
    """
    try:
        user = get_object_or_404(User, username=username)
        original_project = get_object_or_404(Project, slug=slug, owner=user)

        # Check if user has access to fork
        has_access = (
            original_project.owner == request.user
            or original_project.collaborators.filter(id=request.user.id).exists()
            or original_project.visibility == "public"
        )

        if not has_access:
            return JsonResponse(
                {"success": False, "error": "Permission denied"}, status=403
            )

        # Check if user already forked this project
        existing_fork = ProjectFork.objects.filter(
            user=request.user, original_project=original_project
        ).first()

        if existing_fork:
            return JsonResponse(
                {
                    "success": False,
                    "error": "You have already forked this project",
                    "forked_project_url": f"/{request.user.username}/{existing_fork.forked_project.slug}/",
                },
                status=400,
            )

        # Create the fork
        with transaction.atomic():
            # Generate unique slug for fork
            base_slug = original_project.slug
            fork_slug = base_slug
            counter = 1
            while Project.objects.filter(slug=fork_slug, owner=request.user).exists():
                fork_slug = f"{base_slug}-{counter}"
                counter += 1

            # Create forked project
            forked_project = Project.objects.create(
                name=f"{original_project.name} (fork)",
                slug=fork_slug,
                description=f"Forked from {username}/{original_project.name}\n\n{original_project.description}",
                owner=request.user,
                visibility=original_project.visibility,
                # Copy other relevant fields
                source_code_url=original_project.source_code_url,
                current_branch=original_project.current_branch,
            )

            # Create fork record
            fork_record = ProjectFork.objects.create(
                user=request.user,
                original_project=original_project,
                forked_project=forked_project,
            )

            # Get updated fork count
            fork_count = original_project.project_forks_set.count()

            return JsonResponse(
                {
                    "success": True,
                    "message": "Project forked successfully",
                    "forked_project": {
                        "id": forked_project.id,
                        "name": forked_project.name,
                        "slug": forked_project.slug,
                        "url": f"/{request.user.username}/{forked_project.slug}/",
                    },
                    "fork_count": fork_count,
                }
            )

    except Exception as e:
        logger.error(f"Error forking project {slug}: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def api_project_stats(request, username, slug):
    """
    Get watch/star/fork counts and user's current status

    Returns:
        JSON with counts and user's interaction status
    """
    try:
        user = get_object_or_404(User, username=username)
        project = get_object_or_404(Project, slug=slug, owner=user)

        # Check if user has access
        has_access = (
            project.owner == request.user
            or project.collaborators.filter(id=request.user.id).exists()
            or project.visibility == "public"
        )

        if not has_access:
            return JsonResponse(
                {"success": False, "error": "Permission denied"}, status=403
            )

        # Get counts
        watch_count = project.project_watchers.count()
        star_count = project.project_stars_set.count()
        fork_count = project.project_forks_set.count()

        # Check user's current status
        is_watching = ProjectWatch.objects.filter(
            user=request.user, project=project
        ).exists()

        is_starred = ProjectStar.objects.filter(
            user=request.user, project=project
        ).exists()

        has_forked = ProjectFork.objects.filter(
            user=request.user, original_project=project
        ).exists()

        return JsonResponse(
            {
                "success": True,
                "stats": {
                    "watch_count": watch_count,
                    "star_count": star_count,
                    "fork_count": fork_count,
                },
                "user_status": {
                    "is_watching": is_watching,
                    "is_starred": is_starred,
                    "has_forked": has_forked,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error getting stats for project {slug}: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)
