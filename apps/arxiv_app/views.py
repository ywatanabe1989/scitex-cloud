#!/usr/bin/env python3
"""
Views for arXiv submission and integration system.
"""

import json
import logging
from typing import Dict, Any
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone

from .models import (
    ArxivSubmission, ArxivCategory, ArxivSubmissionFile, 
    ArxivSubmissionLog, ArxivApiCredentials, ArxivTemplate,
    ArxivPaperMapping
)
from .services import ArxivAPIService, ArxivSubmissionService, ArxivIntegrationService

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """Main arXiv dashboard showing user's submissions."""
    user_submissions = ArxivSubmission.objects.filter(user=request.user).order_by('-created_at')
    
    # Get statistics
    stats = {
        'total_submissions': user_submissions.count(),
        'published': user_submissions.filter(status='published').count(),
        'submitted': user_submissions.filter(status='submitted').count(),
        'drafts': user_submissions.filter(status='draft').count(),
        'errors': user_submissions.filter(status='error').count(),
    }
    
    # Recent submissions
    recent_submissions = user_submissions[:5]
    
    # Check if user has arXiv credentials
    has_credentials = hasattr(request.user, 'arxiv_credentials')
    
    context = {
        'submissions': recent_submissions,
        'stats': stats,
        'has_credentials': has_credentials,
        'page_title': 'arXiv Integration Dashboard'
    }
    
    return render(request, 'arxiv_app/dashboard.html', context)


