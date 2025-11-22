#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-cloud/apps/scholar_app/bibtex_views.py

"""
BibTeX Enrichment Views

Provides functionality to upload BibTeX files and enrich them with:
- Citation counts from multiple sources
- Journal impact factors
- PDF downloads
- Additional metadata
- Full-text extraction

Uses scitex.scholar.pipelines.ScholarPipelineBibTeX under the hood.
"""

import asyncio
import logging
import shutil
from pathlib import Path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.conf import settings
from ...models import BibTeXEnrichmentJob
from apps.scholar_app.api_auth import api_key_optional

logger = logging.getLogger(__name__)


def bibtex_enrichment(request):
    """BibTeX enrichment landing page - upload and manage enrichment jobs (anonymous allowed)."""
    from apps.project_app.models import Project

    # Get user's recent enrichment jobs
    if request.user.is_authenticated:
        recent_jobs = (
            BibTeXEnrichmentJob.objects.filter(user=request.user)
            .select_related("project")
            .order_by("-created_at")[:10]
        )

        # Get user's projects for project selection
        user_projects = Project.objects.filter(owner=request.user).order_by(
            "-created_at"
        )
        current_project = user_projects.first() if user_projects.exists() else None
    else:
        # For anonymous users, get jobs by session key
        recent_jobs = (
            BibTeXEnrichmentJob.objects.filter(
                session_key=request.session.session_key
            ).order_by("-created_at")[:10]
            if request.session.session_key
            else []
        )

        # For visitor users, get their assigned project from the visitor pool
        # The project_context processor should have added 'project' to the context
        from apps.project_app.services.visitor_pool import VisitorPool

        visitor_project_id = request.session.get(VisitorPool.SESSION_KEY_PROJECT_ID)
        current_project = None
        user_projects = []

        if visitor_project_id:
            try:
                current_project = Project.objects.get(id=visitor_project_id)
                user_projects = [current_project]  # Make it available for the template
            except Project.DoesNotExist:
                pass

    context = {
        "recent_jobs": recent_jobs,
        "user_projects": user_projects,
        "current_project": current_project,
        "is_anonymous": not request.user.is_authenticated,
        "show_save_prompt": not request.user.is_authenticated,
    }

    return render(request, "scholar_app/bibtex_enrichment.html", context)


@require_http_methods(["POST"])
def bibtex_enrich_sync(request):
    """
    Synchronous BibTeX enrichment API endpoint.

    Upload a BibTeX file and get the enriched version directly.
    Requires API key authentication.

    Usage:
        curl https://scitex.cloud/scholar/api/bibtex/enrich/ \
          -H "Authorization: Bearer YOUR_API_KEY" \
          -F "bibtex_file=@original.bib" \
          -o enriched.bib
    """
    from scitex.scholar.pipelines import ScholarPipelineMetadataParallel
    from scitex.scholar.storage import BibTeXHandler
    import tempfile

    # Check API authentication (decorator applied in urls.py)
    if not hasattr(request, "api_user"):
        return JsonResponse(
            {
                "success": False,
                "error": "API key required",
                "detail": "Use Authorization: Bearer YOUR_API_KEY header",
            },
            status=401,
        )

    # Check if file was uploaded
    if "bibtex_file" not in request.FILES:
        return JsonResponse(
            {
                "success": False,
                "error": "No file uploaded",
                "detail": "Include bibtex_file in multipart form data",
            },
            status=400,
        )

    bibtex_file = request.FILES["bibtex_file"]

    # Validate file extension
    if not bibtex_file.name.endswith(".bib"):
        return JsonResponse(
            {
                "success": False,
                "error": "Invalid file type",
                "detail": "File must have .bib extension",
            },
            status=400,
        )

    # Get parameters
    use_cache = request.POST.get("use_cache", "true").lower() in (
        "true",
        "1",
        "on",
        "yes",
    )
    num_workers = int(request.POST.get("num_workers", 4))

    try:
        # Save to temporary file
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".bib", delete=False
        ) as tmp_input:
            for chunk in bibtex_file.chunks():
                tmp_input.write(chunk)
            tmp_input_path = Path(tmp_input.name)

        # Load papers
        bibtex_handler = BibTeXHandler()
        papers = bibtex_handler.papers_from_bibtex(tmp_input_path)

        if not papers:
            return JsonResponse(
                {
                    "success": False,
                    "error": "No papers found",
                    "detail": "BibTeX file contains no valid entries",
                },
                status=400,
            )

        # Enrich papers
        pipeline = ScholarPipelineMetadataParallel(num_workers=num_workers)

        async def enrich():
            return await asyncio.wait_for(
                pipeline.enrich_papers_async(
                    papers=papers,
                    force=not use_cache,
                ),
                timeout=600,
            )

        enriched_papers = asyncio.run(enrich())

        # Create temporary output file path (don't open it - let papers_to_bibtex handle that)
        tmp_output = tempfile.NamedTemporaryFile(
            mode="w", suffix=".bib", delete=False, encoding="utf-8"
        )
        tmp_output_path = Path(tmp_output.name)
        tmp_output.close()  # Close but don't delete - papers_to_bibtex will write to it

        bibtex_handler.papers_to_bibtex(enriched_papers, tmp_output_path)

        # Return enriched file
        response = FileResponse(
            open(tmp_output_path, "rb"), content_type="application/x-bibtex"
        )

        original_name = Path(bibtex_file.name).stem
        response["Content-Disposition"] = (
            f'attachment; filename="{original_name}-enriched.bib"'
        )

        # Cleanup temp files
        tmp_input_path.unlink(missing_ok=True)
        # Note: tmp_output_path will be cleaned up after response is sent

        return response

    except asyncio.TimeoutError:
        return JsonResponse(
            {
                "success": False,
                "error": "Enrichment timeout",
                "detail": "Processing exceeded 10 minutes",
            },
            status=408,
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "error": "Enrichment failed", "detail": str(e)},
            status=500,
        )


