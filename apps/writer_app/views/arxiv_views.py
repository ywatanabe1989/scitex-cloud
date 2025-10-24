"""
arXiv Submission Views for SciTeX Writer

This module provides views for handling arXiv submissions, including account setup,
manuscript submission workflow, status tracking, and submission management.
"""

import json
from datetime import datetime
from typing import Dict, Optional

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic import ListView, TemplateView

from ..services.arxiv import (
    ArxivAccountService, ArxivAPIException, ArxivCategoryService,
    ArxivIntegrationService, ArxivSubmissionService
)
from ..models import (
    ArxivAccount, ArxivCategory, ArxivSubmission, ArxivSubmissionHistory,
    ArxivValidationResult, Manuscript
)


class ArxivDashboardView(TemplateView):
    """Main dashboard for arXiv submissions."""
    template_name = 'writer_app/arxiv/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            integration_service = ArxivIntegrationService()
            context['user_status'] = integration_service.get_user_submission_status(self.request.user)
            context['recent_submissions'] = ArxivSubmission.objects.filter(
                user=self.request.user
            ).order_by('-created_at')[:5]
        
        return context


@login_required
def arxiv_account_setup(request: HttpRequest) -> HttpResponse:
    """Setup or manage arXiv account credentials."""
    try:
        arxiv_account = request.user.arxiv_account
    except ArxivAccount.DoesNotExist:
        arxiv_account = None
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get form data
                arxiv_username = request.POST.get('arxiv_username', '').strip()
                arxiv_password = request.POST.get('arxiv_password', '').strip()
                arxiv_email = request.POST.get('arxiv_email', '').strip()
                orcid_id = request.POST.get('orcid_id', '').strip()
                affiliation = request.POST.get('affiliation', '').strip()
                
                # Validate required fields
                if not all([arxiv_username, arxiv_password, arxiv_email]):
                    messages.error(request, 'All fields are required.')
                    return redirect('writer:arxiv-account-setup')
                
                # Create or update account
                if arxiv_account:
                    arxiv_account.arxiv_username = arxiv_username
                    arxiv_account.arxiv_password = arxiv_password  # Should be encrypted in production
                    arxiv_account.arxiv_email = arxiv_email
                    arxiv_account.orcid_id = orcid_id
                    arxiv_account.affiliation = affiliation
                    arxiv_account.is_verified = False  # Re-verify on update
                    arxiv_account.save()
                else:
                    arxiv_account = ArxivAccount.objects.create(
                        user=request.user,
                        arxiv_username=arxiv_username,
                        arxiv_password=arxiv_password,
                        arxiv_email=arxiv_email,
                        orcid_id=orcid_id,
                        affiliation=affiliation
                    )
                
                # Verify account
                account_service = ArxivAccountService()
                verification_success = account_service.verify_account(arxiv_account)
                
                if verification_success:
                    messages.success(request, 'arXiv account verified successfully!')
                else:
                    messages.warning(request, 'Account saved but verification failed. Please check your credentials.')
                
                return redirect('writer:arxiv-dashboard')
                
        except Exception as e:
            messages.error(request, f'Error setting up account: {str(e)}')
    
    context = {
        'arxiv_account': arxiv_account,
        'page_title': 'arXiv Account Setup'
    }
    
    return render(request, 'writer_app/arxiv/account_setup.html', context)


@login_required
def manuscript_submission_form(request: HttpRequest, manuscript_id: int) -> HttpResponse:
    """Form for submitting a manuscript to arXiv."""
    manuscript = get_object_or_404(Manuscript, id=manuscript_id)
    
    # Check permissions
    if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
        raise PermissionDenied("You don't have permission to submit this manuscript.")
    
    # Check for arXiv account
    try:
        arxiv_account = request.user.arxiv_account
        if not arxiv_account.is_verified:
            messages.error(request, 'Please set up and verify your arXiv account first.')
            return redirect('writer:arxiv-account-setup')
    except ArxivAccount.DoesNotExist:
        messages.error(request, 'Please set up your arXiv account first.')
        return redirect('writer:arxiv-account-setup')
    
    # Get categories
    category_service = ArxivCategoryService()
    categories = ArxivCategory.objects.filter(is_active=True).order_by('code')
    suggested_categories = category_service.suggest_categories(manuscript)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                submission_service = ArxivSubmissionService()
                
                # Prepare submission data
                submission_data = {
                    'title': request.POST.get('title', manuscript.title),
                    'abstract': request.POST.get('abstract', manuscript.abstract),
                    'authors': request.POST.get('authors', ''),
                    'primary_category_id': request.POST.get('primary_category'),
                    'secondary_categories': request.POST.getlist('secondary_categories'),
                    'comments': request.POST.get('comments', ''),
                    'journal_reference': request.POST.get('journal_reference', ''),
                    'doi': request.POST.get('doi', ''),
                }
                
                # Create submission
                submission = submission_service.create_submission(
                    manuscript, request.user, submission_data
                )
                
                messages.success(request, 'Submission created successfully!')
                return redirect('writer:arxiv-submission-detail', submission_id=submission.submission_id)
                
        except ArxivAPIException as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error creating submission: {str(e)}')
    
    context = {
        'manuscript': manuscript,
        'categories': categories,
        'suggested_categories': suggested_categories,
        'arxiv_account': arxiv_account,
        'page_title': f'Submit "{manuscript.title}" to arXiv'
    }
    
    return render(request, 'writer_app/arxiv/submission_form.html', context)


