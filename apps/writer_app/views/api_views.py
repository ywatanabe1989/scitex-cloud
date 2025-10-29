"""
REST API views for Writer operations.

Provides endpoints for section reading/writing, compilation, and git operations.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from pathlib import Path

from apps.project_app.models import Project
from ..services.writer_service import WriterService
from scitex import logging

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET", "POST"])
def section_view(request, project_id, section_name):
    """Read or write a manuscript section.

    GET: Read section content
    POST: Write section content and optionally commit

    Query params (GET):
        doc_type: 'manuscript', 'supplementary', or 'revision' (default: manuscript)

    POST body:
        {
            "content": "section text",
            "commit_message": "optional commit message" (if provided, auto-commits)
        }
    """
    try:
        # Verify project access
        project = Project.objects.get(id=project_id, owner=request.user)
        service = WriterService(project_id, request.user.id)

        if request.method == "GET":
            doc_type = request.GET.get("doc_type", "manuscript")
            content = service.read_section(section_name, doc_type)
            return JsonResponse({
                "success": True,
                "section": section_name,
                "doc_type": doc_type,
                "content": content,
            })

        elif request.method == "POST":
            data = json.loads(request.body)
            content = data.get("content")
            commit_message = data.get("commit_message")
            doc_type = data.get("doc_type", "manuscript")

            if content is None:
                return JsonResponse({
                    "success": False,
                    "error": "Missing 'content' in request body",
                }, status=400)

            # Write section
            service.write_section(section_name, content, doc_type)

            # Optionally commit
            if commit_message:
                service.commit_section(section_name, commit_message, doc_type)
                return JsonResponse({
                    "success": True,
                    "section": section_name,
                    "message": f"Section updated and committed: {commit_message}",
                })
            else:
                return JsonResponse({
                    "success": True,
                    "section": section_name,
                    "message": "Section updated (not committed)",
                })

    except Project.DoesNotExist:
        return JsonResponse({"success": False, "error": "Project not found"}, status=404)
    except Exception as e:
        logger.error(f"Section view error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def compile_view(request, project_id):
    """Compile a manuscript document.

    POST body:
        {
            "doc_type": "manuscript", "supplementary", or "revision" (default: manuscript)
            "timeout": compilation timeout in seconds (default: 300)
        }
    """
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        service = WriterService(project_id, request.user.id)

        data = json.loads(request.body)
        doc_type = data.get("doc_type", "manuscript")
        timeout = data.get("timeout", 300)

        # Compile based on document type
        if doc_type == "supplementary":
            result = service.compile_supplementary(timeout=timeout)
        elif doc_type == "revision":
            result = service.compile_revision(timeout=timeout)
        else:  # manuscript
            result = service.compile_manuscript(timeout=timeout)

        return JsonResponse({
            "success": result["success"],
            "doc_type": doc_type,
            "output_pdf": result["output_pdf"],
            "log": result["log"],
            "error": result["error"],
        })

    except Project.DoesNotExist:
        return JsonResponse({"success": False, "error": "Project not found"}, status=404)
    except Exception as e:
        logger.error(f"Compilation view error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def section_history_view(request, project_id, section_name):
    """Get git history for a section.

    Query params:
        doc_type: 'manuscript', 'supplementary', or 'revision' (default: manuscript)
    """
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        service = WriterService(project_id, request.user.id)

        doc_type = request.GET.get("doc_type", "manuscript")
        history = service.get_section_history(section_name, doc_type)

        return JsonResponse({
            "success": True,
            "section": section_name,
            "doc_type": doc_type,
            "history": history,
        })

    except Project.DoesNotExist:
        return JsonResponse({"success": False, "error": "Project not found"}, status=404)
    except Exception as e:
        logger.error(f"History view error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def section_diff_view(request, project_id, section_name):
    """Get uncommitted changes for a section.

    Query params:
        doc_type: 'manuscript', 'supplementary', or 'revision' (default: manuscript)
        ref: git reference to compare against (default: HEAD)
    """
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        service = WriterService(project_id, request.user.id)

        doc_type = request.GET.get("doc_type", "manuscript")
        ref = request.GET.get("ref", "HEAD")
        diff = service.get_section_diff(section_name, ref, doc_type)

        return JsonResponse({
            "success": True,
            "section": section_name,
            "doc_type": doc_type,
            "ref": ref,
            "diff": diff,
            "has_changes": bool(diff),
        })

    except Project.DoesNotExist:
        return JsonResponse({"success": False, "error": "Project not found"}, status=404)
    except Exception as e:
        logger.error(f"Diff view error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def section_checkout_view(request, project_id, section_name):
    """Restore a section from git history.

    POST body:
        {
            "ref": "HEAD~1",  # Git reference (commit, branch, tag, etc.)
            "doc_type": "manuscript"  # (optional, default: manuscript)
        }
    """
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        service = WriterService(project_id, request.user.id)

        data = json.loads(request.body)
        ref = data.get("ref", "HEAD")
        doc_type = data.get("doc_type", "manuscript")

        success = service.checkout_section(section_name, ref, doc_type)

        return JsonResponse({
            "success": success,
            "section": section_name,
            "ref": ref,
            "message": f"Section restored to {ref}" if success else "Checkout failed",
        })

    except Project.DoesNotExist:
        return JsonResponse({"success": False, "error": "Project not found"}, status=404)
    except Exception as e:
        logger.error(f"Checkout view error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def pdf_view(request, project_id):
    """Get path to compiled PDF.

    Query params:
        doc_type: 'manuscript', 'supplementary', or 'revision' (default: manuscript)
    """
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        service = WriterService(project_id, request.user.id)

        doc_type = request.GET.get("doc_type", "manuscript")
        pdf_path = service.get_pdf(doc_type)

        return JsonResponse({
            "success": pdf_path is not None,
            "doc_type": doc_type,
            "pdf_path": pdf_path,
        })

    except Project.DoesNotExist:
        return JsonResponse({"success": False, "error": "Project not found"}, status=404)
    except Exception as e:
        logger.error(f"PDF view error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def available_sections_view(request, project_id):
    """Get list of available sections for each document type."""
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        service = WriterService(project_id, request.user.id)

        # Get available sections from Writer
        sections = {
            "manuscript": [
                "abstract",
                "introduction",
                "methods",
                "results",
                "discussion",
                "conclusion",
                "title",
                "authors",
                "keywords",
                "highlights",
                "graphical_abstract",
            ],
            "supplementary": ["content", "methods", "results"],
            "revision": ["response", "changes"],
        }

        return JsonResponse({
            "success": True,
            "sections": sections,
        })

    except Project.DoesNotExist:
        return JsonResponse({"success": False, "error": "Project not found"}, status=404)
    except Exception as e:
        logger.error(f"Available sections view error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)
