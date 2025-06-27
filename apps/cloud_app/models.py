from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string
import uuid

class EmailVerification(models.Model):
    """Model for storing email verification codes."""
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if code is expired (15 minutes validity)."""
        return timezone.now() > self.created_at + timezone.timedelta(minutes=15)
    
    @classmethod
    def generate_code(cls):
        """Generate a 6-digit verification code."""
        return ''.join(random.choices(string.digits, k=6))
    
    def __str__(self):
        return f"{self.email} - {self.code}"


class Donation(models.Model):
    """Model for tracking donations."""
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('github', 'GitHub Sponsors'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    DONATION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    # Donor information
    donor_name = models.CharField(max_length=255)
    donor_email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Donation details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=DONATION_STATUS, default='pending')
    transaction_id = models.CharField(max_length=255, blank=True)
    
    # Preferences
    is_public = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional information
    message = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.donor_name} - ${self.amount} ({self.status})"
    
    def complete_donation(self, transaction_id):
        """Mark donation as completed."""
        self.status = 'completed'
        self.transaction_id = transaction_id
        self.completed_at = timezone.now()
        self.save()


class DonationTier(models.Model):
    """Model for donation tiers and benefits."""
    name = models.CharField(max_length=100)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    benefits = models.TextField()
    badge_color = models.CharField(max_length=7, default='#4a6baf')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['minimum_amount']
    
    def __str__(self):
        return f"{self.name} (${self.minimum_amount}+)"


# New models for SciTeX-Cloud services

class SubscriptionPlan(models.Model):
    """Model for subscription plans."""
    PLAN_TYPES = [
        ('free', 'Free'),
        ('premium_a', 'Premium A'),
        ('premium_b', 'Premium B'),
        ('enterprise', 'Enterprise'),
        ('custom', 'Custom'),
    ]
    
    # Basic information
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Resource limits
    max_projects = models.IntegerField(default=1)
    storage_gb = models.IntegerField(default=5)
    cpu_cores = models.IntegerField(default=2)
    gpu_vram_gb = models.IntegerField(default=2)
    
    # Feature flags
    has_watermark = models.BooleanField(default=True)
    requires_citation = models.BooleanField(default=True)
    requires_archive = models.BooleanField(default=True)
    has_priority_support = models.BooleanField(default=False)
    has_custom_integrations = models.BooleanField(default=False)
    has_team_collaboration = models.BooleanField(default=False)
    
    # Display
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'price_monthly']
    
    def __str__(self):
        return f"{self.name} - ${self.price_monthly}/month"


class Subscription(models.Model):
    """Model for user subscriptions."""
    SUBSCRIPTION_STATUS = [
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('expired', 'Expired'),
    ]
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cloud_subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    
    # Status
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default='trial')
    
    # Billing
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    
    # Dates
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    canceled_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"
    
    def is_active(self):
        """Check if subscription is currently active."""
        return self.status in ['trial', 'active'] and timezone.now() < self.current_period_end


class CloudResource(models.Model):
    """Model for tracking cloud resource usage."""
    RESOURCE_TYPES = [
        ('cpu', 'CPU Time'),
        ('gpu', 'GPU Time'),
        ('storage', 'Storage'),
        ('bandwidth', 'Bandwidth'),
        ('api_calls', 'API Calls'),
    ]
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cloud_resources')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    
    # Resource details
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    amount_used = models.DecimalField(max_digits=20, decimal_places=6)
    unit = models.CharField(max_length=20)  # e.g., 'hours', 'GB', 'requests'
    
    # Tracking
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'resource_type', 'period_start']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.resource_type}: {self.amount_used} {self.unit}"


class APIKey(models.Model):
    """Model for API keys to access SciTeX services."""
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cloud_api_keys')
    
    # Key details
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    prefix = models.CharField(max_length=8, blank=True)  # Visible prefix for identification
    
    # Permissions
    can_read = models.BooleanField(default=True)
    can_write = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    
    # Rate limiting
    rate_limit_per_hour = models.IntegerField(default=1000)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.prefix:
            self.prefix = str(self.key)[:8]
        super().save(*args, **kwargs)


class ServiceIntegration(models.Model):
    """Model for tracking integrations with external services."""
    INTEGRATION_TYPES = [
        ('orcid', 'ORCID'),
        ('github', 'GitHub'),
        ('gitlab', 'GitLab'),
        ('zenodo', 'Zenodo'),
        ('figshare', 'Figshare'),
        ('mendeley', 'Mendeley'),
        ('zotero', 'Zotero'),
    ]
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cloud_integrations')
    
    # Integration details
    integration_type = models.CharField(max_length=20, choices=INTEGRATION_TYPES)
    external_id = models.CharField(max_length=255)
    access_token = models.TextField(blank=True)  # Encrypted in practice
    refresh_token = models.TextField(blank=True)  # Encrypted in practice
    
    # Status
    is_active = models.BooleanField(default=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'integration_type']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.integration_type}"