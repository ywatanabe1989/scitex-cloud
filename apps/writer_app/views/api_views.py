"""
REST API views for Writer operations.

Provides endpoints for section reading/writing, compilation, and git operations.
"""

from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
import json
import traceback
from pathlib import Path

from apps.project_app.models import Project
from ..services.writer_service import WriterService
from ..configs.sections_config import SECTION_HIERARCHY, get_all_sections_flat, get_sections_by_category
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


@require_http_methods(["POST"])
def compile_preview_view(request, project_id):
    """Compile preview of LaTeX content (for live editing).

    Creates a quick preview PDF from provided content without using workspace.
    Supports both authenticated and anonymous users.

    POST body:
        {
            "content": LaTeX content to compile (required)
            "timeout": compilation timeout in seconds (default: 60)
            "color_mode": PDF color mode - 'light' or 'dark' (default: 'light')
        }
    """
    try:
        data = json.loads(request.body)
        content = data.get("content")

        if not content:
            return JsonResponse({
                'success': False,
                'error': 'Content is required for preview compilation'
            }, status=400)

        timeout = data.get("timeout", 60)  # Shorter timeout for preview
        color_mode = data.get("color_mode", "light")
        section_name = data.get("section_name", "preview")  # For output filename

        # Anonymous users: use demo project from pool
        if not request.user.is_authenticated:
            from apps.project_app.services.demo_project_pool import DemoProjectPool
            demo_project, _ = DemoProjectPool.get_or_create_demo_project(request.session)
            logger.info(f"[CompilePreview] Anonymous user: project_id={demo_project.id}, section={section_name}, content={len(content)} chars")
            service = WriterService(demo_project.id, demo_project.owner.id)
            result = service.compile_preview(content, timeout=timeout, color_mode=color_mode, section_name=section_name)
        else:
            # Authenticated users: use WriterService for proper workspace handling
            project = Project.objects.get(id=project_id, owner=request.user)
            logger.info(f"[CompilePreview] Authenticated user: project={project_id}, section={section_name}, content={len(content)} chars")

            service = WriterService(project_id, request.user.id)
            result = service.compile_preview(content, timeout=timeout, color_mode=color_mode, section_name=section_name)

        logger.info(f"[CompilePreview] Result: success={result.get('success')}")
        if not result.get('success'):
            logger.warning(f"[CompilePreview] Failed: {result.get('error')}")

        # Convert file path to URL for preview PDFs
        pdf_url = None
        if result.get("success") and result.get("output_pdf"):
            if "preview_output" in result.get("output_pdf", ""):
                # Return section-specific preview URL
                pdf_url = f"/writer/api/project/{project_id}/preview-pdf/?section={section_name}"
            else:
                pdf_url = result.get("output_pdf")

        return JsonResponse({
            "success": result["success"],
            "output_pdf": pdf_url,
            "pdf_path": pdf_url,
            "log": result.get("log", ""),
            "error": result.get("error"),
        })

    except Project.DoesNotExist:
        logger.error(f"Project {project_id} not found")
        return JsonResponse({"success": False, "error": "Project not found"}, status=404)
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Preview compilation error: {type(e).__name__}: {e}")
        logger.error(f"Traceback:\n{error_trace}")
        return JsonResponse({
            "success": False,
            "error": str(e),
            "log": str(e),
            "traceback": error_trace
        }, status=500)


