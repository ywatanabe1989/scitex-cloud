"""
Template tags for reference sync integration with Scholar module.
"""

from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser

from ..models import ReferenceMapping, SyncProfile, ConflictResolution
from ..signals import get_paper_sync_status, get_sync_actions_for_paper

register = template.Library()


@register.inclusion_tag('reference_sync_app/templatetags/sync_status_badge.html', takes_context=True)
def sync_status_badge(context, paper):
    """
    Display sync status badge for a paper in Scholar module.
    
    Usage in templates:
    {% load reference_sync_tags %}
    {% sync_status_badge paper %}
    """
    request = context.get('request')
    if not request or isinstance(request.user, AnonymousUser):
        return {'show_badge': False}
    
    sync_status = get_paper_sync_status(paper, request.user)
    
    return {
        'show_badge': sync_status['synced'],
        'sync_status': sync_status,
        'paper': paper,
        'has_conflicts': sync_status['has_conflicts'],
        'service_count': sync_status['sync_count'],
    }


@register.inclusion_tag('reference_sync_app/templatetags/sync_actions.html', takes_context=True)
def sync_actions(context, paper):
    """
    Display available sync actions for a paper.
    
    Usage in templates:
    {% load reference_sync_tags %}
    {% sync_actions paper %}
    """
    request = context.get('request')
    if not request or isinstance(request.user, AnonymousUser):
        return {'show_actions': False}
    
    actions = get_sync_actions_for_paper(paper, request.user)
    
    return {
        'show_actions': bool(actions['available_actions']),
        'actions': actions,
        'paper': paper,
        'sync_dashboard_url': reverse('reference_sync:dashboard'),
    }


@register.simple_tag(takes_context=True)
def sync_profile_count(context):
    """
    Get count of user's sync profiles.
    
    Usage: {% sync_profile_count %}
    """
    request = context.get('request')
    if not request or isinstance(request.user, AnonymousUser):
        return 0
    
    return SyncProfile.objects.filter(user=request.user, is_active=True).count()


@register.simple_tag(takes_context=True)
def synced_papers_count(context):
    """
    Get count of user's synced papers.
    
    Usage: {% synced_papers_count %}
    """
    request = context.get('request')
    if not request or isinstance(request.user, AnonymousUser):
        return 0
    
    return ReferenceMapping.objects.filter(
        account__user=request.user,
        sync_status='synced'
    ).count()


@register.simple_tag(takes_context=True)
def sync_conflicts_count(context):
    """
    Get count of unresolved sync conflicts.
    
    Usage: {% sync_conflicts_count %}
    """
    request = context.get('request')
    if not request or isinstance(request.user, AnonymousUser):
        return 0
    
    return ConflictResolution.objects.filter(
        sync_session__profile__user=request.user,
        resolution__isnull=True
    ).count()


@register.filter
def sync_service_icon(service_name):
    """
    Get icon class for sync service.
    
    Usage: {{ service|sync_service_icon }}
    """
    icons = {
        'mendeley': 'fab fa-mendeley',
        'zotero': 'fas fa-book',
    }
    return icons.get(service_name, 'fas fa-sync')


@register.filter
def sync_status_class(status):
    """
    Get CSS class for sync status.
    
    Usage: {{ status|sync_status_class }}
    """
    classes = {
        'synced': 'success',
        'conflict': 'warning',
        'local_newer': 'info',
        'remote_newer': 'info',
        'error': 'danger',
        'pending': 'secondary',
    }
    return classes.get(status, 'secondary')


@register.simple_tag
def sync_dashboard_url():
    """Get URL for sync dashboard."""
    return reverse('reference_sync:dashboard')


@register.simple_tag
def sync_setup_url():
    """Get URL for sync setup."""
    return reverse('reference_sync:profile_create')


@register.inclusion_tag('reference_sync_app/templatetags/sync_widget.html', takes_context=True)
def sync_widget(context, paper):
    """
    Display complete sync widget for a paper.
    
    Usage in templates:
    {% load reference_sync_tags %}
    {% sync_widget paper %}
    """
    request = context.get('request')
    if not request or isinstance(request.user, AnonymousUser):
        return {'show_widget': False}
    
    sync_status = get_paper_sync_status(paper, request.user)
    sync_actions = get_sync_actions_for_paper(paper, request.user)
    
    # Get recent sync activity for this paper
    recent_mappings = ReferenceMapping.objects.filter(
        local_paper=paper,
        account__user=request.user
    ).select_related('account').order_by('-last_synced')[:3]
    
    recent_activity = []
    for mapping in recent_mappings:
        recent_activity.append({
            'service': mapping.service,
            'account_name': mapping.account.account_name,
            'status': mapping.sync_status,
            'last_synced': mapping.last_synced,
            'external_id': mapping.external_id,
        })
    
    return {
        'show_widget': True,
        'paper': paper,
        'sync_status': sync_status,
        'sync_actions': sync_actions,
        'recent_activity': recent_activity,
        'dashboard_url': reverse('reference_sync:dashboard'),
        'setup_url': reverse('reference_sync:profile_create'),
    }