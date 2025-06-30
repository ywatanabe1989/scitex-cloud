"""
Signal handlers for reference sync app integration with Scholar module.
"""

import logging
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.utils import timezone

from apps.scholar_app.models import SearchIndex, UserLibrary
from .models import ReferenceMapping, SyncProfile, SyncSession


logger = logging.getLogger(__name__)


@receiver(post_save, sender=SearchIndex)
def sync_reference_on_update(sender, instance, created, **kwargs):
    """
    Trigger sync when a reference is updated in the Scholar module.
    """
    if not created:  # Only for updates, not new creations
        # Find mappings for this reference
        mappings = ReferenceMapping.objects.filter(local_paper=instance)
        
        for mapping in mappings:
            # Mark as needing sync
            mapping.sync_status = 'local_newer'
            mapping.save()
            
            # Check if there are active profiles that should auto-sync
            profiles = SyncProfile.objects.filter(
                accounts=mapping.account,
                auto_sync=True,
                is_active=True,
                sync_direction__in=['bidirectional', 'export_only']
            )
            
            for profile in profiles:
                # Check if there's already a running sync
                running_sync = SyncSession.objects.filter(
                    profile=profile,
                    status='running'
                ).exists()
                
                if not running_sync:
                    # Schedule sync (this would be better done with Celery in production)
                    try:
                        from .services import SyncEngine
                        sync_engine = SyncEngine(profile)
                        sync_engine.start_sync(trigger='auto')
                        logger.info(f"Auto-sync triggered for profile {profile.name}")
                    except Exception as e:
                        logger.error(f"Failed to trigger auto-sync: {e}")


@receiver(post_save, sender=UserLibrary)
def sync_user_library_changes(sender, instance, created, **kwargs):
    """
    Sync changes to user library (tags, notes, status, etc.)
    """
    # Find mappings for this reference
    mappings = ReferenceMapping.objects.filter(
        local_paper=instance.paper,
        account__user=instance.user
    )
    
    for mapping in mappings:
        # Update local hash to reflect changes
        from .services import SyncEngine
        sync_engine = SyncEngine(None)  # We'll use utility methods
        new_hash = sync_engine._calculate_local_hash(instance.paper)
        
        if mapping.local_hash != new_hash:
            mapping.local_hash = new_hash
            mapping.sync_status = 'local_newer'
            mapping.save()
            
            logger.debug(f"Updated local hash for mapping {mapping.id}")


@receiver(post_delete, sender=SearchIndex)
def handle_reference_deletion(sender, instance, **kwargs):
    """
    Handle deletion of references from Scholar module.
    """
    # Find mappings for this reference
    mappings = ReferenceMapping.objects.filter(local_paper=instance)
    
    for mapping in mappings:
        # We don't delete the mapping immediately, instead mark it for deletion sync
        mapping.sync_status = 'local_deleted'
        mapping.save()
        
        logger.info(f"Marked mapping {mapping.id} for deletion sync")


@receiver(m2m_changed, sender=SyncProfile.accounts.through)
def update_sync_schedule_on_account_change(sender, instance, action, pk_set, **kwargs):
    """
    Update sync schedule when accounts are added/removed from profiles.
    """
    if action in ['post_add', 'post_remove']:
        # Recalculate next sync time
        if instance.auto_sync:
            instance.next_sync = instance.calculate_next_sync()
            instance.save()
            
            logger.info(f"Updated sync schedule for profile {instance.name}")


@receiver(post_save, sender=SyncProfile)
def schedule_automatic_sync(sender, instance, created, **kwargs):
    """
    Schedule automatic sync when profile is created or updated.
    """
    if instance.auto_sync and instance.is_active:
        # Calculate next sync time
        next_sync = instance.calculate_next_sync()
        if next_sync and next_sync != instance.next_sync:
            instance.next_sync = next_sync
            # Use update to avoid triggering this signal again
            SyncProfile.objects.filter(id=instance.id).update(next_sync=next_sync)
            
            logger.info(f"Scheduled next sync for profile {instance.name} at {next_sync}")


# Custom signal for sync completion
from django.dispatch import Signal

sync_completed = Signal()
sync_failed = Signal()
conflict_detected = Signal()


@receiver(sync_completed)
def handle_sync_completion(sender, session, **kwargs):
    """
    Handle sync completion events.
    """
    profile = session.profile
    
    # Update profile last sync time
    profile.last_sync = timezone.now()
    
    # Calculate next sync time if auto-sync is enabled
    if profile.auto_sync:
        profile.next_sync = profile.calculate_next_sync()
    
    profile.save()
    
    # Send notifications if configured
    if hasattr(profile, 'notification_settings'):
        # This would integrate with a notification system
        pass
    
    logger.info(f"Sync completed for profile {profile.name}: {session.items_processed} items processed")


