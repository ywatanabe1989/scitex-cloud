#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-04 20:49:51 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/writer_app/views/editor/api.py
# ----------------------------------------
from __future__ import annotations
import os

__FILE__ = "./apps/writer_app/views/editor/api.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""API endpoints for editor operations."""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from ...services import CompilerService
from .auth_utils import api_login_optional, get_user_for_request
import json
import logging
import uuid
import threading

logger = logging.getLogger(__name__)

# In-memory compilation job storage
# Format: {job_id: {'status': str, 'progress': int, 'step': str, 'log': list, 'result': dict}}
COMPILATION_JOBS = {}


@api_login_optional
@require_http_methods(["GET", "POST"])
def section_view(request, project_id, section_name):
    """Read or write a section's .tex file from/to disk.

    Supports hierarchical section IDs (e.g., "shared/title", "manuscript/abstract").

    GET: Read section content from disk - returns SectionReadResponse
    POST: Write section content to disk
    """
    try:
        from scitex.writer.dataclasses.results import SectionReadResponse
        from ...services import WriterService
        from apps.project_app.models import Project
        from ...configs.sections_config import parse_section_id

        # Get project
        project = Project.objects.get(id=project_id)

        # Get effective user (authenticated or visitor)
        user, is_visitor = get_user_for_request(request, project_id)
        if not user:
            return JsonResponse(
                {"success": False, "error": "Invalid session"}, status=403
            )

        writer_service = WriterService(project_id, user.id)

        # Parse section ID to get category and name
        category, name = parse_section_id(section_name)

        # GET: Read section from disk
        if request.method == "GET":
            try:
                # Allow query param to override category for legacy compatibility
                doc_type = request.GET.get("doc_type", category)

                logger.info(
                    f"[SectionView GET] Reading section: {section_name} -> category={category}, name={name}, doc_type={doc_type}"
                )

                # Read content from disk using WriterService
                content = writer_service.read_section(name, doc_type)

                # Validate content was actually read
                if content is None:
                    raise ValueError(f"read_section returned None for {name}")

                logger.info(f"[SectionView GET] Read {len(content)} chars for {name}")

                # Build section file path for reference
                doc_dir_map = {
                    "manuscript": "01_manuscript/contents",
                    "supplementary": "02_supplementary/contents",
                    "revision": "03_revision/contents",
                    "shared": "shared",
                }
                section_dir = writer_service.writer_dir / doc_dir_map.get(
                    doc_type, "01_manuscript/contents"
                )
                file_path = section_dir / f"{name}.tex"

                # Create response
                response = SectionReadResponse.create_success(
                    content=content,
                    section_name=name,
                    section_id=section_name,
                    doc_type=doc_type,
                    file_path=file_path if file_path.exists() else None,
                )

                # Validate before returning
                response.validate()
                return JsonResponse(response.to_dict())

            except Exception as e:
                logger.error(
                    f"Error reading section {section_name}: {e}", exc_info=True
                )
                response = SectionReadResponse.create_failure(
                    section_id=section_name,
                    error_message=f"Failed to read section: {str(e)}",
                )
                return JsonResponse(response.to_dict(), status=500)

        # POST: Write section to disk
        elif request.method == "POST":
            try:
                data = json.loads(request.body)
                content = data.get("content")
                # Allow body doc_type to override, but prefer parsed category
                doc_type = data.get("doc_type", category)

                # Validate content
                if content is None:
                    response = SectionReadResponse.create_failure(
                        section_id=section_name, error_message="Content is required"
                    )
                    return JsonResponse(response.to_dict(), status=400)

                if not isinstance(content, str):
                    response = SectionReadResponse.create_failure(
                        section_id=section_name,
                        error_message=f"Content must be string, got {type(content).__name__}",
                    )
                    return JsonResponse(response.to_dict(), status=400)

                logger.info(
                    f"[SectionView POST] Writing section: {section_name} -> category={category}, name={name}, doc_type={doc_type}, length: {len(content)}"
                )

                # Write content to disk using WriterService
                success = writer_service.write_section(name, content, doc_type)

                if success:
                    # Return a read response with the saved content
                    response = SectionReadResponse.create_success(
                        content=content,
                        section_name=name,
                        section_id=section_name,
                        doc_type=doc_type,
                    )
                    response.validate()
                    return JsonResponse(response.to_dict())
                else:
                    response = SectionReadResponse.create_failure(
                        section_id=section_name,
                        error_message="write_section returned False (unknown reason)",
                    )
                    return JsonResponse(response.to_dict(), status=500)

            except Exception as e:
                logger.error(
                    f"Error writing section {section_name}: {e}", exc_info=True
                )
                response = SectionReadResponse.create_failure(
                    section_id=section_name,
                    error_message=f"Failed to write section: {str(e)}",
                )
                return JsonResponse(response.to_dict(), status=500)

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"Error in section_view: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@api_login_optional
@require_http_methods(["POST"])
def compile_api(request, project_id):
    """Compile LaTeX content to PDF.

    POST body:
        {
            "content": <latex_content>,
            "doc_type": "manuscript" (optional),
            "color_mode": "light" (optional: light, dark, sepia, paper),
            "section_name": <section_name> (optional, for naming)
        }
    """
    try:
        from ...services import WriterService
        from apps.project_app.models import Project

        data = json.loads(request.body)
        content = data.get("content", "")
        doc_type = data.get("doc_type", "manuscript")
        color_mode = data.get("color_mode", "light")
        section_name = data.get("section_name", "preview")

        logger.info(
            f"[CompileAPI] project_id={project_id}, section={section_name}, color_mode={color_mode}"
        )

        # Get project and service
        project = Project.objects.get(id=project_id)

        # Get effective user (authenticated or visitor)
        user, is_visitor = get_user_for_request(request, project_id)
        if not user:
            return JsonResponse(
                {"success": False, "error": "Invalid session"}, status=403
            )

        writer_service = WriterService(project_id, user.id)

        # Compile preview
        result = writer_service.compile_preview(
            latex_content=content,
            timeout=60,
            color_mode=color_mode,
            section_name=section_name,
            doc_type=doc_type,
        )

        logger.info(f"[CompileAPI] Compilation result: success={result.get('success')}")

        # Convert absolute filesystem path to servable URL
        if result.get("success") and result.get("output_pdf"):
            from pathlib import Path

            pdf_path = Path(result["output_pdf"])
            # Convert: /app/data/users/USER/PROJECT/scitex/writer/.preview/preview-abstract-light.pdf
            # To URL: /writer/api/project/101/pdf/preview-abstract-light.pdf
            pdf_filename = pdf_path.name
            result["output_pdf"] = (
                f"/writer/api/project/{project_id}/pdf/{pdf_filename}"
            )
            logger.info(
                f"[CompileAPI] Converted PDF path to URL: {result['output_pdf']}"
            )
            logger.info(
                f"[CompileAPI] Note: Alternate theme will be compiled in background for instant switching"
            )

        return JsonResponse(result)

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
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