@require_http_methods(["POST"])
def bibtex_preview(request):
    """Preview BibTeX file contents before enrichment (anonymous allowed)."""
    import bibtexparser

    # Check if file was uploaded
    if "bibtex_file" not in request.FILES:
        return JsonResponse({"success": False, "error": "No file uploaded"}, status=400)

    bibtex_file = request.FILES["bibtex_file"]

    # Validate file extension
    if not bibtex_file.name.endswith(".bib"):
        return JsonResponse(
            {"success": False, "error": "Please upload a .bib file"}, status=400
        )

    try:
        # Read and parse BibTeX file
        content = bibtex_file.read().decode("utf-8")
        bibtex_file.seek(0)  # Reset file pointer for potential reuse

        bib_database = bibtexparser.loads(content)

        # Extract entry information
        entries = []
        for entry in bib_database.entries[:50]:  # Limit to first 50 for preview
            entries.append(
                {
                    "key": entry.get("ID", "Unknown"),
                    "type": entry.get("ENTRYTYPE", "article"),
                    "title": entry.get("title", "No title"),
                    "author": entry.get("author", "Unknown"),
                    "year": entry.get("year", "N/A"),
                    "has_abstract": bool(entry.get("abstract")),
                    "has_url": bool(entry.get("url") or entry.get("doi")),
                    "has_citations": bool(entry.get("citations")),
                }
            )

        total_entries = len(bib_database.entries)

        return JsonResponse(
            {
                "success": True,
                "filename": bibtex_file.name,
                "total_entries": total_entries,
                "entries": entries,
                "showing_limited": total_entries > 50,
            }
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"Failed to parse BibTeX file: {str(e)}"},
            status=400,
        )


@require_http_methods(["POST"])
@api_key_optional
def bibtex_upload(request):
    """Handle BibTeX file upload and start enrichment job (supports API key auth)."""

    # Check for API key authentication
    api_authenticated = hasattr(request, "api_user")

    # Get authenticated user (from API key or session)
    if api_authenticated:
        user = request.api_user
        is_authenticated = True
    else:
        user = request.user
        is_authenticated = request.user.is_authenticated

        # Ensure session exists for anonymous users
        if not is_authenticated and not request.session.session_key:
            request.session.create()

    # Check if file was uploaded
    if "bibtex_file" not in request.FILES:
        if (
            api_authenticated
            or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        ):
            return JsonResponse(
                {
                    "success": False,
                    "error": "No file uploaded",
                    "detail": "Include bibtex_file in request",
                },
                status=400,
            )
        messages.error(request, "Please select a BibTeX file to upload.")
        return redirect("scholar_app:bibtex_enrichment")

    bibtex_file = request.FILES["bibtex_file"]

    # Store original filename (before Django adds suffix)
    original_filename = bibtex_file.name

    # Validate file extension
    if not bibtex_file.name.endswith(".bib"):
        messages.error(request, "Please upload a .bib file.")
        return redirect("scholar_app:bibtex_enrichment")

    # Job management: One user = One job at a time
    # Different handling for authenticated vs anonymous users

    if is_authenticated:
        # Authenticated users: Can cancel old jobs and start new ones
        existing_jobs = BibTeXEnrichmentJob.objects.filter(
            user=user, status__in=["pending", "processing"]
        )

        # Cancel all existing jobs - new upload takes priority
        for old_job in existing_jobs:
            old_job.status = "cancelled"
            old_job.error_message = "Cancelled - new job uploaded"
            old_job.completed_at = timezone.now()
            old_job.processing_log += "\n\n✗ Cancelled by user uploading new file"
            old_job.save(
                update_fields=[
                    "status",
                    "error_message",
                    "completed_at",
                    "processing_log",
                ]
            )

    else:
        # Anonymous users: Ask if they want to cancel old job
        existing_jobs = (
            BibTeXEnrichmentJob.objects.filter(
                session_key=request.session.session_key,
                status__in=["pending", "processing"],
            )
            if request.session.session_key
            else BibTeXEnrichmentJob.objects.none()
        )

        if existing_jobs.exists():
            # Check if user explicitly wants to cancel old job
            force_cancel = request.POST.get("force_cancel") == "true"

            if force_cancel:
                # User chose to cancel old job - proceed with cancellation
                for old_job in existing_jobs:
                    old_job.status = "cancelled"
                    old_job.error_message = "Cancelled - new job uploaded"
                    old_job.completed_at = timezone.now()
                    old_job.processing_log += (
                        "\n\n✗ Cancelled by user uploading new file"
                    )
                    old_job.save(
                        update_fields=[
                            "status",
                            "error_message",
                            "completed_at",
                            "processing_log",
                        ]
                    )
                # Continue to create new job below
            else:
                # Show confirmation dialog to user
                existing_job = existing_jobs.first()
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {
                            "success": False,
                            "requires_confirmation": True,
                            "existing_job": {
                                "id": str(existing_job.id),
                                "filename": existing_job.original_filename or "Unknown",
                                "progress": existing_job.get_progress_percentage(),
                                "status": existing_job.status,
                            },
                            "message": "You already have a job in progress. Cancel it and start new job?",
                        },
                        status=409,
                    )  # 409 Conflict
                else:
                    messages.warning(
                        request,
                        f'You already have a job in progress: "{existing_job.original_filename or "Unknown"}". Please wait for it to complete.',
                    )
                    return redirect("scholar_app:bibtex_enrichment")

    # Get optional parameters
    project_name = request.POST.get("project_name", "").strip() or None
    project_id = request.POST.get("project_id", "").strip() or None
    num_workers = int(request.POST.get("num_workers", 4))
    browser_mode = request.POST.get("browser_mode", "stealth")
    use_cache = (
        request.POST.get("use_cache", "on") == "on"
    )  # Checkbox sends 'on' when checked

    # Get project if specified (only for authenticated users)
    project = None
    if project_id and is_authenticated:
        from apps.project_app.models import Project

        try:
            project = Project.objects.get(id=project_id, owner=user)
        except Project.DoesNotExist:
            if api_authenticated:
                return JsonResponse(
                    {"success": False, "error": "Project not found"}, status=404
                )
            messages.error(request, "Selected project not found.")
            return redirect("scholar_app:bibtex_enrichment")

    # Save uploaded file - use user ID or session key
    if is_authenticated:
        user_identifier = str(user.id)
    else:
        user_identifier = f"anonymous_{request.session.session_key}"

    file_path = default_storage.save(
        f"bibtex_uploads/{user_identifier}/{bibtex_file.name}",
        ContentFile(bibtex_file.read()),
    )

    # Create enrichment job
    job = BibTeXEnrichmentJob.objects.create(
        user=user if is_authenticated else None,
        session_key=request.session.session_key if not is_authenticated else None,
        input_file=file_path,
        original_filename=original_filename,
        project_name=project_name,
        project=project,
        num_workers=num_workers,
        browser_mode=browser_mode,
        use_cache=use_cache,
        status="pending",
    )

    # Start processing immediately in a background thread
    import threading

    thread = threading.Thread(target=_process_bibtex_job, args=(job,))
    thread.daemon = True
    thread.start()

    # Return JSON for API and AJAX requests
    if api_authenticated or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "job_id": str(job.id),
                "status": "pending",
                "message": "Enrichment job started",
                "api_endpoints": {
                    "status": f"/scholar/api/bibtex/job/{job.id}/status/",
                    "download": f"/scholar/api/bibtex/job/{job.id}/download/",
                    "papers": f"/scholar/api/bibtex/job/{job.id}/papers/",
                },
            }
        )

    return redirect("scholar_app:bibtex_job_detail", job_id=job.id)


