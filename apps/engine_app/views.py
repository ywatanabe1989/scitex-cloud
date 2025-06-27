from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import models
from .models import (
    EngineConfiguration, EngineSession, EngineRequest, 
    EngineSnippet, EngineWorkflow, EngineIntegration
)
import json


def index(request):
    """Engine app index view."""
    context = {
        'features': [
            {
                'icon': 'fa-keyboard',
                'title': 'Seamless Emacs Integration',
                'description': 'Access Claude AI directly from Emacs with keybindings and commands.'
            },
            {
                'icon': 'fa-code',
                'title': 'Context-Aware Code Assistance',
                'description': 'Get intelligent code suggestions that understand your project.'
            },
            {
                'icon': 'fa-flask',
                'title': 'Scientific Writing Support',
                'description': 'Enhanced org-mode support for research notes and manuscripts.'
            },
        ]
    }
    return render(request, 'engine_app/index.html', context)


def features(request):
    """Engine features view."""
    return render(request, 'engine_app/features.html')


def pricing(request):
    """Engine pricing view."""
    return render(request, 'engine_app/pricing.html')


@login_required
def dashboard(request):
    """Engine dashboard for authenticated users."""
    # Get user's configurations
    configs = EngineConfiguration.objects.filter(user=request.user)
    
    # Get recent sessions
    recent_sessions = EngineSession.objects.filter(
        user=request.user
    ).select_related('configuration')[:5]
    
    # Get usage statistics
    total_requests = EngineRequest.objects.filter(
        session__user=request.user
    ).count()
    
    total_tokens = EngineSession.objects.filter(
        user=request.user
    ).aggregate(total=models.Sum('tokens_used'))['total'] or 0
    
    context = {
        'configurations': configs,
        'recent_sessions': recent_sessions,
        'total_requests': total_requests,
        'total_tokens': total_tokens,
    }
    
    return render(request, 'engine_app/dashboard.html', context)


@login_required
def configuration(request, config_id=None):
    """Manage Engine configurations."""
    if config_id:
        config = get_object_or_404(EngineConfiguration, id=config_id, user=request.user)
    else:
        config = None
    
    if request.method == 'POST':
        # Handle configuration updates
        data = request.POST
        
        if config:
            # Update existing
            config.name = data.get('name', config.name)
            config.model_version = data.get('model_version', config.model_version)
            config.max_tokens = int(data.get('max_tokens', config.max_tokens))
            config.temperature = float(data.get('temperature', config.temperature))
            
            # Update feature flags
            config.enable_code_completion = data.get('enable_code_completion') == 'on'
            config.enable_org_mode_assistance = data.get('enable_org_mode_assistance') == 'on'
            config.enable_latex_support = data.get('enable_latex_support') == 'on'
            config.enable_shell_integration = data.get('enable_shell_integration') == 'on'
            config.enable_project_awareness = data.get('enable_project_awareness') == 'on'
            
            config.save()
            messages.success(request, 'Configuration updated successfully.')
        else:
            # Create new
            config = EngineConfiguration.objects.create(
                user=request.user,
                name=data.get('name', 'New Configuration'),
                model_version=data.get('model_version', 'claude-3-opus-20240229'),
                max_tokens=int(data.get('max_tokens', 4000)),
                temperature=float(data.get('temperature', 0.7)),
                enable_code_completion=data.get('enable_code_completion') == 'on',
                enable_org_mode_assistance=data.get('enable_org_mode_assistance') == 'on',
                enable_latex_support=data.get('enable_latex_support') == 'on',
                enable_shell_integration=data.get('enable_shell_integration') == 'on',
                enable_project_awareness=data.get('enable_project_awareness') == 'on',
            )
            messages.success(request, 'Configuration created successfully.')
        
        return redirect('engine_app:configuration', config_id=config.id)
    
    context = {
        'config': config,
        'model_options': [
            ('claude-3-opus-20240229', 'Claude 3 Opus'),
            ('claude-3-sonnet-20240229', 'Claude 3 Sonnet'),
            ('claude-3-haiku-20240307', 'Claude 3 Haiku'),
        ]
    }
    
    return render(request, 'engine_app/configuration.html', context)


@login_required
def sessions(request):
    """View Engine session history."""
    session_list = EngineSession.objects.filter(
        user=request.user
    ).select_related('configuration').order_by('-start_time')
    
    # Pagination
    paginator = Paginator(session_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'engine_app/sessions.html', context)


@login_required
def session_detail(request, session_id):
    """View detailed session information."""
    session = get_object_or_404(EngineSession, session_id=session_id, user=request.user)
    
    # Get all requests in this session
    requests = session.requests.all().order_by('created_at')
    
    # Calculate session statistics
    total_time = (session.end_time - session.start_time).total_seconds() if session.end_time else 0
    avg_response_time = requests.aggregate(avg=models.Avg('response_time'))['avg'] or 0
    
    context = {
        'session': session,
        'requests': requests,
        'total_time': total_time,
        'avg_response_time': avg_response_time,
    }
    
    return render(request, 'engine_app/session_detail.html', context)


@login_required
def snippets(request):
    """Manage code snippets."""
    # Get user's snippets
    user_snippets = EngineSnippet.objects.filter(user=request.user)
    
    # Get public snippets
    public_snippets = EngineSnippet.objects.filter(
        is_public=True
    ).exclude(user=request.user)[:10]
    
    # Handle search
    query = request.GET.get('q')
    if query:
        user_snippets = user_snippets.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(tags__icontains=query)
        )
    
    # Handle language filter
    language = request.GET.get('language')
    if language:
        user_snippets = user_snippets.filter(language=language)
    
    # Get available languages
    languages = EngineSnippet.objects.filter(
        user=request.user
    ).values_list('language', flat=True).distinct()
    
    context = {
        'user_snippets': user_snippets,
        'public_snippets': public_snippets,
        'languages': languages,
        'current_language': language,
        'search_query': query,
    }
    
    return render(request, 'engine_app/snippets.html', context)


@login_required
@require_http_methods(["POST"])
def create_snippet(request):
    """Create a new snippet via AJAX."""
    try:
        data = json.loads(request.body)
        
        snippet = EngineSnippet.objects.create(
            user=request.user,
            title=data['title'],
            description=data.get('description', ''),
            language=data['language'],
            code=data['code'],
            tags=data.get('tags', ''),
            is_public=data.get('is_public', False),
            is_template=data.get('is_template', False),
        )
        
        return JsonResponse({
            'success': True,
            'snippet_id': snippet.id,
            'message': 'Snippet created successfully.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def workflows(request):
    """Manage research workflows."""
    workflow_list = EngineWorkflow.objects.filter(user=request.user)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        workflow_list = workflow_list.filter(status=status)
    
    context = {
        'workflows': workflow_list,
        'status_filter': status,
    }
    
    return render(request, 'engine_app/workflows.html', context)


@login_required
def integrations(request):
    """Manage external integrations."""
    integration_list = EngineIntegration.objects.filter(user=request.user)
    
    # Group by type
    integrations_by_type = {}
    for integration in integration_list:
        if integration.integration_type not in integrations_by_type:
            integrations_by_type[integration.integration_type] = []
        integrations_by_type[integration.integration_type].append(integration)
    
    context = {
        'integrations_by_type': integrations_by_type,
        'available_types': EngineIntegration.INTEGRATION_TYPES,
    }
    
    return render(request, 'engine_app/integrations.html', context)