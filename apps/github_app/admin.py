#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Integration Admin Configuration

Django admin interface for managing GitHub integration models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    GitHubOAuth2Token, GitHubProfile, GitHubRepository, 
    GitHubConnection, GitHubSyncLog, GitHubCollaborator
)


@admin.register(GitHubOAuth2Token)
class GitHubOAuth2TokenAdmin(admin.ModelAdmin):
    """Admin interface for GitHub OAuth2 tokens"""
    list_display = [
        'user', 'github_username', 'token_type', 'scope', 
        'created_at', 'is_token_old'
    ]
    list_filter = ['token_type', 'created_at']
    search_fields = ['user__username', 'github_username', 'scope']
    readonly_fields = ['access_token', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'github_username')
        }),
        ('Token Details', {
            'fields': ('access_token', 'token_type', 'scope'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_token_old(self, obj):
        """Display token age status"""
        if obj.is_expired():
            return format_html('<span style="color: red;">Old (>1 year)</span>')
        else:
            return format_html('<span style="color: green;">Valid</span>')
    is_token_old.short_description = 'Token Status'


@admin.register(GitHubProfile)
class GitHubProfileAdmin(admin.ModelAdmin):
    """Admin interface for GitHub profiles"""
    list_display = [
        'user', 'github_username', 'name', 'public_repos', 
        'followers', 'is_synced', 'last_sync_at'
    ]
    list_filter = [
        'is_synced', 'auto_sync_enabled', 'public_profile', 
        'show_repositories', 'last_sync_at'
    ]
    search_fields = [
        'user__username', 'github_username', 'name', 
        'email', 'company', 'location'
    ]
    readonly_fields = [
        'github_id', 'github_data', 'created_at', 
        'updated_at', 'github_profile_link'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'github_id', 'github_username', 'github_profile_link')
        }),
        ('Profile Details', {
            'fields': ('name', 'email', 'bio', 'blog', 'location', 'company')
        }),
        ('Statistics', {
            'fields': ('public_repos', 'public_gists', 'followers', 'following'),
            'classes': ('collapse',)
        }),
        ('Sync Settings', {
            'fields': (
                'is_synced', 'last_sync_at', 'sync_repositories', 
                'auto_sync_enabled'
            )
        }),
        ('Privacy Settings', {
            'fields': ('public_profile', 'show_repositories')
        }),
        ('Raw Data', {
            'fields': ('github_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def github_profile_link(self, obj):
        """Display clickable GitHub profile link"""
        if obj.github_username:
            url = obj.get_github_url()
            return format_html('<a href="{}" target="_blank">{}</a>', url, url)
        return '-'
    github_profile_link.short_description = 'GitHub Profile'


class GitHubCollaboratorInline(admin.TabularInline):
    """Inline admin for repository collaborators"""
    model = GitHubCollaborator
    extra = 0
    readonly_fields = ['github_id', 'github_username', 'scitex_user']
    fields = ['github_username', 'permission', 'scitex_user', 'can_sync']


class GitHubConnectionInline(admin.StackedInline):
    """Inline admin for repository connections"""
    model = GitHubConnection
    extra = 0
    readonly_fields = [
        'last_sync_at', 'last_sync_commit', 'total_syncs', 
        'successful_syncs', 'failed_syncs'
    ]
    
    fieldsets = (
        ('Connection Settings', {
            'fields': ('sync_direction', 'sync_status', 'auto_sync_enabled')
        }),
        ('Sync Configuration', {
            'fields': ('sync_branches', 'sync_files', 'ignore_patterns'),
            'classes': ('collapse',)
        }),
        ('Webhook Configuration', {
            'fields': ('webhook_url', 'webhook_secret', 'webhook_active'),
            'classes': ('collapse',)
        }),
        ('Sync Status', {
            'fields': (
                'last_sync_at', 'last_sync_commit', 'last_error',
                'total_syncs', 'successful_syncs', 'failed_syncs'
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(GitHubRepository)
class GitHubRepositoryAdmin(admin.ModelAdmin):
    """Admin interface for GitHub repositories"""
    list_display = [
        'name', 'profile', 'language', 'is_private', 
        'is_connected', 'stargazers_count', 'forks_count', 
        'github_updated_at'
    ]
    list_filter = [
        'is_private', 'is_fork', 'is_archived', 'is_disabled',
        'is_connected', 'language', 'github_created_at'
    ]
    search_fields = [
        'name', 'full_name', 'description', 'profile__github_username',
        'language'
    ]
    readonly_fields = [
        'github_id', 'github_data', 'github_created_at', 
        'github_updated_at', 'github_pushed_at', 'created_at', 
        'updated_at', 'github_repo_link'
    ]
    inlines = [GitHubCollaboratorInline, GitHubConnectionInline]
    
    fieldsets = (
        ('Repository Information', {
            'fields': (
                'profile', 'github_id', 'name', 'full_name', 
                'description', 'github_repo_link'
            )
        }),
        ('Repository Settings', {
            'fields': (
                'is_private', 'is_fork', 'is_archived', 'is_disabled',
                'default_branch', 'language', 'topics'
            )
        }),
        ('Statistics', {
            'fields': (
                'size', 'stargazers_count', 'watchers_count', 
                'forks_count', 'open_issues_count'
            ),
            'classes': ('collapse',)
        }),
        ('Clone URLs', {
            'fields': ('clone_url', 'ssh_url', 'git_url'),
            'classes': ('collapse',)
        }),
        ('Integration', {
            'fields': ('is_connected', 'code_project', 'auto_sync_enabled', 'sync_issues', 'sync_commits')
        }),
        ('GitHub Dates', {
            'fields': ('github_created_at', 'github_updated_at', 'github_pushed_at'),
            'classes': ('collapse',)
        }),
        ('Raw Data', {
            'fields': ('github_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def github_repo_link(self, obj):
        """Display clickable GitHub repository link"""
        if obj.full_name:
            url = obj.get_github_url()
            return format_html('<a href="{}" target="_blank">{}</a>', url, obj.full_name)
        return '-'
    github_repo_link.short_description = 'GitHub Repository'


@admin.register(GitHubConnection)
class GitHubConnectionAdmin(admin.ModelAdmin):
    """Admin interface for GitHub connections"""
    list_display = [
        'repository', 'sync_direction', 'sync_status', 
        'auto_sync_enabled', 'last_sync_at', 'success_rate'
    ]
    list_filter = [
        'sync_direction', 'sync_status', 'auto_sync_enabled',
        'webhook_active', 'last_sync_at'
    ]
    search_fields = [
        'repository__name', 'repository__full_name',
        'repository__profile__github_username'
    ]
    readonly_fields = [
        'last_sync_at', 'last_sync_commit', 'total_syncs',
        'successful_syncs', 'failed_syncs', 'created_at', 
        'updated_at', 'success_rate'
    ]
    
    fieldsets = (
        ('Repository', {
            'fields': ('repository',)
        }),
        ('Connection Settings', {
            'fields': ('sync_direction', 'sync_status', 'auto_sync_enabled')
        }),
        ('Sync Configuration', {
            'fields': ('sync_branches', 'sync_files', 'ignore_patterns')
        }),
        ('Webhook Configuration', {
            'fields': ('webhook_url', 'webhook_secret', 'webhook_active')
        }),
        ('Sync Status', {
            'fields': (
                'last_sync_at', 'last_sync_commit', 'last_error',
                'total_syncs', 'successful_syncs', 'failed_syncs', 'success_rate'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def success_rate(self, obj):
        """Display sync success rate"""
        rate = obj.get_sync_success_rate()
        if rate >= 90:
            color = 'green'
        elif rate >= 70:
            color = 'orange'
        else:
            color = 'red'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, rate)
    success_rate.short_description = 'Success Rate'


@admin.register(GitHubSyncLog)
class GitHubSyncLogAdmin(admin.ModelAdmin):
    """Admin interface for GitHub sync logs"""
    list_display = [
        'profile', 'repository', 'sync_type', 'status',
        'items_processed', 'started_at', 'duration_display'
    ]
    list_filter = [
        'sync_type', 'status', 'started_at',
        'profile__github_username'
    ]
    search_fields = [
        'profile__github_username', 'repository__name',
        'error_message'
    ]
    readonly_fields = [
        'started_at', 'completed_at', 'duration_seconds',
        'duration_display'
    ]
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Sync Information', {
            'fields': ('profile', 'repository', 'sync_type', 'status')
        }),
        ('Results', {
            'fields': (
                'items_processed', 'items_created', 'items_updated',
                'items_deleted', 'items_skipped'
            )
        }),
        ('Code Sync Details', {
            'fields': ('commits_synced', 'files_synced', 'sync_details'),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': ('error_message', 'error_details'),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'duration_seconds', 'duration_display'),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        """Display human-readable duration"""
        return obj.get_duration_display()
    duration_display.short_description = 'Duration'


@admin.register(GitHubCollaborator)
class GitHubCollaboratorAdmin(admin.ModelAdmin):
    """Admin interface for GitHub collaborators"""
    list_display = [
        'github_username', 'repository', 'permission',
        'scitex_user', 'can_sync', 'notifications_enabled'
    ]
    list_filter = [
        'permission', 'can_sync', 'notifications_enabled',
        'repository__profile__github_username'
    ]
    search_fields = [
        'github_username', 'repository__name',
        'repository__full_name', 'scitex_user__username'
    ]
    readonly_fields = ['github_id', 'created_at', 'updated_at', 'github_profile_link']
    
    fieldsets = (
        ('Collaborator Information', {
            'fields': ('repository', 'github_id', 'github_username', 'github_profile_link')
        }),
        ('Permissions', {
            'fields': ('permission', 'can_sync')
        }),
        ('SciTeX Integration', {
            'fields': ('scitex_user', 'notifications_enabled')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def github_profile_link(self, obj):
        """Display clickable GitHub profile link"""
        if obj.github_username:
            url = obj.get_github_url()
            return format_html('<a href="{}" target="_blank">{}</a>', url, obj.github_username)
        return '-'
    github_profile_link.short_description = 'GitHub Profile'


# Admin site customization
admin.site.site_header = 'SciTeX Cloud Administration'
admin.site.site_title = 'SciTeX Cloud Admin'
admin.site.index_title = 'Welcome to SciTeX Cloud Administration'