def bibtex_job_detail(request, job_id):
    """View details and progress of a BibTeX enrichment job (anonymous allowed)."""

    # Get job by user or session key
    if request.user.is_authenticated:
        job = get_object_or_404(BibTeXEnrichmentJob, id=job_id, user=request.user)
    else:
        job = get_object_or_404(
            BibTeXEnrichmentJob, id=job_id, session_key=request.session.session_key
        )

    # If job is pending, start processing
    if job.status == "pending":
        # In production, this would be a Celery task
        # For now, start processing synchronously
        _process_bibtex_job(job)
        job.refresh_from_db()

    context = {
        "job": job,
    }

    return render(request, "scholar_app/bibtex_job_detail.html", context)


@api_key_optional
def bibtex_download_enriched(request, job_id):
    """Download the enriched BibTeX file (supports API key auth)."""

    # Check for API key authentication
    api_authenticated = hasattr(request, "api_user")
    user = request.api_user if api_authenticated else request.user

    # Get job by user or session key
    if api_authenticated or request.user.is_authenticated:
        job = get_object_or_404(BibTeXEnrichmentJob, id=job_id, user=user)
    else:
        job = get_object_or_404(
            BibTeXEnrichmentJob, id=job_id, session_key=request.session.session_key
        )

    if job.status != "completed" or not job.output_file:
        if api_authenticated:
            return JsonResponse(
                {
                    "success": False,
                    "error": "File not ready",
                    "detail": f"Job status: {job.status}",
                    "job_id": str(job_id),
                },
                status=400,
            )
        messages.error(request, "Enriched BibTeX file not available yet.")
        return redirect("scholar_app:bibtex_job_detail", job_id=job_id)

    # Serve the file
    file_path = Path(settings.MEDIA_ROOT) / job.output_file.name

    if not file_path.exists():
        if api_authenticated:
            return JsonResponse(
                {"success": False, "error": "File not found on server"}, status=404
            )
        messages.error(request, "File not found.")
        return redirect("scholar_app:bibtex_job_detail", job_id=job_id)

    response = FileResponse(open(file_path, "rb"), content_type="application/x-bibtex")
    response["Content-Disposition"] = f'attachment; filename="{file_path.name}"'

    return response


def bibtex_download_original(request, job_id):
    """Download the original BibTeX file (supports API key auth)."""

    # Check for API key authentication
    api_authenticated = hasattr(request, "api_user")
    user = request.api_user if api_authenticated else request.user

    # Get job by user or session key
    if api_authenticated or request.user.is_authenticated:
        job = get_object_or_404(BibTeXEnrichmentJob, id=job_id, user=user)
    else:
        job = get_object_or_404(
            BibTeXEnrichmentJob, id=job_id, session_key=request.session.session_key
        )

    if not job.input_file:
        if api_authenticated:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Original file not available",
                    "job_id": str(job_id),
                },
                status=400,
            )
        messages.error(request, "Original BibTeX file not available.")
        return redirect("scholar_app:bibtex_job_detail", job_id=job_id)

    # Serve the file
    file_path = Path(settings.MEDIA_ROOT) / job.input_file.name

    if not file_path.exists():
        if api_authenticated:
            return JsonResponse(
                {"success": False, "error": "File not found on server"}, status=404
            )
        messages.error(request, "File not found.")
        return redirect("scholar_app:bibtex_job_detail", job_id=job_id)

    response = FileResponse(open(file_path, "rb"), content_type="application/x-bibtex")
    response["Content-Disposition"] = f'attachment; filename="{file_path.name}"'

    return response


@require_http_methods(["GET"])
@api_key_optional
def bibtex_job_status(request, job_id):
    """API endpoint to get job status and progress (supports API key auth)."""

    # Check for API key authentication
    api_authenticated = hasattr(request, "api_user")
    user = request.api_user if api_authenticated else request.user

    # Get job by user or session key
    if api_authenticated or request.user.is_authenticated:
        job = get_object_or_404(BibTeXEnrichmentJob, id=job_id, user=user)
    else:
        job = get_object_or_404(
            BibTeXEnrichmentJob, id=job_id, session_key=request.session.session_key
        )

    data = {
        "status": job.status,
        "progress_percentage": job.get_progress_percentage(),
        "total_papers": job.total_papers,
        "processed_papers": job.processed_papers,
        "failed_papers": job.failed_papers,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error_message": job.error_message,
        "has_output": bool(job.output_file),
        "log": job.processing_log,  # Add processing log for real-time updates
    }

    return JsonResponse(data)


