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
import logging
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

logger = logging.getLogger(__name__)


def bibtex_enrichment(request):
    """BibTeX enrichment landing page - upload and manage enrichment jobs."""
    from apps.project_app.models import Project

    # Initialize context
    context = {
        'recent_jobs': [],
        'user_projects': [],
    }

    # Only show user-specific data if authenticated
    if request.user.is_authenticated:
        # Get user's recent enrichment jobs
        context['recent_jobs'] = BibTeXEnrichmentJob.objects.filter(
            user=request.user
        ).select_related('project').order_by('-created_at')[:10]

        # Get user's projects for project selection
        context['user_projects'] = Project.objects.filter(
            owner=request.user
        ).order_by('-created_at')

    return render(request, 'scholar_app/bibtex_enrichment.html', context)


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
    project_id = request.POST.get('project_id', '').strip() or None
    num_workers = int(request.POST.get('num_workers', 4))
    # No browser needed - enrichment uses APIs only

    # Get project if specified (only for authenticated users)
    project = None
    if project_id and request.user.is_authenticated:
        from apps.project_app.models import Project
        try:
            project = Project.objects.get(id=project_id, owner=request.user)
        except Project.DoesNotExist:
            messages.error(request, 'Selected project not found.')
            return redirect('scholar_app:bibtex_enrichment')

    # Save uploaded file
    # Use user ID for authenticated users, 'anonymous' for anonymous users
    user_folder = request.user.id if request.user.is_authenticated else 'anonymous'
    file_path = default_storage.save(
        f'bibtex_uploads/{user_folder}/{bibtex_file.name}',
        ContentFile(bibtex_file.read())
    )

    # Create enrichment job
    # For anonymous users, user field will be None
    job = BibTeXEnrichmentJob.objects.create(
        user=request.user if request.user.is_authenticated else None,
        input_file=file_path,
        project_name=project_name,
        project=project,
        num_workers=num_workers,
        browser_mode='none',  # BibTeX enrichment is API-only, no browser needed
        status='pending',
    )

    # Store job ID in session for anonymous users to track their job
    if not request.user.is_authenticated:
        if 'anonymous_jobs' not in request.session:
            request.session['anonymous_jobs'] = []
        request.session['anonymous_jobs'].append(str(job.id))
        request.session.modified = True

    # Start processing asynchronously in background thread
    import threading

    def process_in_background():
        try:
            # Run in thread (not async) to avoid Django ORM issues
            _process_bibtex_job(job)
        except Exception as e:
            logger.error(f"Background processing error for job {job.id}: {e}")
            # Try to save error to job
            try:
                job.refresh_from_db()
                job.status = 'failed'
                job.error_message = f"Background thread error: {str(e)}"
                job.processing_log += f"\n\n✗ FATAL ERROR: {str(e)}\n"
                job.completed_at = timezone.now()
                job.save()
            except:
                pass

    thread = threading.Thread(target=process_in_background, daemon=True)
    thread.start()

    # Mark as processing immediately so polling shows it's started
    job.status = 'processing'
    job.started_at = timezone.now()
    job.save()

    messages.success(request, f'BibTeX file uploaded successfully. Starting enrichment job #{job.id}')

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'job_id': str(job.id),
            'message': 'BibTeX enrichment job started successfully'
        })

    # For non-AJAX requests, redirect back to scholar page with a message
    # No need for separate job detail page anymore - progress shows in panel
    messages.info(request, f'BibTeX enrichment started. Job ID: {job.id}. Please use the AJAX interface.')
    return redirect('scholar_app:index')


def bibtex_job_detail(request, job_id):
    """View details and progress of a BibTeX enrichment job."""

    # For authenticated users, verify ownership
    if request.user.is_authenticated:
        job = get_object_or_404(
            BibTeXEnrichmentJob,
            id=job_id,
            user=request.user
        )
    else:
        # For anonymous users, verify job is in their session
        anonymous_jobs = request.session.get('anonymous_jobs', [])
        if str(job_id) not in anonymous_jobs:
            messages.error(request, 'Job not found or access denied.')
            return redirect('scholar_app:bibtex_enrichment')

        job = get_object_or_404(
            BibTeXEnrichmentJob,
            id=job_id,
            user=None
        )

    # If job is pending, start processing in background
    if job.status == 'pending':
        # In production, this would be a Celery task
        # For now, start processing in a background thread
        import threading

        def process_in_background():
            try:
                # Run in thread (not async) to avoid Django ORM issues
                _process_bibtex_job(job)
            except Exception as e:
                logger.error(f"Background processing error for job {job.id}: {e}")
                # Try to save error to job
                try:
                    job.refresh_from_db()
                    job.status = 'failed'
                    job.error_message = f"Background thread error: {str(e)}"
                    job.processing_log += f"\n\n✗ FATAL ERROR: {str(e)}\n"
                    job.completed_at = timezone.now()
                    job.save()
                except:
                    pass

        thread = threading.Thread(target=process_in_background, daemon=True)
        thread.start()

        # Mark as processing immediately so polling shows it's started
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save()

    context = {
        'job': job,
    }

    return render(request, 'scholar_app/bibtex_job_detail.html', context)


