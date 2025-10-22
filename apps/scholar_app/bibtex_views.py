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
import json
from pathlib import Path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.conf import settings
from .models import BibTeXEnrichmentJob


def bibtex_enrichment(request):
    """BibTeX enrichment landing page - upload and manage enrichment jobs (anonymous allowed)."""
    from apps.project_app.models import Project

    # Get user's recent enrichment jobs
    if request.user.is_authenticated:
        recent_jobs = BibTeXEnrichmentJob.objects.filter(
            user=request.user
        ).select_related('project').order_by('-created_at')[:10]

        # Get user's projects for project selection
        user_projects = Project.objects.filter(
            owner=request.user
        ).order_by('-created_at')
    else:
        # For anonymous users, get jobs by session key
        recent_jobs = BibTeXEnrichmentJob.objects.filter(
            session_key=request.session.session_key
        ).order_by('-created_at')[:10] if request.session.session_key else []
        user_projects = []

    context = {
        'recent_jobs': recent_jobs,
        'user_projects': user_projects,
        'is_anonymous': not request.user.is_authenticated,
        'show_save_prompt': not request.user.is_authenticated,
    }

    return render(request, 'scholar_app/bibtex_enrichment.html', context)


@require_http_methods(["POST"])
def bibtex_upload(request):
    """Handle BibTeX file upload and start enrichment job (anonymous allowed)."""

    # Ensure session exists for anonymous users
    if not request.user.is_authenticated and not request.session.session_key:
        request.session.create()

    # Check if file was uploaded
    if 'bibtex_file' not in request.FILES:
        messages.error(request, 'Please select a BibTeX file to upload.')
        return redirect('scholar_app:bibtex_enrichment')

    bibtex_file = request.FILES['bibtex_file']

    # Validate file extension
    if not bibtex_file.name.endswith('.bib'):
        messages.error(request, 'Please upload a .bib file.')
        return redirect('scholar_app:bibtex_enrichment')

    # Get optional parameters
    project_name = request.POST.get('project_name', '').strip() or None
    project_id = request.POST.get('project_id', '').strip() or None
    num_workers = int(request.POST.get('num_workers', 4))
    browser_mode = request.POST.get('browser_mode', 'stealth')

    # Get project if specified (only for authenticated users)
    project = None
    if project_id and request.user.is_authenticated:
        from apps.project_app.models import Project
        try:
            project = Project.objects.get(id=project_id, owner=request.user)
        except Project.DoesNotExist:
            messages.error(request, 'Selected project not found.')
            return redirect('scholar_app:bibtex_enrichment')

    # Save uploaded file - use user ID or session key
    if request.user.is_authenticated:
        user_identifier = str(request.user.id)
    else:
        user_identifier = f"anonymous_{request.session.session_key}"

    file_path = default_storage.save(
        f'bibtex_uploads/{user_identifier}/{bibtex_file.name}',
        ContentFile(bibtex_file.read())
    )

    # Create enrichment job
    job = BibTeXEnrichmentJob.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key if not request.user.is_authenticated else None,
        input_file=file_path,
        project_name=project_name,
        project=project,
        num_workers=num_workers,
        browser_mode=browser_mode,
        status='pending',
    )

    # Start processing asynchronously (in production, use Celery)
    # For now, we'll process synchronously with a loading page
    if not request.user.is_authenticated:
        messages.info(request, 'Working as guest. Sign up to save your enriched files permanently!')
    messages.success(request, f'BibTeX file uploaded successfully. Starting enrichment job #{job.id}')

    return redirect('scholar_app:bibtex_job_detail', job_id=job.id)


def bibtex_job_detail(request, job_id):
    """View details and progress of a BibTeX enrichment job (anonymous allowed)."""

    # Get job by user or session key
    if request.user.is_authenticated:
        job = get_object_or_404(
            BibTeXEnrichmentJob,
            id=job_id,
            user=request.user
        )
    else:
        job = get_object_or_404(
            BibTeXEnrichmentJob,
            id=job_id,
            session_key=request.session.session_key
        )

    # If job is pending, start processing
    if job.status == 'pending':
        # In production, this would be a Celery task
        # For now, start processing synchronously
        _process_bibtex_job(job)
        job.refresh_from_db()

    context = {
        'job': job,
    }

    return render(request, 'scholar_app/bibtex_job_detail.html', context)