@receiver(sync_failed)
def handle_sync_failure(sender, session, error, **kwargs):
    """
    Handle sync failure events.
    """
    profile = session.profile
    
    # Log the failure
    logger.error(f"Sync failed for profile {profile.name}: {error}")
    
    # Could implement retry logic here
    # Could send failure notifications
    
    # Mark accounts as potentially having issues
    for account in profile.accounts.all():
        if 'authentication' in str(error).lower():
            account.status = 'error'
            account.save()


@receiver(conflict_detected)
def handle_conflict_detection(sender, conflict, **kwargs):
    """
    Handle conflict detection during sync.
    """
    logger.warning(f"Conflict detected: {conflict.conflict_type} for {conflict.reference_mapping}")
    
    # Could implement automatic resolution for certain conflict types
    if conflict.conflict_type == 'keywords' and conflict.sync_session.profile.conflict_resolution == 'merge':
        try:
            # Automatically merge keywords
            local_keywords = conflict.local_value.get('keywords', [])
            remote_keywords = conflict.remote_value.get('keywords', [])
            merged_keywords = list(set(local_keywords + remote_keywords))
            
            conflict.resolution = 'merged'
            conflict.resolved_value = {'keywords': merged_keywords}
            conflict.resolved_at = timezone.now()
            conflict.save()
            
            logger.info(f"Auto-resolved keyword conflict for {conflict.reference_mapping}")
            
        except Exception as e:
            logger.error(f"Failed to auto-resolve conflict: {e}")


# Integration with Scholar module search
def enhance_scholar_search_with_sync_data(queryset, user):
    """
    Enhance Scholar search results with sync information.
    This function can be called from Scholar views to add sync status.
    """
    if not user.is_authenticated:
        return queryset
    
    # Add sync status annotations
    from django.db.models import Exists, OuterRef, Case, When, Value, CharField
    
    # Check if paper is synced
    synced_subquery = ReferenceMapping.objects.filter(
        local_paper=OuterRef('pk'),
        account__user=user,
        sync_status='synced'
    )
    
    # Check if paper has conflicts
    conflict_subquery = ReferenceMapping.objects.filter(
        local_paper=OuterRef('pk'),
        account__user=user,
        sync_status='conflict'
    )
    
    # Add annotations
    enhanced_queryset = queryset.annotate(
        is_synced=Exists(synced_subquery),
        has_conflicts=Exists(conflict_subquery),
        sync_status=Case(
            When(has_conflicts=True, then=Value('conflict')),
            When(is_synced=True, then=Value('synced')),
            default=Value('not_synced'),
            output_field=CharField()
        )
    )
    
    return enhanced_queryset


# Utility function to get sync status for a paper
def get_paper_sync_status(paper, user):
    """
    Get sync status for a specific paper and user.
    
    Returns:
        dict: Sync status information
    """
    if not user.is_authenticated:
        return {'synced': False, 'services': []}
    
    mappings = ReferenceMapping.objects.filter(
        local_paper=paper,
        account__user=user
    ).select_related('account')
    
    services = []
    for mapping in mappings:
        services.append({
            'service': mapping.service,
            'account_name': mapping.account.account_name,
            'status': mapping.sync_status,
            'last_synced': mapping.last_synced,
            'external_id': mapping.external_id,
        })
    
    return {
        'synced': mappings.exists(),
        'services': services,
        'sync_count': len(services),
        'has_conflicts': mappings.filter(sync_status='conflict').exists(),
    }


# Function to add sync actions to Scholar templates
def get_sync_actions_for_paper(paper, user):
    """
    Get available sync actions for a paper.
    This can be used in Scholar templates to show sync buttons.
    
    Returns:
        dict: Available actions and their URLs
    """
    if not user.is_authenticated:
        return {}
    
    # Get user's active sync profiles
    profiles = SyncProfile.objects.filter(
        user=user,
        is_active=True
    ).prefetch_related('accounts')
    
    actions = []
    
    # Check if paper is already synced
    synced_services = set(
        ReferenceMapping.objects.filter(
            local_paper=paper,
            account__user=user
        ).values_list('service', flat=True)
    )
    
    for profile in profiles:
        for account in profile.accounts.filter(is_active=True):
            if account.service not in synced_services:
                actions.append({
                    'action': 'sync_to',
                    'service': account.service,
                    'account_name': account.account_name,
                    'profile_id': str(profile.id),
                    'url': f'/reference-sync/profiles/{profile.id}/sync/',
                })
    
    # Add update action if already synced
    if synced_services:
        actions.append({
            'action': 'update_sync',
            'services': list(synced_services),
            'url': '/reference-sync/dashboard/',
        })
    
    return {
        'available_actions': actions,
        'is_synced': bool(synced_services),
        'synced_services': list(synced_services),
    }