@require_http_methods(["POST"])
def compile_full_view(request, project_id):
    """Compile full manuscript from workspace (NOT preview).

    Uses scitex.writer.Writer to compile the complete manuscript from all sections.
    Only available for authenticated users with a project workspace.

    POST body:
        {
            "doc_type": "manuscript", "supplementary", or "revision" (default: manuscript)
            "timeout": compilation timeout in seconds (default: 300)
        }
    """
    try:
        # Only authenticated users can compile from workspace
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Full compilation requires authentication. Use /compile_preview/ for anonymous compilation.'
            }, status=403)

        data = json.loads(request.body)
        project = Project.objects.get(id=project_id, owner=request.user)

        service = WriterService(project_id, request.user.id)
        doc_type = data.get("doc_type", "manuscript")
        timeout = data.get("timeout", 300)

        logger.info(f"[CompileFull] Starting: project={project_id}, doc_type={doc_type}, timeout={timeout}")

        # Compile based on document type
        if doc_type == "supplementary":
            logger.info(f"[CompileFull] Compiling supplementary")
            result = service.compile_supplementary(timeout=timeout)
        elif doc_type == "revision":
            logger.info(f"[CompileFull] Compiling revision")
            result = service.compile_revision(timeout=timeout)
        else:  # manuscript
            logger.info(f"[CompileFull] Compiling manuscript")
            result = service.compile_manuscript(timeout=timeout)

        logger.info(f"[CompileFull] Result: success={result.get('success')}, output_pdf={result.get('output_pdf')}")
        if not result.get('success'):
            logger.warning(f"[CompileFull] Failed: {result.get('error')}")
            logger.warning(f"[CompileFull] Log: {result.get('log', '')[:500]}")  # First 500 chars

        return JsonResponse({
            "success": result["success"],
            "doc_type": doc_type,
            "output_pdf": result.get("output_pdf"),
            "pdf_path": result.get("output_pdf"),
            "log": result.get("log", ""),
            "error": result.get("error"),
        })

    except Project.DoesNotExist:
        logger.error(f"Project {project_id} not found")
        return JsonResponse({"success": False, "error": "Project not found"}, status=404)
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Full compilation error: {type(e).__name__}: {e}")
        logger.error(f"Traceback:\n{error_trace}")
        return JsonResponse({
            "success": False,
            "error": str(e),
            "log": str(e),
            "traceback": error_trace
        }, status=500)


@require_http_methods(["POST"])
def compile_view(request, project_id):
    """DEPRECATED: Use compile_preview_view or compile_full_view instead.

    This view is kept for backward compatibility but will be removed.
    """
    logger.warning("[Compile] Using deprecated compile_view. Use compile_preview_view or compile_full_view instead.")

    data = json.loads(request.body)
    if data.get("content"):
        return compile_preview_view(request, project_id)
    else:
        return compile_full_view(request, project_id)


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
@require_http_methods(["POST"])
def section_commit_view(request, project_id, section_name):
    """Commit changes to a section with a user-provided message.

    This creates a git commit for the auto-saved changes.
    The hybrid approach: auto-save (continuous) + manual commit (user-controlled).

    POST body:
        {
            "message": "Updated introduction section",
            "doc_type": "manuscript"  # (optional, default: manuscript)
        }

    **NEW**: Uses standardized error handling with full error cascading.
    Returns stdout, stderr, exit_code for debugging.
    """
    from apps.core.responses import api_response, error_response, success_response
    import logging

    git_logger = logging.getLogger('scitex.git')

    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        service = WriterService(project_id, request.user.id)

        data = json.loads(request.body)
        commit_message = data.get("message", "").strip()
        doc_type = data.get("doc_type", "manuscript")

        if not commit_message:
            return error_response(
                message="Commit message is required",
                error_type="validation",
                endpoint=request.path
            )

        # Log git operation
        git_logger.info(f"Committing section {section_name} (doc_type={doc_type}): {commit_message}")

        # Commit the section with the provided message
        success = service.commit_section(section_name, commit_message, doc_type)

        if not success:
            # No changes to commit
            git_logger.warning(f"No changes to commit for {section_name}")
            return error_response(
                message="No changes to commit. The section has not been modified since the last commit.",
                error_type="git_no_changes",
                error_details="Make changes to the section and save before committing.",
                stderr="nothing to commit, working tree clean",  # Git's message
                exit_code=1,
                endpoint=request.path
            )

        # Success!
        git_logger.info(f"Successfully committed {section_name}: {commit_message}")
        return success_response(
            message=f"Section committed: {commit_message}",
            data={
                "section": section_name,
                "doc_type": doc_type,
                "commit_message": commit_message
            },
            endpoint=request.path
        )

    except Project.DoesNotExist:
        return error_response(
            message="Project not found",
            error_type="not_found",
            endpoint=request.path,
            status_code=404
        )
    except Exception as e:
        logger.error(f"Commit error: {e}", exc_info=True)
        return error_response(
            message=str(e),
            error_type="unexpected",
            endpoint=request.path,
            status_code=500
        )