@login_required
def submission_detail(request: HttpRequest, submission_id: str) -> HttpResponse:
    """Detail view for an arXiv submission."""
    submission = get_object_or_404(ArxivSubmission, submission_id=submission_id)
    
    # Check permissions
    if submission.user != request.user:
        raise PermissionDenied("You don't have permission to view this submission.")
    
    # Get submission history
    history = submission.history.all()[:10]
    
    # Get validation results
    try:
        validation = submission.validation
    except ArxivValidationResult.DoesNotExist:
        validation = None
    
    context = {
        'submission': submission,
        'history': history,
        'validation': validation,
        'page_title': f'Submission: {submission.title[:50]}...'
    }
    
    return render(request, 'writer_app/arxiv/submission_detail.html', context)


@login_required
@require_POST
def validate_submission(request: HttpRequest, submission_id: str) -> JsonResponse:
    """Validate a submission for arXiv requirements."""
    submission = get_object_or_404(ArxivSubmission, submission_id=submission_id)
    
    # Check permissions
    if submission.user != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        submission_service = ArxivSubmissionService()
        validation_result = submission_service.validate_submission(submission)
        
        return JsonResponse({
            'success': True,
            'validation': validation_result.get_validation_summary(),
            'ready_for_submission': validation_result.is_ready_for_submission()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def prepare_submission_files(request: HttpRequest, submission_id: str) -> JsonResponse:
    """Prepare LaTeX and PDF files for submission."""
    submission = get_object_or_404(ArxivSubmission, submission_id=submission_id)
    
    # Check permissions
    if submission.user != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        submission_service = ArxivSubmissionService()
        latex_path, pdf_path = submission_service.prepare_submission_files(submission)
        
        return JsonResponse({
            'success': True,
            'message': 'Files prepared successfully',
            'latex_file': submission.latex_source.url if submission.latex_source else None,
            'pdf_file': submission.pdf_file.url if submission.pdf_file else None
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def submit_to_arxiv(request: HttpRequest, submission_id: str) -> JsonResponse:
    """Submit manuscript to arXiv."""
    submission = get_object_or_404(ArxivSubmission, submission_id=submission_id)
    
    # Check permissions
    if submission.user != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Check if submission is ready
    try:
        validation = submission.validation
        if not validation.is_ready_for_submission():
            return JsonResponse({
                'error': 'Submission failed validation. Please fix issues first.',
                'validation_errors': validation.error_messages
            }, status=400)
    except ArxivValidationResult.DoesNotExist:
        return JsonResponse({'error': 'Please validate submission first'}, status=400)
    
    try:
        submission_service = ArxivSubmissionService()
        success = submission_service.submit_to_arxiv(submission)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Submission sent to arXiv successfully!',
                'arxiv_id': submission.arxiv_id,
                'status': submission.status
            })
        else:
            return JsonResponse({'error': 'Submission failed'}, status=500)
            
    except ArxivAPIException as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def check_submission_status(request: HttpRequest, submission_id: str) -> JsonResponse:
    """Check submission status from arXiv."""
    submission = get_object_or_404(ArxivSubmission, submission_id=submission_id)
    
    # Check permissions
    if submission.user != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        submission_service = ArxivSubmissionService()
        status_info = submission_service.check_submission_status(submission)
        
        return JsonResponse({
            'success': True,
            'status_info': status_info
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def withdraw_submission(request: HttpRequest, submission_id: str) -> JsonResponse:
    """Withdraw a submission from arXiv."""
    submission = get_object_or_404(ArxivSubmission, submission_id=submission_id)
    
    # Check permissions
    if submission.user != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        reason = data.get('reason', 'Withdrawn by author')
        
        submission_service = ArxivSubmissionService()
        success = submission_service.withdraw_submission(submission, reason)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Submission withdrawn successfully'
            })
        else:
            return JsonResponse({'error': 'Withdrawal failed'}, status=500)
            
    except ArxivAPIException as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def create_replacement(request: HttpRequest, submission_id: str) -> HttpResponse:
    """Create a replacement submission for an existing arXiv paper."""
    original_submission = get_object_or_404(ArxivSubmission, submission_id=submission_id)
    
    # Check permissions
    if original_submission.user != request.user:
        raise PermissionDenied("You don't have permission to replace this submission.")
    
    if not original_submission.can_be_replaced():
        messages.error(request, 'This submission cannot be replaced.')
        return redirect('writer:arxiv-submission-detail', submission_id=submission_id)
    
    # Get user's manuscripts for replacement
    manuscripts = Manuscript.objects.filter(
        owner=request.user
    ).exclude(
        id=original_submission.manuscript.id
    ).order_by('-updated_at')
    
    if request.method == 'POST':
        try:
            manuscript_id = request.POST.get('manuscript_id')
            manuscript = get_object_or_404(Manuscript, id=manuscript_id, owner=request.user)
            
            replacement_data = {
                'title': request.POST.get('title', manuscript.title),
                'abstract': request.POST.get('abstract', manuscript.abstract),
                'authors': request.POST.get('authors', original_submission.authors),
                'comments': request.POST.get('comments', ''),
                'journal_reference': request.POST.get('journal_reference', ''),
                'doi': request.POST.get('doi', ''),
            }
            
            submission_service = ArxivSubmissionService()
            replacement = submission_service.replace_submission(
                original_submission, manuscript, replacement_data
            )
            
            messages.success(request, 'Replacement submission created successfully!')
            return redirect('writer:arxiv-submission-detail', submission_id=replacement.submission_id)
            
        except Exception as e:
            messages.error(request, f'Error creating replacement: {str(e)}')
    
    context = {
        'original_submission': original_submission,
        'manuscripts': manuscripts,
        'page_title': f'Replace Submission: {original_submission.arxiv_id}'
    }
    
    return render(request, 'writer_app/arxiv/create_replacement.html', context)


class SubmissionListView(ListView):
    """List view for user's arXiv submissions."""
    model = ArxivSubmission
    template_name = 'writer_app/arxiv/submission_list.html'
    context_object_name = 'submissions'
    paginate_by = 20
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ArxivSubmission.objects.none()
        
        return ArxivSubmission.objects.filter(
            user=self.request.user
        ).select_related(
            'manuscript', 'primary_category', 'arxiv_account'
        ).prefetch_related(
            'secondary_categories'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My arXiv Submissions'
        
        if self.request.user.is_authenticated:
            # Add submission statistics
            submissions = self.get_queryset()
            context['stats'] = {
                'total': submissions.count(),
                'draft': submissions.filter(status='draft').count(),
                'submitted': submissions.filter(status='submitted').count(),
                'published': submissions.filter(status='published').count(),
                'rejected': submissions.filter(status='rejected').count(),
            }
        
        return context


@login_required
def categories_api(request: HttpRequest) -> JsonResponse:
    """API endpoint for arXiv categories."""
    categories = ArxivCategory.objects.filter(is_active=True).order_by('code')
    
    # Group by field if requested
    group_by_field = request.GET.get('group_by_field', False)
    if group_by_field:
        grouped_categories = {}
        for category in categories:
            field = category.code.split('.')[0]
            if field not in grouped_categories:
                grouped_categories[field] = []
            grouped_categories[field].append({
                'id': category.id,
                'code': category.code,
                'name': category.name,
                'description': category.description
            })
        return JsonResponse({'categories': grouped_categories})
    
    # Return flat list
    categories_data = [
        {
            'id': category.id,
            'code': category.code,
            'name': category.name,
            'description': category.description
        }
        for category in categories
    ]
    
    return JsonResponse({'categories': categories_data})


@login_required
def suggest_categories_api(request: HttpRequest, manuscript_id: int) -> JsonResponse:
    """API endpoint for category suggestions."""
    manuscript = get_object_or_404(Manuscript, id=manuscript_id)
    
    # Check permissions
    if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        category_service = ArxivCategoryService()
        suggestions = category_service.suggest_categories(manuscript)
        
        suggestions_data = [
            {
                'id': category.id,
                'code': category.code,
                'name': category.name,
                'description': category.description
            }
            for category in suggestions
        ]
        
        return JsonResponse({'suggestions': suggestions_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def submission_history_api(request: HttpRequest, submission_id: str) -> JsonResponse:
    """API endpoint for submission history."""
    submission = get_object_or_404(ArxivSubmission, submission_id=submission_id)
    
    # Check permissions
    if submission.user != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    history_entries = submission.history.all()[:20]
    
    history_data = [
        {
            'id': entry.id,
            'previous_status': entry.previous_status,
            'new_status': entry.new_status,
            'change_reason': entry.change_reason,
            'changed_by': entry.changed_by.username if entry.changed_by else 'System',
            'is_automatic': entry.is_automatic,
            'created_at': entry.created_at.isoformat(),
            'error_details': entry.error_details
        }
        for entry in history_entries
    ]
    
    return JsonResponse({'history': history_data})


@require_http_methods(["GET"])
def arxiv_status_check(request: HttpRequest) -> JsonResponse:
    """Check arXiv service status and integration health."""
    try:
        # Basic health checks
        checks = {
            'categories_loaded': ArxivCategory.objects.count() > 0,
            'service_available': True,  # Would check actual arXiv API in production
            'database_connected': True,
        }
        
        overall_status = all(checks.values())
        
        return JsonResponse({
            'status': 'healthy' if overall_status else 'degraded',
            'checks': checks,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)


@login_required
@require_POST
def initialize_categories(request: HttpRequest) -> JsonResponse:
    """Initialize arXiv categories (admin function)."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        category_service = ArxivCategoryService()
        created_count = category_service.populate_categories()
        
        return JsonResponse({
            'success': True,
            'message': f'Initialized {created_count} categories',
            'created_count': created_count
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)