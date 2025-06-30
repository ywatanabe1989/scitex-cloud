"""
Views for reference manager synchronization.
Handles OAuth authentication, sync operations, conflict resolution, and monitoring.
"""

import json
import logging
from datetime import timedelta
from typing import Dict, Any

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.core.paginator import Paginator

from .models import (
    ReferenceManagerAccount,
    SyncProfile,
    SyncSession,
    ReferenceMapping,
    ConflictResolution,
    SyncLog,
    SyncStatistics
)
from .services import MendeleyService, ZoteroService, SyncEngine
from .forms import SyncProfileForm, AccountConnectionForm, ConflictResolutionForm


logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard for reference sync overview."""
    template_name = 'reference_sync_app/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get accounts
        accounts = ReferenceManagerAccount.objects.filter(user=user)
        
        # Get sync profiles
        profiles = SyncProfile.objects.filter(user=user)
        
        # Get recent sync sessions
        recent_sessions = SyncSession.objects.filter(
            profile__user=user
        ).order_by('-started_at')[:5]
        
        # Get pending conflicts
        pending_conflicts = ConflictResolution.objects.filter(
            sync_session__profile__user=user,
            resolution__isnull=True
        ).count()
        
        # Get sync statistics for last 30 days
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        stats = SyncStatistics.objects.filter(
            user=user,
            date__gte=thirty_days_ago
        ).first()
        
        context.update({
            'accounts': accounts,
            'profiles': profiles,
            'recent_sessions': recent_sessions,
            'pending_conflicts': pending_conflicts,
            'stats': stats,
            'active_accounts': accounts.filter(is_active=True).count(),
            'total_mappings': ReferenceMapping.objects.filter(
                account__user=user
            ).count(),
        })
        
        return context


class AccountListView(LoginRequiredMixin, ListView):
    """List all reference manager accounts."""
    model = ReferenceManagerAccount
    template_name = 'reference_sync_app/accounts/list.html'
    context_object_name = 'accounts'
    paginate_by = 20
    
    def get_queryset(self):
        return ReferenceManagerAccount.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class AccountDetailView(LoginRequiredMixin, DetailView):
    """View details of a reference manager account."""
    model = ReferenceManagerAccount
    template_name = 'reference_sync_app/accounts/detail.html'
    context_object_name = 'account'
    
    def get_queryset(self):
        return ReferenceManagerAccount.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account = self.object
        
        # Get recent sync sessions for this account
        recent_sessions = SyncSession.objects.filter(
            profile__accounts=account
        ).order_by('-started_at')[:10]
        
        # Get mappings count
        mappings_count = ReferenceMapping.objects.filter(account=account).count()
        
        context.update({
            'recent_sessions': recent_sessions,
            'mappings_count': mappings_count,
        })
        
        return context


class ConnectAccountView(LoginRequiredMixin, TemplateView):
    """Initiate OAuth connection to a reference manager."""
    template_name = 'reference_sync_app/accounts/connect.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.kwargs.get('service')
        
        if service not in ['mendeley', 'zotero']:
            raise Http404("Invalid service")
        
        context['service'] = service
        context['service_name'] = service.title()
        return context
    
    def post(self, request, service):
        """Start OAuth flow."""
        if service not in ['mendeley', 'zotero']:
            return JsonResponse({'error': 'Invalid service'}, status=400)
        
        # Create temporary account to hold OAuth state
        account = ReferenceManagerAccount.objects.create(
            user=request.user,
            service=service,
            account_name=f"Connecting to {service.title()}...",
            status='inactive'
        )
        
        # Generate OAuth URL
        redirect_uri = request.build_absolute_uri(
            reverse('reference_sync:oauth_callback', kwargs={'service': service})
        )
        
        if service == 'mendeley':
            service_obj = MendeleyService(account)
        else:
            service_obj = ZoteroService(account)
        
        oauth_url = service_obj.get_oauth_url(
            redirect_uri=redirect_uri,
            state=str(account.id)
        )
        
        return JsonResponse({
            'oauth_url': oauth_url,
            'account_id': str(account.id)
        })


@csrf_exempt
@require_http_methods(["GET"])
def oauth_callback(request, service):
    """Handle OAuth callback from reference manager."""
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    
    if error:
        messages.error(request, f"OAuth error: {error}")
        return redirect('reference_sync:accounts')
    
    if not code:
        messages.error(request, "No authorization code received")
        return redirect('reference_sync:accounts')
    
    try:
        # Get account from state
        account = get_object_or_404(
            ReferenceManagerAccount,
            id=state,
            user=request.user,
            service=service
        )
        
        # Create service and exchange code for token
        if service == 'mendeley':
            service_obj = MendeleyService(account)
        else:
            service_obj = ZoteroService(account)
        
        redirect_uri = request.build_absolute_uri(
            reverse('reference_sync:oauth_callback', kwargs={'service': service})
        )
        
        token_data = service_obj.exchange_code_for_token(code, redirect_uri)
        
        # Get user info to update account
        user_info = service_obj.get_user_info()
        
        messages.success(
            request, 
            f"Successfully connected to {service.title()} account: {account.account_name}"
        )
        
        return redirect('reference_sync:account_detail', pk=account.id)
        
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        messages.error(request, f"Failed to connect account: {e}")
        return redirect('reference_sync:accounts')


class DisconnectAccountView(LoginRequiredMixin, View):
    """Disconnect a reference manager account."""
    
    def post(self, request, pk):
        account = get_object_or_404(
            ReferenceManagerAccount,
            pk=pk,
            user=request.user
        )
        
        # Deactivate account and clear tokens
        account.is_active = False
        account.status = 'inactive'
        account.access_token = ''
        account.refresh_token = ''
        account.save()
        
        messages.success(
            request,
            f"Disconnected from {account.service.title()} account: {account.account_name}"
        )
        
        return redirect('reference_sync:accounts')


class SyncProfileListView(LoginRequiredMixin, ListView):
    """List all sync profiles."""
    model = SyncProfile
    template_name = 'reference_sync_app/profiles/list.html'
    context_object_name = 'profiles'
    paginate_by = 20
    
    def get_queryset(self):
        return SyncProfile.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class SyncProfileDetailView(LoginRequiredMixin, DetailView):
    """View details of a sync profile."""
    model = SyncProfile
    template_name = 'reference_sync_app/profiles/detail.html'
    context_object_name = 'profile'
    
    def get_queryset(self):
        return SyncProfile.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        
        # Get recent sync sessions
        recent_sessions = SyncSession.objects.filter(
            profile=profile
        ).order_by('-started_at')[:10]
        
        # Get sync engine status
        sync_engine = SyncEngine(profile)
        sync_status = sync_engine.get_sync_status()
        
        context.update({
            'recent_sessions': recent_sessions,
            'sync_status': sync_status,
        })
        
        return context


class SyncProfileCreateView(LoginRequiredMixin, CreateView):
    """Create a new sync profile."""
    model = SyncProfile
    form_class = SyncProfileForm
    template_name = 'reference_sync_app/profiles/create.html'
    success_url = reverse_lazy('reference_sync:profiles')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        messages.success(
            self.request,
            f"Created sync profile: {form.instance.name}"
        )
        
        return response
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class SyncProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update a sync profile."""
    model = SyncProfile
    form_class = SyncProfileForm
    template_name = 'reference_sync_app/profiles/update.html'
    
    def get_queryset(self):
        return SyncProfile.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        return reverse('reference_sync:profile_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        messages.success(
            self.request,
            f"Updated sync profile: {form.instance.name}"
        )
        
        return response
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class SyncProfileDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a sync profile."""
    model = SyncProfile
    template_name = 'reference_sync_app/profiles/delete.html'
    success_url = reverse_lazy('reference_sync:profiles')
    
    def get_queryset(self):
        return SyncProfile.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        profile = self.get_object()
        profile_name = profile.name
        
        response = super().delete(request, *args, **kwargs)
        
        messages.success(
            request,
            f"Deleted sync profile: {profile_name}"
        )
        
        return response


class StartSyncView(LoginRequiredMixin, View):
    """Manually start synchronization for a profile."""
    
    def post(self, request, pk):
        profile = get_object_or_404(
            SyncProfile,
            pk=pk,
            user=request.user
        )
        
        if not profile.is_active:
            return JsonResponse({
                'error': 'Profile is not active'
            }, status=400)
        
        # Check if there's already a running sync
        running_sync = SyncSession.objects.filter(
            profile=profile,
            status='running'
        ).first()
        
        if running_sync:
            return JsonResponse({
                'error': 'Sync is already running',
                'session_id': str(running_sync.id)
            }, status=400)
        
        try:
            # Start sync
            sync_engine = SyncEngine(profile)
            session = sync_engine.start_sync(trigger='manual')
            
            return JsonResponse({
                'success': True,
                'session_id': str(session.id),
                'status': session.status
            })
            
        except Exception as e:
            logger.error(f"Failed to start sync: {e}")
            return JsonResponse({
                'error': f"Failed to start sync: {e}"
            }, status=500)


class SyncSessionDetailView(LoginRequiredMixin, DetailView):
    """View details of a sync session."""
    model = SyncSession
    template_name = 'reference_sync_app/sessions/detail.html'
    context_object_name = 'session'
    
    def get_queryset(self):
        return SyncSession.objects.filter(profile__user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        
        # Get sync logs
        logs = SyncLog.objects.filter(
            sync_session=session
        ).order_by('-created_at')[:100]
        
        # Get conflicts
        conflicts = ConflictResolution.objects.filter(
            sync_session=session
        ).order_by('-created_at')
        
        context.update({
            'logs': logs,
            'conflicts': conflicts,
        })
        
        return context


class SyncSessionListView(LoginRequiredMixin, ListView):
    """List sync sessions."""
    model = SyncSession
    template_name = 'reference_sync_app/sessions/list.html'
    context_object_name = 'sessions'
    paginate_by = 20
    
    def get_queryset(self):
        return SyncSession.objects.filter(
            profile__user=self.request.user
        ).order_by('-started_at')


class ConflictResolutionListView(LoginRequiredMixin, ListView):
    """List pending conflicts."""
    model = ConflictResolution
    template_name = 'reference_sync_app/conflicts/list.html'
    context_object_name = 'conflicts'
    paginate_by = 20
    
    def get_queryset(self):
        return ConflictResolution.objects.filter(
            sync_session__profile__user=self.request.user
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options
        status_filter = self.request.GET.get('status', 'pending')
        if status_filter == 'pending':
            context['conflicts'] = context['conflicts'].filter(resolution__isnull=True)
        elif status_filter == 'resolved':
            context['conflicts'] = context['conflicts'].filter(resolution__isnull=False)
        
        context['status_filter'] = status_filter
        return context


class ConflictResolutionDetailView(LoginRequiredMixin, DetailView):
    """View and resolve a specific conflict."""
    model = ConflictResolution
    template_name = 'reference_sync_app/conflicts/detail.html'
    context_object_name = 'conflict'
    
    def get_queryset(self):
        return ConflictResolution.objects.filter(
            sync_session__profile__user=self.request.user
        )
    
    def post(self, request, pk):
        """Resolve the conflict."""
        conflict = self.get_object()
        
        if conflict.is_resolved():
            return JsonResponse({'error': 'Conflict already resolved'}, status=400)
        
        resolution = request.POST.get('resolution')
        resolution_notes = request.POST.get('resolution_notes', '')
        
        if resolution not in ['local_wins', 'remote_wins', 'merged', 'manual', 'skipped']:
            return JsonResponse({'error': 'Invalid resolution'}, status=400)
        
        try:
            with transaction.atomic():
                # Update conflict
                conflict.resolution = resolution
                conflict.resolution_notes = resolution_notes
                conflict.resolved_at = timezone.now()
                conflict.resolved_by = request.user
                
                # Apply resolution to the actual data
                if resolution == 'local_wins':
                    conflict.resolved_value = conflict.local_value
                elif resolution == 'remote_wins':
                    conflict.resolved_value = conflict.remote_value
                elif resolution == 'manual':
                    # Get custom value from form
                    custom_value = request.POST.get('custom_value')
                    if custom_value:
                        try:
                            conflict.resolved_value = json.loads(custom_value)
                        except json.JSONDecodeError:
                            conflict.resolved_value = custom_value
                
                conflict.save()
                
                # Update session statistics
                session = conflict.sync_session
                session.conflicts_resolved += 1
                session.save()
                
                messages.success(request, 'Conflict resolved successfully')
                
                return JsonResponse({
                    'success': True,
                    'resolution': resolution
                })
                
        except Exception as e:
            logger.error(f"Failed to resolve conflict: {e}")
            return JsonResponse({'error': f'Failed to resolve conflict: {e}'}, status=500)


class BulkImportView(LoginRequiredMixin, TemplateView):
    """Bulk import references from file."""
    template_name = 'reference_sync_app/bulk/import.html'
    
    def post(self, request):
        """Handle bulk import."""
        uploaded_file = request.FILES.get('file')
        profile_id = request.POST.get('profile')
        
        if not uploaded_file:
            messages.error(request, 'No file uploaded')
            return redirect('reference_sync:bulk_import')
        
        if not profile_id:
            messages.error(request, 'No sync profile selected')
            return redirect('reference_sync:bulk_import')
        
        try:
            profile = SyncProfile.objects.get(
                id=profile_id,
                user=request.user
            )
        except SyncProfile.DoesNotExist:
            messages.error(request, 'Invalid sync profile')
            return redirect('reference_sync:bulk_import')
        
        # Process file based on extension
        file_extension = uploaded_file.name.lower().split('.')[-1]
        
        try:
            if file_extension == 'bib':
                imported_count = self._process_bibtex_file(uploaded_file, profile)
            elif file_extension == 'json':
                imported_count = self._process_json_file(uploaded_file, profile)
            elif file_extension in ['csv', 'tsv']:
                imported_count = self._process_csv_file(uploaded_file, profile)
            else:
                messages.error(request, f'Unsupported file format: {file_extension}')
                return redirect('reference_sync:bulk_import')
            
            messages.success(
                request,
                f'Successfully imported {imported_count} references'
            )
            
        except Exception as e:
            logger.error(f"Bulk import failed: {e}")
            messages.error(request, f'Import failed: {e}')
        
        return redirect('reference_sync:bulk_import')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profiles'] = SyncProfile.objects.filter(user=self.request.user)
        return context
    
    def _process_bibtex_file(self, uploaded_file, profile):
        """Process BibTeX file."""
        # This would need a BibTeX parser
        # For now, return mock count
        return 0
    
    def _process_json_file(self, uploaded_file, profile):
        """Process JSON file."""
        # Parse JSON and create references
        return 0
    
    def _process_csv_file(self, uploaded_file, profile):
        """Process CSV file."""
        # Parse CSV and create references
        return 0


class BulkExportView(LoginRequiredMixin, TemplateView):
    """Bulk export references to file."""
    template_name = 'reference_sync_app/bulk/export.html'
    
    def post(self, request):
        """Handle bulk export."""
        export_format = request.POST.get('format')
        profile_id = request.POST.get('profile')
        collection_filter = request.POST.get('collection', '')
        
        if not export_format or export_format not in ['bibtex', 'json', 'csv', 'ris']:
            messages.error(request, 'Invalid export format')
            return redirect('reference_sync:bulk_export')
        
        try:
            profile = SyncProfile.objects.get(
                id=profile_id,
                user=request.user
            ) if profile_id else None
        except SyncProfile.DoesNotExist:
            profile = None
        
        # Generate export file
        try:
            if export_format == 'bibtex':
                return self._export_bibtex(profile, collection_filter)
            elif export_format == 'json':
                return self._export_json(profile, collection_filter)
            elif export_format == 'csv':
                return self._export_csv(profile, collection_filter)
            elif export_format == 'ris':
                return self._export_ris(profile, collection_filter)
            
        except Exception as e:
            logger.error(f"Bulk export failed: {e}")
            messages.error(request, f'Export failed: {e}')
            return redirect('reference_sync:bulk_export')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profiles'] = SyncProfile.objects.filter(user=self.request.user)
        return context
    
    def _export_bibtex(self, profile, collection_filter):
        """Export as BibTeX."""
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='application/x-bibtex')
        response['Content-Disposition'] = 'attachment; filename="references.bib"'
        
        # Mock content for now
        response.write("% BibTeX export\n")
        
        return response
    
    def _export_json(self, profile, collection_filter):
        """Export as JSON."""
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="references.json"'
        
        # Mock content for now
        response.write('{"references": []}')
        
        return response
    
    def _export_csv(self, profile, collection_filter):
        """Export as CSV."""
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="references.csv"'
        
        # Mock content for now
        response.write('title,authors,year,journal\n')
        
        return response
    
    def _export_ris(self, profile, collection_filter):
        """Export as RIS."""
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='application/x-research-info-systems')
        response['Content-Disposition'] = 'attachment; filename="references.ris"'
        
        # Mock content for now
        response.write('TY  - JOUR\nER  - \n')
        
        return response


class SyncStatusAPIView(LoginRequiredMixin, View):
    """API endpoint for sync status updates."""
    
    def get(self, request, pk):
        """Get current sync status."""
        session = get_object_or_404(
            SyncSession,
            pk=pk,
            profile__user=request.user
        )
        
        return JsonResponse({
            'id': str(session.id),
            'status': session.status,
            'progress': session.progress_percentage(),
            'items_processed': session.items_processed,
            'total_items': session.total_items,
            'conflicts_found': session.conflicts_found,
            'errors_count': session.errors_count,
            'started_at': session.started_at.isoformat(),
            'completed_at': session.completed_at.isoformat() if session.completed_at else None,
        })


@method_decorator(login_required, name='dispatch')
class WebhookEndpointView(View):
    """Handle webhooks from reference managers."""
    
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, service):
        """Handle webhook from reference manager."""
        if service not in ['mendeley', 'zotero']:
            return JsonResponse({'error': 'Invalid service'}, status=400)
        
        # Verify webhook signature (implementation would depend on service)
        # For now, just log the webhook
        logger.info(f"Received webhook from {service}: {request.body}")
        
        # Trigger sync for relevant profiles
        try:
            profiles = SyncProfile.objects.filter(
                user=request.user,
                auto_sync=True,
                is_active=True,
                accounts__service=service
            )
            
            for profile in profiles:
                sync_engine = SyncEngine(profile)
                sync_engine.start_sync(trigger='webhook')
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return JsonResponse({'error': str(e)}, status=500)