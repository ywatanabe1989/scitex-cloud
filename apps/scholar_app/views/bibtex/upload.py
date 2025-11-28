#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-cloud/apps/scholar_app/views/bibtex/upload.py

"""
BibTeX Upload View

Handle BibTeX file upload and start enrichment job.
"""

import logging
from pathlib import Path
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from ...models import BibTeXEnrichmentJob
from apps.scholar_app.api_auth import api_key_optional

logger = logging.getLogger(__name__)


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

        # Ensure session exists for visitor users
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
        # Visitor users: Ask if they want to cancel old job
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
                    )
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
    use_cache = request.POST.get("use_cache", "on") == "on"

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
        user_identifier = f"visitor_{request.session.session_key}"

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
    from .utils import process_bibtex_job

    thread = threading.Thread(target=process_bibtex_job, args=(job,))
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


# EOF
