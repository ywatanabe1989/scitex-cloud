"""Section move views (up/down)."""

from __future__ import annotations
import json
import logging
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def section_move_up_view(request, project_id, section_name):
    """Move section up in the compilation order.

    This will be stored in a project-level configuration file.
    """
    try:
        from apps.project_app.models import Project
        from .....configs.sections_config import parse_section_id
        from .....services import WriterService

        # Get project
        project = Project.objects.get(id=project_id, owner=request.user)
        writer_service = WriterService(project_id, request.user.id)

        # Parse section ID
        category, name = parse_section_id(section_name)
        section_id = f"{category}/{name}"

        # Load section order configuration
        config_file = writer_service.writer_dir / ".scitex_section_config.json"
        config = {}
        if config_file.exists():
            config = json.loads(config_file.read_text())

        if "section_order" not in config:
            config["section_order"] = {}

        if category not in config["section_order"]:
            config["section_order"][category] = []

        order = config["section_order"][category]

        # Find current index
        if section_id in order:
            idx = order.index(section_id)
            if idx > 0:
                # Swap with previous
                order[idx], order[idx - 1] = order[idx - 1], order[idx]
                config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")

                logger.info(f"[SectionMoveUp] Moved {section_name} up")

                return JsonResponse({"success": True, "message": "Section moved up"})
            else:
                return JsonResponse(
                    {"success": False, "error": "Section is already at the top"},
                    status=400,
                )
        else:
            return JsonResponse(
                {"success": False, "error": "Section not in custom order"}, status=400
            )

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"[SectionMoveUp] Error: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def section_move_down_view(request, project_id, section_name):
    """Move section down in the compilation order.

    This will be stored in a project-level configuration file.
    """
    try:
        from apps.project_app.models import Project
        from .....configs.sections_config import parse_section_id
        from .....services import WriterService

        # Get project
        project = Project.objects.get(id=project_id, owner=request.user)
        writer_service = WriterService(project_id, request.user.id)

        # Parse section ID
        category, name = parse_section_id(section_name)
        section_id = f"{category}/{name}"

        # Load section order configuration
        config_file = writer_service.writer_dir / ".scitex_section_config.json"
        config = {}
        if config_file.exists():
            config = json.loads(config_file.read_text())

        if "section_order" not in config:
            config["section_order"] = {}

        if category not in config["section_order"]:
            config["section_order"][category] = []

        order = config["section_order"][category]

        # Find current index
        if section_id in order:
            idx = order.index(section_id)
            if idx < len(order) - 1:
                # Swap with next
                order[idx], order[idx + 1] = order[idx + 1], order[idx]
                config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")

                logger.info(f"[SectionMoveDown] Moved {section_name} down")

                return JsonResponse({"success": True, "message": "Section moved down"})
            else:
                return JsonResponse(
                    {"success": False, "error": "Section is already at the bottom"},
                    status=400,
                )
        else:
            return JsonResponse(
                {"success": False, "error": "Section not in custom order"}, status=400
            )

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"[SectionMoveDown] Error: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
