"""Section toggle exclude view."""

from __future__ import annotations
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from ...auth_utils import api_login_optional, get_user_for_request

logger = logging.getLogger(__name__)


@api_login_optional
@require_http_methods(["POST"])
def section_toggle_exclude_view(request, project_id, section_name):
    """Toggle section include/exclude state for compilation.

    POST body:
        {
            "excluded": true/false
        }

    This will be stored in a project-level configuration file.
    """
    try:
        from apps.project_app.models import Project
        from .....configs.sections_config import parse_section_id

        # Get effective user (authenticated or visitor)
        user, is_visitor = get_user_for_request(request, project_id)
        if not user:
            return JsonResponse(
                {"success": False, "error": "Invalid session"}, status=403
            )

        # Get project
        project = Project.objects.get(id=project_id)

        # Parse request body
        data = json.loads(request.body)
        excluded = data.get("excluded", False)

        # Parse section ID
        category, name = parse_section_id(section_name)

        # Store in project configuration file
        from .....services import WriterService

        writer_service = WriterService(project_id, user.id)
        config_file = writer_service.writer_dir / ".scitex_section_config.json"

        # Load existing config
        config = {}
        if config_file.exists():
            config = json.loads(config_file.read_text())

        # Update excluded sections list
        if "excluded_sections" not in config:
            config["excluded_sections"] = []

        section_id = f"{category}/{name}"
        if excluded:
            if section_id not in config["excluded_sections"]:
                config["excluded_sections"].append(section_id)
        else:
            if section_id in config["excluded_sections"]:
                config["excluded_sections"].remove(section_id)

        # Save config
        config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")

        logger.info(f"[SectionToggleExclude] {section_name} excluded={excluded}")

        return JsonResponse(
            {
                "success": True,
                "excluded": excluded,
                "message": f"Section {'excluded' if excluded else 'included'}",
            }
        )

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"[SectionToggleExclude] Error: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
