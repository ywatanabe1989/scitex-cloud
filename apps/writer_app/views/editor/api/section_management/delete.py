"""Section delete view."""

from __future__ import annotations
import logging
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from .helpers import DOC_DIR_MAP, CORE_SECTIONS

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["DELETE"])
def section_delete_view(request, project_id, section_name):
    """Delete a custom section.

    Only custom sections can be deleted (not core sections like abstract, introduction, etc.).
    """
    try:
        from .....services import WriterService
        from apps.project_app.models import Project
        from .....configs.sections_config import parse_section_id

        # Get project
        project = Project.objects.get(id=project_id, owner=request.user)
        writer_service = WriterService(project_id, request.user.id)

        # Parse section ID
        category, name = parse_section_id(section_name)

        # Prevent deletion of core sections
        if name in CORE_SECTIONS:
            return JsonResponse(
                {"success": False, "error": f"Cannot delete core section: {name}"},
                status=400,
            )

        section_dir = writer_service.writer_dir / DOC_DIR_MAP.get(
            category, "01_manuscript/contents"
        )
        section_file = section_dir / f"{name}.tex"

        if not section_file.exists():
            return JsonResponse(
                {"success": False, "error": f"Section file not found: {name}.tex"},
                status=404,
            )

        # Delete the file
        section_file.unlink()

        logger.info(f"[SectionDelete] Deleted section: {name} from {category}")

        return JsonResponse(
            {"success": True, "message": f"Section '{name}' deleted successfully"}
        )

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"[SectionDelete] Error: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
