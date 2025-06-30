#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SciTeX-Cloud Billing Services
Core business logic for subscription, billing, and usage management
"""

import stripe
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from decimal import Decimal
from datetime import timedelta, datetime
import logging

from .models import (
    SubscriptionTier, UserSubscription, UsageTracking, QuotaLimit,
    BillingHistory, InstitutionalLicense, PaymentMethod, PromoCode,
    FeatureFlag
)

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


class SubscriptionService:
    """Service for managing user subscriptions"""
    
    @staticmethod
    def create_subscription(user, tier, billing_cycle='monthly', payment_method_id=None, promo_code=None):
        """Create a new subscription for a user"""
        try:
            with transaction.atomic():
                # Check if user already has a subscription
                existing_sub = UserSubscription.objects.filter(user=user).first()
                if existing_sub and existing_sub.is_active():
                    raise ValueError("User already has an active subscription")
                
                # Calculate pricing
                if billing_cycle == 'yearly' and tier.price_yearly:
                    price = tier.price_yearly
                else:
                    price = tier.price_monthly
                    billing_cycle = 'monthly'
                
                # Apply promo code if provided
                discount_amount = Decimal('0')
                if promo_code:
                    promo = PromoCode.objects.filter(code=promo_code).first()
                    if promo and promo.can_be_used_by(user):
                        discount_amount = promo.apply_discount(price)
                        price -= discount_amount
                        promo.current_uses += 1
                        promo.save()
                
                # Set up dates
                now = timezone.now()
                if tier.allows_trial and tier.trial_days > 0:
                    # Start with trial
                    trial_end = now + timedelta(days=tier.trial_days)
                    current_period_end = trial_end
                    status = 'trialing'
                else:
                    # Start immediately
                    if billing_cycle == 'yearly':
                        current_period_end = now + timedelta(days=365)
                    else:
                        current_period_end = now + timedelta(days=30)
                    status = 'active'
                
                # Create Stripe customer and subscription if not free tier
                stripe_customer_id = ''
                stripe_subscription_id = ''
                
                if price > 0 and payment_method_id:
                    # Create or update Stripe customer
                    stripe_customer = SubscriptionService._get_or_create_stripe_customer(user)
                    stripe_customer_id = stripe_customer.id
                    
                    # Attach payment method
                    stripe.PaymentMethod.attach(
                        payment_method_id,
                        customer=stripe_customer_id
                    )
                    
                    # Create Stripe subscription
                    stripe_price_id = tier.stripe_price_id_yearly if billing_cycle == 'yearly' else tier.stripe_price_id_monthly
                    
                    stripe_sub = stripe.Subscription.create(
                        customer=stripe_customer_id,
                        items=[{'price': stripe_price_id}],
                        default_payment_method=payment_method_id,
                        trial_end=int(trial_end.timestamp()) if status == 'trialing' else None
                    )
                    stripe_subscription_id = stripe_sub.id
                
                # Create subscription record
                subscription = UserSubscription.objects.create(
                    user=user,
                    tier=tier,
                    status=status,
                    billing_cycle=billing_cycle,
                    stripe_customer_id=stripe_customer_id,
                    stripe_subscription_id=stripe_subscription_id,
                    stripe_payment_method_id=payment_method_id,
                    trial_start=now if status == 'trialing' else None,
                    trial_end=trial_end if status == 'trialing' else None,
                    current_period_start=now,
                    current_period_end=current_period_end,
                    next_billing_date=current_period_end
                )
                
                # Create initial quota limits
                QuotaService.initialize_quotas(subscription)
                
                # Record billing history
                if price > 0:
                    BillingHistory.objects.create(
                        user=user,
                        subscription=subscription,
                        transaction_type='subscription',
                        amount=price,
                        status='succeeded',
                        description=f"{tier.name} subscription ({billing_cycle})",
                        period_start=now,
                        period_end=current_period_end
                    )
                
                logger.info(f"Created subscription for {user.username}: {tier.name}")
                return subscription
                
        except Exception as e:
            logger.error(f"Failed to create subscription for {user.username}: {str(e)}")
            raise
    
    @staticmethod
    def _get_or_create_stripe_customer(user):
        """Get or create Stripe customer for user"""
        try:
            # Try to find existing customer
            subscription = UserSubscription.objects.filter(user=user).first()
            if subscription and subscription.stripe_customer_id:
                return stripe.Customer.retrieve(subscription.stripe_customer_id)
        except:
            pass
        
        # Create new customer
        return stripe.Customer.create(
            email=user.email,
            name=user.get_full_name() or user.username,
            metadata={'user_id': user.id}
        )
    
    @staticmethod
    def upgrade_subscription(subscription, new_tier, billing_cycle=None):
        """Upgrade subscription to a higher tier"""
        try:
            with transaction.atomic():
                if not subscription.can_upgrade_to(new_tier):
                    raise ValueError("Cannot upgrade to this tier")
                
                old_tier = subscription.tier
                billing_cycle = billing_cycle or subscription.billing_cycle
                
                # Calculate prorated amount
                days_remaining = subscription.days_remaining()
                if billing_cycle == 'yearly' and new_tier.price_yearly:
                    new_price = new_tier.price_yearly
                    period_days = 365
                else:
                    new_price = new_tier.price_monthly
                    period_days = 30
                
                prorated_amount = (new_price * days_remaining) / period_days
                
                # Update Stripe subscription if needed
                if subscription.stripe_subscription_id and prorated_amount > 0:
                    stripe_price_id = new_tier.stripe_price_id_yearly if billing_cycle == 'yearly' else new_tier.stripe_price_id_monthly
                    
                    stripe.Subscription.modify(
                        subscription.stripe_subscription_id,
                        items=[{
                            'id': subscription.stripe_subscription_id,
                            'price': stripe_price_id
                        }],
                        proration_behavior='always_invoice'
                    )
                
                # Update subscription
                subscription.tier = new_tier
                subscription.billing_cycle = billing_cycle
                subscription.save()
                
                # Update quotas
                QuotaService.update_quotas_for_tier_change(subscription, old_tier, new_tier)
                
                # Record billing history
                BillingHistory.objects.create(
                    user=subscription.user,
                    subscription=subscription,
                    transaction_type='subscription',
                    amount=prorated_amount,
                    status='succeeded',
                    description=f"Upgrade to {new_tier.name}",
                    period_start=timezone.now(),
                    period_end=subscription.current_period_end
                )
                
                logger.info(f"Upgraded {subscription.user.username} from {old_tier.name} to {new_tier.name}")
                return subscription
                
        except Exception as e:
            logger.error(f"Failed to upgrade subscription: {str(e)}")
            raise
    
    @staticmethod
    def cancel_subscription(subscription, reason='', immediate=False):
        """Cancel subscription"""
        try:
            with transaction.atomic():
                # Cancel Stripe subscription
                if subscription.stripe_subscription_id:
                    stripe.Subscription.modify(
                        subscription.stripe_subscription_id,
                        cancel_at_period_end=not immediate
                    )
                
                if immediate:
                    subscription.status = 'canceled'
                    subscription.current_period_end = timezone.now()
                else:
                    subscription.schedule_cancellation(reason)
                
                subscription.save()
                
                logger.info(f"Canceled subscription for {subscription.user.username}")
                return subscription
                
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {str(e)}")
            raise


class UsageService:
    """Service for tracking and managing resource usage"""
    
    @staticmethod
    def record_usage(user, resource_type, amount, unit='units', module='', feature='', project_id=None, metadata=None):
        """Record resource usage for a user"""
        try:
            subscription = UserSubscription.objects.filter(user=user).first()
            if not subscription:
                logger.warning(f"No subscription found for user {user.username}")
                return None
            
            now = timezone.now()
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Calculate period end (next month)
            if period_start.month == 12:
                period_end = period_start.replace(year=period_start.year + 1, month=1)
            else:
                period_end = period_start.replace(month=period_start.month + 1)
            
            # Record usage
            usage = UsageTracking.objects.create(
                user=user,
                subscription=subscription,
                resource_type=resource_type,
                amount_used=amount,
                unit=unit,
                module=module,
                feature=feature,
                project_id=project_id,
                period_start=period_start,
                period_end=period_end,
                metadata=metadata or {}
            )
            
            # Update quota
            QuotaService.update_quota_usage(user, resource_type, amount, period_start, period_end)
            
            return usage
            
        except Exception as e:
            logger.error(f"Failed to record usage for {user.username}: {str(e)}")
            return None
    
    @staticmethod
    def get_usage_summary(user, period_start=None, period_end=None):
        """Get usage summary for a user"""
        if not period_start:
            now = timezone.now()
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if not period_end:
            if period_start.month == 12:
                period_end = period_start.replace(year=period_start.year + 1, month=1)
            else:
                period_end = period_start.replace(month=period_start.month + 1)
        
        usage_records = UsageTracking.objects.filter(
            user=user,
            period_start__gte=period_start,
            period_end__lte=period_end
        )
        
        summary = {}
        for record in usage_records:
            resource_type = record.resource_type
            if resource_type not in summary:
                summary[resource_type] = {
                    'total_used': Decimal('0'),
                    'unit': record.unit,
                    'records': []
                }
            summary[resource_type]['total_used'] += record.amount_used
            summary[resource_type]['records'].append(record)
        
        return summary


class QuotaService:
    """Service for managing user quotas and limits"""
    
    @staticmethod
    def initialize_quotas(subscription):
        """Initialize quotas for a new subscription"""
        limits = subscription.get_effective_limits()
        now = timezone.now()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate period end (next month)
        if period_start.month == 12:
            period_end = period_start.replace(year=period_start.year + 1, month=1)
        else:
            period_end = period_start.replace(month=period_start.month + 1)
        
        # Create quota limits
        quota_mappings = {
            'storage_gb': ('storage', 'GB'),
            'compute_hours_monthly': ('compute_hours', 'hours'),
            'gpu_hours_monthly': ('gpu_hours', 'hours'),
            'api_calls_monthly': ('api_calls', 'calls'),
        }
        
        for limit_key, (resource_type, unit) in quota_mappings.items():
            if limit_key in limits:
                QuotaLimit.objects.update_or_create(
                    user=subscription.user,
                    resource_type=resource_type,
                    period_start=period_start,
                    defaults={
                        'subscription': subscription,
                        'limit_amount': limits[limit_key],
                        'unit': unit,
                        'period_end': period_end,
                        'used_amount': 0,
                        'warning_sent': False,
                        'limit_exceeded': False
                    }
                )
    
    @staticmethod
    def update_quota_usage(user, resource_type, amount, period_start, period_end):
        """Update quota usage for a resource"""
        try:
            quota = QuotaLimit.objects.get(
                user=user,
                resource_type=resource_type,
                period_start=period_start
            )
            quota.add_usage(amount)
            
        except QuotaLimit.DoesNotExist:
            # Quota doesn't exist, try to create it
            subscription = UserSubscription.objects.filter(user=user).first()
            if subscription:
                QuotaService.initialize_quotas(subscription)
                # Try again
                try:
                    quota = QuotaLimit.objects.get(
                        user=user,
                        resource_type=resource_type,
                        period_start=period_start
                    )
                    quota.add_usage(amount)
                except QuotaLimit.DoesNotExist:
                    logger.warning(f"Could not find or create quota for {user.username} - {resource_type}")
    
    @staticmethod
    def check_quota_availability(user, resource_type, requested_amount):
        """Check if user has enough quota for requested amount"""
        now = timezone.now()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        try:
            quota = QuotaLimit.objects.get(
                user=user,
                resource_type=resource_type,
                period_start=period_start
            )
            
            available = quota.limit_amount - quota.used_amount
            return available >= requested_amount, available
            
        except QuotaLimit.DoesNotExist:
            return False, 0
    
    @staticmethod
    def update_quotas_for_tier_change(subscription, old_tier, new_tier):
        """Update quotas when tier changes"""
        old_limits = {
            'storage_gb': old_tier.storage_gb,
            'compute_hours_monthly': old_tier.compute_hours_monthly,
            'gpu_hours_monthly': old_tier.gpu_hours_monthly,
            'api_calls_monthly': old_tier.api_calls_monthly,
        }
        
        new_limits = subscription.get_effective_limits()
        
        now = timezone.now()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        quota_mappings = {
            'storage_gb': 'storage',
            'compute_hours_monthly': 'compute_hours',
            'gpu_hours_monthly': 'gpu_hours',
            'api_calls_monthly': 'api_calls',
        }
        
        for limit_key, resource_type in quota_mappings.items():
            try:
                quota = QuotaLimit.objects.get(
                    user=subscription.user,
                    resource_type=resource_type,
                    period_start=period_start
                )
                quota.limit_amount = new_limits[limit_key]
                quota.save()
                
            except QuotaLimit.DoesNotExist:
                pass  # Will be created by initialize_quotas if needed


class FeatureAccessService:
    """Service for managing feature access based on subscriptions"""
    
    @staticmethod
    def has_feature_access(user, feature_name):
        """Check if user has access to a specific feature"""
        try:
            subscription = UserSubscription.objects.filter(user=user).first()
            if not subscription or not subscription.is_active():
                # Check free tier access
                free_tier = SubscriptionTier.objects.filter(tier_type='free').first()
                if not free_tier:
                    return False
                tier = free_tier
            else:
                tier = subscription.tier
            
            # Check feature flag
            feature_flag = FeatureFlag.objects.filter(name=feature_name).first()
            if feature_flag:
                return feature_flag.is_enabled_for_user(user)
            
            # Check tier-based access
            feature_mappings = {
                'unlimited_scholar_searches': 'allows_scholar_unlimited',
                'advanced_writer_features': 'allows_writer_advanced',
                'viz_export': 'allows_viz_export',
                'private_code_repos': 'allows_code_private_repos',
                'ai_assistant': 'allows_ai_assistant',
                'priority_support': 'has_priority_support',
                'custom_integrations': 'has_custom_integrations',
                'advanced_analytics': 'has_advanced_analytics',
                'team_management': 'has_team_management',
                'remove_watermarks': lambda t: not t.has_watermark,
                'commercial_use': 'allows_commercial_use',
                'private_projects': 'allows_private_projects',
            }
            
            if feature_name in feature_mappings:
                attr_or_func = feature_mappings[feature_name]
                if callable(attr_or_func):
                    return attr_or_func(tier)
                return getattr(tier, attr_or_func, False)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking feature access for {user.username}: {str(e)}")
            return False
    
    @staticmethod
    def get_user_tier_info(user):
        """Get comprehensive tier information for user"""
        try:
            subscription = UserSubscription.objects.filter(user=user).first()
            if not subscription or not subscription.is_active():
                tier = SubscriptionTier.objects.filter(tier_type='free').first()
                subscription_info = None
            else:
                tier = subscription.tier
                subscription_info = {
                    'status': subscription.status,
                    'days_remaining': subscription.days_remaining(),
                    'billing_cycle': subscription.billing_cycle,
                    'is_trial': subscription.is_trial(),
                    'monthly_price': subscription.get_monthly_price(),
                }
            
            if not tier:
                return None
            
            return {
                'tier': tier,
                'subscription': subscription_info,
                'limits': subscription.get_effective_limits() if subscription else {
                    'max_projects': tier.max_projects,
                    'storage_gb': tier.storage_gb,
                    'compute_hours_monthly': tier.compute_hours_monthly,
                    'gpu_hours_monthly': tier.gpu_hours_monthly,
                    'api_calls_monthly': tier.api_calls_monthly,
                },
                'features': tier.get_feature_list(),
            }
            
        except Exception as e:
            logger.error(f"Error getting tier info for {user.username}: {str(e)}")
            return None


class BillingService:
    """Service for managing billing and payments"""
    
    @staticmethod
    def process_webhook(webhook_data):
        """Process Stripe webhook events"""
        try:
            event_type = webhook_data.get('type')
            data = webhook_data.get('data', {}).get('object', {})
            
            if event_type == 'invoice.payment_succeeded':
                BillingService._handle_payment_succeeded(data)
            elif event_type == 'invoice.payment_failed':
                BillingService._handle_payment_failed(data)
            elif event_type == 'customer.subscription.updated':
                BillingService._handle_subscription_updated(data)
            elif event_type == 'customer.subscription.deleted':
                BillingService._handle_subscription_canceled(data)
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
    
    @staticmethod
    def _handle_payment_succeeded(invoice_data):
        """Handle successful payment"""
        subscription_id = invoice_data.get('subscription')
        amount = invoice_data.get('amount_paid', 0) / 100  # Convert from cents
        
        try:
            subscription = UserSubscription.objects.get(stripe_subscription_id=subscription_id)
            
            # Update subscription status
            subscription.status = 'active'
            subscription.save()
            
            # Record payment
            BillingHistory.objects.create(
                user=subscription.user,
                subscription=subscription,
                transaction_type='subscription',
                amount=amount,
                status='succeeded',
                stripe_invoice_id=invoice_data.get('id'),
                description=f"Payment for {subscription.tier.name}",
                period_start=timezone.now(),
                period_end=subscription.current_period_end
            )
            
        except UserSubscription.DoesNotExist:
            logger.warning(f"Subscription not found for Stripe ID: {subscription_id}")
    
    @staticmethod
    def _handle_payment_failed(invoice_data):
        """Handle failed payment"""
        subscription_id = invoice_data.get('subscription')
        
        try:
            subscription = UserSubscription.objects.get(stripe_subscription_id=subscription_id)
            subscription.status = 'payment_failed'
            subscription.save()
            
            # Record failed payment
            BillingHistory.objects.create(
                user=subscription.user,
                subscription=subscription,
                transaction_type='subscription',
                amount=invoice_data.get('amount_due', 0) / 100,
                status='failed',
                stripe_invoice_id=invoice_data.get('id'),
                description=f"Failed payment for {subscription.tier.name}"
            )
            
        except UserSubscription.DoesNotExist:
            logger.warning(f"Subscription not found for Stripe ID: {subscription_id}")
    
    @staticmethod
    def _handle_subscription_updated(subscription_data):
        """Handle subscription updates from Stripe"""
        subscription_id = subscription_data.get('id')
        
        try:
            subscription = UserSubscription.objects.get(stripe_subscription_id=subscription_id)
            
            # Update period dates
            current_period_start = datetime.fromtimestamp(
                subscription_data.get('current_period_start'), tz=timezone.utc
            )
            current_period_end = datetime.fromtimestamp(
                subscription_data.get('current_period_end'), tz=timezone.utc
            )
            
            subscription.current_period_start = current_period_start
            subscription.current_period_end = current_period_end
            subscription.next_billing_date = current_period_end
            subscription.save()
            
        except UserSubscription.DoesNotExist:
            logger.warning(f"Subscription not found for Stripe ID: {subscription_id}")
    
    @staticmethod
    def _handle_subscription_canceled(subscription_data):
        """Handle subscription cancellation"""
        subscription_id = subscription_data.get('id')
        
        try:
            subscription = UserSubscription.objects.get(stripe_subscription_id=subscription_id)
            subscription.status = 'canceled'
            subscription.canceled_at = timezone.now()
            subscription.save()
            
        except UserSubscription.DoesNotExist:
            logger.warning(f"Subscription not found for Stripe ID: {subscription_id}")


class InstitutionalService:
    """Service for managing institutional licenses"""
    
    @staticmethod
    def create_institutional_license(institution_data):
        """Create new institutional license"""
        # Implementation for institutional license creation
        pass
    
    @staticmethod
    def add_user_to_institution(user, license):
        """Add user to institutional license"""
        if not license.can_add_user():
            raise ValueError("Institution has reached maximum users")
        
        if not license.is_user_eligible(user):
            raise ValueError("User not eligible for this institution")
        
        # Create subscription under institutional license
        subscription = UserSubscription.objects.create(
            user=user,
            tier=license.tier,
            status='active',
            billing_cycle='monthly',
            current_period_start=timezone.now(),
            current_period_end=license.end_date,
            institution_name=license.institution_name,
            institution_domain=license.domain,
            institutional_discount=license.discount_percentage
        )
        
        license.current_users += 1
        license.save()
        
        return subscription