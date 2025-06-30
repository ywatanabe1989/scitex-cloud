#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Integration Models

This module provides models for GitHub OAuth2 authentication, repository management,
code synchronization, and collaboration features.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid
import json


class GitHubOAuth2Token(models.Model):
    """Store GitHub OAuth2 tokens for authenticated users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='github_token')
    access_token = models.CharField(max_length=255, help_text="GitHub access token")
    token_type = models.CharField(max_length=50, default='bearer')
    scope = models.CharField(max_length=255, help_text="OAuth scope granted")
    github_username = models.CharField(max_length=100, help_text="GitHub username")
    
    # GitHub tokens don't expire by default, but we track creation for security
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "GitHub OAuth2 Token"
        verbose_name_plural = "GitHub OAuth2 Tokens"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['github_username']),
        ]
    
    def __str__(self):
        return f"GitHub Token for {self.user.username} ({self.github_username})"
    
    def is_expired(self):
        """GitHub tokens don't expire, but check if token is too old (1 year)"""
        return timezone.now() - self.created_at > timedelta(days=365)
    
    def get_authorization_header(self):
        """Get formatted authorization header"""
        return f"Bearer {self.access_token}"


class GitHubProfile(models.Model):
    """GitHub profile information for users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='github_profile')
    
    # GitHub profile information
    github_id = models.BigIntegerField(unique=True, help_text="GitHub user ID")
    github_username = models.CharField(max_length=100, unique=True, help_text="GitHub username")
    name = models.CharField(max_length=255, blank=True, help_text="Full name")
    email = models.EmailField(blank=True, help_text="Public email")
    bio = models.TextField(blank=True, help_text="Profile bio")
    blog = models.URLField(blank=True, help_text="Website/blog URL")
    location = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    
    # GitHub statistics
    public_repos = models.IntegerField(default=0, help_text="Number of public repositories")
    public_gists = models.IntegerField(default=0, help_text="Number of public gists")
    followers = models.IntegerField(default=0, help_text="Number of followers")
    following = models.IntegerField(default=0, help_text="Number of following")
    
    # Sync settings
    is_synced = models.BooleanField(default=False, help_text="Profile has been synced with GitHub")
    last_sync_at = models.DateTimeField(null=True, blank=True)
    sync_repositories = models.BooleanField(default=True, help_text="Auto-sync repositories from GitHub")
    auto_sync_enabled = models.BooleanField(default=True, help_text="Enable automatic periodic sync")
    
    # Privacy settings
    public_profile = models.BooleanField(default=True, help_text="Make GitHub profile visible to other users")
    show_repositories = models.BooleanField(default=True, help_text="Show GitHub repositories in Code module")
    
    # Metadata
    github_data = models.JSONField(default=dict, blank=True, help_text="Raw GitHub profile data")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "GitHub Profile"
        verbose_name_plural = "GitHub Profiles"
        ordering = ['github_username']
        indexes = [
            models.Index(fields=['github_id']),
            models.Index(fields=['github_username']),
            models.Index(fields=['user']),
            models.Index(fields=['last_sync_at']),
        ]
    
    def __str__(self):
        return f"{self.github_username} ({self.name or 'No name'})"
    
    def get_display_name(self):
        """Get the best display name for this profile"""
        return self.name or self.github_username
    
    def get_github_url(self):
        """Get the GitHub profile URL"""
        return f"https://github.com/{self.github_username}"
    
    def needs_sync(self, hours=24):
        """Check if profile needs syncing (hasn't been synced in X hours)"""
        if not self.last_sync_at:
            return True
        return timezone.now() - self.last_sync_at > timedelta(hours=hours)
    
    def get_repository_count(self):
        """Get the count of synced repositories"""
        return self.github_repositories.count()
    
    def get_recent_repositories(self, limit=5):
        """Get recent GitHub repositories"""
        return self.github_repositories.order_by('-updated_at')[:limit]


class GitHubRepository(models.Model):
    """GitHub repositories associated with user profiles"""
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('internal', 'Internal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(GitHubProfile, on_delete=models.CASCADE, related_name='github_repositories')
    
    # Repository information
    github_id = models.BigIntegerField(help_text="GitHub repository ID")
    name = models.CharField(max_length=255, help_text="Repository name")
    full_name = models.CharField(max_length=255, help_text="Full repository name (owner/repo)")
    description = models.TextField(blank=True, help_text="Repository description")
    
    # Repository settings
    is_private = models.BooleanField(default=False, help_text="Repository is private")
    is_fork = models.BooleanField(default=False, help_text="Repository is a fork")
    is_archived = models.BooleanField(default=False, help_text="Repository is archived")
    is_disabled = models.BooleanField(default=False, help_text="Repository is disabled")
    
    # Repository metadata
    default_branch = models.CharField(max_length=100, default='main', help_text="Default branch name")
    language = models.CharField(max_length=50, blank=True, help_text="Primary language")
    topics = models.JSONField(default=list, blank=True, help_text="Repository topics/tags")
    
    # Repository statistics
    size = models.IntegerField(default=0, help_text="Repository size in KB")
    stargazers_count = models.IntegerField(default=0, help_text="Number of stars")
    watchers_count = models.IntegerField(default=0, help_text="Number of watchers")
    forks_count = models.IntegerField(default=0, help_text="Number of forks")
    open_issues_count = models.IntegerField(default=0, help_text="Number of open issues")
    
    # URLs
    clone_url = models.URLField(help_text="HTTPS clone URL")
    ssh_url = models.CharField(max_length=255, help_text="SSH clone URL")
    git_url = models.URLField(help_text="Git protocol URL")
    
    # Dates
    github_created_at = models.DateTimeField(help_text="Repository creation date on GitHub")
    github_updated_at = models.DateTimeField(help_text="Last update on GitHub")
    github_pushed_at = models.DateTimeField(null=True, blank=True, help_text="Last push to GitHub")
    
    # Integration with Code module - link to notebook instead since CodeProject doesn't exist
    is_connected = models.BooleanField(default=False, help_text="Connected to Code module")
    linked_notebook = models.ForeignKey(
        'code_app.Notebook', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='github_repositories',
        help_text="Linked Code notebook"
    )
    
    # Sync settings
    auto_sync_enabled = models.BooleanField(default=True, help_text="Enable automatic sync")
    sync_issues = models.BooleanField(default=False, help_text="Sync issues and pull requests")
    sync_commits = models.BooleanField(default=True, help_text="Sync commit history")
    
    # Raw data
    github_data = models.JSONField(default=dict, blank=True, help_text="Raw GitHub repository data")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "GitHub Repository"
        verbose_name_plural = "GitHub Repositories"
        ordering = ['-github_updated_at', 'name']
        unique_together = ['profile', 'github_id']
        indexes = [
            models.Index(fields=['profile', '-github_updated_at']),
            models.Index(fields=['github_id']),
            models.Index(fields=['full_name']),
            models.Index(fields=['language']),
            models.Index(fields=['is_private']),
            models.Index(fields=['is_connected']),
        ]
    
    def __str__(self):
        return f"{self.full_name}"
    
    def get_github_url(self):
        """Get the GitHub repository URL"""
        return f"https://github.com/{self.full_name}"
    
    def get_visibility_display(self):
        """Get human-readable visibility status"""
        return "Private" if self.is_private else "Public"
    
    def can_connect_to_code(self):
        """Check if repository can be connected to Code module"""
        return not self.is_connected and not self.is_archived and not self.is_disabled
    
    def get_primary_language(self):
        """Get primary programming language"""
        return self.language or "Unknown"
    
    def is_recently_active(self, days=30):
        """Check if repository has been active recently"""
        if not self.github_pushed_at:
            return False
        return timezone.now() - self.github_pushed_at <= timedelta(days=days)


class GitHubConnection(models.Model):
    """Connections between GitHub repositories and SciTeX Code projects"""
    
    SYNC_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('syncing', 'Syncing'),
        ('synced', 'Synced'),
        ('error', 'Error'),
        ('paused', 'Paused'),
    ]
    
    SYNC_DIRECTION_CHOICES = [
        ('github_to_code', 'GitHub → Code'),
        ('code_to_github', 'Code → GitHub'),
        ('bidirectional', 'Bidirectional'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    repository = models.OneToOneField(GitHubRepository, on_delete=models.CASCADE, related_name='connection')
    
    # Connection settings
    sync_direction = models.CharField(max_length=20, choices=SYNC_DIRECTION_CHOICES, default='bidirectional')
    sync_status = models.CharField(max_length=20, choices=SYNC_STATUS_CHOICES, default='pending')
    auto_sync_enabled = models.BooleanField(default=True, help_text="Enable automatic synchronization")
    
    # Sync configuration
    sync_branches = models.JSONField(default=list, blank=True, help_text="Branches to sync")
    sync_files = models.JSONField(default=list, blank=True, help_text="File patterns to sync")
    ignore_patterns = models.JSONField(default=list, blank=True, help_text="Patterns to ignore during sync")
    
    # Webhook configuration
    webhook_url = models.URLField(blank=True, help_text="GitHub webhook URL")
    webhook_secret = models.CharField(max_length=255, blank=True, help_text="Webhook secret for verification")
    webhook_active = models.BooleanField(default=False, help_text="Webhook is active")
    
    # Sync metadata
    last_sync_at = models.DateTimeField(null=True, blank=True, help_text="Last successful sync")
    last_sync_commit = models.CharField(max_length=40, blank=True, help_text="Last synced commit SHA")
    last_error = models.TextField(blank=True, help_text="Last sync error message")
    
    # Statistics
    total_syncs = models.IntegerField(default=0, help_text="Total number of syncs performed")
    successful_syncs = models.IntegerField(default=0, help_text="Number of successful syncs")
    failed_syncs = models.IntegerField(default=0, help_text="Number of failed syncs")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "GitHub Connection"
        verbose_name_plural = "GitHub Connections"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['repository']),
            models.Index(fields=['sync_status']),
            models.Index(fields=['last_sync_at']),
            models.Index(fields=['auto_sync_enabled']),
        ]
    
    def __str__(self):
        return f"Connection: {self.repository.full_name} → {self.sync_direction}"
    
    def get_sync_success_rate(self):
        """Calculate sync success rate as percentage"""
        if self.total_syncs == 0:
            return 0.0
        return (self.successful_syncs / self.total_syncs) * 100
    
    def is_healthy(self):
        """Check if connection is healthy (recent successful sync)"""
        if not self.last_sync_at:
            return False
        return (
            self.sync_status == 'synced' and 
            timezone.now() - self.last_sync_at <= timedelta(hours=24)
        )
    
    def needs_sync(self, hours=1):
        """Check if connection needs syncing"""
        if not self.last_sync_at:
            return True
        return timezone.now() - self.last_sync_at > timedelta(hours=hours)


class GitHubSyncLog(models.Model):
    """Log GitHub synchronization activities"""
    
    SYNC_TYPES = [
        ('profile', 'Profile Sync'),
        ('repositories', 'Repositories Sync'),
        ('repository', 'Single Repository Sync'),
        ('code_sync', 'Code Synchronization'),
        ('webhook', 'Webhook Event'),
        ('full', 'Full Sync'),
    ]
    
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(GitHubProfile, on_delete=models.CASCADE, related_name='sync_logs')
    repository = models.ForeignKey(GitHubRepository, on_delete=models.CASCADE, null=True, blank=True, related_name='sync_logs')
    
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    
    # Sync results
    items_processed = models.IntegerField(default=0)
    items_created = models.IntegerField(default=0)
    items_updated = models.IntegerField(default=0)
    items_deleted = models.IntegerField(default=0)
    items_skipped = models.IntegerField(default=0)
    
    # Sync details
    sync_details = models.JSONField(default=dict, blank=True, help_text="Detailed sync information")
    commits_synced = models.IntegerField(default=0, help_text="Number of commits synced")
    files_synced = models.IntegerField(default=0, help_text="Number of files synced")
    
    # Error information
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    class Meta:
        verbose_name = "GitHub Sync Log"
        verbose_name_plural = "GitHub Sync Logs"
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['profile', '-started_at']),
            models.Index(fields=['repository', '-started_at']),
            models.Index(fields=['status']),
            models.Index(fields=['sync_type']),
        ]
    
    def __str__(self):
        repo_name = f" - {self.repository.name}" if self.repository else ""
        return f"{self.sync_type} sync for {self.profile.github_username}{repo_name} - {self.status}"
    
    def mark_completed(self, status='success'):
        """Mark sync as completed with status"""
        self.completed_at = timezone.now()
        self.status = status
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.save()
    
    def add_error(self, message, details=None):
        """Add error information to the sync log"""
        self.error_message = message
        if details:
            self.error_details = details
        self.status = 'failed'
        self.save()
    
    def get_success_rate(self):
        """Calculate success rate for this sync"""
        if self.items_processed == 0:
            return 0.0
        return (self.items_created + self.items_updated) / self.items_processed * 100
    
    def get_duration_display(self):
        """Get human-readable duration"""
        if not self.duration_seconds:
            return "Unknown"
        
        if self.duration_seconds < 60:
            return f"{self.duration_seconds:.1f} seconds"
        elif self.duration_seconds < 3600:
            minutes = self.duration_seconds / 60
            return f"{minutes:.1f} minutes"
        else:
            hours = self.duration_seconds / 3600
            return f"{hours:.1f} hours"


