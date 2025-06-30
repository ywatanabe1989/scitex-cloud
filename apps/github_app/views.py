#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Integration Views

This module provides views for GitHub OAuth2 authentication, repository management,
code synchronization, and collaboration features.
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

from .models import GitHubProfile, GitHubOAuth2Token, GitHubRepository, GitHubConnection, GitHubSyncLog, GitHubCollaborator
from .services import (
    GitHubAuthService, GitHubAPIService, GitHubSyncService, 
    GitHubCodeSyncService, GitHubAPIError, is_github_configured
)

User = get_user_model()


@login_required
def github_dashboard(request):
    """Main GitHub integration dashboard"""
    context = {
        'is_configured': is_github_configured(),
        'has_token': False,
        'has_profile': False,
        'github_profile': None,
        'repositories_count': 0,
        'recent_repositories': [],
        'sync_logs': [],
    }
    
    # Check if user has GitHub token
    try:
        token = GitHubOAuth2Token.objects.get(user=request.user)
        context['has_token'] = True
        context['token'] = token
        
        # Check if token is too old
        if token.is_expired():
            context['token_status'] = 'old'
        else:
            context['token_status'] = 'valid'
            
    except GitHubOAuth2Token.DoesNotExist:
        pass
    
    # Check if user has GitHub profile
    try:
        profile = GitHubProfile.objects.get(user=request.user)
        context['has_profile'] = True
        context['github_profile'] = profile
        context['repositories_count'] = profile.get_repository_count()
        context['recent_repositories'] = profile.get_recent_repositories()
        
        # Get recent sync logs
        context['sync_logs'] = profile.sync_logs.order_by('-started_at')[:5]
        
    except GitHubProfile.DoesNotExist:
        pass
    
    return render(request, 'github_app/dashboard.html', context)


@login_required
def github_connect(request):
    """Initiate GitHub OAuth2 authentication"""
    if not is_github_configured():
        messages.error(request, 'GitHub integration is not configured.')
        return redirect('github_app:dashboard')
    
    # Generate state parameter for security
    state = str(uuid.uuid4())
    request.session['github_oauth_state'] = state
    
    # Generate authorization URL
    auth_url = GitHubAuthService.get_authorization_url(state=state)
    
    return redirect(auth_url)


@login_required
def github_callback(request):
    """Handle GitHub OAuth2 callback"""
    # Check for errors
    error = request.GET.get('error')
    if error:
        error_description = request.GET.get('error_description', 'Unknown error')
        messages.error(request, f'GitHub authentication failed: {error_description}')
        return redirect('github_app:dashboard')
    
    # Validate state parameter
    state = request.GET.get('state')
    session_state = request.session.get('github_oauth_state')
    
    if not state or state != session_state:
        messages.error(request, 'Invalid authentication state. Please try again.')
        return redirect('github_app:dashboard')
    
    # Get authorization code
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'No authorization code received from GitHub.')
        return redirect('github_app:dashboard')
    
    try:
        # Exchange code for token
        token_data = GitHubAuthService.exchange_code_for_token(code, state)
        
        # Get GitHub user information
        api_service = GitHubAPIService(access_token=token_data['access_token'])
        github_user_data = api_service.get_user()
        
        # Store token
        token = GitHubAuthService.store_token(request.user, token_data, github_user_data)
        
        # Create or update GitHub profile
        profile, created = GitHubProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'github_id': github_user_data['id'],
                'github_username': github_user_data['login'],
                'name': github_user_data.get('name', '') or '',
                'email': github_user_data.get('email', '') or '',
            }
        )
        
        if not created:
            profile.github_id = github_user_data['id']
            profile.github_username = github_user_data['login']
            profile.save()
        
        # Clean up session
        if 'github_oauth_state' in request.session:
            del request.session['github_oauth_state']
        
        messages.success(request, f'Successfully connected to GitHub ({github_user_data["login"]})')
        
        # Redirect to sync profile
        return redirect('github_app:sync_profile')
        
    except GitHubAPIError as e:
        messages.error(request, f'Failed to authenticate with GitHub: {str(e)}')
        return redirect('github_app:dashboard')