@require_http_methods(["GET"])
def bibtex_job_papers(request, job_id):
    """API endpoint to get all papers in a job as placeholders (anonymous allowed)."""
    import bibtexparser
    from pathlib import Path

    # Get job by user or session key
    if request.user.is_authenticated:
        job = get_object_or_404(BibTeXEnrichmentJob, id=job_id, user=request.user)
    else:
        job = get_object_or_404(
            BibTeXEnrichmentJob, id=job_id, session_key=request.session.session_key
        )

    # Determine which file to read (output if completed, input otherwise)
    if job.status == "completed" and job.output_file:
        file_path = Path(settings.MEDIA_ROOT) / job.output_file.name
    else:
        file_path = Path(settings.MEDIA_ROOT) / job.input_file.name

    if not file_path.exists():
        return JsonResponse({"success": False, "error": "File not found"}, status=404)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            bib_database = bibtexparser.load(f)

        papers = []
        for entry in bib_database.entries:
            papers.append(
                {
                    "key": entry.get("ID", "Unknown"),
                    "type": entry.get("ENTRYTYPE", "article"),
                    "title": entry.get("title", "No title"),
                    "author": entry.get("author", "Unknown"),
                    "year": entry.get("year", "N/A"),
                    "journal": entry.get("journal", ""),
                    "abstract": entry.get("abstract", ""),
                    "url": entry.get("url", ""),
                    "doi": entry.get("doi", ""),
                    "citations": entry.get("citations", ""),
                    "has_abstract": bool(entry.get("abstract")),
                    "has_url": bool(entry.get("url") or entry.get("doi")),
                    "has_citations": bool(entry.get("citations")),
                }
            )

        return JsonResponse(
            {
                "success": True,
                "job_id": str(job_id),
                "total_papers": len(papers),
                "papers": papers,
                "status": job.status,
            }
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"Failed to read papers: {str(e)}"}, status=500
        )