@login_required
def submission_list(request):
    """List all user submissions with filtering and pagination."""
    submissions = ArxivSubmission.objects.filter(user=request.user).order_by('-created_at')
    
    # Filtering
    status_filter = request.GET.get('status')
    if status_filter:
        submissions = submissions.filter(status=status_filter)
    
    category_filter = request.GET.get('category')
    if category_filter:
        submissions = submissions.filter(primary_category__code=category_filter)
    
    search_query = request.GET.get('q')
    if search_query:
        submissions = submissions.filter(
            Q(title__icontains=search_query) |
            Q(abstract__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(submissions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get available categories for filter
    categories = ArxivCategory.objects.filter(is_active=True).order_by('code')
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_status': status_filter,
        'current_category': category_filter,
        'search_query': search_query,
        'status_choices': ArxivSubmission.STATUS_CHOICES,
        'page_title': 'My arXiv Submissions'
    }
    
    return render(request, 'arxiv_app/submission_list.html', context)


@login_required
def submission_detail(request, submission_id):
    """View submission details."""
    submission = get_object_or_404(ArxivSubmission, id=submission_id, user=request.user)
    
    # Get submission files
    files = submission.files.all().order_by('file_type', 'filename')
    
    # Get submission logs
    logs = submission.logs.all().order_by('-created_at')[:20]
    
    # Get related Writer project if exists
    writer_project = submission.writer_project
    
    context = {
        'submission': submission,
        'files': files,
        'logs': logs,
        'writer_project': writer_project,
        'page_title': f'Submission: {submission.title[:50]}'
    }
    
    return render(request, 'arxiv_app/submission_detail.html', context)


@login_required
def create_submission(request):
    """Create new arXiv submission."""
    if request.method == 'POST':
        try:
            data = request.POST
            
            # Create submission
            submission = ArxivSubmission.objects.create(
                user=request.user,
                title=data.get('title'),
                abstract=data.get('abstract'),
                primary_category=get_object_or_404(ArxivCategory, code=data.get('primary_category')),
                comments=data.get('comments', ''),
                journal_ref=data.get('journal_ref', ''),
                doi=data.get('doi', '')
            )
            
            # Add secondary categories
            secondary_cats = data.getlist('secondary_categories')
            if secondary_cats:
                submission.secondary_categories.set(ArxivCategory.objects.filter(code__in=secondary_cats))
            
            # Add authors
            authors_data = json.loads(data.get('authors', '[]'))
            submission.authors = authors_data
            submission.save()
            
            messages.success(request, 'Submission created successfully!')
            return redirect('arxiv_app:submission_detail', submission_id=submission.id)
            
        except Exception as e:
            logger.error(f"Error creating submission: {e}")
            messages.error(request, f'Error creating submission: {str(e)}')
    
    # Get categories for form
    categories = ArxivCategory.objects.filter(is_active=True).order_by('code')
    templates = ArxivTemplate.objects.filter(is_public=True).order_by('-usage_count')
    
    # Get user's Writer projects
    writer_projects = []
    try:
        from apps.writer_app.models import WriterProject
        writer_projects = WriterProject.objects.filter(user=request.user).order_by('-updated_at')
    except ImportError:
        pass
    
    context = {
        'categories': categories,
        'templates': templates,
        'writer_projects': writer_projects,
        'page_title': 'Create arXiv Submission'
    }
    
    return render(request, 'arxiv_app/create_submission.html', context)


@login_required
def edit_submission(request, submission_id):
    """Edit existing submission."""
    submission = get_object_or_404(ArxivSubmission, id=submission_id, user=request.user)
    
    if submission.status not in ['draft', 'error']:
        messages.error(request, 'Cannot edit submission in current status.')
        return redirect('arxiv_app:submission_detail', submission_id=submission.id)
    
    if request.method == 'POST':
        try:
            data = request.POST
            
            # Update submission
            submission.title = data.get('title')
            submission.abstract = data.get('abstract')
            submission.primary_category = get_object_or_404(ArxivCategory, code=data.get('primary_category'))
            submission.comments = data.get('comments', '')
            submission.journal_ref = data.get('journal_ref', '')
            submission.doi = data.get('doi', '')
            
            # Update authors
            authors_data = json.loads(data.get('authors', '[]'))
            submission.authors = authors_data
            
            submission.save()
            
            # Update secondary categories
            secondary_cats = data.getlist('secondary_categories')
            submission.secondary_categories.set(ArxivCategory.objects.filter(code__in=secondary_cats))
            
            messages.success(request, 'Submission updated successfully!')
            return redirect('arxiv_app:submission_detail', submission_id=submission.id)
            
        except Exception as e:
            logger.error(f"Error updating submission: {e}")
            messages.error(request, f'Error updating submission: {str(e)}')
    
    # Get categories for form
    categories = ArxivCategory.objects.filter(is_active=True).order_by('code')
    
    context = {
        'submission': submission,
        'categories': categories,
        'page_title': f'Edit: {submission.title[:50]}'
    }
    
    return render(request, 'arxiv_app/edit_submission.html', context)


@login_required
@require_http_methods(["POST"])
def prepare_submission(request, submission_id):
    """Prepare submission for arXiv."""
    submission = get_object_or_404(ArxivSubmission, id=submission_id, user=request.user)
    
    if submission.status != 'draft':
        return JsonResponse({'status': 'error', 'message': 'Submission is not in draft status'})
    
    try:
        service = ArxivSubmissionService()
        success = service.prepare_submission(submission)
        
        if success:
            return JsonResponse({
                'status': 'success',
                'message': 'Submission prepared successfully',
                'submission_status': submission.status,
                'validation_status': submission.validation_status
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Submission preparation failed',
                'validation_log': submission.validation_log
            })
    
    except Exception as e:
        logger.error(f"Error preparing submission: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_http_methods(["POST"])
def submit_to_arxiv(request, submission_id):
    """Submit to arXiv."""
    submission = get_object_or_404(ArxivSubmission, id=submission_id, user=request.user)
    
    if not submission.can_submit():
        return JsonResponse({'status': 'error', 'message': 'Submission is not ready for arXiv'})
    
    try:
        service = ArxivSubmissionService()
        success = service.submit_to_arxiv(submission)
        
        if success:
            return JsonResponse({
                'status': 'success',
                'message': f'Successfully submitted to arXiv: {submission.arxiv_id}',
                'arxiv_id': submission.arxiv_id,
                'arxiv_url': submission.get_arxiv_url()
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Submission to arXiv failed',
                'error': submission.last_error
            })
    
    except Exception as e:
        logger.error(f"Error submitting to arXiv: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
def search_arxiv(request):
    """Search arXiv papers."""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    page = int(request.GET.get('page', 1))
    
    results = {'papers': [], 'total_results': 0}
    
    if query:
        try:
            service = ArxivAPIService()
            start = (page - 1) * 20
            results = service.search_papers(
                query=query,
                category=category,
                max_results=20,
                start=start
            )
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
            messages.error(request, f'Search error: {str(e)}')
    
    # Get categories for filter
    categories = ArxivCategory.objects.filter(is_active=True).order_by('code')
    
    # Pagination info
    total_pages = (results['total_results'] + 19) // 20
    has_next = page < total_pages
    has_previous = page > 1
    
    context = {
        'query': query,
        'category': category,
        'results': results,
        'categories': categories,
        'current_page': page,
        'total_pages': total_pages,
        'has_next': has_next,
        'has_previous': has_previous,
        'page_title': 'Search arXiv'
    }
    
    return render(request, 'arxiv_app/search.html', context)


@login_required
def paper_detail(request, arxiv_id):
    """View details of an arXiv paper."""
    try:
        service = ArxivAPIService()
        paper = service.get_paper_by_id(arxiv_id)
        
        if not paper:
            messages.error(request, 'Paper not found on arXiv')
            return redirect('arxiv_app:search')
        
        # Check if paper is mapped to Scholar
        mapping = ArxivPaperMapping.objects.filter(arxiv_id=arxiv_id).first()
        
        # Check if user has a submission for this paper
        user_submission = ArxivSubmission.objects.filter(
            user=request.user,
            arxiv_id=arxiv_id
        ).first()
        
        context = {
            'paper': paper,
            'mapping': mapping,
            'user_submission': user_submission,
            'page_title': f'arXiv:{arxiv_id}'
        }
        
        return render(request, 'arxiv_app/paper_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error fetching paper {arxiv_id}: {e}")
        messages.error(request, f'Error fetching paper: {str(e)}')
        return redirect('arxiv_app:search')


@login_required
def credentials_setup(request):
    """Setup arXiv API credentials."""
    try:
        credentials = request.user.arxiv_credentials
    except ArxivApiCredentials.DoesNotExist:
        credentials = None
    
    if request.method == 'POST':
        try:
            data = request.POST
            
            if credentials:
                credentials.arxiv_username = data.get('username', '')
                credentials.arxiv_password = data.get('password', '')  # Should be encrypted
                credentials.default_category = get_object_or_404(ArxivCategory, code=data.get('default_category')) if data.get('default_category') else None
                credentials.auto_submit = data.get('auto_submit') == 'on'
                credentials.save()
            else:
                credentials = ArxivApiCredentials.objects.create(
                    user=request.user,
                    arxiv_username=data.get('username', ''),
                    arxiv_password=data.get('password', ''),
                    default_category=get_object_or_404(ArxivCategory, code=data.get('default_category')) if data.get('default_category') else None,
                    auto_submit=data.get('auto_submit') == 'on'
                )
            
            messages.success(request, 'Credentials saved successfully!')
            return redirect('arxiv_app:dashboard')
            
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            messages.error(request, f'Error saving credentials: {str(e)}')
    
    categories = ArxivCategory.objects.filter(is_active=True).order_by('code')
    
    context = {
        'credentials': credentials,
        'categories': categories,
        'page_title': 'arXiv Credentials'
    }
    
    return render(request, 'arxiv_app/credentials_setup.html', context)


@login_required
def integration_settings(request):
    """Manage integration settings with other SciTeX modules."""
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            
            if action == 'sync_scholar':
                service = ArxivIntegrationService()
                stats = service.sync_with_scholar(request.user)
                messages.success(request, f'Scholar sync completed: {stats["imported"]} imported, {stats["updated"]} updated')
            
            elif action == 'enhance_scholar':
                service = ArxivIntegrationService()
                count = service.enhance_scholar_papers(request.user)
                messages.success(request, f'Enhanced {count} Scholar papers with arXiv data')
            
        except Exception as e:
            logger.error(f"Error in integration action: {e}")
            messages.error(request, f'Integration error: {str(e)}')
    
    # Get integration statistics
    try:
        from apps.scholar_app.models import SearchIndex
        scholar_papers_count = SearchIndex.objects.count()
        arxiv_mapped_count = ArxivPaperMapping.objects.count()
    except ImportError:
        scholar_papers_count = 0
        arxiv_mapped_count = 0
    
    user_submissions = ArxivSubmission.objects.filter(user=request.user).count()
    
    context = {
        'scholar_papers_count': scholar_papers_count,
        'arxiv_mapped_count': arxiv_mapped_count,
        'user_submissions': user_submissions,
        'page_title': 'Integration Settings'
    }
    
    return render(request, 'arxiv_app/integration_settings.html', context)


# API Views

@login_required
@require_http_methods(["GET"])
def api_submission_status(request, submission_id):
    """Get submission status via API."""
    try:
        submission = get_object_or_404(ArxivSubmission, id=submission_id, user=request.user)
        
        return JsonResponse({
            'status': 'success',
            'submission': {
                'id': str(submission.id),
                'title': submission.title,
                'status': submission.status,
                'validation_status': submission.validation_status,
                'arxiv_id': submission.arxiv_id,
                'created_at': submission.created_at.isoformat(),
                'updated_at': submission.updated_at.isoformat(),
                'submitted_at': submission.submitted_at.isoformat() if submission.submitted_at else None,
                'published_at': submission.published_at.isoformat() if submission.published_at else None,
            }
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_http_methods(["GET"])
def api_search(request):
    """Search arXiv via API."""
    try:
        query = request.GET.get('q', '')
        category = request.GET.get('category', '')
        max_results = min(int(request.GET.get('max_results', 10)), 50)
        start = int(request.GET.get('start', 0))
        
        if not query:
            return JsonResponse({'status': 'error', 'message': 'Query parameter required'})
        
        service = ArxivAPIService()
        results = service.search_papers(
            query=query,
            category=category,
            max_results=max_results,
            start=start
        )
        
        return JsonResponse({
            'status': 'success',
            **results
        })
        
    except Exception as e:
        logger.error(f"API search error: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_http_methods(["GET"])
def api_categories(request):
    """Get arXiv categories via API."""
    try:
        categories = ArxivCategory.objects.filter(is_active=True).values(
            'code', 'name', 'description', 'parent_category'
        )
        
        return JsonResponse({
            'status': 'success',
            'categories': list(categories)
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_http_methods(["POST"])
def api_check_status(request, submission_id):
    """Check submission status on arXiv via API."""
    try:
        submission = get_object_or_404(ArxivSubmission, id=submission_id, user=request.user)
        
        service = ArxivSubmissionService()
        success = service.check_submission_status(submission)
        
        if success:
            return JsonResponse({
                'status': 'success',
                'message': 'Status updated from arXiv',
                'submission_status': submission.status,
                'published_at': submission.published_at.isoformat() if submission.published_at else None
            })
        else:
            return JsonResponse({
                'status': 'warning',
                'message': 'Could not check status on arXiv'
            })
        
    except Exception as e:
        logger.error(f"Error checking submission status: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})