@login_required
def github_disconnect(request):
    """Disconnect GitHub account"""
    if request.method == 'POST':
        try:
            # Delete token
            GitHubOAuth2Token.objects.filter(user=request.user).delete()
            
            # Delete profile (optional - you might want to keep it)
            if request.POST.get('delete_profile') == 'true':
                GitHubProfile.objects.filter(user=request.user).delete()
                messages.success(request, 'GitHub account disconnected and profile data removed.')
            else:
                # Just mark as not synced
                try:
                    profile = GitHubProfile.objects.get(user=request.user)
                    profile.is_synced = False
                    profile.save()
                except GitHubProfile.DoesNotExist:
                    pass
                messages.success(request, 'GitHub account disconnected. Profile data preserved.')
            
        except Exception as e:
            messages.error(request, f'Error disconnecting GitHub: {str(e)}')
    
    return redirect('github_app:dashboard')


@login_required
def sync_profile(request):
    """Sync GitHub profile data"""
    try:
        sync_service = GitHubSyncService(request.user)
        success = sync_service.sync_profile()
        
        if success:
            messages.success(request, 'GitHub profile synchronized successfully.')
        else:
            messages.error(request, 'Failed to sync GitHub profile. Please check the sync logs.')
            
    except GitHubAPIError as e:
        messages.error(request, f'Error syncing profile: {str(e)}')
    except Exception as e:
        messages.error(request, f'Unexpected error: {str(e)}')
    
    return redirect('github_app:dashboard')


@login_required
def sync_repositories(request):
    """Sync GitHub repositories"""
    try:
        sync_service = GitHubSyncService(request.user)
        success = sync_service.sync_repositories()
        
        if success:
            messages.success(request, 'GitHub repositories synchronized successfully.')
        else:
            messages.error(request, 'Failed to sync GitHub repositories. Please check the sync logs.')
            
    except GitHubAPIError as e:
        messages.error(request, f'Error syncing repositories: {str(e)}')
    except Exception as e:
        messages.error(request, f'Unexpected error: {str(e)}')
    
    return redirect('github_app:repositories')


@login_required
def full_sync(request):
    """Perform full GitHub synchronization"""
    try:
        sync_service = GitHubSyncService(request.user)
        success = sync_service.full_sync()
        
        if success:
            messages.success(request, 'Full GitHub synchronization completed successfully.')
        else:
            messages.error(request, 'Full synchronization completed with errors. Please check the sync logs.')
            
    except GitHubAPIError as e:
        messages.error(request, f'Error during full sync: {str(e)}')
    except Exception as e:
        messages.error(request, f'Unexpected error: {str(e)}')
    
    return redirect('github_app:dashboard')


