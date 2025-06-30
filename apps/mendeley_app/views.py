#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mendeley Integration Views

This module provides views for Mendeley/Zotero OAuth2 authentication, profile management,
and document synchronization.
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

from .models import MendeleyProfile, MendeleyOAuth2Token, MendeleyDocument, MendeleyGroup, MendeleySyncLog
from .services import (
    MendeleyAuthService, MendeleyAPIService, MendeleySyncService, 
    MendeleyIntegrationService, MendeleyAPIError, is_mendeley_configured,
    USE_ZOTERO_FALLBACK
)

User = get_user_model()


@login_required
def mendeley_dashboard(request):
    """Main Mendeley integration dashboard"""
    context = {
        'is_configured': is_mendeley_configured(),
        'has_token': False,
        'has_profile': False,
        'mendeley_profile': None,
        'documents_count': 0,
        'recent_documents': [],
        'sync_logs': [],
        'use_zotero_fallback': USE_ZOTERO_FALLBACK,
        'platform_name': 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley',
    }
    
    # Check if user has Mendeley token
    try:
        token = MendeleyOAuth2Token.objects.get(user=request.user)
        context['has_token'] = True
        context['token'] = token
        
        # Check if token is expired or expiring soon
        if token.is_expired():
            context['token_status'] = 'expired'
        elif token.is_expiring_soon():
            context['token_status'] = 'expiring'
        else:
            context['token_status'] = 'valid'
            
    except MendeleyOAuth2Token.DoesNotExist:
        pass
    
    # Check if user has Mendeley profile
    try:
        profile = MendeleyProfile.objects.get(user=request.user)
        context['has_profile'] = True
        context['mendeley_profile'] = profile
        context['documents_count'] = profile.get_document_count()
        context['recent_documents'] = profile.get_recent_documents()
        
        # Get recent sync logs
        context['sync_logs'] = profile.sync_logs.order_by('-started_at')[:5]
        
    except MendeleyProfile.DoesNotExist:
        pass
    
    return render(request, 'mendeley_app/dashboard.html', context)


@login_required
def mendeley_connect(request):
    """Initiate Mendeley/Zotero authentication"""
    if not is_mendeley_configured():
        platform_name = 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley'
        messages.error(request, f'{platform_name} integration is not configured.')
        return redirect('mendeley_app:dashboard')
    
    if USE_ZOTERO_FALLBACK:
        # For Zotero, redirect to API key setup page
        messages.info(request, 'Please create a Zotero API key and paste it below.')
        return redirect('mendeley_app:zotero_api_key_setup')
    
    # Generate state parameter for security
    state = str(uuid.uuid4())
    request.session['mendeley_oauth_state'] = state
    
    # Generate authorization URL
    auth_url = MendeleyAuthService.get_authorization_url(state=state)
    
    return redirect(auth_url)


@login_required
def zotero_api_key_setup(request):
    """Setup Zotero API key (alternative to OAuth2)"""
    if request.method == 'POST':
        api_key = request.POST.get('api_key', '').strip()
        
        if not api_key:
            messages.error(request, 'Please provide a valid Zotero API key.')
            return render(request, 'mendeley_app/zotero_api_key_setup.html')
        
        try:
            # Store the API key as a token
            token_data = MendeleyAuthService.exchange_code_for_token(api_key)
            token = MendeleyAuthService.store_token(request.user, token_data)
            
            # Create or update profile with Zotero user ID
            profile, created = MendeleyProfile.objects.get_or_create(
                user=request.user,
                defaults={
                    'mendeley_id': str(request.user.id),  # Use Django user ID as Zotero ID
                }
            )
            
            messages.success(request, 'Successfully connected to Zotero!')
            return redirect('mendeley_app:sync_profile')
            
        except Exception as e:
            messages.error(request, f'Failed to setup Zotero API key: {str(e)}')
    
    context = {
        'zotero_api_url': 'https://www.zotero.org/settings/keys/new',
    }
    return render(request, 'mendeley_app/zotero_api_key_setup.html', context)


