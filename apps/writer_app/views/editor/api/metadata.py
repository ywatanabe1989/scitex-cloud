#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-cloud/apps/writer_app/views/editor/api/metadata.py
"""Metadata endpoints - sections config, citations, bibliography."""

from __future__ import annotations
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ..auth_utils import api_login_optional, get_user_for_request

logger = logging.getLogger(__name__)


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
        from ....services import WriterService
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
            from ....configs.sections_config import SECTION_HIERARCHY

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
        from ....configs.sections_config import SECTION_HIERARCHY

        return JsonResponse(
            {
                "success": True,
                "hierarchy": SECTION_HIERARCHY,
                "message": f"Using static configuration (error: {str(e)})",
            }
        )


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
            from apps.project_app.services.project_filesystem import get_project_filesystem_manager
            manager = get_project_filesystem_manager(user)
            visitor_dir = manager.get_project_root_path(project)
            if not visitor_dir:
                return JsonResponse(
                    {"success": False, "error": "Project path not found"}, status=404
                )
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


# View alias for backward compatibility
file_tree_view = sections_config_view

# EOF
