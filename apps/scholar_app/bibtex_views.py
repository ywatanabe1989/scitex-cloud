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


@login_required
def bibtex_enrichment(request):
    """BibTeX enrichment landing page - upload and manage enrichment jobs."""

    # Get user's recent enrichment jobs
    recent_jobs = BibTeXEnrichmentJob.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]

    context = {
        'recent_jobs': recent_jobs,
    }

    return render(request, 'scholar_app/bibtex_enrichment.html', context)


@login_required
@require_http_methods(["POST"])
def bibtex_upload(request):
    """Handle BibTeX file upload and start enrichment job."""

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
    num_workers = int(request.POST.get('num_workers', 4))
    browser_mode = request.POST.get('browser_mode', 'stealth')

    # Save uploaded file
    file_path = default_storage.save(
        f'bibtex_uploads/{request.user.id}/{bibtex_file.name}',
        ContentFile(bibtex_file.read())
    )

    # Create enrichment job
    job = BibTeXEnrichmentJob.objects.create(
        user=request.user,
        input_file=file_path,
        project_name=project_name,
        num_workers=num_workers,
        browser_mode=browser_mode,
        status='pending',
    )

    # Start processing asynchronously (in production, use Celery)
    # For now, we'll process synchronously with a loading page
    messages.success(request, f'BibTeX file uploaded successfully. Starting enrichment job #{job.id}')

    return redirect('scholar_app:bibtex_job_detail', job_id=job.id)


@login_required
def bibtex_job_detail(request, job_id):
    """View details and progress of a BibTeX enrichment job."""

    job = get_object_or_404(
        BibTeXEnrichmentJob,
        id=job_id,
        user=request.user
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


@login_required
def bibtex_download_enriched(request, job_id):
    """Download the enriched BibTeX file."""

    job = get_object_or_404(
        BibTeXEnrichmentJob,
        id=job_id,
        user=request.user
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


@login_required
@require_http_methods(["GET"])
def bibtex_job_status(request, job_id):
    """AJAX endpoint to get job status and progress."""

    job = get_object_or_404(
        BibTeXEnrichmentJob,
        id=job_id,
        user=request.user
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