@login_required
def mendeley_callback(request):
    """Handle Mendeley OAuth2 callback"""
    # Check for errors
    error = request.GET.get('error')
    if error:
        error_description = request.GET.get('error_description', 'Unknown error')
        messages.error(request, f'Mendeley authentication failed: {error_description}')
        return redirect('mendeley_app:dashboard')
    
    # Validate state parameter
    state = request.GET.get('state')
    session_state = request.session.get('mendeley_oauth_state')
    
    if not state or state != session_state:
        messages.error(request, 'Invalid authentication state. Please try again.')
        return redirect('mendeley_app:dashboard')
    
    # Get authorization code
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'No authorization code received from Mendeley.')
        return redirect('mendeley_app:dashboard')
    
    try:
        # Exchange code for token
        token_data = MendeleyAuthService.exchange_code_for_token(code, state)
        
        # Store token
        token = MendeleyAuthService.store_token(request.user, token_data)
        
        # Create or update Mendeley profile
        profile, created = MendeleyProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'mendeley_id': str(request.user.id),  # Will be updated during profile sync
            }
        )
        
        # Clean up session
        if 'mendeley_oauth_state' in request.session:
            del request.session['mendeley_oauth_state']
        
        platform_name = 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley'
        messages.success(request, f'Successfully connected to {platform_name}!')
        
        # Redirect to sync profile
        return redirect('mendeley_app:sync_profile')
        
    except MendeleyAPIError as e:
        platform_name = 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley'
        messages.error(request, f'Failed to authenticate with {platform_name}: {str(e)}')
        return redirect('mendeley_app:dashboard')


@login_required
def mendeley_disconnect(request):
    """Disconnect Mendeley/Zotero account"""
    if request.method == 'POST':
        try:
            # Delete token
            MendeleyOAuth2Token.objects.filter(user=request.user).delete()
            
            # Delete profile (optional - you might want to keep it)
            if request.POST.get('delete_profile') == 'true':
                MendeleyProfile.objects.filter(user=request.user).delete()
                platform_name = 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley'
                messages.success(request, f'{platform_name} account disconnected and profile data removed.')
            else:
                # Just mark as not synced
                try:
                    profile = MendeleyProfile.objects.get(user=request.user)
                    profile.is_synced = False
                    profile.save()
                except MendeleyProfile.DoesNotExist:
                    pass
                platform_name = 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley'
                messages.success(request, f'{platform_name} account disconnected. Profile data preserved.')
            
        except Exception as e:
            platform_name = 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley'
            messages.error(request, f'Error disconnecting {platform_name}: {str(e)}')
    
    return redirect('mendeley_app:dashboard')


@login_required
def sync_profile(request):
    """Sync Mendeley/Zotero profile data"""
    try:
        sync_service = MendeleySyncService(request.user)
        success = sync_service.sync_profile()
        
        platform_name = 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley'
        if success:
            messages.success(request, f'{platform_name} profile synchronized successfully.')
        else:
            messages.error(request, f'Failed to sync {platform_name} profile. Please check the sync logs.')
            
    except MendeleyAPIError as e:
        messages.error(request, f'Error syncing profile: {str(e)}')
    except Exception as e:
        messages.error(request, f'Unexpected error: {str(e)}')
    
    return redirect('mendeley_app:dashboard')


@login_required
def sync_documents(request):
    """Sync Mendeley/Zotero documents"""
    try:
        sync_service = MendeleySyncService(request.user)
        success = sync_service.sync_documents()
        
        platform_name = 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley'
        if success:
            messages.success(request, f'{platform_name} documents synchronized successfully.')
        else:
            messages.error(request, f'Failed to sync {platform_name} documents. Please check the sync logs.')
            
    except MendeleyAPIError as e:
        messages.error(request, f'Error syncing documents: {str(e)}')
    except Exception as e:
        messages.error(request, f'Unexpected error: {str(e)}')
    
    return redirect('mendeley_app:documents')


@login_required
def full_sync(request):
    """Perform full Mendeley/Zotero synchronization"""
    try:
        sync_service = MendeleySyncService(request.user)
        success = sync_service.full_sync()
        
        platform_name = 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley'
        if success:
            messages.success(request, f'Full {platform_name} synchronization completed successfully.')
        else:
            messages.error(request, f'Full synchronization completed with errors. Please check the sync logs.')
            
    except MendeleyAPIError as e:
        messages.error(request, f'Error during full sync: {str(e)}')
    except Exception as e:
        messages.error(request, f'Unexpected error: {str(e)}')
    
    return redirect('mendeley_app:dashboard')