def bibtex_download_enriched(request, job_id):
    """Download the enriched BibTeX file."""

    # For authenticated users, verify ownership
    if request.user.is_authenticated:
        job = get_object_or_404(
            BibTeXEnrichmentJob,
            id=job_id,
            user=request.user
        )
    else:
        # For anonymous users, verify job is in their session
        anonymous_jobs = request.session.get('anonymous_jobs', [])
        if str(job_id) not in anonymous_jobs:
            messages.error(request, 'Job not found or access denied.')
            return redirect('scholar_app:bibtex_enrichment')

        job = get_object_or_404(
            BibTeXEnrichmentJob,
            id=job_id,
            user=None
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
    """AJAX endpoint to get job status and progress."""

    # For authenticated users, verify ownership
    if request.user.is_authenticated:
        job = get_object_or_404(
            BibTeXEnrichmentJob,
            id=job_id,
            user=request.user
        )
    else:
        # For anonymous users, verify job is in their session
        anonymous_jobs = request.session.get('anonymous_jobs', [])
        if str(job_id) not in anonymous_jobs:
            return JsonResponse({'error': 'Job not found or access denied.'}, status=403)

        job = get_object_or_404(
            BibTeXEnrichmentJob,
            id=job_id,
            user=None
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
        'log': job.processing_log,  # Real-time processing log
    }

    return JsonResponse(data)


def _append_log_sync(job, message):
    """Helper function to append log message to job and save (sync version for threading)."""
    timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}\n"
    job.processing_log += log_line
    job.save(update_fields=['processing_log'])
    return log_line


