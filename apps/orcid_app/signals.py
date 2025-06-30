#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORCID App Signals

This module contains Django signals for the ORCID integration app.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import OrcidProfile, OrcidPublication, OrcidOAuth2Token
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=OrcidOAuth2Token)
def create_or_update_orcid_profile(sender, instance, created, **kwargs):
    """
    Create or update ORCID profile when token is saved
    """
    try:
        profile, profile_created = OrcidProfile.objects.get_or_create(
            user=instance.user,
            defaults={'orcid_id': instance.orcid_id}
        )
        
        if not profile_created and profile.orcid_id != instance.orcid_id:
            # Update ORCID ID if it changed
            profile.orcid_id = instance.orcid_id
            profile.save()
        
        logger.info(f"ORCID profile {'created' if profile_created else 'updated'} for user {instance.user.username}")
        
    except Exception as e:
        logger.error(f"Error creating/updating ORCID profile for user {instance.user.username}: {e}")


@receiver(post_delete, sender=OrcidOAuth2Token)
def handle_token_deletion(sender, instance, **kwargs):
    """
    Handle cleanup when ORCID token is deleted
    """
    try:
        # Optionally mark profile as not synced
        try:
            profile = OrcidProfile.objects.get(user=instance.user)
            profile.is_synced = False
            profile.save()
            logger.info(f"Marked ORCID profile as not synced for user {instance.user.username}")
        except OrcidProfile.DoesNotExist:
            pass
            
    except Exception as e:
        logger.error(f"Error handling token deletion for user {instance.user.username}: {e}")


@receiver(post_save, sender=OrcidPublication)
def update_core_user_profile(sender, instance, created, **kwargs):
    """
    Update core UserProfile when ORCID publications are added/updated
    """
    try:
        # Get or create core UserProfile
        from apps.auth_app.models import UserProfile
        
        user_profile, _ = UserProfile.objects.get_or_create(
            user=instance.profile.user
        )
        
        # Update ORCID field in core profile if not set
        if not user_profile.orcid and instance.profile.orcid_id:
            user_profile.orcid = instance.profile.orcid_id
            user_profile.save()
            logger.info(f"Updated core UserProfile ORCID for user {instance.profile.user.username}")
            
    except Exception as e:
        logger.error(f"Error updating core UserProfile for publication {instance.title}: {e}")


@receiver(post_save, sender=OrcidProfile)
def sync_with_core_profile(sender, instance, created, **kwargs):
    """
    Sync ORCID profile data with core UserProfile
    """
    try:
        from apps.auth_app.models import UserProfile
        
        user_profile, _ = UserProfile.objects.get_or_create(
            user=instance.user
        )
        
        # Update core profile fields if they're empty
        updated = False
        
        if not user_profile.orcid and instance.orcid_id:
            user_profile.orcid = instance.orcid_id
            updated = True
        
        if not user_profile.bio and instance.biography:
            user_profile.bio = instance.biography[:500]  # Truncate to fit core profile
            updated = True
        
        if not user_profile.research_interests and instance.keywords:
            user_profile.research_interests = ', '.join(instance.keywords[:10])  # Take first 10 keywords
            updated = True
        
        if instance.current_affiliation and not user_profile.institution:
            user_profile.institution = instance.current_affiliation[:200]  # Truncate to fit
            updated = True
        
        if updated:
            user_profile.save()
            logger.info(f"Synced ORCID profile data to core UserProfile for user {instance.user.username}")
            
    except Exception as e:
        logger.error(f"Error syncing ORCID profile to core UserProfile for user {instance.user.username}: {e}")


@receiver(post_save, sender=User)
def handle_user_update(sender, instance, created, **kwargs):
    """
    Handle user profile updates that might affect ORCID integration
    """
    if not created:  # Only for existing users
        try:
            # Check if user has ORCID profile
            if hasattr(instance, 'orcid_profile'):
                profile = instance.orcid_profile
                
                # Update display name components if they changed
                updated = False
                
                if instance.first_name != profile.given_name and not profile.given_name:
                    profile.given_name = instance.first_name
                    updated = True
                
                if instance.last_name != profile.family_name and not profile.family_name:
                    profile.family_name = instance.last_name
                    updated = True
                
                if updated:
                    profile.save()
                    logger.info(f"Updated ORCID profile name for user {instance.username}")
                    
        except Exception as e:
            logger.error(f"Error handling user update for ORCID profile: {e}")