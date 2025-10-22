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

    # Store original filename (before Django adds suffix)
    original_filename = bibtex_file.name

    # Validate file extension
    if not bibtex_file.name.endswith('.bib'):
        messages.error(request, 'Please upload a .bib file.')
        return redirect('scholar_app:bibtex_enrichment')

    # Job management: One user = One job at a time
    # Different handling for authenticated vs anonymous users

    if request.user.is_authenticated:
        # Authenticated users: Can cancel old jobs and start new ones
        existing_jobs = BibTeXEnrichmentJob.objects.filter(
            user=request.user,
            status__in=['pending', 'processing']
        )

        # Cancel all existing jobs - new upload takes priority
        for old_job in existing_jobs:
            old_job.status = 'cancelled'
            old_job.error_message = 'Cancelled - new job uploaded'
            old_job.completed_at = timezone.now()
            old_job.processing_log += '\n\n✗ Cancelled by user uploading new file'
            old_job.save(update_fields=['status', 'error_message', 'completed_at', 'processing_log'])

    else:
        # Anonymous users: Ask if they want to cancel old job
        existing_jobs = BibTeXEnrichmentJob.objects.filter(
            session_key=request.session.session_key,
            status__in=['pending', 'processing']
        ) if request.session.session_key else BibTeXEnrichmentJob.objects.none()

        if existing_jobs.exists():
            # Check if user explicitly wants to cancel old job
            force_cancel = request.POST.get('force_cancel') == 'true'

            if force_cancel:
                # User chose to cancel old job - proceed with cancellation
                for old_job in existing_jobs:
                    old_job.status = 'cancelled'
                    old_job.error_message = 'Cancelled - new job uploaded'
                    old_job.completed_at = timezone.now()
                    old_job.processing_log += '\n\n✗ Cancelled by user uploading new file'
                    old_job.save(update_fields=['status', 'error_message', 'completed_at', 'processing_log'])
                # Continue to create new job below
            else:
                # Show confirmation dialog to user
                existing_job = existing_jobs.first()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'requires_confirmation': True,
                        'existing_job': {
                            'id': str(existing_job.id),
                            'filename': existing_job.original_filename or 'Unknown',
                            'progress': existing_job.get_progress_percentage(),
                            'status': existing_job.status,
                        },
                        'message': 'You already have a job in progress. Cancel it and start new job?'
                    }, status=409)  # 409 Conflict
                else:
                    messages.warning(request, f'You already have a job in progress: "{existing_job.original_filename or "Unknown"}". Please wait for it to complete.')
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
        original_filename=original_filename,
        project_name=project_name,
        project=project,
        num_workers=num_workers,
        browser_mode=browser_mode,
        status='pending',
    )

    # Start processing immediately in a background thread
    import threading
    thread = threading.Thread(target=_process_bibtex_job, args=(job,))
    thread.daemon = True
    thread.start()

    # Return JSON for AJAX requests (no Django messages needed - we show progress in the UI)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'job_id': str(job.id),
        })

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
        'log': job.processing_log,  # Add processing log for real-time updates
    }

    return JsonResponse(data)


