#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Integration Signals

Django signals for GitHub integration models.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import GitHubProfile, GitHubRepository, GitHubConnection
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=GitHubRepository)
def repository_post_save(sender, instance, created, **kwargs):
    """Handle repository creation/update"""
    if created:
        logger.info(f"New GitHub repository synced: {instance.full_name}")
        
        # Auto-create connection if user has auto-sync enabled
        if instance.profile.auto_sync_enabled and instance.can_connect_to_code():
            try:
                connection, conn_created = GitHubConnection.objects.get_or_create(
                    repository=instance,
                    defaults={
                        'sync_direction': 'bidirectional',
                        'auto_sync_enabled': True,
                    }
                )
                if conn_created:
                    instance.is_connected = True
                    instance.save(update_fields=['is_connected'])
                    logger.info(f"Auto-connected repository: {instance.full_name}")
            except Exception as e:
                logger.error(f"Failed to auto-connect repository {instance.full_name}: {e}")


@receiver(post_save, sender=GitHubConnection)
def connection_post_save(sender, instance, created, **kwargs):
    """Handle connection creation/update"""
    if created:
        logger.info(f"New GitHub connection created: {instance.repository.full_name}")
        
        # Update repository connection status
        if not instance.repository.is_connected:
            instance.repository.is_connected = True
            instance.repository.save(update_fields=['is_connected'])


@receiver(post_delete, sender=GitHubConnection)
def connection_post_delete(sender, instance, **kwargs):
    """Handle connection deletion"""
    logger.info(f"GitHub connection deleted: {instance.repository.full_name}")
    
    # Update repository connection status
    if instance.repository.is_connected:
        instance.repository.is_connected = False
        instance.repository.save(update_fields=['is_connected'])


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """Handle user creation"""
    if created:
        logger.info(f"New user created: {instance.username}")
        # Note: GitHubProfile will be created when user connects to GitHub