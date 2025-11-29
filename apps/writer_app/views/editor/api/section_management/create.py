"""Section create view."""

from __future__ import annotations
import json
import logging
import re
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from .helpers import DOC_DIR_MAP

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def section_create_view(request, project_id):
    """Create a new custom section.

    POST body:
        {
            "doc_type": "manuscript|shared|supplementary|revision",
            "section_name": "background",  # lowercase, underscore-separated
            "section_label": "Background"  # optional, display label
        }
    """
    try:
        from .....services import WriterService
        from apps.project_app.models import Project

        # Get project
        project = Project.objects.get(id=project_id, owner=request.user)
        writer_service = WriterService(project_id, request.user.id)

        # Parse request body
        data = json.loads(request.body)
        doc_type = data.get("doc_type", "manuscript")
        section_name = data.get("section_name", "").strip().lower()
        section_label = data.get("section_label", "").strip()

        if not section_name:
            return JsonResponse(
                {"success": False, "error": "Section name is required"}, status=400
            )

        # Validate section name format
        if not re.match(r"^[a-z0-9_]+$", section_name):
            return JsonResponse(
                {
                    "success": False,
                    "error": "Section name must contain only lowercase letters, numbers, and underscores",
                },
                status=400,
            )

        if doc_type not in DOC_DIR_MAP:
            return JsonResponse(
                {"success": False, "error": f"Invalid doc_type: {doc_type}"}, status=400
            )

        # Create section file
        section_dir = writer_service.writer_dir / DOC_DIR_MAP[doc_type]
        section_file = section_dir / f"{section_name}.tex"

        if section_file.exists():
            return JsonResponse(
                {"success": False, "error": f"Section '{section_name}' already exists"},
                status=400,
            )

        # Create directory if needed
        section_dir.mkdir(parents=True, exist_ok=True)

        # Create empty section file with header comment
        section_file.write_text(
            f"% {section_label or section_name.replace('_', ' ').title()}\n\n",
            encoding="utf-8",
        )

        logger.info(f"[SectionCreate] Created section: {section_name} in {doc_type}")

        return JsonResponse(
            {
                "success": True,
                "section_id": f"{doc_type}/{section_name}",
                "section_name": section_name,
                "section_label": section_label
                or section_name.replace("_", " ").title(),
                "message": "Section created successfully",
            }
        )

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"[SectionCreate] Error: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