def _process_bibtex_job(job):
    """Process a BibTeX enrichment job using ScholarPipelineMetadataParallel directly.

    In production, this should be a Celery task for async processing.
    """
    import logging

    logger = logging.getLogger(__name__)

    # Create a cancellation flag that can be checked
    cancellation_flag = {"cancelled": False}

    def check_cancellation():
        """Check if job should be cancelled (either by user or timeout)."""
        job.refresh_from_db()
        if job.status == "cancelled":
            cancellation_flag["cancelled"] = True
            return True
        return False

    def progress_callback(current: int, total: int, info: dict):
        """Callback to capture and store progress messages in real-time.

        Args:
            current: Number of papers processed (1-indexed)
            total: Total number of papers
            info: Dict with 'title', 'success', 'error', 'index'
        """
        from asgiref.sync import sync_to_async
        import asyncio

        async def update_job():
            try:
                # Wrap Django ORM operations in sync_to_async
                await sync_to_async(job.refresh_from_db)()

                # Check if job was cancelled
                if await sync_to_async(lambda: job.status)() == "cancelled":
                    return  # Job was cancelled, stop updating

                # Create progress message
                title = info.get("title", "Unknown")
                # Truncate with "..." indicator if too long
                if len(title) > 50:
                    title = title[:50] + "..."
                status_icon = "✓" if info.get("success") else "✗"
                message = f"[{current}/{total}] {status_icon} {title}"

                current_log = await sync_to_async(lambda: job.processing_log)()
                if current_log:
                    job.processing_log = current_log + f"\n{message}"
                else:
                    job.processing_log = message

                # Update counters
                job.processed_papers = current
                await sync_to_async(job.save)(
                    update_fields=["processing_log", "processed_papers"]
                )
            except Exception as e:
                # Job may have been deleted or cancelled - ignore update errors
                logger.warning(f"Failed to update job {job.id}: {e}")

        # Run the async update
        try:
            asyncio.create_task(update_job())
        except RuntimeError:
            # If there's no event loop, run it synchronously
            asyncio.run(update_job())

    try:
        # Set user-specific SCITEX_DIR to avoid cache conflicts between users
        import os

        if job.user:
            user_scitex_dir = (
                Path(settings.BASE_DIR)
                / "data"
                / "users"
                / job.user.username
                / ".scitex"
            )
        else:
            # Anonymous users get session-based directory
            session_key = job.session_key or "anonymous"
            user_scitex_dir = (
                Path(settings.BASE_DIR) / "data" / "anonymous" / session_key / ".scitex"
            )

        user_scitex_dir.mkdir(parents=True, exist_ok=True)
        os.environ["SCITEX_DIR"] = str(user_scitex_dir)
        logger.info(f"Set SCITEX_DIR to {user_scitex_dir} for job {job.id}")

        # Update job status - refresh first to avoid conflicts
        try:
            job.refresh_from_db()
            # Check if job was cancelled before we even started
            if job.status == "cancelled":
                logger.info(f"Job {job.id} was cancelled before processing started")
                return
        except BibTeXEnrichmentJob.DoesNotExist:
            logger.warning(f"Job {job.id} was deleted before processing started")
            return

        job.status = "processing"
        job.started_at = timezone.now()
        job.processing_log = "Loading BibTeX file..."
        job.save(update_fields=["status", "started_at", "processing_log"])
        logger.info(f"Starting BibTeX job {job.id}")

        # Import scholar components
        from scitex.scholar.pipelines import ScholarPipelineMetadataParallel
        from scitex.scholar.storage import BibTeXHandler

        # Get input file path
        input_path = Path(settings.MEDIA_ROOT) / job.input_file.name
        logger.info(f"Input file path: {input_path}")

        # Load papers from BibTeX
        logger.info("Creating BibTeXHandler...")
        bibtex_handler = BibTeXHandler(project=job.project_name)
        logger.info("Loading papers from BibTeX...")
        papers = bibtex_handler.papers_from_bibtex(input_path)
        logger.info(f"Loaded {len(papers) if papers else 0} papers")

        if not papers:
            raise ValueError("No papers found in BibTeX file")

        job.total_papers = len(papers)
        job.processing_log += f"\nFound {len(papers)} papers in BibTeX file"
        job.save(update_fields=["total_papers", "processing_log"])

        # Create metadata enrichment pipeline
        pipeline = ScholarPipelineMetadataParallel(
            num_workers=job.num_workers,
        )

        # Enrich papers with progress callback and 10-minute timeout
        async def enrich_with_timeout():
            return await asyncio.wait_for(
                pipeline.enrich_papers_async(
                    papers=papers,
                    force=not job.use_cache,  # force=True means ignore cache
                    on_progress=progress_callback,
                ),
                timeout=600,  # 10 minutes = 600 seconds
            )

        try:
            enriched_papers = asyncio.run(enrich_with_timeout())
        except asyncio.TimeoutError:
            # Mark job as failed due to timeout
            job.status = "failed"
            job.error_message = "Enrichment process timed out after 10 minutes. Please try with fewer papers or contact support."
            job.completed_at = timezone.now()
            job.processing_log += f"\n\n✗ TIMEOUT: Job exceeded 10-minute limit"
            job.save(
                update_fields=[
                    "status",
                    "error_message",
                    "completed_at",
                    "processing_log",
                ]
            )
            logger.error(f"BibTeX job {job.id} timed out after 10 minutes")
            return  # Exit the function without raising exception

        # Create output path with format: originalname-enriched-by-scitex_timestamp.bib
        # Use stored original filename (without .bib extension)
        from datetime import datetime

        original_name = (
            Path(job.original_filename).stem
            if job.original_filename
            else Path(job.input_file.name).stem
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{original_name}-enriched-by-scitex_{timestamp}.bib"

        user_dir = str(job.user.id) if job.user else "anonymous"
        output_path = (
            Path(settings.MEDIA_ROOT) / "bibtex_enriched" / user_dir / output_filename
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save enriched BibTeX
        bibtex_handler.papers_to_bibtex(enriched_papers, output_path)

        # Update job with results
        job.total_papers = len(papers)
        job.processed_papers = len(enriched_papers)  # All papers were processed
        job.failed_papers = 0  # No failures if we got here
        job.output_file = str(output_path.relative_to(settings.MEDIA_ROOT))

        # Gitea Integration: Auto-commit enriched .bib file to project repository
        if job.project and job.project.git_clone_path:
            try:
                from apps.project_app.services.git_service import auto_commit_file
                from datetime import datetime

                # Create scitex/scholar/bib_files directory (no __init__.py, no Python conflict)
                project_bib_dir = (
                    Path(job.project.git_clone_path)
                    / "scitex"
                    / "scholar"
                    / "bib_files"
                )
                project_bib_dir.mkdir(parents=True, exist_ok=True)

                # Generate filenames with original name and timestamp
                original_name = (
                    Path(job.original_filename).stem
                    if job.original_filename
                    else "references"
                )
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                original_filename = f"{original_name}_original-{timestamp}.bib"
                enriched_filename = f"{original_name}_enriched-{timestamp}.bib"

                # Copy both original and enriched .bib files to project repository
                input_file_path = Path(settings.MEDIA_ROOT) / job.input_file.name

                project_original_path = project_bib_dir / original_filename
                shutil.copy(input_file_path, project_original_path)
                logger.info(f"Copied original .bib to {project_original_path}")

                project_enriched_path = project_bib_dir / enriched_filename
                shutil.copy(output_path, project_enriched_path)
                logger.info(f"Copied enriched .bib to {project_enriched_path}")

                # ============================================================
                # AUTO-MERGE: Regenerate bibliography using shared utility
                # ============================================================
                from apps.project_app.services.bibliography_manager import (
                    ensure_bibliography_structure,
                    regenerate_bibliography,
                )

                project_path = Path(job.project.git_clone_path)

                # Ensure structure exists
                ensure_bibliography_structure(project_path)

                # Regenerate all bibliographies
                results = regenerate_bibliography(project_path, job.project.name)

                if results["success"]:
                    logger.info(
                        f"✓ Bibliography regenerated: "
                        f"scholar={results['scholar_count']}, "
                        f"writer={results['writer_count']}, "
                        f"total={results['total_count']}"
                    )
                    job.enrichment_summary["bibliography_merged"] = True
                    job.enrichment_summary["total_citations"] = results["total_count"]
                else:
                    logger.warning(
                        f"Bibliography regeneration had errors: {results['errors']}"
                    )

                # Auto-commit both files to Gitea
                commit_message = f"Scholar: Added bibliography - {job.processed_papers}/{job.total_papers} papers enriched"
                success, output = auto_commit_file(
                    project_dir=Path(job.project.git_clone_path),
                    filepath="scitex/",  # Commit entire scitex directory
                    message=commit_message,
                )

                if success:
                    logger.info(f"✓ Auto-committed enriched .bib to Gitea: {output}")
                    job.enrichment_summary["gitea_commit"] = True
                    job.enrichment_summary["gitea_message"] = commit_message
                else:
                    logger.warning(f"Failed to auto-commit to Gitea: {output}")
                    job.enrichment_summary["gitea_commit"] = False
                    job.enrichment_summary["gitea_error"] = output

            except Exception as gitea_error:
                logger.error(f"Gitea integration error: {gitea_error}")
                job.enrichment_summary["gitea_commit"] = False
                job.enrichment_summary["gitea_error"] = str(gitea_error)

        job.status = "completed"
        job.completed_at = timezone.now()
        job.save(
            update_fields=[
                "status",
                "completed_at",
                "total_papers",
                "processed_papers",
                "failed_papers",
                "output_file",
                "enrichment_summary",
            ]
        )

    except Exception as e:
        import traceback

        error_details = str(e)

        # Provide user-friendly error messages
        if "duplicate key" in error_details.lower():
            job.error_message = "Database constraint error - this may be a temporary issue. Please try uploading the file again."
        elif "no papers found" in error_details.lower():
            job.error_message = "No valid BibTeX entries found in the uploaded file. Please check your file format."
        else:
            job.error_message = f"Processing failed: {error_details}"

        job.status = "failed"
        job.completed_at = timezone.now()
        job.processing_log += f"\n\n✗ ERROR: {job.error_message}"
        job.save(
            update_fields=["status", "error_message", "completed_at", "processing_log"]
        )

        logger.error(
            f"BibTeX job {job.id} failed: {error_details}\n{traceback.format_exc()}"
        )


def bibtex_get_urls(request, job_id):
    """API endpoint to extract URLs and DOIs from enriched BibTeX file."""
    import bibtexparser
    from pathlib import Path

    # Get the job (handle both authenticated and anonymous users)
    if request.user.is_authenticated:
        try:
            job = BibTeXEnrichmentJob.objects.get(id=job_id, user=request.user)
        except BibTeXEnrichmentJob.DoesNotExist:
            return JsonResponse(
                {"error": "Job not found or access denied."}, status=404
            )
    else:
        # For anonymous users, check by session_key
        try:
            job = BibTeXEnrichmentJob.objects.get(
                id=job_id, session_key=request.session.session_key
            )
        except BibTeXEnrichmentJob.DoesNotExist:
            return JsonResponse({"error": "Job not found."}, status=404)

    # Check if job is completed and has output file
    if job.status != "completed":
        return JsonResponse(
            {"error": "Job not completed yet.", "status": job.status}, status=400
        )

    if not job.output_file:
        return JsonResponse({"error": "No output file available."}, status=404)

    # Read and parse the BibTeX file
    file_path = Path(settings.MEDIA_ROOT) / job.output_file.name
    if not file_path.exists():
        return JsonResponse({"error": "Output file not found on server."}, status=404)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            bib_database = bibtexparser.load(f)

        urls = []
        for entry in bib_database.entries:
            title = entry.get("title", "Unknown")
            doi = entry.get("doi", "").strip()
            url = entry.get("url", "").strip()

            # Prioritize DOI over URL
            if doi:
                # Add https://doi.org/ prefix if not already present
                if not doi.startswith("http"):
                    final_url = f"https://doi.org/{doi}"
                else:
                    final_url = doi
                urls.append({"title": title, "url": final_url, "type": "doi"})
            elif url:
                urls.append({"title": title, "url": url, "type": "url"})

        return JsonResponse(
            {"job_id": str(job_id), "total_urls": len(urls), "urls": urls}
        )

    except Exception as e:
        return JsonResponse({"error": f"Failed to extract URLs: {str(e)}"}, status=500)


@require_http_methods(["GET"])
def bibtex_recent_jobs(request):
    """API endpoint to get user's recent jobs with summary (anonymous allowed)."""

    # Get recent jobs
    if request.user.is_authenticated:
        jobs = (
            BibTeXEnrichmentJob.objects.filter(user=request.user)
            .select_related("project")
            .order_by("-created_at")[:10]
        )
    else:
        # For anonymous users, get jobs by session key
        jobs = (
            BibTeXEnrichmentJob.objects.filter(
                session_key=request.session.session_key
            ).order_by("-created_at")[:10]
            if request.session.session_key
            else BibTeXEnrichmentJob.objects.none()
        )

    jobs_data = []
    for job in jobs:
        jobs_data.append(
            {
                "id": str(job.id),
                "original_filename": job.original_filename or "Unknown",
                "status": job.status,
                "total_papers": job.total_papers,
                "processed_papers": job.processed_papers,
                "failed_papers": job.failed_papers,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "completed_at": job.completed_at.isoformat()
                if job.completed_at
                else None,
                "progress_percentage": job.get_progress_percentage(),
                "project_name": job.project.name if job.project else None,
            }
        )

    return JsonResponse(
        {
            "success": True,
            "jobs": jobs_data,
            "total": len(jobs_data),
        }
    )


@require_http_methods(["GET"])
def bibtex_resource_status(request):
    """AJAX endpoint to get current resource usage and job queue status."""
    import psutil
    from django.db.models import Q

    # Get all active and queued jobs
    active_jobs = (
        BibTeXEnrichmentJob.objects.filter(status="processing")
        .select_related("user")
        .order_by("started_at")
    )

    queued_jobs = (
        BibTeXEnrichmentJob.objects.filter(status="pending")
        .select_related("user")
        .order_by("created_at")
    )

    # Get recently completed jobs (last hour)
    from django.utils import timezone
    from datetime import timedelta

    one_hour_ago = timezone.now() - timedelta(hours=1)

    recent_completed = BibTeXEnrichmentJob.objects.filter(
        Q(status="completed") | Q(status="failed"), completed_at__gte=one_hour_ago
    ).count()

    # Get system resource usage
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()

    # Check if current user owns any jobs (for showing cancel button)
    if request.user.is_authenticated:
        user_identifier = request.user
        user_session = None
    else:
        user_identifier = None
        user_session = request.session.session_key

    # Build active jobs list (security: only show details for owner's jobs)
    active_jobs_list = []
    for job in active_jobs:
        # Check if this job belongs to current user
        is_owner = (request.user.is_authenticated and job.user == request.user) or (
            not request.user.is_authenticated
            and job.session_key == request.session.session_key
        )

        # For security: only show detailed info for owner's jobs, otherwise show anonymous
        if is_owner:
            active_jobs_list.append(
                {
                    "id": str(job.id),
                    "user": "You",
                    "filename": job.original_filename or "Unknown",
                    "progress": job.get_progress_percentage(),
                    "processed": job.processed_papers,
                    "total": job.total_papers,
                    "started": job.started_at.isoformat() if job.started_at else None,
                    "can_cancel": True,
                    "is_owner": True,
                }
            )
        # Don't add other users' jobs to the list (for privacy/security)

    # Build queued jobs list with position (security: only show owner's jobs)
    queued_jobs_list = []
    user_queue_position = None
    total_queue_position = 0

    for idx, job in enumerate(queued_jobs):
        total_queue_position = idx + 1
        is_owner = (request.user.is_authenticated and job.user == request.user) or (
            not request.user.is_authenticated
            and job.session_key == request.session.session_key
        )

        # For security: only show detailed info for owner's jobs
        if is_owner:
            user_queue_position = idx + 1
            queued_jobs_list.append(
                {
                    "id": str(job.id),
                    "user": "You",
                    "filename": job.original_filename or "Unknown",
                    "position": idx + 1,
                    "created": job.created_at.isoformat() if job.created_at else None,
                    "can_cancel": True,
                    "is_owner": True,
                }
            )
        # Don't add other users' jobs to the list (for privacy/security)

    return JsonResponse(
        {
            "system": {
                "cpu_percent": round(cpu_percent, 1),
                "memory_percent": round(memory.percent, 1),
                "memory_available_gb": round(memory.available / (1024**3), 2),
            },
            "jobs": {
                "active_count": active_jobs.count(),  # Total system active jobs
                "queued_count": queued_jobs.count(),  # Total system queued jobs
                "completed_last_hour": recent_completed,
                "active": active_jobs_list,  # Only user's active jobs
                "queued": queued_jobs_list,  # Only user's queued jobs
                "user_queue_position": user_queue_position,  # User's position in queue (if queued)
            },
            "timestamp": timezone.now().isoformat(),
        }
    )


@require_http_methods(["POST"])
@api_key_optional
def bibtex_save_to_project(request, job_id):
    """Save enriched BibTeX to selected project."""
    from datetime import datetime

    # Get authenticated user
    api_authenticated = hasattr(request, "api_user")
    user = request.api_user if api_authenticated else request.user

    if not user or not user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": "Authentication required"}, status=401
        )

    # Get job
    try:
        job = BibTeXEnrichmentJob.objects.get(id=job_id, user=user)
    except BibTeXEnrichmentJob.DoesNotExist:
        return JsonResponse({"success": False, "error": "Job not found"}, status=404)

    if job.status != "completed":
        return JsonResponse(
            {"success": False, "error": f"Job not completed (status: {job.status})"},
            status=400,
        )

    # Get project_id from request
    project_id = request.POST.get("project_id")
    if not project_id:
        return JsonResponse(
            {"success": False, "error": "No project selected"}, status=400
        )

    # Get project
    from apps.project_app.models import Project

    try:
        project = Project.objects.get(id=project_id, owner=user)
    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )

    try:
        # Validate job has required files
        if not job.input_file or not job.input_file.name:
            logger.error(f"Job {job_id} has no input file")
            return JsonResponse(
                {"success": False, "error": "Original BibTeX file not found"},
                status=404,
            )

        if not job.output_file or not job.output_file.name:
            logger.error(f"Job {job_id} has no output file")
            return JsonResponse(
                {
                    "success": False,
                    "error": "Enriched BibTeX file not found. Job may not be completed yet.",
                },
                status=404,
            )

        # Generate filenames
        original_name = (
            Path(job.original_filename).stem if job.original_filename else "references"
        )
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Copy source files - build paths carefully
        input_path = Path(settings.MEDIA_ROOT) / job.input_file.name
        output_path = Path(settings.MEDIA_ROOT) / job.output_file.name

        logger.info(f"Save to project - Input: {input_path}, Output: {output_path}")

        # Validate the paths exist and are files, not directories
        if not input_path.exists() or not input_path.is_file():
            logger.error(
                f"Input path invalid: exists={input_path.exists()}, is_file={input_path.is_file()}, path={input_path}"
            )
            return JsonResponse(
                {
                    "success": False,
                    "error": f"Original BibTeX file not found at expected location: {job.input_file.name}",
                },
                status=404,
            )

        if not output_path.exists() or not output_path.is_file():
            logger.error(
                f"Output path invalid: exists={output_path.exists()}, is_file={output_path.is_file()}, path={output_path}"
            )
            return JsonResponse(
                {
                    "success": False,
                    "error": f"Enriched BibTeX file not found at expected location: {job.output_file.name}",
                },
                status=404,
            )

        original_filename = f"{original_name}_original-{timestamp}.bib"
        enriched_filename = f"{original_name}_enriched-{timestamp}.bib"

        committed = False

        # If project has git repository, save to git and commit
        if project.git_clone_path:
            from apps.project_app.services.git_service import auto_commit_file

            # Create directory in git repo
            project_bib_dir = (
                Path(project.git_clone_path) / "scitex" / "scholar" / "bib_files"
            )
            project_bib_dir.mkdir(parents=True, exist_ok=True)

            # Copy both files to git directory
            shutil.copy(input_path, project_bib_dir / original_filename)
            shutil.copy(output_path, project_bib_dir / enriched_filename)

            # ============================================================
            # AUTO-MERGE: Regenerate bibliography using shared utility
            # ============================================================
            from apps.project_app.services.bibliography_manager import (
                ensure_bibliography_structure,
                regenerate_bibliography,
            )

            project_path = Path(project.git_clone_path)

            # Ensure structure exists
            ensure_bibliography_structure(project_path)

            # Regenerate all bibliographies
            results = regenerate_bibliography(project_path, project.name)

            if results["success"]:
                logger.info(
                    f"✓ Bibliography regenerated: "
                    f"scholar={results['scholar_count']}, "
                    f"writer={results['writer_count']}, "
                    f"total={results['total_count']}"
                )
            else:
                logger.warning(
                    f"Bibliography regeneration had errors: {results['errors']}"
                )

            # Commit
            success, output = auto_commit_file(
                project_dir=Path(project.git_clone_path),
                filepath="scitex/",  # Commit entire scitex directory
                message=f"Scholar: Added bibliography - {job.processed_papers}/{job.total_papers} papers",
            )
            committed = success

        else:
            # Fallback: Save to media directory structure for projects without git
            project_media_dir = (
                Path(settings.MEDIA_ROOT)
                / "projects"
                / str(project.id)
                / "scholar"
                / "bib_files"
            )
            project_media_dir.mkdir(parents=True, exist_ok=True)

            # Copy both files to media directory
            shutil.copy(input_path, project_media_dir / original_filename)
            shutil.copy(output_path, project_media_dir / enriched_filename)

        # Build file paths for response
        if project.git_clone_path:
            file_paths = {
                "original": f"scitex/scholar/bib_files/{original_filename}",
                "enriched": f"scitex/scholar/bib_files/{enriched_filename}",
                "merged": "scitex/scholar/references.bib",
            }
        else:
            file_paths = {
                "original": f"projects/{project.id}/scholar/bib_files/{original_filename}",
                "enriched": f"projects/{project.id}/scholar/bib_files/{enriched_filename}",
            }

        return JsonResponse(
            {
                "success": True,
                "message": f"Saved to {project.name}",
                "project": project.name,
                "committed": committed,
                "storage": "git" if project.git_clone_path else "media",
                "paths": file_paths,
            }
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"Save failed: {str(e)}"}, status=500
        )