def bibtex_download_enriched(request, job_id):
    """Download the enriched BibTeX file (anonymous allowed)."""

    # Get job by user or session key
    if request.user.is_authenticated:
        job = get_object_or_404(
            BibTeXEnrichmentJob,
            id=job_id,
            user=request.user
        )
    else:
        job = get_object_or_404(
            BibTeXEnrichmentJob,
            id=job_id,
            session_key=request.session.session_key
        )

    if job.status != 'completed' or not job.output_file:
        messages.error(request, 'Enriched BibTeX file not available yet.')
        return redirect('scholar_app:bibtex_job_detail', job_id=job_id)

    # Serve the file
    file_path = Path(settings.MEDIA_ROOT) / job.output_file.name

    if not file_path.exists():
        messages.error(request, 'File not found.')
        return redirect('scholar_app:bibtex_job_detail', job_id=job_id)

    response = FileResponse(
        open(file_path, 'rb'),
        content_type='application/x-bibtex'
    )
    response['Content-Disposition'] = f'attachment; filename="{file_path.name}"'

    return response


@require_http_methods(["GET"])
def bibtex_job_status(request, job_id):
    """AJAX endpoint to get job status and progress (anonymous allowed)."""

    # Get job by user or session key
    if request.user.is_authenticated:
        job = get_object_or_404(
            BibTeXEnrichmentJob,
            id=job_id,
            user=request.user
        )
    else:
        job = get_object_or_404(
            BibTeXEnrichmentJob,
            id=job_id,
            session_key=request.session.session_key
        )

    data = {
        'status': job.status,
        'progress_percentage': job.get_progress_percentage(),
        'total_papers': job.total_papers,
        'processed_papers': job.processed_papers,
        'failed_papers': job.failed_papers,
        'started_at': job.started_at.isoformat() if job.started_at else None,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None,
        'error_message': job.error_message,
        'has_output': bool(job.output_file),
    }

    return JsonResponse(data)


def _process_bibtex_job(job):
    """Process a BibTeX enrichment job using ScholarPipelineBibTeX.

    In production, this should be a Celery task for async processing.
    """
    import shutil
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Update job status
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save()

        # Import scholar pipeline
        from scitex.scholar.pipelines import ScholarPipelineBibTeX

        # Get input file path
        input_path = Path(settings.MEDIA_ROOT) / job.input_file.name

        # Create output path
        output_filename = f"{Path(job.input_file.name).stem}_enriched_{job.id}.bib"
        output_path = Path(settings.MEDIA_ROOT) / 'bibtex_enriched' / str(job.user.id) / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create pipeline
        pipeline = ScholarPipelineBibTeX(
            num_workers=job.num_workers,
            browser_mode=job.browser_mode,
            base_chrome_profile='system',
        )

        # Process BibTeX file
        papers = asyncio.run(
            pipeline.process_bibtex_file_async(
                bibtex_path=input_path,
                project=job.project_name,
                output_bibtex_path=output_path,
            )
        )

        # Update job with results
        job.total_papers = len(papers)
        job.processed_papers = len([p for p in papers if p.metadata.path.pdfs])
        job.failed_papers = len(papers) - job.processed_papers
        job.output_file = str(output_path.relative_to(settings.MEDIA_ROOT))

        # Gitea Integration: Auto-commit enriched .bib file to project repository
        if job.project and job.project.git_clone_path:
            try:
                from apps.core_app.git_operations import auto_commit_file

                # Create references directory in project if it doesn't exist
                project_refs_dir = Path(job.project.git_clone_path) / 'references'
                project_refs_dir.mkdir(parents=True, exist_ok=True)

                # Copy enriched .bib to project repository
                project_bib_path = project_refs_dir / 'references.bib'
                shutil.copy(output_path, project_bib_path)

                logger.info(f"Copied enriched .bib to {project_bib_path}")

                # Auto-commit to Gitea
                commit_message = f"Scholar: Enriched bibliography ({job.processed_papers}/{job.total_papers} papers enriched)"
                success, output = auto_commit_file(
                    project_dir=Path(job.project.git_clone_path),
                    filepath='references/references.bib',
                    message=commit_message
                )

                if success:
                    logger.info(f"✓ Auto-committed enriched .bib to Gitea: {output}")
                    job.enrichment_summary['gitea_commit'] = True
                    job.enrichment_summary['gitea_message'] = commit_message
                else:
                    logger.warning(f"Failed to auto-commit to Gitea: {output}")
                    job.enrichment_summary['gitea_commit'] = False
                    job.enrichment_summary['gitea_error'] = output

            except Exception as gitea_error:
                logger.error(f"Gitea integration error: {gitea_error}")
                job.enrichment_summary['gitea_commit'] = False
                job.enrichment_summary['gitea_error'] = str(gitea_error)

        job.status = 'completed'
        job.completed_at = timezone.now()
        job.save()

    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        job.completed_at = timezone.now()
        job.save()
        raise


# EOF
