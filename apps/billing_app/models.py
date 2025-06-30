#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SciTeX-Cloud Billing and Monetization Models
Comprehensive subscription, billing, usage tracking, and quota management
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
import json
from datetime import datetime, timedelta


class SubscriptionTier(models.Model):
    """Enhanced subscription tiers with comprehensive feature controls"""
    
    TIER_TYPES = [
        ('free', 'Free'),
        ('individual', 'Individual'),
        ('team', 'Team'),
        ('institutional', 'Institutional'),
        ('enterprise', 'Enterprise'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=100)
    tier_type = models.CharField(max_length=20, choices=TIER_TYPES, unique=True)
    description = models.TextField()
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Resource Limits
    max_projects = models.IntegerField(default=1)
    max_collaborators_per_project = models.IntegerField(default=1)
    storage_gb = models.IntegerField(default=1)
    compute_hours_monthly = models.IntegerField(default=10)
    gpu_hours_monthly = models.IntegerField(default=2)
    api_calls_monthly = models.IntegerField(default=1000)
    
    # Feature Access Controls
    has_watermark = models.BooleanField(default=True)
    requires_citation = models.BooleanField(default=True) 
    requires_scitex_archive = models.BooleanField(default=True)
    allows_commercial_use = models.BooleanField(default=False)
    allows_private_projects = models.BooleanField(default=False)
    
    # Advanced Features
    has_priority_support = models.BooleanField(default=False)
    has_custom_integrations = models.BooleanField(default=False)
    has_advanced_analytics = models.BooleanField(default=False)
    has_team_management = models.BooleanField(default=False)
    has_institutional_licensing = models.BooleanField(default=False)
    has_white_labeling = models.BooleanField(default=False)
    has_dedicated_support = models.BooleanField(default=False)
    has_sla_guarantee = models.BooleanField(default=False)
    
    # Module Access
    allows_scholar_unlimited = models.BooleanField(default=False)
    allows_writer_advanced = models.BooleanField(default=False)
    allows_viz_export = models.BooleanField(default=False)
    allows_code_private_repos = models.BooleanField(default=False)
    allows_ai_assistant = models.BooleanField(default=False)
    
    # Display and Marketing
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    marketing_tagline = models.CharField(max_length=200, blank=True)
    
    # Pricing Strategy
    stripe_price_id_monthly = models.CharField(max_length=100, blank=True)
    stripe_price_id_yearly = models.CharField(max_length=100, blank=True)
    discount_percentage_yearly = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(50)])
    
    # Trial Settings
    trial_days = models.IntegerField(default=14)
    allows_trial = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'price_monthly']
        verbose_name = 'Subscription Tier'
        verbose_name_plural = 'Subscription Tiers'
    
    def __str__(self):
        return f"{self.name} - ${self.price_monthly}/month"
    
    def get_yearly_savings(self):
        """Calculate yearly savings percentage"""
        if self.price_yearly and self.price_monthly:
            monthly_total = self.price_monthly * 12
            savings = (monthly_total - self.price_yearly) / monthly_total * 100
            return round(savings, 1)
        return 0
    
    def get_feature_list(self):
        """Get list of enabled features for display"""
        features = []
        
        # Basic features
        if self.max_projects > 1:
            features.append(f"Up to {self.max_projects} projects")
        elif self.max_projects == 1:
            features.append("1 project")
        else:
            features.append("Unlimited projects")
            
        features.append(f"{self.storage_gb}GB storage")
        features.append(f"{self.compute_hours_monthly}h compute time")
        
        if self.gpu_hours_monthly > 0:
            features.append(f"{self.gpu_hours_monthly}h GPU time")
        
        # Premium features
        if not self.has_watermark:
            features.append("No watermarks")
        if not self.requires_citation:
            features.append("No citation requirements")
        if self.allows_commercial_use:
            features.append("Commercial use allowed")
        if self.allows_private_projects:
            features.append("Private projects")
        if self.has_priority_support:
            features.append("Priority support")
        if self.has_advanced_analytics:
            features.append("Advanced analytics")
        if self.has_team_management:
            features.append("Team management")
        if self.has_institutional_licensing:
            features.append("Institutional licensing")
        
        return features