def _scan_project_sections(project_path):
    """Scan project directories to build section hierarchy from actual files.

    Excludes:
    - Symlinked files (e.g., authors.tex symlinked from shared to manuscript)
    - System files (wordcount.tex, .compiled.tex, etc.)
    - Template files
    - Subdirectories (figures/, tables/, latex_styles/, etc.)

    Args:
        project_path: Path to project root (contains 00_shared/, 01_manuscript/, etc.)

    Returns:
        dict: Hierarchy matching SECTION_HIERARCHY structure
    """

    hierarchy = {
        "shared": {
            "label": "Shared",
            "description": "Shared content across all documents",
            "sections": [],
        },
        "manuscript": {
            "label": "Manuscript",
            "description": "Main manuscript content",
            "sections": [],
        },
        "supplementary": {
            "label": "Supplementary",
            "description": "Supplementary materials",
            "sections": [],
        },
        "revision": {
            "label": "Revision",
            "description": "Revision materials",
            "supports_crud": True,
            "sections": [],
        },
    }

    # System files to skip
    skip_files = {
        "wordcount.tex",
        ".compiled.tex",
        "compiled.tex",
        "main.tex",
        "preamble.tex",
        "base.tex",
    }

    # Load excluded sections from config
    config_file = project_path / ".scitex_section_config.json"
    excluded_sections = []
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text())
            excluded_sections = config.get("excluded_sections", [])
        except Exception as e:
            logger.warning(f"Failed to load section config: {e}")
            excluded_sections = []

    # Scan 00_shared/ directory (renamed from shared/ in v2.0.0-rc1)
    shared_dir = project_path / "00_shared"
    if shared_dir.exists() and shared_dir.is_dir():
        for tex_file in sorted(shared_dir.glob("*.tex")):
            if tex_file.name in skip_files:
                continue
            if tex_file.is_symlink():
                logger.debug(f"Skipping symlink: {tex_file}")
                continue

            section_name = tex_file.stem
            section_id = f"shared/{section_name}"
            hierarchy["shared"]["sections"].append(
                {
                    "id": section_id,
                    "name": section_name,
                    "label": section_name.replace("_", " ").title(),
                    "path": str(tex_file.relative_to(project_path)),
                    "excluded": section_id in excluded_sections,
                }
            )

    # Scan manuscript/contents/ directory
    manuscript_dir = project_path / "01_manuscript" / "contents"
    manuscript_sections = []

    if manuscript_dir.exists() and manuscript_dir.is_dir():
        for tex_file in sorted(manuscript_dir.glob("*.tex")):
            if tex_file.name in skip_files:
                continue
            if tex_file.is_symlink():
                logger.debug(f"Skipping symlink: {tex_file}")
                continue

            section_name = tex_file.stem
            # Mark optional sections (can be excluded from compilation)
            # Core sections: abstract, introduction, methods, discussion, results
            # Optional sections: everything else
            optional_sections = [
                "highlights",
                "graphical_abstract",
                "additional_info",
                "data_availability",
                "conclusion",
                "acknowledgments",
                "funding",
                "conflict_of_interest",
            ]
            section_id = f"manuscript/{section_name}"
            manuscript_sections.append(
                {
                    "id": section_id,
                    "name": section_name,
                    "label": section_name.replace("_", " ").title(),
                    "path": str(tex_file.relative_to(project_path)),
                    "optional": section_name in optional_sections,
                    "excluded": section_id in excluded_sections,
                }
            )

    # Define preferred order for manuscript sections (matches standard manuscript structure)
    section_order = {
        "abstract": 0,
        "introduction": 1,
        "methods": 2,
        "discussion": 3,
        "results": 4,
        "highlights": 5,
        "graphical_abstract": 6,
        "additional_info": 7,
        "data_availability": 8,
        "conclusion": 9,
        # Everything else goes after
    }

    # Sort sections by preferred order, then alphabetically
    manuscript_sections.sort(
        key=lambda s: (section_order.get(s["name"], 999), s["name"])
    )

    # Add sorted sections to hierarchy
    hierarchy["manuscript"]["sections"] = manuscript_sections

    # Add "Full Manuscript" compiled PDF section at the END
    compiled_tex_path = project_path / "01_manuscript" / "manuscript.tex"
    if compiled_tex_path.exists():
        hierarchy["manuscript"]["sections"].append(
            {
                "id": "manuscript/compiled_pdf",
                "name": "compiled_pdf",
                "label": "📄 Full Manuscript",
                "path": str(compiled_tex_path.relative_to(project_path)),
                "view_only": True,
                "is_compiled": True,
                "no_preview": True,
            }
        )

    # Scan supplementary/contents/ directory
    supplementary_dir = project_path / "02_supplementary" / "contents"
    if supplementary_dir.exists() and supplementary_dir.is_dir():
        for tex_file in sorted(supplementary_dir.glob("*.tex")):
            if tex_file.name in skip_files:
                continue
            if tex_file.is_symlink():
                logger.debug(f"Skipping symlink: {tex_file}")
                continue

            section_name = tex_file.stem
            section_id = f"supplementary/{section_name}"
            hierarchy["supplementary"]["sections"].append(
                {
                    "id": section_id,
                    "name": section_name,
                    "label": f"Supplementary {section_name.replace('_', ' ').title()}",
                    "path": str(tex_file.relative_to(project_path)),
                    "excluded": section_id in excluded_sections,
                }
            )

    # Add "Full Supplementary File" compiled PDF section at the END
    supplementary_tex_path = project_path / "02_supplementary" / "supplementary.tex"
    if supplementary_tex_path.exists():
        hierarchy["supplementary"]["sections"].append(
            {
                "id": "supplementary/compiled_pdf",
                "name": "compiled_pdf",
                "label": "📄 Full Supplementary File",
                "path": str(supplementary_tex_path.relative_to(project_path)),
                "view_only": True,
                "is_compiled": True,
                "no_preview": True,
            }
        )

    # Scan revision/contents/ directory
    revision_dir = project_path / "03_revision" / "contents"
    if revision_dir.exists() and revision_dir.is_dir():
        for tex_file in sorted(revision_dir.glob("*.tex")):
            if tex_file.name in skip_files:
                continue
            if tex_file.is_symlink():
                logger.debug(f"Skipping symlink: {tex_file}")
                continue

            section_name = tex_file.stem
            section_id = f"revision/{section_name}"
            hierarchy["revision"]["sections"].append(
                {
                    "id": section_id,
                    "name": section_name,
                    "label": f"Revision {section_name.replace('_', ' ').title()}",
                    "path": str(tex_file.relative_to(project_path)),
                    "excluded": section_id in excluded_sections,
                }
            )

    # Add "Full Revision" compiled PDF section at the END
    revision_tex_path = project_path / "03_revision" / "revision.tex"
    if revision_tex_path.exists():
        hierarchy["revision"]["sections"].append(
            {
                "id": "revision/compiled_pdf",
                "name": "compiled_pdf",
                "label": "📄 Full Revision",
                "path": str(revision_tex_path.relative_to(project_path)),
                "view_only": True,
                "is_compiled": True,
                "no_preview": True,
            }
        )

    logger.info(
        f"Scanned project sections: {sum(len(cat['sections']) for cat in hierarchy.values())} total sections"
    )
    return hierarchy