@login_required
def repositories_list(request):
    """List GitHub repositories"""
    try:
        profile = GitHubProfile.objects.get(user=request.user)
        repositories = profile.github_repositories.all()
        
        # Filter by visibility
        visibility = request.GET.get('visibility')
        if visibility == 'public':
            repositories = repositories.filter(is_private=False)
        elif visibility == 'private':
            repositories = repositories.filter(is_private=True)
        
        # Filter by language
        language = request.GET.get('language')
        if language:
            repositories = repositories.filter(language=language)
        
        # Search
        search_query = request.GET.get('search')
        if search_query:
            repositories = repositories.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(topics__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(repositories, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get unique languages for filter
        languages = profile.github_repositories.exclude(language='').values_list('language', flat=True).distinct()
        
        context = {
            'profile': profile,
            'page_obj': page_obj,
            'repositories': page_obj.object_list,
            'search_query': search_query,
            'selected_visibility': visibility,
            'selected_language': language,
            'languages': sorted(languages),
        }
        
    except GitHubProfile.DoesNotExist:
        context = {
            'profile': None,
            'repositories': [],
            'page_obj': None,
        }
    
    return render(request, 'github_app/repositories_list.html', context)


@login_required
def repository_detail(request, repository_id):
    """View detailed information about a GitHub repository"""
    try:
        profile = GitHubProfile.objects.get(user=request.user)
        repository = get_object_or_404(
            GitHubRepository, 
            id=repository_id, 
            profile=profile
        )
        
        # Get connection if exists
        connection = None
        try:
            connection = GitHubConnection.objects.get(repository=repository)
        except GitHubConnection.DoesNotExist:
            pass
        
        # Get recent sync logs for this repository
        sync_logs = repository.sync_logs.order_by('-started_at')[:10]
        
        # Get collaborators
        collaborators = repository.collaborators.all()
        
        context = {
            'profile': profile,
            'repository': repository,
            'connection': connection,
            'sync_logs': sync_logs,
            'collaborators': collaborators,
        }
        
    except GitHubProfile.DoesNotExist:
        messages.error(request, 'GitHub profile not found.')
        return redirect('github_app:dashboard')
    
    return render(request, 'github_app/repository_detail.html', context)


@login_required
def connect_to_code(request, repository_id):
    """Connect a GitHub repository to Code module"""
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST method allowed')
    
    try:
        profile = GitHubProfile.objects.get(user=request.user)
        repository = get_object_or_404(
            GitHubRepository, 
            id=repository_id, 
            profile=profile
        )
        
        if repository.is_connected:
            messages.info(request, 'Repository is already connected to Code module.')
        else:
            # Create connection
            connection = GitHubConnection.objects.create(
                repository=repository,
                sync_direction=request.POST.get('sync_direction', 'bidirectional'),
                auto_sync_enabled=request.POST.get('auto_sync', 'true') == 'true',
            )
            
            repository.is_connected = True
            repository.save()
            
            messages.success(request, f'Successfully connected "{repository.name}" to Code module.')
        
    except GitHubProfile.DoesNotExist:
        messages.error(request, 'GitHub profile not found.')
    except Exception as e:
        messages.error(request, f'Error connecting repository: {str(e)}')
    
    return redirect('github_app:repository_detail', repository_id=repository_id)


@login_required
def sync_repository_code(request, repository_id):
    """Sync repository code with Code module"""
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST method allowed')
    
    try:
        profile = GitHubProfile.objects.get(user=request.user)
        repository = get_object_or_404(
            GitHubRepository, 
            id=repository_id, 
            profile=profile
        )
        
        if not repository.is_connected:
            messages.error(request, 'Repository must be connected to Code module first.')
        else:
            connection = GitHubConnection.objects.get(repository=repository)
            sync_service = GitHubCodeSyncService(connection)
            success = sync_service.sync_repository_to_code()
            
            if success:
                messages.success(request, f'Successfully synced code from "{repository.name}".')
            else:
                messages.error(request, 'Failed to sync repository code. Please check the sync logs.')
        
    except GitHubProfile.DoesNotExist:
        messages.error(request, 'GitHub profile not found.')
    except GitHubConnection.DoesNotExist:
        messages.error(request, 'Repository connection not found.')
    except Exception as e:
        messages.error(request, f'Error syncing repository code: {str(e)}')
    
    return redirect('github_app:repository_detail', repository_id=repository_id)


@login_required
def sync_repository_collaborators(request, repository_id):
    """Sync repository collaborators"""
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST method allowed')
    
    try:
        profile = GitHubProfile.objects.get(user=request.user)
        repository = get_object_or_404(
            GitHubRepository, 
            id=repository_id, 
            profile=profile
        )
        
        sync_service = GitHubSyncService(request.user)
        success = sync_service.sync_repository_collaborators(repository)
        
        if success:
            messages.success(request, f'Successfully synced collaborators for "{repository.name}".')
        else:
            messages.error(request, 'Failed to sync repository collaborators.')
        
    except GitHubProfile.DoesNotExist:
        messages.error(request, 'GitHub profile not found.')
    except Exception as e:
        messages.error(request, f'Error syncing collaborators: {str(e)}')
    
    return redirect('github_app:repository_detail', repository_id=repository_id)


@login_required
def sync_logs(request):
    """View GitHub synchronization logs"""
    try:
        profile = GitHubProfile.objects.get(user=request.user)
        logs = profile.sync_logs.order_by('-started_at')
        
        # Filter by sync type
        sync_type = request.GET.get('type')
        if sync_type:
            logs = logs.filter(sync_type=sync_type)
        
        # Filter by status
        status = request.GET.get('status')
        if status:
            logs = logs.filter(status=status)
        
        # Filter by repository
        repository_id = request.GET.get('repository')
        if repository_id:
            logs = logs.filter(repository_id=repository_id)
        
        # Pagination
        paginator = Paginator(logs, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get repositories for filter
        repositories = profile.github_repositories.all()
        
        context = {
            'profile': profile,
            'page_obj': page_obj,
            'logs': page_obj.object_list,
            'selected_type': sync_type,
            'selected_status': status,
            'selected_repository': repository_id,
            'sync_types': GitHubSyncLog.SYNC_TYPES,
            'statuses': GitHubSyncLog.STATUS_CHOICES,
            'repositories': repositories,
        }
        
    except GitHubProfile.DoesNotExist:
        context = {
            'profile': None,
            'logs': [],
            'page_obj': None,
        }
    
    return render(request, 'github_app/sync_logs.html', context)


@login_required
def profile_settings(request):
    """GitHub profile settings"""
    try:
        profile = GitHubProfile.objects.get(user=request.user)
        
        if request.method == 'POST':
            # Update sync settings
            profile.sync_repositories = request.POST.get('sync_repositories') == 'on'
            profile.auto_sync_enabled = request.POST.get('auto_sync_enabled') == 'on'
            profile.public_profile = request.POST.get('public_profile') == 'on'
            profile.show_repositories = request.POST.get('show_repositories') == 'on'
            profile.save()
            
            messages.success(request, 'Profile settings updated successfully.')
            return redirect('github_app:profile_settings')
        
        context = {
            'profile': profile,
        }
        
    except GitHubProfile.DoesNotExist:
        messages.error(request, 'GitHub profile not found.')
        return redirect('github_app:dashboard')
    
    return render(request, 'github_app/profile_settings.html', context)


# API Views
@login_required
@require_http_methods(["GET"])
def api_profile_status(request):
    """API endpoint to get GitHub profile status"""
    try:
        token = GitHubOAuth2Token.objects.get(user=request.user)
        profile = GitHubProfile.objects.get(user=request.user)
        
        return JsonResponse({
            'connected': True,
            'github_username': profile.github_username,
            'display_name': profile.get_display_name(),
            'is_synced': profile.is_synced,
            'last_sync_at': profile.last_sync_at.isoformat() if profile.last_sync_at else None,
            'needs_sync': profile.needs_sync(),
            'repositories_count': profile.get_repository_count(),
            'token_status': 'old' if token.is_expired() else 'valid',
            'github_url': profile.get_github_url(),
        })
        
    except (GitHubOAuth2Token.DoesNotExist, GitHubProfile.DoesNotExist):
        return JsonResponse({
            'connected': False,
            'github_username': None,
            'display_name': None,
            'is_synced': False,
            'last_sync_at': None,
            'needs_sync': False,
            'repositories_count': 0,
            'token_status': 'none',
            'github_url': None,
        })


@login_required
@require_http_methods(["POST"])
def api_sync_profile(request):
    """API endpoint to sync GitHub profile"""
    try:
        sync_service = GitHubSyncService(request.user)
        success = sync_service.sync_profile()
        
        return JsonResponse({
            'success': success,
            'message': 'Profile synced successfully' if success else 'Profile sync failed'
        })
        
    except GitHubAPIError as e:
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
def api_sync_repositories(request):
    """API endpoint to sync GitHub repositories"""
    try:
        sync_service = GitHubSyncService(request.user)
        success = sync_service.sync_repositories()
        
        return JsonResponse({
            'success': success,
            'message': 'Repositories synced successfully' if success else 'Repositories sync failed'
        })
        
    except GitHubAPIError as e:
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
def api_repositories_list(request):
    """API endpoint to get user's GitHub repositories"""
    try:
        profile = GitHubProfile.objects.get(user=request.user)
        repositories = profile.github_repositories.all()
        
        # Filter by visibility if specified
        visibility = request.GET.get('visibility')
        if visibility == 'public':
            repositories = repositories.filter(is_private=False)
        elif visibility == 'private':
            repositories = repositories.filter(is_private=True)
        
        # Search if specified
        search = request.GET.get('search')
        if search:
            repositories = repositories.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        paginator = Paginator(repositories, page_size)
        page_obj = paginator.get_page(page)
        
        repositories_data = []
        for repo in page_obj.object_list:
            repositories_data.append({
                'id': str(repo.id),
                'name': repo.name,
                'full_name': repo.full_name,
                'description': repo.description,
                'is_private': repo.is_private,
                'is_fork': repo.is_fork,
                'language': repo.language,
                'stargazers_count': repo.stargazers_count,
                'forks_count': repo.forks_count,
                'is_connected': repo.is_connected,
                'github_url': repo.get_github_url(),
                'updated_at': repo.github_updated_at.isoformat() if repo.github_updated_at else None,
            })
        
        return JsonResponse({
            'repositories': repositories_data,
            'pagination': {
                'page': page_obj.number,
                'pages': paginator.num_pages,
                'total': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
        
    except GitHubProfile.DoesNotExist:
        return JsonResponse({
            'repositories': [],
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
        profile = GitHubProfile.objects.get(user=request.user)
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
                'repository_name': log.repository.name if log.repository else None,
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
        
    except GitHubProfile.DoesNotExist:
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


# Webhook endpoint (for GitHub webhooks)
@csrf_exempt
@require_http_methods(["POST"])
def github_webhook(request):
    """Handle GitHub webhook events"""
    try:
        import hmac
        import hashlib
        
        # Verify webhook signature if secret is configured
        signature = request.headers.get('X-Hub-Signature-256')
        if signature and hasattr(settings, 'GITHUB_WEBHOOK_SECRET'):
            secret = settings.GITHUB_WEBHOOK_SECRET.encode('utf-8')
            expected_signature = 'sha256=' + hmac.new(
                secret, 
                request.body, 
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return JsonResponse({'error': 'Invalid signature'}, status=403)
        
        # Parse webhook payload
        event_type = request.headers.get('X-GitHub-Event')
        payload = json.loads(request.body)
        
        # Handle different event types
        if event_type == 'push':
            # Handle push events
            repository_data = payload.get('repository', {})
            full_name = repository_data.get('full_name')
            
            if full_name:
                try:
                    repo = GitHubRepository.objects.get(full_name=full_name)
                    connection = GitHubConnection.objects.get(repository=repo)
                    
                    if connection.auto_sync_enabled:
                        # Trigger sync
                        sync_service = GitHubCodeSyncService(connection)
                        sync_service.sync_repository_to_code()
                        
                except (GitHubRepository.DoesNotExist, GitHubConnection.DoesNotExist):
                    pass
        
        elif event_type == 'pull_request':
            # Handle pull request events
            # Implement as needed
            pass
        
        return JsonResponse({'status': 'ok'})
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JsonResponse({'error': 'Internal error'}, status=500)