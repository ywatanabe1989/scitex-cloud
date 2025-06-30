"""
Integration utilities for connecting reference sync with Scholar module.
Provides template tags, context processors, and utility functions.
"""

import logging
from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser

from .models import ReferenceMapping, SyncProfile
from .signals import get_paper_sync_status, get_sync_actions_for_paper

logger = logging.getLogger(__name__)

# Register template tags
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
    
    from .models import ConflictResolution
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


def sync_context_processor(request):
    """
    Context processor to add sync information to all templates.
    
    Add to settings.py TEMPLATES context_processors:
    'apps.reference_sync_app.scholar_integration.sync_context_processor'
    """
    if not request.user.is_authenticated:
        return {}
    
    try:
        # Get basic sync statistics
        sync_profiles_count = SyncProfile.objects.filter(
            user=request.user,
            is_active=True
        ).count()
        
        synced_count = ReferenceMapping.objects.filter(
            account__user=request.user,
            sync_status='synced'
        ).count()
        
        from .models import ConflictResolution
        conflicts_count = ConflictResolution.objects.filter(
            sync_session__profile__user=request.user,
            resolution__isnull=True
        ).count()
        
        return {
            'sync_info': {
                'profiles_count': sync_profiles_count,
                'synced_papers_count': synced_count,
                'conflicts_count': conflicts_count,
                'has_sync_setup': sync_profiles_count > 0,
                'dashboard_url': reverse('reference_sync:dashboard'),
            }
        }
        
    except Exception as e:
        logger.error(f"Error in sync context processor: {e}")
        return {}


class ScholarSyncMixin:
    """
    Mixin for Scholar views to add sync information.
    
    Usage:
    class PaperDetailView(ScholarSyncMixin, DetailView):
        model = SearchIndex
        ...
    """
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated and hasattr(self, 'object'):
            # Add sync status for the current paper
            paper = self.object
            context['sync_status'] = get_paper_sync_status(paper, self.request.user)
            context['sync_actions'] = get_sync_actions_for_paper(paper, self.request.user)
        
        return context


def enhance_scholar_queryset(queryset, user):
    """
    Enhance Scholar queryset with sync annotations.
    
    Usage in Scholar views:
    from apps.reference_sync_app.scholar_integration import enhance_scholar_queryset
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return enhance_scholar_queryset(queryset, self.request.user)
    """
    if not user.is_authenticated:
        return queryset
    
    from django.db.models import Exists, OuterRef, Case, When, Value, CharField, Count
    
    # Subqueries for sync status
    synced_subquery = ReferenceMapping.objects.filter(
        local_paper=OuterRef('pk'),
        account__user=user,
        sync_status='synced'
    )
    
    conflict_subquery = ReferenceMapping.objects.filter(
        local_paper=OuterRef('pk'),
        account__user=user,
        sync_status='conflict'
    )
    
    local_newer_subquery = ReferenceMapping.objects.filter(
        local_paper=OuterRef('pk'),
        account__user=user,
        sync_status='local_newer'
    )
    
    remote_newer_subquery = ReferenceMapping.objects.filter(
        local_paper=OuterRef('pk'),
        account__user=user,
        sync_status='remote_newer'
    )
    
    # Add annotations
    enhanced_queryset = queryset.annotate(
        is_synced=Exists(synced_subquery),
        has_sync_conflicts=Exists(conflict_subquery),
        has_local_changes=Exists(local_newer_subquery),
        has_remote_changes=Exists(remote_newer_subquery),
        sync_services_count=Count(
            'reference_mappings',
            filter=models.Q(reference_mappings__account__user=user)
        ),
        primary_sync_status=Case(
            When(has_sync_conflicts=True, then=Value('conflict')),
            When(has_local_changes=True, then=Value('local_newer')),
            When(has_remote_changes=True, then=Value('remote_newer')),
            When(is_synced=True, then=Value('synced')),
            default=Value('not_synced'),
            output_field=CharField()
        )
    )
    
    return enhanced_queryset