@require_http_methods(["GET"])
def sections_config_view(request):
    """Return hierarchical sections configuration dynamically from filesystem.

    Scans the actual project directory to find available sections,
    excluding symlinks and system files.

    Query params:
        - project_id: (optional) Project ID to load sections from

    Returns:
        JSON with hierarchical section structure based on actual files
    """
    try:
        from ...services import WriterService
        from apps.project_app.models import Project

        # Get project - try from query param, session, or user's default
        project_id = request.GET.get("project_id")
        if not project_id and request.user.is_authenticated:
            project_id = request.session.get("current_project_id")
            if not project_id:
                # Get user's first project
                project = Project.objects.filter(owner=request.user).first()
                if project:
                    project_id = project.id

        if not project_id:
            # Return static config as fallback
            from ...configs.sections_config import SECTION_HIERARCHY

            return JsonResponse(
                {
                    "success": True,
                    "hierarchy": SECTION_HIERARCHY,
                    "message": "Using static configuration (no project found)",
                }
            )

        # Get Writer service
        user_id = request.user.id if request.user.is_authenticated else None
        writer_service = WriterService(int(project_id), user_id)

        # Build hierarchy from actual filesystem
        hierarchy = _scan_project_sections(writer_service.writer_dir)

        return JsonResponse({"success": True, "hierarchy": hierarchy})

    except Exception as e:
        logger.error(f"Error getting sections config: {e}", exc_info=True)
        # Return static config as fallback
        from ...configs.sections_config import SECTION_HIERARCHY

        return JsonResponse(
            {
                "success": True,
                "hierarchy": SECTION_HIERARCHY,
                "message": f"Using static configuration (error: {str(e)})",
            }
        )


