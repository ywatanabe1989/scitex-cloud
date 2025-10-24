"""Collaboration models for writer_app."""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid


class CollaborativeSession(models.Model):
    """Track collaborative editing sessions for real-time collaboration."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manuscript = models.ForeignKey('Manuscript', on_delete=models.CASCADE, related_name='collaborative_sessions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='writing_sessions')

    # Session details
    session_id = models.CharField(max_length=100)  # WebSocket session identifier
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # Collaboration features
    locked_sections = models.JSONField(default=list, blank=True)  # List of section IDs locked by this user
    cursor_position = models.JSONField(default=dict, blank=True)  # Current cursor position

    # Statistics
    characters_typed = models.IntegerField(default=0)
    operations_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_activity']
        unique_together = ['manuscript', 'user', 'session_id']

    def __str__(self):
        return f"{self.user.username} - {self.manuscript.title[:30]} ({self.session_id[:8]})"

    @property
    def session_duration(self):
        """Calculate session duration."""
        end_time = self.ended_at or timezone.now()
        return end_time - self.started_at

    def is_session_active(self):
        """Check if session is still active (within 5 minutes of last activity)."""
        if not self.is_active:
            return False
        return timezone.now() - self.last_activity < timedelta(minutes=5)


class DocumentChange(models.Model):
    """Track individual document changes for version control and operational transforms."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manuscript = models.ForeignKey('Manuscript', on_delete=models.CASCADE, related_name='document_changes')
    section = models.ForeignKey('ManuscriptSection', on_delete=models.CASCADE, related_name='changes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_changes')
    session = models.ForeignKey('CollaborativeSession', on_delete=models.CASCADE, related_name='changes')

    # Change details
    change_type = models.CharField(max_length=20, choices=[
        ('insert', 'Text Insertion'),
        ('delete', 'Text Deletion'),
        ('replace', 'Text Replacement'),
        ('format', 'Formatting Change'),
    ])

    # Operation details for operational transforms
    operation_data = models.JSONField()  # Contains position, text, length, etc.

    # Content tracking
    content_before = models.TextField(blank=True)  # Content before change
    content_after = models.TextField(blank=True)   # Content after change

    # Version control
    version_number = models.IntegerField(default=1)
    parent_change = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    # Operational transform state
    transform_applied = models.BooleanField(default=False)
    conflict_resolved = models.BooleanField(default=False)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_change_type_display()} by {self.user.username} - {self.section.title}"