class UserSubscription(models.Model):
    """Enhanced user subscription management"""
    
    STATUS_CHOICES = [
        ('trialing', 'Trial Period'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('paused', 'Paused'),
        ('expired', 'Expired'),
        ('payment_failed', 'Payment Failed'),
    ]
    
    BILLING_CYCLES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom'),
    ]
    
    # Core Relationships
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    tier = models.ForeignKey(SubscriptionTier, on_delete=models.PROTECT, related_name='subscribers')
    
    # Status and Billing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trialing')
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, default='monthly')
    
    # Stripe Integration
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    stripe_payment_method_id = models.CharField(max_length=255, blank=True)
    
    # Date Management
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    next_billing_date = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    # Usage Tracking
    last_activity = models.DateTimeField(auto_now=True)
    total_billed_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Institutional Features
    institution_name = models.CharField(max_length=200, blank=True)
    institution_domain = models.CharField(max_length=100, blank=True)
    institutional_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Custom Pricing (for enterprise)
    custom_price_monthly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    custom_limits = models.JSONField(default=dict)  # Override tier limits
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Subscription'
        verbose_name_plural = 'User Subscriptions'
        indexes = [
            models.Index(fields=['status', 'next_billing_date']),
            models.Index(fields=['stripe_customer_id']),
            models.Index(fields=['current_period_end']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.tier.name} ({self.status})"
    
    def is_active(self):
        """Check if subscription is currently active"""
        return self.status in ['trialing', 'active'] and timezone.now() < self.current_period_end
    
    def is_trial(self):
        """Check if currently in trial period"""
        return self.status == 'trialing' and self.trial_end and timezone.now() < self.trial_end
    
    def days_remaining(self):
        """Get days remaining in current period"""
        if self.current_period_end:
            remaining = self.current_period_end - timezone.now()
            return max(0, remaining.days)
        return 0
    
    def get_effective_limits(self):
        """Get effective limits considering custom overrides"""
        limits = {
            'max_projects': self.tier.max_projects,
            'max_collaborators_per_project': self.tier.max_collaborators_per_project,
            'storage_gb': self.tier.storage_gb,
            'compute_hours_monthly': self.tier.compute_hours_monthly,
            'gpu_hours_monthly': self.tier.gpu_hours_monthly,
            'api_calls_monthly': self.tier.api_calls_monthly,
        }
        
        # Apply custom overrides
        if self.custom_limits:
            limits.update(self.custom_limits)
        
        return limits
    
    def get_monthly_price(self):
        """Get effective monthly price"""
        if self.custom_price_monthly:
            return self.custom_price_monthly
        
        price = self.tier.price_monthly
        if self.institutional_discount > 0:
            price = price * (1 - self.institutional_discount / 100)
        
        return price
    
    def can_upgrade_to(self, target_tier):
        """Check if user can upgrade to target tier"""
        current_price = self.get_monthly_price()
        target_price = target_tier.price_monthly
        
        # Can only upgrade to higher tier
        return target_price > current_price
    
    def schedule_cancellation(self, reason=''):
        """Schedule cancellation at end of current period"""
        self.canceled_at = timezone.now()
        self.cancellation_reason = reason
        self.save()
    
    def reactivate(self):
        """Reactivate canceled subscription"""
        if self.status == 'canceled':
            self.status = 'active'
            self.canceled_at = None
            self.cancellation_reason = ''
            self.save()


class UsageTracking(models.Model):
    """Track resource usage across all modules"""
    
    RESOURCE_TYPES = [
        ('storage', 'Storage'),
        ('compute_hours', 'Compute Hours'),
        ('gpu_hours', 'GPU Hours'),
        ('api_calls', 'API Calls'),
        ('scholar_searches', 'Scholar Searches'),
        ('writer_compiles', 'Writer Compiles'),
        ('viz_exports', 'Visualization Exports'),
        ('ai_queries', 'AI Assistant Queries'),
        ('collaborator_invites', 'Collaborator Invites'),
        ('project_creations', 'Project Creations'),
    ]
    
    # Core Fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage_tracking')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='usage_records')
    resource_type = models.CharField(max_length=30, choices=RESOURCE_TYPES)
    
    # Usage Data
    amount_used = models.DecimalField(max_digits=15, decimal_places=6)
    unit = models.CharField(max_length=20)  # GB, hours, calls, searches, etc.
    
    # Context
    module = models.CharField(max_length=30, blank=True)  # scholar, writer, viz, code, core
    feature = models.CharField(max_length=100, blank=True)  # specific feature
    project_id = models.IntegerField(null=True, blank=True)  # related project
    
    # Time Tracking
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)  # Additional context
    
    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['user', 'resource_type', 'period_start']),
            models.Index(fields=['subscription', 'period_start']),
            models.Index(fields=['module', 'period_start']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.resource_type}: {self.amount_used} {self.unit}"