@login_required
@require_http_methods(["GET"])
@xframe_options_exempt
def pdf_view(request, project_id):
    """Serve compiled PDF file.

    Query params:
        doc_type: 'manuscript', 'supplementary', or 'revision' (default: manuscript)
    """
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        service = WriterService(project_id, request.user.id)

        doc_type = request.GET.get("doc_type", "manuscript")
        pdf_path = service.get_pdf(doc_type)

        if pdf_path and Path(pdf_path).exists():
            logger.info(f"[PDFView] Serving PDF: {pdf_path}")
            return FileResponse(
                open(pdf_path, 'rb'),
                content_type='application/pdf',
                as_attachment=False,
                filename=f"{doc_type}.pdf"
            )
        else:
            logger.warning(f"[PDFView] PDF not found: {pdf_path}")
            return JsonResponse({
                "success": False,
                "error": f"PDF not found. Please compile {doc_type} first.",
                "doc_type": doc_type,
            }, status=404)

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
                "highlights",
                "introduction",
                "methods",
                "results",
                "discussion",
                "conclusion",
                "title",
                "authors",
                "keywords",
                "graphical_abstract",
            ],
            "supplementary": ["methods", "results", "figures", "tables"],
            "shared": ["abstract"],
            "revision": [
                "cover-letter",
                "summary-of-changes",
                # Dynamic triplets (comment, response, revision) will be added via UI
                # Example: reviewer-01-point-01-comment, reviewer-01-point-01-response, reviewer-01-point-01-revision
            ],
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