@login_required
def documents_list(request):
    """List Mendeley/Zotero documents"""
    try:
        profile = MendeleyProfile.objects.get(user=request.user)
        documents = profile.mendeley_documents.all()
        
        # Filter by document type
        doc_type = request.GET.get('type')
        if doc_type:
            documents = documents.filter(document_type=doc_type)
        
        # Search
        search_query = request.GET.get('search')
        if search_query:
            documents = documents.filter(
                Q(title__icontains=search_query) |
                Q(source__icontains=search_query) |
                Q(authors__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(documents, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'profile': profile,
            'page_obj': page_obj,
            'documents': page_obj.object_list,
            'search_query': search_query,
            'selected_type': doc_type,
            'document_types': MendeleyDocument.DOCUMENT_TYPES,
            'platform_name': 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley',
        }
        
    except MendeleyProfile.DoesNotExist:
        context = {
            'profile': None,
            'documents': [],
            'page_obj': None,
            'platform_name': 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley',
        }
    
    return render(request, 'mendeley_app/documents_list.html', context)


@login_required
def document_detail(request, document_id):
    """View detailed information about a Mendeley/Zotero document"""
    try:
        profile = MendeleyProfile.objects.get(user=request.user)
        document = get_object_or_404(
            MendeleyDocument, 
            id=document_id, 
            profile=profile
        )
        
        context = {
            'profile': profile,
            'document': document,
            'platform_name': 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley',
        }
        
    except MendeleyProfile.DoesNotExist:
        messages.error(request, 'Mendeley profile not found.')
        return redirect('mendeley_app:dashboard')
    
    return render(request, 'mendeley_app/document_detail.html', context)


@login_required
def import_to_scholar(request, document_id):
    """Import a Mendeley/Zotero document to Scholar module"""
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST method allowed')
    
    try:
        profile = MendeleyProfile.objects.get(user=request.user)
        document = get_object_or_404(
            MendeleyDocument, 
            id=document_id, 
            profile=profile
        )
        
        if document.is_imported:
            messages.info(request, 'Document is already imported to Scholar.')
        else:
            scholar_paper = MendeleyIntegrationService.import_document_to_scholar(document)
            
            if scholar_paper:
                messages.success(request, f'Successfully imported "{document.title}" to Scholar.')
            else:
                messages.error(request, 'Failed to import document to Scholar.')
        
    except MendeleyProfile.DoesNotExist:
        messages.error(request, 'Mendeley profile not found.')
    except Exception as e:
        messages.error(request, f'Error importing document: {str(e)}')
    
    return redirect('mendeley_app:document_detail', document_id=document_id)


@login_required
def bulk_import_to_scholar(request):
    """Bulk import Mendeley/Zotero documents to Scholar"""
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST method allowed')
    
    try:
        document_ids = request.POST.getlist('document_ids')
        
        if not document_ids:
            messages.error(request, 'No documents selected for import.')
        else:
            imported_count = MendeleyIntegrationService.bulk_import_documents(
                request.user, 
                document_ids
            )
            
            if imported_count > 0:
                messages.success(request, f'Successfully imported {imported_count} documents to Scholar.')
            else:
                messages.error(request, 'No documents were imported.')
        
    except Exception as e:
        messages.error(request, f'Error during bulk import: {str(e)}')
    
    return redirect('mendeley_app:documents')


@login_required
def sync_logs(request):
    """View Mendeley/Zotero synchronization logs"""
    try:
        profile = MendeleyProfile.objects.get(user=request.user)
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
            'sync_types': MendeleySyncLog.SYNC_TYPES,
            'statuses': MendeleySyncLog.STATUS_CHOICES,
            'platform_name': 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley',
        }
        
    except MendeleyProfile.DoesNotExist:
        context = {
            'profile': None,
            'logs': [],
            'page_obj': None,
            'platform_name': 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley',
        }
    
    return render(request, 'mendeley_app/sync_logs.html', context)


@login_required
def profile_settings(request):
    """Mendeley/Zotero profile settings"""
    try:
        profile = MendeleyProfile.objects.get(user=request.user)
        
        if request.method == 'POST':
            # Update sync settings
            profile.sync_documents = request.POST.get('sync_documents') == 'on'
            profile.auto_sync_enabled = request.POST.get('auto_sync_enabled') == 'on'
            profile.public_profile = request.POST.get('public_profile') == 'on'
            profile.show_documents = request.POST.get('show_documents') == 'on'
            profile.save()
            
            messages.success(request, 'Profile settings updated successfully.')
            return redirect('mendeley_app:profile_settings')
        
        context = {
            'profile': profile,
            'platform_name': 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley',
        }
        
    except MendeleyProfile.DoesNotExist:
        messages.error(request, 'Mendeley profile not found.')
        return redirect('mendeley_app:dashboard')
    
    return render(request, 'mendeley_app/profile_settings.html', context)


# API Views
@login_required
@require_http_methods(["GET"])
def api_profile_status(request):
    """API endpoint to get Mendeley/Zotero profile status"""
    try:
        token = MendeleyOAuth2Token.objects.get(user=request.user)
        profile = MendeleyProfile.objects.get(user=request.user)
        
        return JsonResponse({
            'connected': True,
            'mendeley_id': profile.mendeley_id,
            'display_name': profile.get_display_name(),
            'is_synced': profile.is_synced,
            'last_sync_at': profile.last_sync_at.isoformat() if profile.last_sync_at else None,
            'needs_sync': profile.needs_sync(),
            'documents_count': profile.get_document_count(),
            'token_status': 'expired' if token.is_expired() else 'valid',
            'platform_name': 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley',
        })
        
    except (MendeleyOAuth2Token.DoesNotExist, MendeleyProfile.DoesNotExist):
        return JsonResponse({
            'connected': False,
            'mendeley_id': None,
            'display_name': None,
            'is_synced': False,
            'last_sync_at': None,
            'needs_sync': False,
            'documents_count': 0,
            'token_status': 'none',
            'platform_name': 'Zotero' if USE_ZOTERO_FALLBACK else 'Mendeley',
        })


@login_required
@require_http_methods(["POST"])
def api_sync_profile(request):
    """API endpoint to sync Mendeley/Zotero profile"""
    try:
        sync_service = MendeleySyncService(request.user)
        success = sync_service.sync_profile()
        
        return JsonResponse({
            'success': success,
            'message': 'Profile synced successfully' if success else 'Profile sync failed'
        })
        
    except MendeleyAPIError as e:
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
def api_sync_documents(request):
    """API endpoint to sync Mendeley/Zotero documents"""
    try:
        sync_service = MendeleySyncService(request.user)
        success = sync_service.sync_documents()
        
        return JsonResponse({
            'success': success,
            'message': 'Documents synced successfully' if success else 'Documents sync failed'
        })
        
    except MendeleyAPIError as e:
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
def api_documents_list(request):
    """API endpoint to get user's Mendeley/Zotero documents"""
    try:
        profile = MendeleyProfile.objects.get(user=request.user)
        documents = profile.mendeley_documents.all()
        
        # Filter by type if specified
        doc_type = request.GET.get('type')
        if doc_type:
            documents = documents.filter(document_type=doc_type)
        
        # Search if specified
        search = request.GET.get('search')
        if search:
            documents = documents.filter(
                Q(title__icontains=search) |
                Q(source__icontains=search)
            )
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        paginator = Paginator(documents, page_size)
        page_obj = paginator.get_page(page)
        
        documents_data = []
        for doc in page_obj.object_list:
            documents_data.append({
                'id': str(doc.id),
                'title': doc.title,
                'document_type': doc.document_type,
                'year': doc.year,
                'source': doc.source,
                'doi': doc.doi,
                'authors': doc.get_authors_display(),
                'is_imported': doc.is_imported,
                'scholar_paper_id': str(doc.scholar_paper.id) if doc.scholar_paper else None,
            })
        
        return JsonResponse({
            'documents': documents_data,
            'pagination': {
                'page': page_obj.number,
                'pages': paginator.num_pages,
                'total': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
        
    except MendeleyProfile.DoesNotExist:
        return JsonResponse({
            'documents': [],
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
        profile = MendeleyProfile.objects.get(user=request.user)
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
        
    except MendeleyProfile.DoesNotExist:
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