@api_login_optional
@require_http_methods(["POST"])
def save_sections_view(request, project_id):
    """Save multiple sections at once.

    POST body:
        {
            "sections": {
                "section_name1": "content1",
                "section_name2": "content2",
                ...
            },
            "doc_type": "manuscript" (optional, default: manuscript)
        }

    Returns:
        JSON response with SaveSectionsResponse structure
    """
    try:
        from scitex.writer.dataclasses.results import SaveSectionsResponse

        data = json.loads(request.body)
        sections = data.get("sections", {})
        doc_type = data.get("doc_type", "manuscript")

        # Validate input
        if not isinstance(sections, dict):
            response = SaveSectionsResponse.create_failure(
                "Invalid request: 'sections' must be a dictionary"
            )
            return JsonResponse(response.to_dict(), status=400)

        if not sections:
            response = SaveSectionsResponse.create_failure("No sections provided")
            return JsonResponse(response.to_dict(), status=400)

        # Get project and service
        from ...services import WriterService
        from apps.project_app.models import Project

        project = Project.objects.get(id=project_id)

        # Get effective user (authenticated or visitor)
        user, is_visitor = get_user_for_request(request, project_id)
        if not user:
            response = SaveSectionsResponse.create_failure("Invalid session")
            return JsonResponse(response.to_dict(), status=403)

        writer_service = WriterService(project_id, user.id)

        # Save each section
        saved_count = 0
        error_list = []
        error_details = {}

        from ...configs.sections_config import parse_section_id

        for section_id, content in sections.items():
            try:
                # Validate content type
                if not isinstance(content, str):
                    error_msg = f"Content must be string, got {type(content).__name__}"
                    error_list.append(f"{section_id}: {error_msg}")
                    error_details[section_id] = error_msg
                    continue

                # Parse hierarchical section ID
                category, section_name = parse_section_id(section_id)

                # Use parsed category instead of global doc_type
                success = writer_service.write_section(section_name, content, category)

                if success:
                    saved_count += 1
                else:
                    error_msg = "write_section returned False (unknown reason)"
                    error_list.append(f"{section_id}: {error_msg}")
                    error_details[section_id] = error_msg

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error saving section {section_id}: {e}", exc_info=True)
                error_list.append(f"{section_id}: {error_msg}")
                error_details[section_id] = error_msg

        # Create response
        if error_list:
            response = SaveSectionsResponse(
                success=saved_count > 0,  # Partial success if some saved
                sections_saved=saved_count,
                sections_skipped=len(error_list),
                message=f"Saved {saved_count}/{len(sections)} sections",
                errors=error_list,
                error_details=error_details,
            )
            # Validate before returning
            response.validate()
            return JsonResponse(
                response.to_dict(), status=500 if saved_count == 0 else 200
            )

        response = SaveSectionsResponse.create_success(
            sections_saved=saved_count, message=f"Saved {saved_count} sections"
        )
        # Validate before returning
        response.validate()
        return JsonResponse(response.to_dict())

    except Project.DoesNotExist:
        response = SaveSectionsResponse.create_failure("Project not found")
        return JsonResponse(response.to_dict(), status=404)
    except Exception as e:
        logger.error(f"Error saving sections: {e}", exc_info=True)
        response = SaveSectionsResponse.create_failure(
            f"Server error: {str(e)}", errors=[str(e)]
        )
        return JsonResponse(response.to_dict(), status=500)


