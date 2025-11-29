"""
RepositoryConnection model - User credentials for repository access.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class RepositoryConnection(models.Model):
    """User's connection credentials to research data repositories"""

    CONNECTION_STATUS = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("invalid", "Invalid"),
        ("suspended", "Suspended"),
        ("pending", "Pending Verification"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="repository_connections"
    )
    repository = models.ForeignKey(
        "scholar_app.Repository", on_delete=models.CASCADE, related_name="user_connections"
    )

    # Authentication credentials (encrypted)
    api_token = models.CharField(max_length=500, blank=True)
    api_secret = models.CharField(max_length=500, blank=True)
    oauth_token = models.CharField(max_length=500, blank=True)
    oauth_refresh_token = models.CharField(max_length=500, blank=True)
    username = models.CharField(max_length=200, blank=True)

    # Connection metadata
    connection_name = models.CharField(
        max_length=200, help_text="User-defined name for this connection"
    )
    status = models.CharField(
        max_length=20, choices=CONNECTION_STATUS, default="pending"
    )
    last_verified = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # User preferences
    is_default = models.BooleanField(default=False)
    auto_sync_enabled = models.BooleanField(default=True)
    notification_enabled = models.BooleanField(default=True)

    # Usage tracking
    total_deposits = models.IntegerField(default=0)
    total_downloads = models.IntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)

    # Error tracking
    last_error = models.TextField(blank=True)
    error_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["user", "repository", "connection_name"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["repository", "status"]),
        ]

    def __str__(self):
        return (
            f"{self.user.username} -> {self.repository.name} ({self.connection_name})"
        )

    def is_active(self):
        """Check if connection is active and not expired"""
        if self.status != "active":
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True