@login_required
@require_http_methods(["POST"])
def save_sections_view(request, project_id):
    """Save multiple sections at once.

    POST body:
        {
            "sections": {
                "abstract": "section content",
                "introduction": "section content",
                ...
            },
            "doc_type": "manuscript" (optional, default: manuscript),
            "commit_message": "optional commit message"
        }
    """
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        service = WriterService(project_id, request.user.id)

        data = json.loads(request.body)
        sections = data.get("sections", {})
        doc_type = data.get("doc_type", "manuscript")
        commit_message = data.get("commit_message")

        logger.info(f"Save sections request: project={project_id}, doc_type={doc_type}, sections={len(sections)}, user={request.user.id}")

        if not sections:
            return JsonResponse({
                "success": True,
                "message": "No sections to save",
                "sections_saved": 0,
            })

        # Save each section
        saved_count = 0
        failed_sections = []
        for section_name, content in sections.items():
            try:
                content_str = str(content) if content else ""
                content_size = len(content_str.encode('utf-8'))
                logger.debug(f"Writing section {section_name} ({content_size} bytes) for {doc_type}")

                service.write_section(section_name, content, doc_type)
                saved_count += 1
                logger.info(f"Successfully saved section {section_name}")
            except AttributeError as e:
                # Section doesn't exist in this document type
                logger.info(f"Section {section_name} not found for {doc_type}: {e}")
                failed_sections.append(section_name)
            except TypeError as e:
                # Type mismatch or conversion error
                logger.error(f"Type error saving section {section_name}: {e}")
                logger.error(f"Content type: {type(content)}, Content: {repr(content)[:100]}")
                failed_sections.append(section_name)
            except Exception as e:
                logger.error(f"Failed to save section {section_name}: {type(e).__name__}: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                failed_sections.append(section_name)

        logger.info(f"Save sections completed: saved={saved_count}, failed={len(failed_sections)}")

        # Return success even if no sections were saved
        # (they may be empty or not exist in this document type)
        return JsonResponse({
            "success": True,
            "message": f"Processed {len(sections)} sections ({saved_count} saved)",
            "sections_saved": saved_count,
            "sections_skipped": len(failed_sections),
        })

    except Project.DoesNotExist:
        logger.error(f"Project {project_id} not found for user {request.user.id}")
        return JsonResponse({"success": False, "error": "Project not found"}, status=404)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({"success": False, "error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Save sections view error: {e}")
        logger.error(f"Traceback:\n{error_trace}")
        return JsonResponse({
            "success": False,
            "error": str(e),
            "traceback": error_trace
        }, status=500)


@login_required
@require_http_methods(["GET"])
def file_tree_view(request, project_id):
    """Get file tree structure of the writer workspace.

    Returns a hierarchical tree of all .tex files in the workspace.
    """
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        service = WriterService(project_id, request.user.id)

        # Get the writer path
        writer_path = service.project_path

        if not writer_path.exists():
            return JsonResponse({
                "success": False,
                "error": "Writer workspace not initialized"
            }, status=404)

        # Build file tree
        def build_tree(path: Path, base_path: Path):
            """Recursively build file tree structure."""
            items = []

            # Skip hidden directories and git
            if path.name.startswith('.'):
                return items

            try:
                for item in sorted(path.iterdir()):
                    # Skip hidden files and directories
                    if item.name.startswith('.'):
                        continue

                    # Get relative path from base
                    rel_path = str(item.relative_to(base_path))

                    if item.is_dir():
                        children = build_tree(item, base_path)
                        items.append({
                            "name": item.name,
                            "path": rel_path,
                            "type": "directory",
                            "children": children
                        })
                    elif item.suffix == '.tex':
                        items.append({
                            "name": item.name,
                            "path": rel_path,
                            "type": "file"
                        })
            except PermissionError:
                pass

            return items

        tree = build_tree(writer_path, writer_path)

        return JsonResponse({
            "success": True,
            "tree": tree
        })

    except Project.DoesNotExist:
        return JsonResponse({"success": False, "error": "Project not found"}, status=404)
    except Exception as e:
        logger.error(f"File tree view error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def read_tex_file_view(request, project_id):
    """Read content of a .tex file.

    Query params:
        path: relative path to the .tex file (e.g., "main.tex" or "chapters/intro.tex")
    """
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        service = WriterService(project_id, request.user.id)

        file_path = request.GET.get("path")
        if not file_path:
            return JsonResponse({"success": False, "error": "File path required"}, status=400)

        # Read the file from the writer workspace
        content = service.read_tex_file(file_path)

        return JsonResponse({
            "success": True,
            "path": file_path,
            "content": content
        })

    except Project.DoesNotExist:
        return JsonResponse({"success": False, "error": "Project not found"}, status=404)
    except FileNotFoundError:
        return JsonResponse({"success": False, "error": "File not found"}, status=404)
    except Exception as e:
        logger.error(f"Read tex file error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@xframe_options_exempt
@require_http_methods(["GET"])
@xframe_options_exempt
def preview_pdf_view(request, project_id):
    """Serve section-specific preview PDF file.

    Query params:
        section: Section name (e.g., 'abstract', 'introduction') - defaults to 'preview'

    Note: No login required - users can view previews anonymously.
    """
    try:
        # For anonymous users (projectId=0), use demo project path
        if project_id == 0 or not request.user.is_authenticated:
            project_id = 0
            user_id = 0
        else:
            # Verify project exists for authenticated users
            project = Project.objects.get(id=project_id)
            user_id = request.user.id

        service = WriterService(project_id, user_id)

        # Get section name from query params
        section_name = request.GET.get('section', 'preview')
        safe_section_name = section_name.replace('/', '-').replace(' ', '-').lower()

        # Get the section-specific preview PDF path
        pdf_path = service.project_path / "preview_output" / f"preview-{safe_section_name}.pdf"

        logger.info(f"[PreviewPDF] Looking for: {pdf_path}")

        if not pdf_path.exists():
            logger.warning(f"[PreviewPDF] Not found: {pdf_path}")
            return JsonResponse({
                "success": False,
                "error": f"Preview PDF not found: {pdf_path.name}. Please edit the section and wait 2 seconds for auto-compile.",
                "attempted_path": str(pdf_path)
            }, status=404)

        if not pdf_path.is_file():
            return JsonResponse({"success": False, "error": "Invalid PDF path"}, status=400)

        # Serve the file
        logger.info(f"[PreviewPDF] Serving: {pdf_path}")
        response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="preview-{safe_section_name}.pdf"'
        return response

    except Project.DoesNotExist:
        return JsonResponse({"success": False, "error": "Project not found"}, status=404)
    except Exception as e:
        logger.error(f"Preview PDF view error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["GET"])
def sections_config_view(request):
    """Get hierarchical sections configuration for dropdown.

    Returns structured section hierarchy matching scitex.writer backend.
    No authentication required - configuration is the same for all users.

    Returns:
        {
            "success": True,
            "hierarchy": {
                "shared": {...},
                "manuscript": {...},
                "supplementary": {...},
                "revision": {...}
            }
        }
    """
    try:
        return JsonResponse({
            "success": True,
            "hierarchy": SECTION_HIERARCHY
        })
    except Exception as e:
        logger.error(f"Sections config view error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)
