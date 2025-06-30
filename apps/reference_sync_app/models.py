from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
# from django.contrib.postgres.fields import ArrayField
from cryptography.fernet import Fernet
from django.conf import settings
import uuid
import json
import logging

logger = logging.getLogger(__name__)


class EncryptedTextField(models.TextField):
    """Custom field to encrypt sensitive data like OAuth tokens."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # In production, this should be from settings or environment
        self.cipher = Fernet(Fernet.generate_key())
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return self.cipher.decrypt(value.encode()).decode()
        except Exception:
            return value  # Return as-is if decryption fails
    
    def get_prep_value(self, value):
        if value is None:
            return value
        try:
            return self.cipher.encrypt(value.encode()).decode()
        except Exception:
            return value  # Return as-is if encryption fails


class ReferenceManagerAccount(models.Model):
    """Store OAuth credentials and account info for reference managers."""
    
    SERVICE_CHOICES = [
        ('mendeley', 'Mendeley'),
        ('zotero', 'Zotero'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reference_accounts')
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    account_name = models.CharField(max_length=200, help_text="Display name for the account")
    
    # OAuth credentials (encrypted)
    access_token = EncryptedTextField(blank=True, help_text="OAuth access token")
    refresh_token = EncryptedTextField(blank=True, help_text="OAuth refresh token")
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Account metadata
    external_user_id = models.CharField(max_length=100, blank=True, help_text="User ID from the service")
    account_email = models.EmailField(blank=True, help_text="Email associated with the account")
    account_metadata = models.JSONField(default=dict, blank=True, help_text="Additional account info")
    
    # Status and sync info
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_count = models.IntegerField(default=0)
    
    # Rate limiting
    api_calls_today = models.IntegerField(default=0)
    api_quota_reset = models.DateTimeField(default=timezone.now)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'service', 'external_user_id']
        indexes = [
            models.Index(fields=['user', 'service']),
            models.Index(fields=['status', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.service} ({self.account_name})"
    
    def is_token_valid(self):
        """Check if the OAuth token is still valid."""
        if not self.token_expires_at:
            return True
        return timezone.now() < self.token_expires_at
    
    def can_make_api_call(self):
        """Check if we can make an API call based on rate limits."""
        # Reset daily quota if needed
        if timezone.now().date() > self.api_quota_reset.date():
            self.api_calls_today = 0
            self.api_quota_reset = timezone.now()
            self.save()
        
        # Define service-specific limits
        limits = {
            'mendeley': 100,  # Mendeley API limit per day
            'zotero': 1000,   # Zotero API limit per day
        }
        
        return self.api_calls_today < limits.get(self.service, 100)


class SyncProfile(models.Model):
    """Configuration for how syncing should work for a user."""
    
    FREQUENCY_CHOICES = [
        ('manual', 'Manual Only'),
        ('hourly', 'Every Hour'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('never', 'Disabled'),
    ]
    
    CONFLICT_RESOLUTION_CHOICES = [
        ('ask', 'Ask User'),
        ('local_wins', 'Local Wins'),
        ('remote_wins', 'Remote Wins'),
        ('merge', 'Try to Merge'),
        ('skip', 'Skip Conflicts'),
    ]
    
    SYNC_DIRECTION_CHOICES = [
        ('bidirectional', 'Bidirectional'),
        ('import_only', 'Import Only'),
        ('export_only', 'Export Only'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sync_profiles')
    name = models.CharField(max_length=200, help_text="Name for this sync profile")
    description = models.TextField(blank=True, help_text="Description of sync settings")
    
    # Associated accounts
    accounts = models.ManyToManyField(ReferenceManagerAccount, related_name='sync_profiles')
    
    # Sync settings
    auto_sync = models.BooleanField(default=False, help_text="Enable automatic syncing")
    sync_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='manual')
    sync_direction = models.CharField(max_length=20, choices=SYNC_DIRECTION_CHOICES, default='bidirectional')
    
    # Conflict resolution
    conflict_resolution = models.CharField(max_length=20, choices=CONFLICT_RESOLUTION_CHOICES, default='ask')
    
    # Filter settings (stored as JSON instead of ArrayField for SQLite compatibility)
    sync_collections = models.JSONField(
        default=list,
        blank=True,
        help_text="Specific collections to sync (empty = all)"
    )
    sync_tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Only sync items with these tags"
    )
    exclude_tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Exclude items with these tags"
    )
    
    # Content settings
    sync_pdfs = models.BooleanField(default=True, help_text="Sync PDF files")
    sync_notes = models.BooleanField(default=True, help_text="Sync notes and annotations")
    sync_attachments = models.BooleanField(default=False, help_text="Sync other attachments")
    
    # Date filters
    sync_after_date = models.DateField(null=True, blank=True, help_text="Only sync items after this date")
    sync_before_date = models.DateField(null=True, blank=True, help_text="Only sync items before this date")
    
    # Status
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    next_sync = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'name']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['auto_sync', 'next_sync']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.name}"
    
    def should_sync_now(self):
        """Check if this profile should sync now based on schedule."""
        if not self.auto_sync or not self.is_active:
            return False
        
        if not self.next_sync:
            return True
            
        return timezone.now() >= self.next_sync
    
    def calculate_next_sync(self):
        """Calculate when the next sync should occur."""
        if not self.auto_sync or self.sync_frequency == 'manual':
            return None
        
        now = timezone.now()
        if self.sync_frequency == 'hourly':
            return now + timezone.timedelta(hours=1)
        elif self.sync_frequency == 'daily':
            return now + timezone.timedelta(days=1)
        elif self.sync_frequency == 'weekly':
            return now + timezone.timedelta(weeks=1)
        
        return None


class SyncSession(models.Model):
    """Track individual sync sessions."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('paused', 'Paused'),
    ]
    
    TRIGGER_CHOICES = [
        ('manual', 'Manual'),
        ('scheduled', 'Scheduled'),
        ('webhook', 'Webhook'),
        ('startup', 'Application Startup'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(SyncProfile, on_delete=models.CASCADE, related_name='sync_sessions')
    
    # Session metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    trigger = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default='manual')
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_duration = models.DurationField(null=True, blank=True)
    
    # Progress tracking
    total_items = models.IntegerField(default=0)
    items_processed = models.IntegerField(default=0)
    items_created = models.IntegerField(default=0)
    items_updated = models.IntegerField(default=0)
    items_deleted = models.IntegerField(default=0)
    items_skipped = models.IntegerField(default=0)
    
    # Conflict tracking
    conflicts_found = models.IntegerField(default=0)
    conflicts_resolved = models.IntegerField(default=0)
    
    # Error handling
    errors_count = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)
    
    # Performance metrics
    api_calls_made = models.IntegerField(default=0)
    data_transferred_mb = models.FloatField(default=0.0)
    
    # Results
    result_summary = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['profile', '-started_at']),
            models.Index(fields=['status', '-started_at']),
        ]
    
    def __str__(self):
        return f"Sync {self.id} - {self.profile.name} ({self.status})"
    
    def duration(self):
        """Calculate session duration."""
        if self.completed_at:
            return self.completed_at - self.started_at
        return timezone.now() - self.started_at
    
    def progress_percentage(self):
        """Calculate progress percentage."""
        if self.total_items == 0:
            return 0
        return (self.items_processed / self.total_items) * 100
    
    def mark_completed(self):
        """Mark session as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_failed(self, error_message=None):
        """Mark session as failed."""
        self.status = 'failed'
        self.completed_at = timezone.now()
        if error_message:
            self.last_error = error_message
        self.save()


class ReferenceMapping(models.Model):
    """Map local references to external service references."""
    
    SERVICE_CHOICES = [
        ('mendeley', 'Mendeley'),
        ('zotero', 'Zotero'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Local reference (from Scholar app) - using string reference to avoid import issues
    local_paper = models.ForeignKey('scholar_app.SearchIndex', on_delete=models.CASCADE, related_name='reference_mappings')
    
    # External reference info
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    external_id = models.CharField(max_length=200, help_text="ID in the external service")
    external_group_id = models.CharField(max_length=200, blank=True, help_text="Group/collection ID")
    
    # Sync metadata
    local_hash = models.CharField(max_length=64, blank=True, help_text="Hash of local data for change detection")
    remote_hash = models.CharField(max_length=64, blank=True, help_text="Hash of remote data")
    
    # Sync status
    sync_status = models.CharField(max_length=20, default='synced', choices=[
        ('synced', 'Synced'),
        ('local_newer', 'Local Newer'),
        ('remote_newer', 'Remote Newer'),
        ('conflict', 'Conflict'),
        ('error', 'Error'),
    ])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_synced = models.DateTimeField(auto_now=True)
    
    # Account reference
    account = models.ForeignKey(ReferenceManagerAccount, on_delete=models.CASCADE, related_name='mappings')
    
    class Meta:
        unique_together = ['service', 'external_id', 'account']
        indexes = [
            models.Index(fields=['local_paper', 'service']),
            models.Index(fields=['service', 'external_id']),
            models.Index(fields=['sync_status']),
        ]
    
    def __str__(self):
        return f"{self.local_paper.title[:50]} -> {self.service}:{self.external_id}"


class ConflictResolution(models.Model):
    """Track how conflicts were resolved during sync."""
    
    CONFLICT_TYPE_CHOICES = [
        ('title', 'Title Mismatch'),
        ('authors', 'Authors Mismatch'),
        ('publication_date', 'Publication Date Mismatch'),
        ('abstract', 'Abstract Mismatch'),
        ('keywords', 'Keywords Mismatch'),
        ('notes', 'Notes Conflict'),
        ('tags', 'Tags Conflict'),
        ('pdf', 'PDF File Conflict'),
        ('metadata', 'Metadata Conflict'),
        ('deleted', 'Deletion Conflict'),
    ]
    
    RESOLUTION_CHOICES = [
        ('local_wins', 'Local Version Kept'),
        ('remote_wins', 'Remote Version Kept'),
        ('merged', 'Merged Both Versions'),
        ('manual', 'Manually Resolved'),
        ('skipped', 'Skipped/Ignored'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sync_session = models.ForeignKey(SyncSession, on_delete=models.CASCADE, related_name='conflicts')
    reference_mapping = models.ForeignKey(ReferenceMapping, on_delete=models.CASCADE, related_name='conflicts')
    
    # Conflict details
    conflict_type = models.CharField(max_length=30, choices=CONFLICT_TYPE_CHOICES)
    local_value = models.JSONField(help_text="Local version of the conflicted data")
    remote_value = models.JSONField(help_text="Remote version of the conflicted data")
    
    # Resolution
    resolution = models.CharField(max_length=20, choices=RESOLUTION_CHOICES, blank=True)
    resolved_value = models.JSONField(null=True, blank=True, help_text="Final resolved value")
    resolution_notes = models.TextField(blank=True, help_text="Notes about the resolution")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # User who resolved (if manual)
    resolved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    
    class Meta:
        indexes = [
            models.Index(fields=['sync_session', 'conflict_type']),
            models.Index(fields=['reference_mapping', '-created_at']),
        ]
    
    def __str__(self):
        return f"Conflict: {self.conflict_type} - {self.reference_mapping}"
    
    def is_resolved(self):
        """Check if the conflict has been resolved."""
        return self.resolution is not None and self.resolved_at is not None


class SyncLog(models.Model):
    """Detailed logging for sync operations."""
    
    LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    OPERATION_CHOICES = [
        ('auth', 'Authentication'),
        ('fetch', 'Fetch Data'),
        ('create', 'Create Item'),
        ('update', 'Update Item'),
        ('delete', 'Delete Item'),
        ('conflict', 'Conflict Resolution'),
        ('error', 'Error Handling'),
        ('cleanup', 'Cleanup'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sync_session = models.ForeignKey(SyncSession, on_delete=models.CASCADE, related_name='logs')
    
    # Log details
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    operation = models.CharField(max_length=20, choices=OPERATION_CHOICES)
    message = models.TextField()
    
    # Optional references
    reference_mapping = models.ForeignKey(ReferenceMapping, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Additional data
    extra_data = models.JSONField(default=dict, blank=True)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sync_session', '-created_at']),
            models.Index(fields=['level', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.level}: {self.operation} - {self.message[:100]}"


class SyncStatistics(models.Model):
    """Store aggregated sync statistics for reporting."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sync_statistics')
    
    # Time period
    date = models.DateField()
    
    # Counts
    sync_sessions = models.IntegerField(default=0)
    successful_syncs = models.IntegerField(default=0)
    failed_syncs = models.IntegerField(default=0)
    
    items_synced = models.IntegerField(default=0)
    items_created = models.IntegerField(default=0)
    items_updated = models.IntegerField(default=0)
    items_deleted = models.IntegerField(default=0)
    
    conflicts_found = models.IntegerField(default=0)
    conflicts_resolved = models.IntegerField(default=0)
    
    # Performance
    total_sync_time = models.DurationField(default=timezone.timedelta)
    api_calls_made = models.IntegerField(default=0)
    data_transferred_mb = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"Stats for {self.user.username} on {self.date}"


class WebhookEndpoint(models.Model):
    """Store webhook endpoints for real-time sync triggers."""
    
    SERVICE_CHOICES = [
        ('mendeley', 'Mendeley'),
        ('zotero', 'Zotero'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(ReferenceManagerAccount, on_delete=models.CASCADE, related_name='webhooks')
    
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    webhook_url = models.URLField(help_text="URL for the webhook endpoint")
    secret_key = models.CharField(max_length=100, help_text="Secret key for webhook verification")
    
    # Events to listen for (stored as JSON for SQLite compatibility)
    events = models.JSONField(
        default=list,
        help_text="List of events to trigger sync on"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['account', 'service']
        indexes = [
            models.Index(fields=['service', 'is_active']),
        ]
    
    def __str__(self):
        return f"Webhook for {self.account} - {self.service}"