from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class ORCIDProfile(models.Model):
    """ORCID profile integration for researchers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='legacy_orcid_profile')
    
    # ORCID data
    orcid_id = models.CharField(max_length=19, unique=True, db_index=True)  # Format: 0000-0000-0000-0000
    access_token = models.TextField()  # OAuth2 access token
    refresh_token = models.TextField(blank=True)  # OAuth2 refresh token
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Profile data from ORCID
    given_name = models.CharField(max_length=100, blank=True)
    family_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    biography = models.TextField(blank=True)
    
    # Sync settings
    auto_sync_profile = models.BooleanField(default=True)
    auto_sync_works = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('manual', 'Manual Only'),
    ], default='weekly')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'integrations'
        indexes = [
            models.Index(fields=['orcid_id']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - ORCID: {self.orcid_id}"
    
    @property
    def full_name(self):
        """Get full name from ORCID data"""
        if self.given_name and self.family_name:
            return f"{self.given_name} {self.family_name}"
        return self.user.get_full_name() or self.user.username
    
    def is_token_expired(self):
        """Check if access token is expired"""
        if not self.token_expires_at:
            return False
        return timezone.now() >= self.token_expires_at


class ExternalServiceConnection(models.Model):
    """Generic model for external service integrations"""
    SERVICE_CHOICES = [
        ('orcid', 'ORCID'),
        ('google_scholar', 'Google Scholar'),
        ('researchgate', 'ResearchGate'),
        ('mendeley', 'Mendeley'),
        ('zotero', 'Zotero'),
        ('github', 'GitHub'),
        ('gitlab', 'GitLab'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Token Expired'),
        ('revoked', 'Access Revoked'),
        ('error', 'Connection Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='external_connections')
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    service_user_id = models.CharField(max_length=100, help_text="User ID on external service")
    service_username = models.CharField(max_length=100, blank=True)
    
    # OAuth credentials
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Connection status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_enabled = models.BooleanField(default=True)
    
    # Metadata
    connection_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'integrations'
        unique_together = ['user', 'service']
        indexes = [
            models.Index(fields=['user', 'service']),
            models.Index(fields=['service', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_service_display()}"