def get_sync_navigation_items(user):
    """
    Get navigation items for sync functionality to add to Scholar navigation.
    
    Returns list of navigation items that can be added to Scholar templates.
    """
    if not user.is_authenticated:
        return []
    
    from .models import ConflictResolution
    
    # Get counts for badges
    conflicts_count = ConflictResolution.objects.filter(
        sync_session__profile__user=user,
        resolution__isnull=True
    ).count()
    
    items = [
        {
            'name': 'Reference Sync',
            'url': reverse('reference_sync:dashboard'),
            'icon': 'fas fa-sync-alt',
            'description': 'Sync with Mendeley & Zotero',
            'badge': None,
        },
        {
            'name': 'Sync Profiles',
            'url': reverse('reference_sync:profiles'),
            'icon': 'fas fa-cog',
            'description': 'Manage sync settings',
            'badge': None,
        },
        {
            'name': 'Sync History',
            'url': reverse('reference_sync:sessions'),
            'icon': 'fas fa-history',
            'description': 'View sync history',
            'badge': None,
        },
    ]
    
    # Add conflicts item only if there are conflicts
    if conflicts_count > 0:
        items.append({
            'name': 'Conflicts',
            'url': reverse('reference_sync:conflicts'),
            'icon': 'fas fa-exclamation-triangle',
            'description': 'Resolve sync conflicts',
            'badge': {
                'count': conflicts_count,
                'class': 'badge-warning',
            },
        })
    
    return items


def add_sync_to_scholar_search_results(search_results, user):
    """
    Add sync information to Scholar search results.
    
    Usage in Scholar search views:
    results = perform_search(query)
    results = add_sync_to_scholar_search_results(results, request.user)
    """
    if not user.is_authenticated:
        return search_results
    
    if not hasattr(search_results, '__iter__'):
        return search_results
    
    # Get all paper IDs from results
    paper_ids = []
    for result in search_results:
        if hasattr(result, 'id'):
            paper_ids.append(result.id)
        elif isinstance(result, dict) and 'id' in result:
            paper_ids.append(result['id'])
    
    if not paper_ids:
        return search_results
    
    # Get sync mappings for these papers
    mappings = ReferenceMapping.objects.filter(
        local_paper_id__in=paper_ids,
        account__user=user
    ).select_related('account').values(
        'local_paper_id',
        'service',
        'sync_status',
        'account__account_name'
    )
    
    # Group by paper ID
    sync_data = {}
    for mapping in mappings:
        paper_id = mapping['local_paper_id']
        if paper_id not in sync_data:
            sync_data[paper_id] = []
        
        sync_data[paper_id].append({
            'service': mapping['service'],
            'status': mapping['sync_status'],
            'account_name': mapping['account__account_name'],
        })
    
    # Add sync info to results
    for result in search_results:
        result_id = getattr(result, 'id', result.get('id') if isinstance(result, dict) else None)
        if result_id in sync_data:
            if hasattr(result, '__dict__'):
                result.sync_info = sync_data[result_id]
            elif isinstance(result, dict):
                result['sync_info'] = sync_data[result_id]
    
    return search_results


# Utility function for Scholar paper detail pages
def get_sync_widget_data(paper, user):
    """
    Get all data needed for sync widget in Scholar paper detail page.
    
    Returns dict with all sync-related information for the paper.
    """
    if not user.is_authenticated:
        return {'enabled': False}
    
    sync_status = get_paper_sync_status(paper, user)
    sync_actions = get_sync_actions_for_paper(paper, user)
    
    # Get recent sync activity for this paper
    recent_mappings = ReferenceMapping.objects.filter(
        local_paper=paper,
        account__user=user
    ).select_related('account').order_by('-last_synced')[:5]
    
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
        'enabled': True,
        'status': sync_status,
        'actions': sync_actions,
        'recent_activity': recent_activity,
        'dashboard_url': reverse('reference_sync:dashboard'),
        'setup_url': reverse('reference_sync:profiles'),
    }