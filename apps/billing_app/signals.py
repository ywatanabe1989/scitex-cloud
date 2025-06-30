#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SciTeX-Cloud Billing Signals
Automatic subscription and usage management through Django signals
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .models import UserSubscription, SubscriptionTier, UsageTracking, QuotaLimit
from .services import QuotaService, UsageService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_free_subscription(sender, instance, created, **kwargs):
    """Automatically create free subscription for new users"""
    if created:
        try:
            # Get free tier
            free_tier = SubscriptionTier.objects.filter(tier_type='free').first()
            if not free_tier:
                logger.warning("No free tier found - creating default")
                free_tier = SubscriptionTier.objects.create(
                    name='Free',
                    tier_type='free',
                    description='Free tier with basic features',
                    price_monthly=0,
                    price_yearly=0,
                    max_projects=1,
                    storage_gb=1,
                    compute_hours_monthly=10,
                    gpu_hours_monthly=1,
                    api_calls_monthly=100,
                    has_watermark=True,
                    requires_citation=True,
                    requires_scitex_archive=True,
                    trial_days=14,
                    allows_trial=True,
                    is_active=True,
                    display_order=1
                )
            
            # Create subscription
            now = timezone.now()
            trial_end = now + timedelta(days=free_tier.trial_days) if free_tier.allows_trial else now
            
            subscription = UserSubscription.objects.create(
                user=instance,
                tier=free_tier,
                status='trialing' if free_tier.allows_trial else 'active',
                billing_cycle='monthly',
                trial_start=now if free_tier.allows_trial else None,
                trial_end=trial_end if free_tier.allows_trial else None,
                current_period_start=now,
                current_period_end=trial_end,
                next_billing_date=trial_end
            )
            
            # Initialize quotas
            QuotaService.initialize_quotas(subscription)
            
            logger.info(f"Created free subscription for new user: {instance.username}")
            
        except Exception as e:
            logger.error(f"Failed to create free subscription for {instance.username}: {str(e)}")


@receiver(post_save, sender=UserSubscription)
def update_quotas_on_subscription_change(sender, instance, created, **kwargs):
    """Update quotas when subscription changes"""
    if not created:
        # Subscription was updated, reinitialize quotas
        try:
            QuotaService.initialize_quotas(instance)
            logger.info(f"Updated quotas for {instance.user.username}")
        except Exception as e:
            logger.error(f"Failed to update quotas for {instance.user.username}: {str(e)}")


# Usage tracking signals for different modules
from apps.document_app.models import Document
from apps.project_app.models import Project
from apps.auth_app.models import UserProfile
from apps.scholar_app.models import Paper
from apps.writer_app.models import Manuscript
from apps.viz_app.models import Visualization
from apps.code_app.models import CodeExecution


@receiver(post_save, sender=Project)
def track_project_creation(sender, instance, created, **kwargs):
    """Track project creation usage"""
    if created:
        UsageService.record_usage(
            user=instance.owner,
            resource_type='project_creations',
            amount=1,
            unit='projects',
            module='core',
            feature='project_creation',
            project_id=instance.id,
            metadata={'project_name': instance.name}
        )


@receiver(post_save, sender=Document)
def track_document_creation(sender, instance, created, **kwargs):
    """Track document creation and storage usage"""
    if created:
        # Track document creation
        UsageService.record_usage(
            user=instance.owner,
            resource_type='storage',
            amount=instance.file_size / (1024 * 1024 * 1024),  # Convert to GB
            unit='GB',
            module='core',
            feature='document_storage',
            project_id=instance.project.id if instance.project else None,
            metadata={
                'document_type': instance.document_type,
                'document_title': instance.title
            }
        )


@receiver(post_save, sender=Paper)
def track_scholar_usage(sender, instance, created, **kwargs):
    """Track scholar paper saves"""
    if created and hasattr(instance, '_created_by_user'):
        UsageService.record_usage(
            user=instance._created_by_user,
            resource_type='scholar_searches',
            amount=1,
            unit='searches',
            module='scholar',
            feature='paper_save',
            metadata={'paper_title': instance.title}
        )


@receiver(post_save, sender=Manuscript)
def track_writer_compilation(sender, instance, created, **kwargs):
    """Track writer manuscript compilation"""
    if hasattr(instance, '_compiled_by_user'):
        UsageService.record_usage(
            user=instance._compiled_by_user,
            resource_type='writer_compiles',
            amount=1,
            unit='compiles',
            module='writer',
            feature='compilation',
            project_id=instance.project.id if hasattr(instance, 'project') else None,
            metadata={'manuscript_title': instance.title}
        )


