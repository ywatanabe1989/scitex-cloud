#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORCID Integration Views

This module provides views for ORCID OAuth2 authentication, profile management,
and publication synchronization.
"""

import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q

from .models import OrcidProfile, OrcidOAuth2Token, OrcidPublication, OrcidWork, OrcidSyncLog
from .services import (
    OrcidAuthService, OrcidAPIService, OrcidSyncService, 
    OrcidIntegrationService, OrcidAPIError, is_orcid_configured
)

User = get_user_model()


@login_required
def orcid_dashboard(request):
    """Main ORCID integration dashboard"""
    context = {
        'is_configured': is_orcid_configured(),
        'has_token': False,
        'has_profile': False,
        'orcid_profile': None,
        'publications_count': 0,
        'recent_publications': [],
        'sync_logs': [],
    }
    
    # Check if user has ORCID token
    try:
        token = OrcidOAuth2Token.objects.get(user=request.user)
        context['has_token'] = True
        context['token'] = token
        
        # Check if token is expired or expiring soon
        if token.is_expired():
            context['token_status'] = 'expired'
        elif token.is_expiring_soon():
            context['token_status'] = 'expiring'
        else:
            context['token_status'] = 'valid'
            
    except OrcidOAuth2Token.DoesNotExist:
        pass
    
    # Check if user has ORCID profile
    try:
        profile = OrcidProfile.objects.get(user=request.user)
        context['has_profile'] = True
        context['orcid_profile'] = profile
        context['publications_count'] = profile.get_publication_count()
        context['recent_publications'] = profile.get_recent_publications()
        
        # Get recent sync logs
        context['sync_logs'] = profile.sync_logs.order_by('-started_at')[:5]
        
    except OrcidProfile.DoesNotExist:
        pass
    
    return render(request, 'orcid_app/dashboard.html', context)


@login_required
def orcid_connect(request):
    """Initiate ORCID OAuth2 authentication"""
    if not is_orcid_configured():
        messages.error(request, 'ORCID integration is not configured.')
        return redirect('orcid_app:dashboard')
    
    # Generate state parameter for security
    state = str(uuid.uuid4())
    request.session['orcid_oauth_state'] = state
    
    # Generate authorization URL
    auth_url = OrcidAuthService.get_authorization_url(state=state)
    
    return redirect(auth_url)


@login_required
def orcid_callback(request):
    """Handle ORCID OAuth2 callback"""
    # Check for errors
    error = request.GET.get('error')
    if error:
        error_description = request.GET.get('error_description', 'Unknown error')
        messages.error(request, f'ORCID authentication failed: {error_description}')
        return redirect('orcid_app:dashboard')
    
    # Validate state parameter
    state = request.GET.get('state')
    session_state = request.session.get('orcid_oauth_state')
    
    if not state or state != session_state:
        messages.error(request, 'Invalid authentication state. Please try again.')
        return redirect('orcid_app:dashboard')
    
    # Get authorization code
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'No authorization code received from ORCID.')
        return redirect('orcid_app:dashboard')
    
    try:
        # Exchange code for token
        token_data = OrcidAuthService.exchange_code_for_token(code, state)
        
        # Store token
        token = OrcidAuthService.store_token(request.user, token_data)
        
        # Create or update ORCID profile
        profile, created = OrcidProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'orcid_id': token_data['orcid_id'],
            }
        )
        
        if not created:
            profile.orcid_id = token_data['orcid_id']
            profile.save()
        
        # Clean up session
        if 'orcid_oauth_state' in request.session:
            del request.session['orcid_oauth_state']
        
        messages.success(request, f'Successfully connected to ORCID ({token_data["orcid_id"]})')
        
        # Redirect to sync profile
        return redirect('orcid_app:sync_profile')
        
    except OrcidAPIError as e:
        messages.error(request, f'Failed to authenticate with ORCID: {str(e)}')
        return redirect('orcid_app:dashboard')


@login_required
def orcid_disconnect(request):
    """Disconnect ORCID account"""
    if request.method == 'POST':
        try:
            # Delete token
            OrcidOAuth2Token.objects.filter(user=request.user).delete()
            
            # Delete profile (optional - you might want to keep it)
            if request.POST.get('delete_profile') == 'true':
                OrcidProfile.objects.filter(user=request.user).delete()
                messages.success(request, 'ORCID account disconnected and profile data removed.')
            else:
                # Just mark as not synced
                try:
                    profile = OrcidProfile.objects.get(user=request.user)
                    profile.is_synced = False
                    profile.save()
                except OrcidProfile.DoesNotExist:
                    pass
                messages.success(request, 'ORCID account disconnected. Profile data preserved.')
            
        except Exception as e:
            messages.error(request, f'Error disconnecting ORCID: {str(e)}')
    
    return redirect('orcid_app:dashboard')


@login_required
def sync_profile(request):
    """Sync ORCID profile data"""
    try:
        sync_service = OrcidSyncService(request.user)
        success = sync_service.sync_profile()
        
        if success:
            messages.success(request, 'ORCID profile synchronized successfully.')
        else:
            messages.error(request, 'Failed to sync ORCID profile. Please check the sync logs.')
            
    except OrcidAPIError as e:
        messages.error(request, f'Error syncing profile: {str(e)}')
    except Exception as e:
        messages.error(request, f'Unexpected error: {str(e)}')
    
    return redirect('orcid_app:dashboard')


@login_required
def sync_publications(request):
    """Sync ORCID publications/works"""
    try:
        sync_service = OrcidSyncService(request.user)
        success = sync_service.sync_works()
        
        if success:
            messages.success(request, 'ORCID publications synchronized successfully.')
        else:
            messages.error(request, 'Failed to sync ORCID publications. Please check the sync logs.')
            
    except OrcidAPIError as e:
        messages.error(request, f'Error syncing publications: {str(e)}')
    except Exception as e:
        messages.error(request, f'Unexpected error: {str(e)}')
    
    return redirect('orcid_app:publications')


@login_required
def full_sync(request):
    """Perform full ORCID synchronization"""
    try:
        sync_service = OrcidSyncService(request.user)
        success = sync_service.full_sync()
        
        if success:
            messages.success(request, 'Full ORCID synchronization completed successfully.')
        else:
            messages.error(request, 'Full synchronization completed with errors. Please check the sync logs.')
            
    except OrcidAPIError as e:
        messages.error(request, f'Error during full sync: {str(e)}')
    except Exception as e:
        messages.error(request, f'Unexpected error: {str(e)}')
    
    return redirect('orcid_app:dashboard')


@login_required
def publications_list(request):
    """List ORCID publications"""
    try:
        profile = OrcidProfile.objects.get(user=request.user)
        publications = profile.orcid_publications.all()
        
        # Filter by publication type
        pub_type = request.GET.get('type')
        if pub_type:
            publications = publications.filter(publication_type=pub_type)
        
        # Search
        search_query = request.GET.get('search')
        if search_query:
            publications = publications.filter(
                Q(title__icontains=search_query) |
                Q(journal__icontains=search_query) |
                Q(authors__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(publications, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'profile': profile,
            'page_obj': page_obj,
            'publications': page_obj.object_list,
            'search_query': search_query,
            'selected_type': pub_type,
            'publication_types': OrcidPublication.PUBLICATION_TYPES,
        }
        
    except OrcidProfile.DoesNotExist:
        context = {
            'profile': None,
            'publications': [],
            'page_obj': None,
        }
    
    return render(request, 'orcid_app/publications_list.html', context)


@login_required
def publication_detail(request, publication_id):
    """View detailed information about an ORCID publication"""
    try:
        profile = OrcidProfile.objects.get(user=request.user)
        publication = get_object_or_404(
            OrcidPublication, 
            id=publication_id, 
            profile=profile
        )
        
        context = {
            'profile': profile,
            'publication': publication,
        }
        
    except OrcidProfile.DoesNotExist:
        messages.error(request, 'ORCID profile not found.')
        return redirect('orcid_app:dashboard')
    
    return render(request, 'orcid_app/publication_detail.html', context)


@login_required
def import_to_scholar(request, publication_id):
    """Import an ORCID publication to Scholar module"""
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST method allowed')
    
    try:
        profile = OrcidProfile.objects.get(user=request.user)
        publication = get_object_or_404(
            OrcidPublication, 
            id=publication_id, 
            profile=profile
        )
        
        if publication.is_imported:
            messages.info(request, 'Publication is already imported to Scholar.')
        else:
            scholar_paper = OrcidIntegrationService.import_publication_to_scholar(publication)
            
            if scholar_paper:
                messages.success(request, f'Successfully imported "{publication.title}" to Scholar.')
            else:
                messages.error(request, 'Failed to import publication to Scholar.')
        
    except OrcidProfile.DoesNotExist:
        messages.error(request, 'ORCID profile not found.')
    except Exception as e:
        messages.error(request, f'Error importing publication: {str(e)}')
    
    return redirect('orcid_app:publication_detail', publication_id=publication_id)


@login_required
def bulk_import_to_scholar(request):
    """Bulk import ORCID publications to Scholar"""
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST method allowed')
    
    try:
        publication_ids = request.POST.getlist('publication_ids')
        
        if not publication_ids:
            messages.error(request, 'No publications selected for import.')
        else:
            imported_count = OrcidIntegrationService.bulk_import_publications(
                request.user, 
                publication_ids
            )
            
            if imported_count > 0:
                messages.success(request, f'Successfully imported {imported_count} publications to Scholar.')
            else:
                messages.error(request, 'No publications were imported.')
        
    except Exception as e:
        messages.error(request, f'Error during bulk import: {str(e)}')
    
    return redirect('orcid_app:publications')


@login_required
def sync_logs(request):
    """View ORCID synchronization logs"""
    try:
        profile = OrcidProfile.objects.get(user=request.user)
        logs = profile.sync_logs.order_by('-started_at')
        
        # Filter by sync type
        sync_type = request.GET.get('type')
        if sync_type:
            logs = logs.filter(sync_type=sync_type)
        
        # Filter by status
        status = request.GET.get('status')
        if status:
            logs = logs.filter(status=status)
        
        # Pagination
        paginator = Paginator(logs, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'profile': profile,
            'page_obj': page_obj,
            'logs': page_obj.object_list,
            'selected_type': sync_type,
            'selected_status': status,
            'sync_types': OrcidSyncLog.SYNC_TYPES,
            'statuses': OrcidSyncLog.STATUS_CHOICES,
        }
        
    except OrcidProfile.DoesNotExist:
        context = {
            'profile': None,
            'logs': [],
            'page_obj': None,
        }
    
    return render(request, 'orcid_app/sync_logs.html', context)


@login_required
def profile_settings(request):
    """ORCID profile settings"""
    try:
        profile = OrcidProfile.objects.get(user=request.user)
        
        if request.method == 'POST':
            # Update sync settings
            profile.sync_publications = request.POST.get('sync_publications') == 'on'
            profile.auto_sync_enabled = request.POST.get('auto_sync_enabled') == 'on'
            profile.public_profile = request.POST.get('public_profile') == 'on'
            profile.show_publications = request.POST.get('show_publications') == 'on'
            profile.save()
            
            messages.success(request, 'Profile settings updated successfully.')
            return redirect('orcid_app:profile_settings')
        
        context = {
            'profile': profile,
        }
        
    except OrcidProfile.DoesNotExist:
        messages.error(request, 'ORCID profile not found.')
        return redirect('orcid_app:dashboard')
    
    return render(request, 'orcid_app/profile_settings.html', context)


# API Views
@login_required
@require_http_methods(["GET"])
def api_profile_status(request):
    """API endpoint to get ORCID profile status"""
    try:
        token = OrcidOAuth2Token.objects.get(user=request.user)
        profile = OrcidProfile.objects.get(user=request.user)
        
        return JsonResponse({
            'connected': True,
            'orcid_id': profile.orcid_id,
            'display_name': profile.get_display_name(),
            'is_synced': profile.is_synced,
            'last_sync_at': profile.last_sync_at.isoformat() if profile.last_sync_at else None,
            'needs_sync': profile.needs_sync(),
            'publications_count': profile.get_publication_count(),
            'token_status': 'expired' if token.is_expired() else 'valid',
        })
        
    except (OrcidOAuth2Token.DoesNotExist, OrcidProfile.DoesNotExist):
        return JsonResponse({
            'connected': False,
            'orcid_id': None,
            'display_name': None,
            'is_synced': False,
            'last_sync_at': None,
            'needs_sync': False,
            'publications_count': 0,
            'token_status': 'none',
        })


@login_required
@require_http_methods(["POST"])
def api_sync_profile(request):
    """API endpoint to sync ORCID profile"""
    try:
        sync_service = OrcidSyncService(request.user)
        success = sync_service.sync_profile()
        
        return JsonResponse({
            'success': success,
            'message': 'Profile synced successfully' if success else 'Profile sync failed'
        })
        
    except OrcidAPIError as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Unexpected error: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_sync_publications(request):
    """API endpoint to sync ORCID publications"""
    try:
        sync_service = OrcidSyncService(request.user)
        success = sync_service.sync_works()
        
        return JsonResponse({
            'success': success,
            'message': 'Publications synced successfully' if success else 'Publications sync failed'
        })
        
    except OrcidAPIError as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Unexpected error: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_publications_list(request):
    """API endpoint to get user's ORCID publications"""
    try:
        profile = OrcidProfile.objects.get(user=request.user)
        publications = profile.orcid_publications.all()
        
        # Filter by type if specified
        pub_type = request.GET.get('type')
        if pub_type:
            publications = publications.filter(publication_type=pub_type)
        
        # Search if specified
        search = request.GET.get('search')
        if search:
            publications = publications.filter(
                Q(title__icontains=search) |
                Q(journal__icontains=search)
            )
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        paginator = Paginator(publications, page_size)
        page_obj = paginator.get_page(page)
        
        publications_data = []
        for pub in page_obj.object_list:
            publications_data.append({
                'id': str(pub.id),
                'title': pub.title,
                'publication_type': pub.publication_type,
                'publication_year': pub.publication_year,
                'journal': pub.journal,
                'doi': pub.doi,
                'authors': pub.get_authors_display(),
                'is_imported': pub.is_imported,
                'scholar_paper_id': str(pub.scholar_paper.id) if pub.scholar_paper else None,
            })
        
        return JsonResponse({
            'publications': publications_data,
            'pagination': {
                'page': page_obj.number,
                'pages': paginator.num_pages,
                'total': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
        
    except OrcidProfile.DoesNotExist:
        return JsonResponse({
            'publications': [],
            'pagination': {
                'page': 1,
                'pages': 0,
                'total': 0,
                'has_next': False,
                'has_previous': False,
            }
        })


@login_required
@require_http_methods(["GET"])
def api_sync_logs(request):
    """API endpoint to get sync logs"""
    try:
        profile = OrcidProfile.objects.get(user=request.user)
        logs = profile.sync_logs.order_by('-started_at')
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        paginator = Paginator(logs, page_size)
        page_obj = paginator.get_page(page)
        
        logs_data = []
        for log in page_obj.object_list:
            logs_data.append({
                'id': str(log.id),
                'sync_type': log.sync_type,
                'status': log.status,
                'started_at': log.started_at.isoformat(),
                'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                'duration_seconds': log.duration_seconds,
                'items_processed': log.items_processed,
                'items_created': log.items_created,
                'items_updated': log.items_updated,
                'items_skipped': log.items_skipped,
                'error_message': log.error_message,
            })
        
        return JsonResponse({
            'logs': logs_data,
            'pagination': {
                'page': page_obj.number,
                'pages': paginator.num_pages,
                'total': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
        
    except OrcidProfile.DoesNotExist:
        return JsonResponse({
            'logs': [],
            'pagination': {
                'page': 1,
                'pages': 0,
                'total': 0,
                'has_next': False,
                'has_previous': False,
            }
        })