@require_http_methods(["POST"])
def bibtex_cancel_job(request, job_id):
    """Cancel a running or queued BibTeX enrichment job."""

    # Get job by user or session key
    if request.user.is_authenticated:
        job = get_object_or_404(BibTeXEnrichmentJob, id=job_id, user=request.user)
    else:
        job = get_object_or_404(
            BibTeXEnrichmentJob, id=job_id, session_key=request.session.session_key
        )

    # Only allow cancelling pending or processing jobs
    if job.status not in ["pending", "processing"]:
        return JsonResponse(
            {"success": False, "error": f"Cannot cancel job with status: {job.status}"},
            status=400,
        )

    # Mark job as cancelled
    job.status = "cancelled"
    job.error_message = "Cancelled by user"
    job.completed_at = timezone.now()
    job.processing_log += "\n\n✗ Job cancelled by user"
    job.save(
        update_fields=["status", "error_message", "completed_at", "processing_log"]
    )

    # Note: The background thread will check job.status and stop processing

    return JsonResponse({"success": True, "message": "Job cancelled successfully"})


@require_http_methods(["GET"])
def bibtex_job_diff(request, job_id):
    """API endpoint to get diff between original and enriched BibTeX files."""
    import bibtexparser
    from pathlib import Path
    from apps.project_app.services.project_utils import get_current_project

    # Get the job (handle both authenticated and anonymous users)
    if request.user.is_authenticated:
        try:
            job = BibTeXEnrichmentJob.objects.get(id=job_id, user=request.user)
        except BibTeXEnrichmentJob.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Job not found or access denied."},
                status=404,
            )
    else:
        # For anonymous users, check by session_key
        try:
            job = BibTeXEnrichmentJob.objects.get(
                id=job_id, session_key=request.session.session_key
            )
        except BibTeXEnrichmentJob.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Job not found."}, status=404
            )

    # Check if job is completed and has output file
    if job.status != "completed":
        return JsonResponse(
            {"success": False, "error": "Job not completed yet.", "status": job.status},
            status=400,
        )

    if not job.output_file:
        return JsonResponse(
            {"success": False, "error": "No output file available."}, status=404
        )

    # Read and parse both files
    input_path = Path(settings.MEDIA_ROOT) / job.input_file.name
    output_path = Path(settings.MEDIA_ROOT) / job.output_file.name

    if not input_path.exists() or not output_path.exists():
        return JsonResponse(
            {"success": False, "error": "Input or output file not found on server."},
            status=404,
        )

    try:
        # Parse original BibTeX
        with open(input_path, "r", encoding="utf-8") as f:
            original_db = bibtexparser.load(f)

        # Parse enriched BibTeX
        with open(output_path, "r", encoding="utf-8") as f:
            enriched_db = bibtexparser.load(f)

        # Create lookup dictionaries
        original_entries = {entry["ID"]: entry for entry in original_db.entries}
        enriched_entries = {entry["ID"]: entry for entry in enriched_db.entries}

        # Calculate diff - show ALL entries
        diff = []
        for entry_id, enriched_entry in enriched_entries.items():
            original_entry = original_entries.get(entry_id, {})

            # Find added fields only
            added_fields = {}
            original_fields = {}

            for key, value in enriched_entry.items():
                if key == "ID" or key == "ENTRYTYPE":
                    continue

                original_value = original_entry.get(key, "")

                if not original_value and value:
                    # Field was added
                    added_fields[key] = value
                elif original_value:
                    # Field existed (show in original)
                    original_fields[key] = original_value

            # Convert dictionaries to arrays for frontend
            added_fields_array = [
                {"name": k, "value": v} for k, v in added_fields.items()
            ]
            original_fields_array = [
                {"name": k, "value": v} for k, v in original_fields.items()
            ]

            # Include ALL entries (even if no changes)
            diff.append(
                {
                    "key": entry_id,
                    "type": enriched_entry.get("ENTRYTYPE", "article"),
                    "title": enriched_entry.get("title", "Unknown"),
                    "unchanged_fields": original_fields_array,  # Frontend expects "unchanged_fields"
                    "added_fields": added_fields_array,
                    "has_changes": len(added_fields) > 0,
                }
            )

        # Calculate statistics
        total_entries = len(enriched_entries)
        entries_enhanced = sum(1 for entry in diff if entry["has_changes"])
        total_fields_added = sum(len(entry["added_fields"]) for entry in diff)
        total_fields_modified = 0  # Not tracking modifications anymore

        # Calculate major metadata success rates
        major_fields_stats = {
            "abstract": {"acquired": 0, "missing": 0},
            "doi": {"acquired": 0, "missing": 0},
            "citation_count": {"acquired": 0, "missing": 0},
            "impact_factor": {"acquired": 0, "missing": 0},
        }

        for entry_id, enriched_entry in enriched_entries.items():
            # Check abstract
            if enriched_entry.get("abstract"):
                major_fields_stats["abstract"]["acquired"] += 1
            else:
                major_fields_stats["abstract"]["missing"] += 1

            # Check DOI
            if enriched_entry.get("doi"):
                major_fields_stats["doi"]["acquired"] += 1
            else:
                major_fields_stats["doi"]["missing"] += 1

            # Check citation count (various field names)
            if any(
                enriched_entry.get(field)
                for field in ["citation_count", "citations", "citationcount"]
            ):
                major_fields_stats["citation_count"]["acquired"] += 1
            else:
                major_fields_stats["citation_count"]["missing"] += 1

            # Check impact factor
            if enriched_entry.get("journal_impact_factor"):
                major_fields_stats["impact_factor"]["acquired"] += 1
            else:
                major_fields_stats["impact_factor"]["missing"] += 1

        # Build file URLs
        original_filename = job.input_file.name.split("/")[-1]
        enhanced_filename = job.output_file.name.split("/")[-1]

        # Try to build filer URLs if user is authenticated and has a project
        original_filer_url = None
        enhanced_filer_url = None

        if request.user.is_authenticated:
            try:
                current_project = get_current_project(request)
                if current_project:
                    # Build filer URLs: /{username}/{project_slug}/scholar/bib_files/{filename}
                    original_filer_url = f"/{request.user.username}/{current_project.slug}/scholar/bib_files/{original_filename}"
                    enhanced_filer_url = f"/{request.user.username}/{current_project.slug}/scholar/bib_files/{enhanced_filename}"
            except Exception:
                # Fall back to download URLs if filer URL building fails
                pass

        # Fall back to download URLs if filer URLs not available
        if not original_filer_url:
            original_filer_url = f"/scholar/api/bibtex/job/{job.id}/download/original/"
        if not enhanced_filer_url:
            enhanced_filer_url = f"/scholar/api/bibtex/job/{job.id}/download/"

        return JsonResponse(
            {
                "success": True,
                "diff": diff,
                "stats": {
                    "total_entries": total_entries,
                    "entries_enhanced": entries_enhanced,
                    "total_fields_added": total_fields_added,
                    "total_fields_modified": total_fields_modified,
                    "enhancement_rate": round(
                        (entries_enhanced / total_entries * 100), 1
                    )
                    if total_entries > 0
                    else 0,
                    "major_fields": major_fields_stats,  # Add major metadata stats
                },
                "files": {
                    "original": original_filename,
                    "enhanced": enhanced_filename,
                    "original_url": original_filer_url,
                    "enhanced_url": enhanced_filer_url,
                },
            }
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"Failed to generate diff: {str(e)}"},
            status=500,
        )


# EOF