@receiver(post_save, sender=Visualization)
def track_viz_creation(sender, instance, created, **kwargs):
    """Track visualization creation and export"""
    if created and hasattr(instance, '_created_by_user'):
        UsageService.record_usage(
            user=instance._created_by_user,
            resource_type='viz_exports',
            amount=1,
            unit='visualizations',
            module='viz',
            feature='creation',
            project_id=instance.project.id if hasattr(instance, 'project') else None,
            metadata={'viz_type': getattr(instance, 'viz_type', 'unknown')}
        )


@receiver(post_save, sender=CodeExecution)
def track_code_execution(sender, instance, created, **kwargs):
    """Track code execution compute usage"""
    if created:
        # Calculate compute time (assuming execution_time is in seconds)
        compute_hours = getattr(instance, 'execution_time', 0) / 3600
        
        UsageService.record_usage(
            user=instance.user,
            resource_type='compute_hours',
            amount=compute_hours,
            unit='hours',
            module='code',
            feature='execution',
            project_id=instance.project.id if hasattr(instance, 'project') else None,
            metadata={
                'language': getattr(instance, 'language', 'unknown'),
                'execution_time_seconds': getattr(instance, 'execution_time', 0)
            }
        )


# API usage tracking
from django.core.signals import request_finished
from django.dispatch import receiver
from django.http import HttpRequest
import threading

# Thread-local storage for request data
_thread_locals = threading.local()


class APIUsageMiddleware:
    """Middleware to track API usage"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Store request start time
        import time
        _thread_locals.start_time = time.time()
        _thread_locals.request = request
        
        response = self.get_response(request)
        
        # Track API usage after response
        if hasattr(_thread_locals, 'start_time') and request.path.startswith('/api/'):
            execution_time = time.time() - _thread_locals.start_time
            
            if request.user.is_authenticated:
                UsageService.record_usage(
                    user=request.user,
                    resource_type='api_calls',
                    amount=1,
                    unit='calls',
                    module='api',
                    feature=request.path.split('/')[2] if len(request.path.split('/')) > 2 else 'unknown',
                    metadata={
                        'endpoint': request.path,
                        'method': request.method,
                        'response_time': execution_time,
                        'status_code': response.status_code
                    }
                )
        
        return response


# Quota enforcement signals
from django.core.exceptions import PermissionDenied


def check_quota_before_action(user, resource_type, amount=1):
    """Check quota before allowing an action"""
    has_quota, available = QuotaService.check_quota_availability(user, resource_type, amount)
    if not has_quota:
        raise PermissionDenied(f"Quota exceeded for {resource_type}. Available: {available}")


# Pre-save signals for quota checking
@receiver(pre_save, sender=Project)
def check_project_quota(sender, instance, **kwargs):
    """Check project quota before creation"""
    if not instance.pk:  # Only for new projects
        check_quota_before_action(instance.owner, 'project_creations', 1)


# Storage quota checking
def check_storage_quota(user, file_size_bytes):
    """Check storage quota before file upload"""
    storage_gb = file_size_bytes / (1024 * 1024 * 1024)
    check_quota_before_action(user, 'storage', storage_gb)


# Subscription expiry checking
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    """Management command to handle subscription expiry"""
    help = 'Check and handle expired subscriptions'
    
    def handle(self, *args, **options):
        now = timezone.now()
        
        # Find expired subscriptions
        expired_subs = UserSubscription.objects.filter(
            current_period_end__lt=now,
            status__in=['active', 'trialing']
        )
        
        for subscription in expired_subs:
            if subscription.canceled_at:
                # Subscription was canceled, deactivate
                subscription.status = 'expired'
                subscription.save()
                logger.info(f"Expired subscription for {subscription.user.username}")
            else:
                # Try to renew if payment method available
                if subscription.stripe_subscription_id:
                    try:
                        # Stripe will handle renewal automatically
                        pass
                    except Exception as e:
                        subscription.status = 'past_due'
                        subscription.save()
                        logger.warning(f"Failed to renew subscription for {subscription.user.username}: {str(e)}")
                else:
                    # Free tier or no payment method
                    subscription.status = 'expired'
                    subscription.save()
        
        # Reset monthly quotas for active subscriptions
        active_subs = UserSubscription.objects.filter(
            status__in=['active', 'trialing']
        )
        
        for subscription in active_subs:
            QuotaService.initialize_quotas(subscription)