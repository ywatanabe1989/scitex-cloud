#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Django management command to process subscription renewals and expirations
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.billing_app.models import UserSubscription, QuotaLimit
from apps.billing_app.services import QuotaService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process subscription renewals, expirations, and quota resets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making changes to see what would happen',
        )
        
        parser.add_argument(
            '--force-quota-reset',
            action='store_true',
            help='Force reset quotas for all active subscriptions',
        )

    def handle(self, *args, **options):
        """Process subscriptions and quotas"""
        
        dry_run = options['dry_run']
        force_quota_reset = options['force_quota_reset']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 DRY RUN MODE - No changes will be made')
            )
        
        now = timezone.now()
        
        # Process expired subscriptions
        self.process_expired_subscriptions(now, dry_run)
        
        # Process trial expirations
        self.process_trial_expirations(now, dry_run)
        
        # Process quota resets
        self.process_quota_resets(now, dry_run, force_quota_reset)
        
        # Process subscription warnings
        self.process_subscription_warnings(now, dry_run)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Subscription processing completed')
        )

    def process_expired_subscriptions(self, now, dry_run):
        """Process expired subscriptions"""
        self.stdout.write('\n📅 Processing expired subscriptions...')
        
        expired_subs = UserSubscription.objects.filter(
            current_period_end__lt=now,
            status__in=['active', 'trialing', 'past_due']
        )
        
        count = 0
        for subscription in expired_subs:
            if subscription.canceled_at:
                # Subscription was canceled, mark as expired
                if not dry_run:
                    subscription.status = 'expired'
                    subscription.save()
                    
                self.stdout.write(
                    f'  ❌ Expired: {subscription.user.username} ({subscription.tier.name})'
                )
                count += 1
            else:
                # Try to renew if payment method available
                if subscription.stripe_subscription_id:
                    # Stripe will handle renewal automatically
                    self.stdout.write(
                        f'  🔄 Auto-renewal: {subscription.user.username} ({subscription.tier.name})'
                    )
                else:
                    # Free tier or no payment method, check if should expire
                    if subscription.tier.price_monthly > 0:
                        if not dry_run:
                            subscription.status = 'expired'
                            subscription.save()
                        
                        self.stdout.write(
                            f'  ❌ Expired (no payment): {subscription.user.username} ({subscription.tier.name})'
                        )
                        count += 1
        
        self.stdout.write(f'📊 Processed {count} expired subscriptions')

    def process_trial_expirations(self, now, dry_run):
        """Process trial expirations"""
        self.stdout.write('\n🆓 Processing trial expirations...')
        
        expired_trials = UserSubscription.objects.filter(
            status='trialing',
            trial_end__lt=now
        )
        
        count = 0
        for subscription in expired_trials:
            if subscription.tier.price_monthly == 0:
                # Free tier trial, convert to active
                if not dry_run:
                    subscription.status = 'active'
                    subscription.trial_start = None
                    subscription.trial_end = None
                    subscription.save()
                
                self.stdout.write(
                    f'  ✅ Trial to Free: {subscription.user.username}'
                )
            else:
                # Paid tier trial, check payment method
                if subscription.stripe_subscription_id and subscription.stripe_payment_method_id:
                    # Has payment method, should auto-convert
                    if not dry_run:
                        subscription.status = 'active'
                        subscription.save()
                    
                    self.stdout.write(
                        f'  💳 Trial to Paid: {subscription.user.username} ({subscription.tier.name})'
                    )
                else:
                    # No payment method, downgrade to free
                    from apps.billing_app.models import SubscriptionTier
                    free_tier = SubscriptionTier.objects.filter(tier_type='free').first()
                    
                    if free_tier and not dry_run:
                        subscription.tier = free_tier
                        subscription.status = 'active'
                        subscription.trial_start = None
                        subscription.trial_end = None
                        subscription.save()
                    
                    self.stdout.write(
                        f'  ⬇️ Trial to Free (no payment): {subscription.user.username}'
                    )
            
            count += 1
        
        self.stdout.write(f'📊 Processed {count} trial expirations')

    def process_quota_resets(self, now, dry_run, force_reset):
        """Process monthly quota resets"""
        self.stdout.write('\n🔄 Processing quota resets...')
        
        # Find quotas that need reset (period ended)
        if force_reset:
            reset_quotas = QuotaLimit.objects.filter(
                subscription__status__in=['active', 'trialing']
            )
            self.stdout.write('  🔧 Force resetting all quotas')
        else:
            reset_quotas = QuotaLimit.objects.filter(
                period_end__lt=now,
                subscription__status__in=['active', 'trialing']
            )
        
        count = 0
        subscriptions_processed = set()
        
        for quota in reset_quotas:
            subscription = quota.subscription
            if subscription.id not in subscriptions_processed:
                if not dry_run:
                    QuotaService.initialize_quotas(subscription)
                
                self.stdout.write(
                    f'  🔄 Reset quotas: {subscription.user.username} ({subscription.tier.name})'
                )
                subscriptions_processed.add(subscription.id)
                count += 1
        
        self.stdout.write(f'📊 Reset quotas for {count} subscriptions')

    def process_subscription_warnings(self, now, dry_run):
        """Send warnings for subscriptions expiring soon"""
        self.stdout.write('\n⚠️ Processing subscription warnings...')
        
        # Find subscriptions expiring in 7 days
        warning_date = now + timedelta(days=7)
        expiring_soon = UserSubscription.objects.filter(
            current_period_end__lte=warning_date,
            current_period_end__gt=now,
            status__in=['active', 'trialing']
        )
        
        count = 0
        for subscription in expiring_soon:
            # TODO: Send warning email
            self.stdout.write(
                f'  ⚠️ Expiring soon: {subscription.user.username} '
                f'({subscription.tier.name}) - {subscription.days_remaining()} days'
            )
            count += 1
        
        # Find quotas near limits
        near_limit_quotas = QuotaLimit.objects.filter(
            period_end__gte=now,
            warning_sent=False,
            subscription__status__in=['active', 'trialing']
        )
        
        quota_warnings = 0
        for quota in near_limit_quotas:
            if quota.is_near_limit():
                # TODO: Send quota warning email
                if not dry_run:
                    quota.warning_sent = True
                    quota.save()
                
                self.stdout.write(
                    f'  📊 Quota warning: {quota.user.username} - '
                    f'{quota.resource_type} at {quota.usage_percentage():.1f}%'
                )
                quota_warnings += 1
        
        self.stdout.write(f'📊 Sent {count} subscription warnings and {quota_warnings} quota warnings')