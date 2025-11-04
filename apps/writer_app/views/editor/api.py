#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-04 20:49:51 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/writer_app/views/editor/api.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./apps/writer_app/views/editor/api.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""API endpoints for editor operations."""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from ...services import DocumentService
from ...services import CompilerService
import json
import logging

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def save_section_api(request):
    """Save a manuscript section.

    POST body:
        {
            "project_id": <project_id>,
            "section_name": <section_name>,
            "content": <latex_content>
        }
    """
    try:
        data = json.loads(request.body)
        project_id = data.get("project_id")
        section_name = data.get("section_name")
        content = data.get("content")

        if not all([project_id, section_name, content is not None]):
            return JsonResponse(
                {"success": False, "error": "Missing required fields"},
                status=400,
            )

        # Save via service
        doc_service = DocumentService(project_id, request.user.id)
        doc_service.save_section(section_name, content)

        return JsonResponse(
            {
                "success": True,
                "message": f"Section {section_name} saved successfully",
            }
        )

    except Exception as e:
        logger.error(f"Error saving section: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def load_section_api(request):
    """Load a manuscript section.

    Query params:
        - project_id: Project ID
        - section_name: Section name
    """
    try:
        project_id = request.GET.get("project_id")
        section_name = request.GET.get("section_name")

        if not all([project_id, section_name]):
            return JsonResponse(
                {"success": False, "error": "Missing required parameters"},
                status=400,
            )

        # Load via service
        doc_service = DocumentService(project_id, request.user.id)
        content = doc_service.load_section(section_name)

        return JsonResponse({"success": True, "content": content})

    except Exception as e:
        logger.error(f"Error loading section: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def compile_api(request):
    """Compile manuscript to PDF.

    POST body:
        {
            "project_id": <project_id>,
            "doc_type": "manuscript" | "supplementary" | "revision"
        }
    """
    try:
        data = json.loads(request.body)
        project_id = data.get("project_id")
        doc_type = data.get("doc_type", "manuscript")

        if not project_id:
            return JsonResponse(
                {"success": False, "error": "project_id required"}, status=400
            )

        # Compile via service
        compilation_service = CompilerService(project_id, request.user.id)
        result = compilation_service.compile(doc_type)

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error compiling: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def compilation_status_api(request):
    """Get compilation job status.

    Query params:
        - job_id: Compilation job ID
    """
    try:
        job_id = request.GET.get("job_id")

        if not job_id:
            return JsonResponse(
                {"success": False, "error": "job_id required"}, status=400
            )

        # Get status via service
        compilation_service = CompilerService(None, request.user.id)
        status = compilation_service.get_status(job_id)

        return JsonResponse({"success": True, "status": status})

    except Exception as e:
        logger.error(f"Error getting status: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# URL pattern view aliases mapping to the API functions above
section_view = save_section_api
compile_preview_view = compile_api
compile_full_view = compile_api
compile_view = compile_api
section_history_view = load_section_api
section_diff_view = load_section_api
section_checkout_view = load_section_api
section_commit_view = save_section_api
pdf_view = compile_api
preview_pdf_view = compile_api
file_tree_view = load_section_api
read_tex_file_view = load_section_api
available_sections_view = load_section_api
save_sections_view = save_section_api
presence_update_view = save_section_api
presence_list_view = load_section_api

# EOF