class GitHubCollaborator(models.Model):
    """GitHub repository collaborators"""
    
    PERMISSION_CHOICES = [
        ('read', 'Read'),
        ('triage', 'Triage'),
        ('write', 'Write'),
        ('maintain', 'Maintain'),
        ('admin', 'Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    repository = models.ForeignKey(GitHubRepository, on_delete=models.CASCADE, related_name='collaborators')
    
    # Collaborator information
    github_id = models.BigIntegerField(help_text="GitHub user ID")
    github_username = models.CharField(max_length=100, help_text="GitHub username")
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES, help_text="Permission level")
    
    # SciTeX user connection
    scitex_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='github_collaborations',
        help_text="Connected SciTeX user"
    )
    
    # Collaboration settings
    can_sync = models.BooleanField(default=False, help_text="Can sync repository to Code module")
    notifications_enabled = models.BooleanField(default=True, help_text="Receive collaboration notifications")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "GitHub Collaborator"
        verbose_name_plural = "GitHub Collaborators"
        ordering = ['github_username']
        unique_together = ['repository', 'github_id']
        indexes = [
            models.Index(fields=['repository', 'permission']),
            models.Index(fields=['github_username']),
            models.Index(fields=['scitex_user']),
        ]
    
    def __str__(self):
        return f"{self.github_username} ({self.permission}) - {self.repository.name}"
    
    def get_github_url(self):
        """Get GitHub profile URL"""
        return f"https://github.com/{self.github_username}"
    
    def can_write(self):
        """Check if collaborator has write permission or higher"""
        return self.permission in ['write', 'maintain', 'admin']
    
    def can_admin(self):
        """Check if collaborator has admin permission"""
        return self.permission == 'admin'