@api_login_optional
@require_http_methods(["GET", "HEAD"])
def pdf_view(request, project_id, pdf_filename=None):
    """Serve PDF files from project's .preview directory.

    Supports both GET (download PDF) and HEAD (check if PDF exists) requests.

    Args:
        project_id: Project ID
        pdf_filename: PDF filename (e.g., 'preview-abstract.pdf')
    """
    try:
        from django.http import FileResponse
        from ...services import WriterService
        from apps.project_app.models import Project

        # Get effective user (authenticated or visitor)
        user, is_visitor = get_user_for_request(request, project_id)
        if not user:
            return JsonResponse(
                {"success": False, "error": "Invalid session"}, status=403
            )

        # Get project
        project = Project.objects.get(id=project_id)
        writer_service = WriterService(project_id, user.id)

        # Handle doc_type query parameter (for compiled full manuscripts)
        doc_type = request.GET.get("doc_type")
        if doc_type and not pdf_filename:
            # Map doc_type to PDF filename
            doc_type_map = {
                "manuscript": "manuscript.pdf",
                "supplementary": "supplementary.pdf",
                "revision": "revision.pdf",
            }
            pdf_filename = doc_type_map.get(doc_type, "manuscript.pdf")
            logger.info(
                f"[PDFView] Mapped doc_type={doc_type} to filename={pdf_filename}"
            )

        # If no filename specified, look for main compiled PDF
        if not pdf_filename:
            pdf_filename = "main.pdf"

        logger.info(f"[PDFView] Serving PDF: {pdf_filename} for project {project_id}")

        # Search for PDF in multiple locations
        writer_dir = writer_service.writer_dir  # Already at scitex/writer/
        pdf_path = None
        checked_paths = []

        # 1. Preview directory (for section previews)
        preview_dir = writer_dir / ".preview"
        preview_path = preview_dir / pdf_filename
        checked_paths.append(str(preview_path))
        if preview_path.exists():
            pdf_path = preview_path
            logger.info(f"[PDFView] Found PDF in .preview directory")

        # 2. Full manuscript PDFs in document type directories
        if not pdf_path and pdf_filename in [
            "manuscript.pdf",
            "supplementary.pdf",
            "revision.pdf",
        ]:
            doc_type_map = {
                "manuscript.pdf": "01_manuscript",
                "supplementary.pdf": "02_supplementary",
                "revision.pdf": "03_revision",
            }
            doc_dir = doc_type_map.get(pdf_filename)
            if doc_dir:
                full_path = writer_dir / doc_dir / pdf_filename
                checked_paths.append(str(full_path))
                if full_path.exists():
                    pdf_path = full_path
                    logger.info(f"[PDFView] Found full PDF in {doc_dir} directory")

        # 3. Fallback to old preview_output directory for backward compatibility
        if not pdf_path:
            legacy_preview = writer_service.writer_dir / "preview_output" / pdf_filename
            checked_paths.append(str(legacy_preview))
            if legacy_preview.exists():
                pdf_path = legacy_preview
                logger.info(f"[PDFView] Found PDF in legacy preview_output directory")

        # If still not found, return 404
        if not pdf_path:
            logger.error(f"[PDFView] PDF not found: {pdf_filename}")
            logger.error(f"[PDFView] Checked paths: {', '.join(checked_paths)}")
            # For HEAD requests, return simple 404 without JSON body
            if request.method == "HEAD":
                from django.http import HttpResponse

                return HttpResponse(status=404)
            return JsonResponse(
                {"success": False, "error": f"PDF not found: {pdf_filename}"},
                status=404,
            )

        logger.info(f"[PDFView] Serving PDF from: {pdf_path}")

        # For HEAD requests, just return 200 OK without file content
        if request.method == "HEAD":
            from django.http import HttpResponse

            response = HttpResponse(status=200)
            response["Content-Type"] = "application/pdf"
            response["Content-Disposition"] = f'inline; filename="{pdf_filename}"'
            return response

        # For GET requests, serve the PDF file
        response = FileResponse(open(pdf_path, "rb"), content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{pdf_filename}"'

        # Add cache control headers to prevent browser caching themed PDFs
        # This is critical for theme switching to work correctly
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"

        return response

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"Error serving PDF: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def presence_list_view(request, project_id):
    """Get list of active users in a project.

    Args:
        project_id: Project ID from URL

    Returns:
        JSON with list of active users and their cursor positions
    """
    try:
        # TODO: Implement proper presence tracking with Redis/Django Channels
        # For now, return empty list to avoid 500 errors
        return JsonResponse(
            {
                "success": True,
                "users": [],
                "message": "Presence tracking not yet implemented",
            }
        )

    except Exception as e:
        logger.error(f"Error getting presence list: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# URL pattern view aliases mapping to the API functions above
# section_view now defined above as proper function (GET=read, POST=write)
compile_preview_view = compile_api
compile_view = compile_api
# save_sections_view now defined above as proper function (bulk save)
# presence_list_view now defined above as proper function
# sections_config_view now defined above as proper function


@api_login_optional
@require_http_methods(["POST"])
def compile_full_view(request, project_id):
    """Compile full manuscript from workspace files.

    POST body:
        {
            "doc_type": "manuscript|supplementary|revision",
            "timeout": 300 (optional),
            # Manuscript options:
            "no_figs": false,
            "ppt2tif": false,
            "crop_tif": false,
            "quiet": false,
            "verbose": false,
            "force": false,
            # Revision options:
            "track_changes": false
        }
    """
    try:
        from apps.project_app.models import Project

        data = json.loads(request.body)
        doc_type = data.get("doc_type", "manuscript")
        timeout = data.get("timeout", 300)

        # Extract compilation options
        comp_options = {
            "no_figs": data.get("no_figs", False),
            "ppt2tif": data.get("ppt2tif", False),
            "crop_tif": data.get("crop_tif", False),
            "quiet": data.get("quiet", False),
            "verbose": data.get("verbose", False),
            "force": data.get("force", False),
            "track_changes": data.get("track_changes", False),
        }

        logger.info(f"[CompileFullAPI] project_id={project_id}, doc_type={doc_type}")

        # Get project and service
        project = Project.objects.get(id=project_id)

        # Get effective user (authenticated or visitor)
        user, is_visitor = get_user_for_request(request, project_id)
        if not user:
            return JsonResponse(
                {"success": False, "error": "Invalid session"}, status=403
            )

        # Create job ID for tracking
        job_id = str(uuid.uuid4())

        # Initialize job
        COMPILATION_JOBS[job_id] = {
            "status": "pending",
            "progress": 0,
            "step": "Initializing...",
            "log": [],
            "result": None,
            "project_id": project_id,
            "doc_type": doc_type,
        }

        # Start compilation in background thread
        thread = threading.Thread(
            target=run_compilation_async,
            args=(job_id, project_id, doc_type, timeout, user.id, comp_options),
            daemon=True,
        )
        thread.start()

        # Return job ID immediately for polling
        return JsonResponse(
            {"success": True, "job_id": job_id, "message": "Compilation started"}
        )

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"[CompileFullAPI] Error: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def run_compilation_async(
    job_id, project_id, doc_type, timeout, user_id, comp_options=None
):
    """Run compilation in background thread with job tracking"""
    try:
        from ...services import WriterService

        writer_service = WriterService(project_id, user_id)
        comp_options = comp_options or {}

        # Define callbacks to update job state
        def on_log(message):
            """Callback to collect logs in real-time"""
            if job_id in COMPILATION_JOBS:
                COMPILATION_JOBS[job_id]["log"].append(message)
            logger.debug(f"[Compilation {job_id}] {message}")

        def on_progress(percent, step):
            """Callback to track progress in real-time"""
            if job_id in COMPILATION_JOBS:
                COMPILATION_JOBS[job_id]["progress"] = percent
                COMPILATION_JOBS[job_id]["step"] = step
                COMPILATION_JOBS[job_id]["status"] = "running"
            logger.info(f"[Compilation {job_id}] {percent}% - {step}")

        # Call appropriate compilation method based on doc_type
        if doc_type == "manuscript":
            result = writer_service.compile_manuscript(
                timeout=timeout,
                log_callback=on_log,
                progress_callback=on_progress,
                no_figs=comp_options.get("no_figs", False),
                ppt2tif=comp_options.get("ppt2tif", False),
                crop_tif=comp_options.get("crop_tif", False),
                quiet=comp_options.get("quiet", False),
                verbose=comp_options.get("verbose", False),
                force=comp_options.get("force", False),
            )
        elif doc_type == "supplementary":
            result = writer_service.compile_supplementary(
                timeout=timeout,
                log_callback=on_log,
                progress_callback=on_progress,
                no_figs=comp_options.get("no_figs", False),
                ppt2tif=comp_options.get("ppt2tif", False),
                crop_tif=comp_options.get("crop_tif", False),
                quiet=comp_options.get("quiet", False),
            )
        elif doc_type == "revision":
            result = writer_service.compile_revision(
                timeout=timeout,
                log_callback=on_log,
                progress_callback=on_progress,
                track_changes=comp_options.get("track_changes", False),
            )
        else:
            raise ValueError(f"Invalid doc_type: {doc_type}")

        logger.info(
            f"[CompileFullAPI {job_id}] Result: success={result.get('success')}"
        )

        # Convert absolute filesystem path to servable URL
        if result.get("success") and result.get("output_pdf"):
            from pathlib import Path

            pdf_path = Path(result["output_pdf"])
            pdf_filename = pdf_path.name
            pdf_url = f"/writer/api/project/{project_id}/pdf/{pdf_filename}"
            result["output_pdf"] = pdf_url
            result["pdf_path"] = pdf_url
            logger.info(f"[CompileFullAPI {job_id}] PDF URL: {pdf_url}")

        # Update job with result
        if job_id in COMPILATION_JOBS:
            COMPILATION_JOBS[job_id]["status"] = (
                "completed" if result.get("success") else "failed"
            )
            COMPILATION_JOBS[job_id]["progress"] = 100
            COMPILATION_JOBS[job_id]["step"] = (
                "Complete!" if result.get("success") else "Failed"
            )
            COMPILATION_JOBS[job_id]["result"] = result

    except Exception as e:
        logger.error(f"[CompileFullAPI {job_id}] Error: {e}", exc_info=True)

        # Update job with error
        if job_id in COMPILATION_JOBS:
            COMPILATION_JOBS[job_id]["status"] = "failed"
            COMPILATION_JOBS[job_id]["step"] = "Error"
            COMPILATION_JOBS[job_id]["log"].append(f"[ERROR] {str(e)}")
            COMPILATION_JOBS[job_id]["result"] = {
                "success": False,
                "error": str(e),
                "log": str(e),
            }


@api_login_optional
@require_http_methods(["GET"])
def compilation_job_status(request, project_id, job_id):
    """Get compilation job status for polling."""
    if job_id not in COMPILATION_JOBS:
        return JsonResponse({"success": False, "error": "Job not found"}, status=404)

    job = COMPILATION_JOBS[job_id]

    # Check if job belongs to this project
    if job["project_id"] != project_id:
        return JsonResponse(
            {"success": False, "error": "Job not found for this project"}, status=404
        )

    # Convert ANSI codes to HTML
    from ...utils.ansi_to_html import ansi_to_html

    raw_log = "\n".join(job["log"])
    html_log = ansi_to_html(raw_log)

    return JsonResponse(
        {
            "success": True,
            "status": job["status"],
            "progress": job["progress"],
            "step": job["step"],
            "log": raw_log,  # Plain text for parsing
            "log_html": html_log,  # HTML with colors
            "result": job["result"],
        }
    )


section_history_view = section_view  # Temp stub
section_diff_view = section_view  # Temp stub
section_checkout_view = section_view  # Temp stub
section_commit_view = section_view  # Temp stub
preview_pdf_view = compile_api
file_tree_view = section_view  # Temp stub
read_tex_file_view = section_view  # Temp stub
available_sections_view = section_view  # Temp stub
presence_update_view = section_view  # Temp stub


# =============================================================================
# Section Management API Endpoints
# =============================================================================


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
        from ...services import WriterService
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
        import re

        if not re.match(r"^[a-z0-9_]+$", section_name):
            return JsonResponse(
                {
                    "success": False,
                    "error": "Section name must contain only lowercase letters, numbers, and underscores",
                },
                status=400,
            )

        # Determine directory path based on doc_type
        doc_dir_map = {
            "manuscript": "01_manuscript/contents",
            "supplementary": "02_supplementary/contents",
            "revision": "03_revision/contents",
            "shared": "shared",
        }

        if doc_type not in doc_dir_map:
            return JsonResponse(
                {"success": False, "error": f"Invalid doc_type: {doc_type}"}, status=400
            )

        # Create section file
        section_dir = writer_service.writer_dir / doc_dir_map[doc_type]
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


@login_required
@require_http_methods(["DELETE"])
def section_delete_view(request, project_id, section_name):
    """Delete a custom section.

    Only custom sections can be deleted (not core sections like abstract, introduction, etc.).
    """
    try:
        from ...services import WriterService
        from apps.project_app.models import Project
        from ...configs.sections_config import parse_section_id

        # Get project
        project = Project.objects.get(id=project_id, owner=request.user)
        writer_service = WriterService(project_id, request.user.id)

        # Parse section ID
        category, name = parse_section_id(section_name)

        # Prevent deletion of core sections
        core_sections = [
            "abstract",
            "introduction",
            "methods",
            "results",
            "discussion",
            "title",
            "authors",
            "keywords",
            "compiled_pdf",
            "compiled_tex",
            "highlights",
            "conclusion",
            "references",
        ]

        if name in core_sections:
            return JsonResponse(
                {"success": False, "error": f"Cannot delete core section: {name}"},
                status=400,
            )

        # Determine file path
        doc_dir_map = {
            "manuscript": "01_manuscript/contents",
            "supplementary": "02_supplementary/contents",
            "revision": "03_revision/contents",
            "shared": "shared",
        }

        section_dir = writer_service.writer_dir / doc_dir_map.get(
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
        from ...configs.sections_config import parse_section_id
        import json

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
        from ...services import WriterService

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


@login_required
@require_http_methods(["POST"])
def section_move_up_view(request, project_id, section_name):
    """Move section up in the compilation order.

    This will be stored in a project-level configuration file.
    """
    try:
        from apps.project_app.models import Project
        from ...configs.sections_config import parse_section_id
        from ...services import WriterService
        import json

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
        from ...configs.sections_config import parse_section_id
        from ...services import WriterService
        import json

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


@api_login_optional
@require_http_methods(["GET"])
def citations_api(request, project_id):
    """Get all citation keys from bibliography for autocomplete.

    Returns:
        JSON with citation keys, authors, years, titles for Monaco autocomplete
    """
    try:
        from apps.project_app.models import Project
        from pathlib import Path

        # Get project
        project = Project.objects.get(id=project_id)
        user, is_visitor = get_user_for_request(request, project_id)
        if not user:
            return JsonResponse(
                {"success": False, "error": "Invalid session"}, status=403
            )

        # Get project path (handle visitor pool)
        if is_visitor:
            from apps.project_app.services.visitor_pool import get_visitor_pool_dir

            visitor_dir = get_visitor_pool_dir(project.slug, user.id)
            project_path = visitor_dir / "scitex" / "writer"
        else:
            project_path = Path(project.git_clone_path) / "scitex" / "writer"

        # Path to bibliography - try multiple locations for v2.0.0-rc1
        # 1. Try manuscript bibliography (symlink to merged bibliography)
        bib_file = project_path / "01_manuscript" / "contents" / "bibliography.bib"

        # 2. If not found, try merged bibliography in 00_shared
        if not bib_file.exists():
            bib_file = project_path / "00_shared" / "bib_files" / "bibliography.bib"

        # 3. If still not found, try old location for backwards compatibility
        if not bib_file.exists():
            bib_file = Path(project.git_clone_path) / "scitex" / "bibliography_all.bib"

        logger.info(f"[Citations] Looking for bibliography at: {bib_file}")

        if not bib_file.exists():
            # Return empty list if no bibliography yet
            return JsonResponse(
                {
                    "success": True,
                    "citations": [],
                    "message": "No bibliography file found",
                }
            )

        # Parse BibTeX file using scitex.scholar
        from scitex.scholar.storage import BibTeXHandler

        bibtex_handler = BibTeXHandler()

        try:
            papers = bibtex_handler.papers_from_bibtex(bib_file)
        except Exception as e:
            logger.warning(f"[Citations] Failed to parse bibliography: {e}")
            return JsonResponse(
                {
                    "success": True,
                    "citations": [],
                    "message": f"Error parsing bibliography: {str(e)}",
                }
            )

        # Extract citation data
        citations = []
        for paper in papers:
            # Get citation key
            key = getattr(paper, "_bibtex_key", None)
            if not key:
                continue

            # Get metadata
            title = paper.metadata.basic.title or "No title"
            authors = paper.metadata.basic.authors or []
            year = paper.metadata.basic.year

            # Format author list - show up to 3 authors for better detail
            if len(authors) == 0:
                author_str = "Unknown"
            elif len(authors) == 1:
                author_str = authors[0]
            elif len(authors) == 2:
                author_str = f"{authors[0]} and {authors[1]}"
            elif len(authors) == 3:
                author_str = f"{authors[0]}, {authors[1]}, and {authors[2]}"
            else:
                # Show first author's last name
                first_author = authors[0].split()[-1] if authors[0] else "Unknown"
                author_str = f"{first_author} et al. ({len(authors)} authors)"

            # Get additional metadata
            journal = (
                getattr(paper.metadata.publication, "journal", None)
                if hasattr(paper.metadata, "publication")
                else None
            )
            impact_factor = (
                getattr(paper.metadata.publication, "impact_factor", None)
                if hasattr(paper.metadata, "publication")
                else None
            )
            citation_count = (
                getattr(paper.metadata.citations, "total", None)
                if hasattr(paper.metadata, "citations")
                else None
            )
            abstract = (
                getattr(paper.metadata.basic, "abstract", None)
                if hasattr(paper.metadata, "basic")
                else None
            )

            # Build rich documentation in markdown format
            doc_parts = [f"## {title}", ""]  # Title as heading

            # Metadata table
            metadata_lines = []
            metadata_lines.append(f"**Authors:** {author_str}")
            if year:
                metadata_lines.append(f"**Year:** {year}")
            if journal:
                journal_line = f"**Journal:** {journal}"
                if impact_factor:
                    journal_line += f" (IF: {impact_factor})"
                metadata_lines.append(journal_line)
            if citation_count:
                metadata_lines.append(f"**Citations:** {citation_count}")

            doc_parts.extend(metadata_lines)
            doc_parts.append("")  # Blank line before abstract

            # Abstract (truncated)
            if abstract:
                abstract_preview = (
                    abstract[:400] + "..." if len(abstract) > 400 else abstract
                )
                doc_parts.append("### Abstract")
                doc_parts.append(abstract_preview)

            documentation = "\n".join(doc_parts)

            # Create citation entry with rich metadata for search
            citations.append(
                {
                    "key": key,
                    "label": key,
                    "detail": f"{author_str} ({year})" if year else author_str,
                    "documentation": documentation,
                    "insertText": key,
                    # Additional fields for fuzzy search and inline display
                    "title": title,
                    "journal": journal or "",
                    "impact_factor": impact_factor,
                    "authors": authors,
                    "citation_count": citation_count or 0,
                    "abstract": abstract or "",
                }
            )

        logger.info(f"[Citations] Found {len(citations)} citations in {bib_file.name}")

        return JsonResponse(
            {"success": True, "citations": citations, "count": len(citations)}
        )

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"[Citations] Error: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@api_login_optional
@require_http_methods(["POST"])
def regenerate_bibliography_api(request, project_id):
    """Manually regenerate bibliography_all.bib by merging all .bib files.

    This is an opt-in operation that actually parses and merges BibTeX files.
    Call this when user wants to refresh bibliography or after adding new .bib files.

    Returns:
        JSON with merge statistics
    """
    try:
        from apps.project_app.models import Project
        from pathlib import Path
        from apps.project_app.services.bibliography_manager import (
            regenerate_bibliography,
        )

        # Get project
        user = get_user_for_request(request)
        if user.is_authenticated:
            project = Project.objects.get(id=project_id, owner=user)
        else:
            return JsonResponse(
                {"success": False, "error": "Authentication required"}, status=401
            )

        if not project.git_clone_path:
            return JsonResponse(
                {"success": False, "error": "Project has no git repository"}, status=400
            )

        # Regenerate bibliography
        project_path = Path(project.git_clone_path)
        results = regenerate_bibliography(project_path, project.name)

        if results["success"]:
            logger.info(
                f"[Bibliography] Regenerated for {project.name}: "
                f"scholar={results['scholar_count']}, writer={results['writer_count']}, "
                f"total={results['total_count']}"
            )

            return JsonResponse(
                {
                    "success": True,
                    "message": f"Bibliography regenerated with {results['total_count']} papers",
                    "scholar_count": results["scholar_count"],
                    "writer_count": results["writer_count"],
                    "total_count": results["total_count"],
                }
            )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Failed to regenerate bibliography",
                    "details": results["errors"],
                },
                status=500,
            )

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"[Bibliography] Error regenerating: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# EOF