class QuotaLimit(models.Model):
    """Define and track quota limits for users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quota_limits')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='quotas')
    resource_type = models.CharField(max_length=30, choices=UsageTracking.RESOURCE_TYPES)
    
    # Limits
    limit_amount = models.DecimalField(max_digits=15, decimal_places=6)
    used_amount = models.DecimalField(max_digits=15, decimal_places=6, default=0)
    unit = models.CharField(max_length=20)
    
    # Period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Notifications
    warning_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=80)  # percentage
    warning_sent = models.BooleanField(default=False)
    limit_exceeded = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'resource_type', 'period_start']
        indexes = [
            models.Index(fields=['user', 'resource_type']),
            models.Index(fields=['period_end']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.resource_type}: {self.used_amount}/{self.limit_amount} {self.unit}"
    
    def usage_percentage(self):
        """Get usage as percentage of limit"""
        if self.limit_amount > 0:
            return (self.used_amount / self.limit_amount) * 100
        return 0
    
    def is_near_limit(self):
        """Check if usage is near the warning threshold"""
        return self.usage_percentage() >= self.warning_threshold
    
    def is_exceeded(self):
        """Check if quota is exceeded"""
        return self.used_amount >= self.limit_amount
    
    def add_usage(self, amount):
        """Add usage to current amount"""
        self.used_amount += amount
        
        if not self.warning_sent and self.is_near_limit():
            self.warning_sent = True
            # TODO: Send warning notification
        
        if self.is_exceeded():
            self.limit_exceeded = True
            # TODO: Send limit exceeded notification
        
        self.save()


class BillingHistory(models.Model):
    """Track all billing transactions and invoice history"""
    
    TRANSACTION_TYPES = [
        ('subscription', 'Subscription Fee'),
        ('usage_overage', 'Usage Overage'),
        ('refund', 'Refund'),
        ('credit', 'Account Credit'),
        ('discount', 'Discount Applied'),
        ('tax', 'Tax'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('disputed', 'Disputed'),
    ]
    
    # Core Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='billing_history')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Transaction Details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # External References
    stripe_invoice_id = models.CharField(max_length=255, blank=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True)
    invoice_number = models.CharField(max_length=50, blank=True)
    
    # Dates
    transaction_date = models.DateTimeField(auto_now_add=True)
    period_start = models.DateTimeField(null=True, blank=True)
    period_end = models.DateTimeField(null=True, blank=True)
    
    # Details
    description = models.TextField()
    metadata = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['user', 'transaction_date']),
            models.Index(fields=['status', 'transaction_date']),
            models.Index(fields=['stripe_invoice_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type}: ${self.amount} ({self.status})"


class InstitutionalLicense(models.Model):
    """Manage institutional licenses and bulk subscriptions"""
    
    LICENSE_TYPES = [
        ('university', 'University License'),
        ('research_institute', 'Research Institute'),
        ('corporate', 'Corporate License'),
        ('government', 'Government License'),
        ('nonprofit', 'Non-Profit License'),
    ]
    
    # Institution Information
    institution_name = models.CharField(max_length=200)
    institution_type = models.CharField(max_length=30, choices=LICENSE_TYPES)
    domain = models.CharField(max_length=100, help_text="Institution email domain (e.g., university.edu)")
    
    # License Details
    tier = models.ForeignKey(SubscriptionTier, on_delete=models.PROTECT)
    max_users = models.IntegerField()
    current_users = models.IntegerField(default=0)
    
    # Pricing
    price_per_user_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_commitment = models.IntegerField(default=1)  # months
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Contact Information
    admin_name = models.CharField(max_length=200)
    admin_email = models.EmailField()
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_licenses')
    
    # Status
    is_active = models.BooleanField(default=True)
    auto_approve_domain = models.BooleanField(default=True, help_text="Auto-approve users from institution domain")
    
    # Dates
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Billing
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    next_billing_date = models.DateTimeField()
    
    class Meta:
        ordering = ['institution_name']
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['is_active', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.institution_name} - {self.current_users}/{self.max_users} users"
    
    def can_add_user(self):
        """Check if license can accommodate more users"""
        return self.current_users < self.max_users
    
    def get_monthly_cost(self):
        """Calculate monthly cost for current usage"""
        base_cost = self.current_users * self.price_per_user_monthly
        discount = base_cost * (self.discount_percentage / 100)
        return base_cost - discount
    
    def is_user_eligible(self, user):
        """Check if user is eligible for this license"""
        if not user.email:
            return False
        
        user_domain = user.email.split('@')[1].lower()
        return user_domain == self.domain.lower()


class PaymentMethod(models.Model):
    """Store payment method information"""
    
    CARD_TYPES = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
        ('discover', 'Discover'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    
    # Stripe Integration
    stripe_payment_method_id = models.CharField(max_length=255, unique=True)
    
    # Card Information (last 4 digits only)
    card_brand = models.CharField(max_length=20, choices=CARD_TYPES)
    card_last4 = models.CharField(max_length=4)
    card_exp_month = models.IntegerField()
    card_exp_year = models.IntegerField()
    
    # Status
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Billing Address
    billing_name = models.CharField(max_length=200)
    billing_address = models.TextField()
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100)
    billing_zip = models.CharField(max_length=20)
    billing_country = models.CharField(max_length=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.card_brand.title()} ****{self.card_last4}"
    
    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one default payment method per user
            PaymentMethod.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class PromoCode(models.Model):
    """Promotional codes and discounts"""
    
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed_amount', 'Fixed Amount'),
        ('free_trial', 'Extended Free Trial'),
    ]
    
    # Code Information
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Discount Details
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_uses = models.IntegerField(null=True, blank=True)
    current_uses = models.IntegerField(default=0)
    
    # Eligibility
    applicable_tiers = models.ManyToManyField(SubscriptionTier, blank=True)
    new_users_only = models.BooleanField(default=False)
    
    # Dates
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'percentage' else '$'} off"
    
    def is_valid(self):
        """Check if promo code is currently valid"""
        now = timezone.now()
        return (
            self.is_active and 
            self.valid_from <= now <= self.valid_until and
            (self.max_uses is None or self.current_uses < self.max_uses)
        )
    
    def can_be_used_by(self, user):
        """Check if user can use this promo code"""
        if not self.is_valid():
            return False
        
        if self.new_users_only:
            # Check if user has ever had a paid subscription
            has_paid_subscription = UserSubscription.objects.filter(
                user=user,
                tier__price_monthly__gt=0
            ).exists()
            return not has_paid_subscription
        
        return True
    
    def apply_discount(self, amount):
        """Calculate discount amount"""
        if self.discount_type == 'percentage':
            return amount * (self.discount_value / 100)
        elif self.discount_type == 'fixed_amount':
            return min(self.discount_value, amount)
        return 0


class FeatureFlag(models.Model):
    """Feature flags for gradual rollouts and A/B testing"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=False)
    
    # Rollout Strategy
    rollout_percentage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    target_tiers = models.ManyToManyField(SubscriptionTier, blank=True)
    target_users = models.ManyToManyField(User, blank=True)
    
    # Conditions
    requires_subscription = models.BooleanField(default=False)
    min_account_age_days = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.rollout_percentage}% rollout"
    
    def is_enabled_for_user(self, user):
        """Check if feature is enabled for specific user"""
        if not self.is_active:
            return False
        
        # Check if user is explicitly targeted
        if self.target_users.filter(id=user.id).exists():
            return True
        
        # Check subscription requirements
        if self.requires_subscription:
            try:
                subscription = user.subscription
                if not subscription.is_active():
                    return False
                
                # Check if user's tier is targeted
                if self.target_tiers.exists() and subscription.tier not in self.target_tiers.all():
                    return False
            except UserSubscription.DoesNotExist:
                return False
        
        # Check account age
        if self.min_account_age_days > 0:
            account_age = (timezone.now() - user.date_joined).days
            if account_age < self.min_account_age_days:
                return False
        
        # Percentage-based rollout (using user ID for consistency)
        if self.rollout_percentage < 100:
            user_hash = hash(f"{self.name}_{user.id}") % 100
            return user_hash < self.rollout_percentage
        
        return True