def _process_bibtex_job(job):
    """Process a BibTeX enrichment job using ScholarPipelineMetadataParallel directly.

    In production, this should be a Celery task for async processing.
    """
    import shutil
    import logging
    import threading

    logger = logging.getLogger(__name__)

    # Create a cancellation flag that can be checked
    cancellation_flag = {'cancelled': False}

    def check_cancellation():
        """Check if job should be cancelled (either by user or timeout)."""
        job.refresh_from_db()
        if job.status == 'cancelled':
            cancellation_flag['cancelled'] = True
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
                if await sync_to_async(lambda: job.status)() == 'cancelled':
                    return  # Job was cancelled, stop updating

                # Create progress message
                title = info.get('title', 'Unknown')[:50]
                status_icon = '✓' if info.get('success') else '✗'
                message = f"[{current}/{total}] {status_icon} {title}"

                current_log = await sync_to_async(lambda: job.processing_log)()
                if current_log:
                    job.processing_log = current_log + f"\n{message}"
                else:
                    job.processing_log = message

                # Update counters
                job.processed_papers = current
                await sync_to_async(job.save)(update_fields=['processing_log', 'processed_papers'])
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
        # Update job status - refresh first to avoid conflicts
        try:
            job.refresh_from_db()
            # Check if job was cancelled before we even started
            if job.status == 'cancelled':
                logger.info(f"Job {job.id} was cancelled before processing started")
                return
        except BibTeXEnrichmentJob.DoesNotExist:
            logger.warning(f"Job {job.id} was deleted before processing started")
            return

        job.status = 'processing'
        job.started_at = timezone.now()
        job.processing_log = "Loading BibTeX file..."
        job.save(update_fields=['status', 'started_at', 'processing_log'])
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
        job.save(update_fields=['total_papers', 'processing_log'])

        # Create metadata enrichment pipeline
        pipeline = ScholarPipelineMetadataParallel(
            num_workers=job.num_workers,
        )

        # Enrich papers with progress callback and 10-minute timeout
        async def enrich_with_timeout():
            return await asyncio.wait_for(
                pipeline.enrich_papers_async(
                    papers=papers,
                    force=False,
                    on_progress=progress_callback,
                ),
                timeout=600  # 10 minutes = 600 seconds
            )

        try:
            enriched_papers = asyncio.run(enrich_with_timeout())
        except asyncio.TimeoutError:
            # Mark job as failed due to timeout
            job.status = 'failed'
            job.error_message = 'Enrichment process timed out after 10 minutes. Please try with fewer papers or contact support.'
            job.completed_at = timezone.now()
            job.processing_log += f"\n\n✗ TIMEOUT: Job exceeded 10-minute limit"
            job.save(update_fields=['status', 'error_message', 'completed_at', 'processing_log'])
            logger.error(f"BibTeX job {job.id} timed out after 10 minutes")
            return  # Exit the function without raising exception

        # Create output path with format: originalname-enriched-by-scitex_timestamp.bib
        # Use stored original filename (without .bib extension)
        from datetime import datetime

        original_name = Path(job.original_filename).stem if job.original_filename else Path(job.input_file.name).stem
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{original_name}-enriched-by-scitex_{timestamp}.bib"

        user_dir = str(job.user.id) if job.user else 'anonymous'
        output_path = Path(settings.MEDIA_ROOT) / 'bibtex_enriched' / user_dir / output_filename
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
        job.save(update_fields=['status', 'completed_at', 'total_papers', 'processed_papers', 'failed_papers', 'output_file', 'enrichment_summary'])

    except Exception as e:
        import traceback
        error_details = str(e)

        # Provide user-friendly error messages
        if 'duplicate key' in error_details.lower():
            job.error_message = "Database constraint error - this may be a temporary issue. Please try uploading the file again."
        elif 'no papers found' in error_details.lower():
            job.error_message = "No valid BibTeX entries found in the uploaded file. Please check your file format."
        else:
            job.error_message = f"Processing failed: {error_details}"

        job.status = 'failed'
        job.completed_at = timezone.now()
        job.processing_log += f"\n\n✗ ERROR: {job.error_message}"
        job.save(update_fields=['status', 'error_message', 'completed_at', 'processing_log'])

        logger.error(f"BibTeX job {job.id} failed: {error_details}\n{traceback.format_exc()}")