def _process_bibtex_job(job):
    """Process a BibTeX enrichment job using metadata-only pipeline (API-only).

    In production, this should be a Celery task for async processing.
    """
    import shutil
    import traceback

    try:
        # IMMEDIATE log write to show we started
        job.processing_log = f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] Function started\n"

        # Update job status (only if not already processing)
        if job.status != 'processing':
            job.status = 'processing'
            job.started_at = timezone.now()

        job.save()

        _append_log_sync(job, "Background thread is running...")
        _append_log_sync(job, "Starting BibTeX enrichment process...")
        _append_log_sync(job, f"Workers: {job.num_workers} (API-only mode)")

        # Import metadata-only pipeline (no browser needed!)
        from scitex.scholar.pipelines import ScholarPipelineMetadataParallel
        from scitex.scholar.storage import BibTeXHandler

        # Get input file path
        input_path = Path(settings.MEDIA_ROOT) / job.input_file.name
        _append_log_sync(job, f"Input file: {input_path.name}")

        # Create output path
        user_folder = str(job.user.id) if job.user else 'anonymous'
        output_filename = f"{Path(job.input_file.name).stem}_enriched_{job.id}.bib"
        output_path = Path(settings.MEDIA_ROOT) / 'bibtex_enriched' / user_folder / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        _append_log_sync(job, f"Output will be saved to: {output_filename}")

        # Create metadata-only pipeline (API-based, no browser)
        _append_log_sync(job, "Initializing metadata enrichment pipeline...")
        _append_log_sync(job, "Using API sources: CrossRef, Semantic Scholar, PubMed, OpenAlex")
        _append_log_sync(job, "No browser automation - fast API-only enrichment")

        pipeline = ScholarPipelineMetadataParallel(num_workers=job.num_workers)
        _append_log_sync(job, "Pipeline initialized successfully")

        # Load papers from BibTeX
        _append_log_sync(job, "Loading BibTeX entries...")
        bibtex_handler = BibTeXHandler(project=job.project_name)
        papers = bibtex_handler.papers_from_bibtex(input_path)

        if not papers:
            _append_log_sync(job, "WARNING: No papers found in BibTeX file")
            raise ValueError("No papers found in BibTeX file")

        _append_log_sync(job, f"Loaded {len(papers)} papers from BibTeX")

        # Set total papers count immediately for progress tracking
        job.total_papers = len(papers)
        job.processed_papers = 0
        job.failed_papers = 0
        job.save(update_fields=['total_papers', 'processed_papers', 'failed_papers'])

        # Enrich papers with metadata (API-only, with progress tracking via callback)
        _append_log_sync(job, "Enriching papers with metadata...")
        _append_log_sync(job, "Fetching citations, impact factors, abstracts...")
        _append_log_sync(job, "")

        # Define progress callback for real-time updates
        def progress_callback(current, total, info):
            """Called after each paper is processed."""
            title = info.get('title', 'Untitled')[:60]
            success = info.get('success', False)
            error = info.get('error')

            # Log progress
            status_icon = "✓" if success else "✗"
            _append_log_sync(job, f"[{current}/{total}] {status_icon} {title}")

            if error:
                _append_log_sync(job, f"    Error: {error[:100]}")

            # Update counters
            if success:
                job.processed_papers = current
            else:
                job.failed_papers += 1

            # Save to database for real-time polling
            job.save(update_fields=['processed_papers', 'failed_papers', 'processing_log'])

        # Enrich all papers with progress callback
        enriched_papers = asyncio.run(
            pipeline.enrich_papers_async(papers, on_progress=progress_callback)
        )

        _append_log_sync(job, "")
        _append_log_sync(job, f"Enrichment complete! Processed {len(enriched_papers)} papers")

        # Save enriched BibTeX
        _append_log_sync(job, "Saving enriched BibTeX file...")
        from scitex.scholar.core import Papers
        enriched_collection = Papers(enriched_papers, project=job.project_name)
        bibtex_handler.papers_to_bibtex(enriched_collection, output_path=output_path)
        _append_log_sync(job, f"Saved enriched BibTeX to: {output_filename}")

        # Update job with output file path (counts already updated incrementally)
        job.output_file = str(output_path.relative_to(settings.MEDIA_ROOT))

        _append_log_sync(job, "")
        _append_log_sync(job, "=" * 50)
        _append_log_sync(job, "ENRICHMENT SUMMARY")
        _append_log_sync(job, "=" * 50)
        _append_log_sync(job, f"Total papers: {job.total_papers}")
        _append_log_sync(job, f"Successfully enriched: {job.processed_papers}")
        _append_log_sync(job, f"Failed: {job.failed_papers}")
        _append_log_sync(job, "=" * 50)

        # Gitea Integration: Auto-commit enriched .bib file to project repository
        if job.project and job.project.git_clone_path:
            try:
                _append_log_sync(job, "")
                _append_log_sync(job, "Gitea Integration: Auto-committing to repository...")

                from apps.core_app.git_operations import auto_commit_file

                # Create references directory in project if it doesn't exist
                project_refs_dir = Path(job.project.git_clone_path) / 'references'
                project_refs_dir.mkdir(parents=True, exist_ok=True)

                # Copy enriched .bib to project repository
                project_bib_path = project_refs_dir / 'references.bib'
                shutil.copy(output_path, project_bib_path)

                _append_log_sync(job, f"Copied enriched .bib to project: {project_bib_path.name}")
                logger.info(f"Copied enriched .bib to {project_bib_path}")

                # Auto-commit to Gitea
                commit_message = f"Scholar: Enriched bibliography ({job.processed_papers}/{job.total_papers} papers enriched)"
                _append_log_sync(job, "Committing to Gitea...")

                success, output = auto_commit_file(
                    project_dir=Path(job.project.git_clone_path),
                    filepath='references/references.bib',
                    message=commit_message
                )

                if success:
                    _append_log_sync(job, "✓ Successfully auto-committed to Gitea!")
                    logger.info(f"✓ Auto-committed enriched .bib to Gitea: {output}")
                    job.enrichment_summary['gitea_commit'] = True
                    job.enrichment_summary['gitea_message'] = commit_message
                else:
                    _append_log_sync(job, f"✗ Failed to auto-commit to Gitea: {output}")
                    logger.warning(f"Failed to auto-commit to Gitea: {output}")
                    job.enrichment_summary['gitea_commit'] = False
                    job.enrichment_summary['gitea_error'] = output

            except Exception as gitea_error:
                _append_log_sync(job, f"✗ Gitea integration error: {str(gitea_error)}")
                logger.error(f"Gitea integration error: {gitea_error}")
                job.enrichment_summary['gitea_commit'] = False
                job.enrichment_summary['gitea_error'] = str(gitea_error)

        _append_log_sync(job, "")
        _append_log_sync(job, "✓ Enrichment process completed successfully!")
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.save()

    except Exception as e:
        error_msg = f"✗ ERROR: {str(e)}"
        error_traceback = traceback.format_exc()

        # Log error with full traceback
        try:
            _append_log_sync(job, "")
            _append_log_sync(job, "=" * 50)
            _append_log_sync(job, error_msg)
            _append_log_sync(job, "=" * 50)
            _append_log_sync(job, "Full traceback:")
            _append_log_sync(job, error_traceback)
        except:
            # If logging fails, write directly
            job.processing_log += f"\n\n{error_msg}\n{error_traceback}\n"

        job.status = 'failed'
        job.error_message = str(e)
        job.completed_at = timezone.now()
        job.save()

        # Also log to Django logger
        logger.error(f"BibTeX job {job.id} failed: {e}")
        logger.error(error_traceback)


# EOF