def bibtex_get_urls(request, job_id):
    """API endpoint to extract URLs and DOIs from enriched BibTeX file."""
    import bibtexparser
    from pathlib import Path

    # Get the job (handle both authenticated and anonymous users)
    if request.user.is_authenticated:
        try:
            job = BibTeXEnrichmentJob.objects.get(id=job_id, user=request.user)
        except BibTeXEnrichmentJob.DoesNotExist:
            return JsonResponse({'error': 'Job not found or access denied.'}, status=404)
    else:
        # For anonymous users, check by session_key
        try:
            job = BibTeXEnrichmentJob.objects.get(
                id=job_id,
                session_key=request.session.session_key
            )
        except BibTeXEnrichmentJob.DoesNotExist:
            return JsonResponse({'error': 'Job not found.'}, status=404)

    # Check if job is completed and has output file
    if job.status != 'completed':
        return JsonResponse({
            'error': 'Job not completed yet.',
            'status': job.status
        }, status=400)

    if not job.output_file:
        return JsonResponse({'error': 'No output file available.'}, status=404)

    # Read and parse the BibTeX file
    file_path = Path(settings.MEDIA_ROOT) / job.output_file.name
    if not file_path.exists():
        return JsonResponse({'error': 'Output file not found on server.'}, status=404)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            bib_database = bibtexparser.load(f)

        urls = []
        for entry in bib_database.entries:
            title = entry.get('title', 'Unknown')
            doi = entry.get('doi', '').strip()
            url = entry.get('url', '').strip()

            # Prioritize DOI over URL
            if doi:
                # Add https://doi.org/ prefix if not already present
                if not doi.startswith('http'):
                    final_url = f"https://doi.org/{doi}"
                else:
                    final_url = doi
                urls.append({
                    'title': title,
                    'url': final_url,
                    'type': 'doi'
                })
            elif url:
                urls.append({
                    'title': title,
                    'url': url,
                    'type': 'url'
                })

        return JsonResponse({
            'job_id': str(job_id),
            'total_urls': len(urls),
            'urls': urls
        })

    except Exception as e:
        return JsonResponse({
            'error': f'Failed to extract URLs: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def bibtex_resource_status(request):
    """AJAX endpoint to get current resource usage and job queue status."""
    import psutil
    from django.db.models import Q

    # Get all active and queued jobs
    active_jobs = BibTeXEnrichmentJob.objects.filter(
        status='processing'
    ).select_related('user').order_by('started_at')

    queued_jobs = BibTeXEnrichmentJob.objects.filter(
        status='pending'
    ).select_related('user').order_by('created_at')

    # Get recently completed jobs (last hour)
    from django.utils import timezone
    from datetime import timedelta
    one_hour_ago = timezone.now() - timedelta(hours=1)

    recent_completed = BibTeXEnrichmentJob.objects.filter(
        Q(status='completed') | Q(status='failed'),
        completed_at__gte=one_hour_ago
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
        is_owner = (request.user.is_authenticated and job.user == request.user) or \
                   (not request.user.is_authenticated and job.session_key == request.session.session_key)

        # For security: only show detailed info for owner's jobs, otherwise show anonymous
        if is_owner:
            active_jobs_list.append({
                'id': str(job.id),
                'user': 'You',
                'filename': job.original_filename or 'Unknown',
                'progress': job.get_progress_percentage(),
                'processed': job.processed_papers,
                'total': job.total_papers,
                'started': job.started_at.isoformat() if job.started_at else None,
                'can_cancel': True,
                'is_owner': True,
            })
        # Don't add other users' jobs to the list (for privacy/security)

    # Build queued jobs list with position (security: only show owner's jobs)
    queued_jobs_list = []
    user_queue_position = None
    total_queue_position = 0

    for idx, job in enumerate(queued_jobs):
        total_queue_position = idx + 1
        is_owner = (request.user.is_authenticated and job.user == request.user) or \
                   (not request.user.is_authenticated and job.session_key == request.session.session_key)

        # For security: only show detailed info for owner's jobs
        if is_owner:
            user_queue_position = idx + 1
            queued_jobs_list.append({
                'id': str(job.id),
                'user': 'You',
                'filename': job.original_filename or 'Unknown',
                'position': idx + 1,
                'created': job.created_at.isoformat() if job.created_at else None,
                'can_cancel': True,
                'is_owner': True,
            })
        # Don't add other users' jobs to the list (for privacy/security)

    return JsonResponse({
        'system': {
            'cpu_percent': round(cpu_percent, 1),
            'memory_percent': round(memory.percent, 1),
            'memory_available_gb': round(memory.available / (1024**3), 2),
        },
        'jobs': {
            'active_count': active_jobs.count(),  # Total system active jobs
            'queued_count': queued_jobs.count(),  # Total system queued jobs
            'completed_last_hour': recent_completed,
            'active': active_jobs_list,  # Only user's active jobs
            'queued': queued_jobs_list,  # Only user's queued jobs
            'user_queue_position': user_queue_position,  # User's position in queue (if queued)
        },
        'timestamp': timezone.now().isoformat(),
    })


@require_http_methods(["POST"])
def bibtex_cancel_job(request, job_id):
    """Cancel a running or queued BibTeX enrichment job."""

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

    # Only allow cancelling pending or processing jobs
    if job.status not in ['pending', 'processing']:
        return JsonResponse({
            'success': False,
            'error': f'Cannot cancel job with status: {job.status}'
        }, status=400)

    # Mark job as cancelled
    job.status = 'cancelled'
    job.error_message = 'Cancelled by user'
    job.completed_at = timezone.now()
    job.processing_log += '\n\n✗ Job cancelled by user'
    job.save(update_fields=['status', 'error_message', 'completed_at', 'processing_log'])

    # Note: The background thread will check job.status and stop processing

    return JsonResponse({
        'success': True,
        'message': 'Job cancelled successfully'
    })


@require_http_methods(["GET"])
def bibtex_job_diff(request, job_id):
    """API endpoint to get diff between original and enriched BibTeX files."""
    import bibtexparser
    from pathlib import Path

    # Get the job (handle both authenticated and anonymous users)
    if request.user.is_authenticated:
        try:
            job = BibTeXEnrichmentJob.objects.get(id=job_id, user=request.user)
        except BibTeXEnrichmentJob.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Job not found or access denied.'}, status=404)
    else:
        # For anonymous users, check by session_key
        try:
            job = BibTeXEnrichmentJob.objects.get(
                id=job_id,
                session_key=request.session.session_key
            )
        except BibTeXEnrichmentJob.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Job not found.'}, status=404)

    # Check if job is completed and has output file
    if job.status != 'completed':
        return JsonResponse({
            'success': False,
            'error': 'Job not completed yet.',
            'status': job.status
        }, status=400)

    if not job.output_file:
        return JsonResponse({'success': False, 'error': 'No output file available.'}, status=404)

    # Read and parse both files
    input_path = Path(settings.MEDIA_ROOT) / job.input_file.name
    output_path = Path(settings.MEDIA_ROOT) / job.output_file.name

    if not input_path.exists() or not output_path.exists():
        return JsonResponse({'success': False, 'error': 'Input or output file not found on server.'}, status=404)

    try:
        # Parse original BibTeX
        with open(input_path, 'r', encoding='utf-8') as f:
            original_db = bibtexparser.load(f)

        # Parse enriched BibTeX
        with open(output_path, 'r', encoding='utf-8') as f:
            enriched_db = bibtexparser.load(f)

        # Create lookup dictionaries
        original_entries = {entry['ID']: entry for entry in original_db.entries}
        enriched_entries = {entry['ID']: entry for entry in enriched_db.entries}

        # Calculate diff - show ALL entries
        diff = []
        for entry_id, enriched_entry in enriched_entries.items():
            original_entry = original_entries.get(entry_id, {})

            # Find added fields only
            added_fields = {}
            original_fields = {}

            for key, value in enriched_entry.items():
                if key == 'ID' or key == 'ENTRYTYPE':
                    continue

                original_value = original_entry.get(key, '')

                if not original_value and value:
                    # Field was added
                    added_fields[key] = value
                elif original_value:
                    # Field existed (show in original)
                    original_fields[key] = original_value

            # Include ALL entries (even if no changes)
            diff.append({
                'key': entry_id,
                'type': enriched_entry.get('ENTRYTYPE', 'article'),
                'title': enriched_entry.get('title', 'Unknown'),
                'original_fields': original_fields,
                'added_fields': added_fields,
                'has_changes': len(added_fields) > 0,
            })

        # Calculate statistics
        total_entries = len(enriched_entries)
        entries_enhanced = sum(1 for entry in diff if entry['has_changes'])
        total_fields_added = sum(len(entry['added_fields']) for entry in diff)
        total_fields_modified = 0  # Not tracking modifications anymore

        return JsonResponse({
            'success': True,
            'diff': diff,
            'stats': {
                'total_entries': total_entries,
                'entries_enhanced': entries_enhanced,
                'total_fields_added': total_fields_added,
                'total_fields_modified': total_fields_modified,
                'enhancement_rate': round((entries_enhanced / total_entries * 100), 1) if total_entries > 0 else 0
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Failed to generate diff: {str(e)}'
        }, status=500)


# EOF
