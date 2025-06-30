from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Team, TeamMembership, TeamInvitation, SharedProject,
    Comment, Review, ActivityFeed, Notification, CollaborativeEdit
)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'team_type', 'owner', 'member_count', 'visibility', 'is_active', 'created_at']
    list_filter = ['team_type', 'visibility', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'owner__username', 'owner__email']
    filter_horizontal = ['admins', 'associated_projects']
    readonly_fields = ['id', 'created_at', 'updated_at', 'member_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'description', 'team_type', 'visibility')
        }),
        ('Leadership', {
            'fields': ('owner', 'admins')
        }),
        ('Settings', {
            'fields': ('allow_member_invites', 'require_approval', 'max_members', 'is_active')
        }),
        ('Integration', {
            'fields': ('research_group', 'associated_projects')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'member_count'),
            'classes': ('collapse',)
        })
    )
    
    def member_count(self, obj):
        return obj.get_member_count()
    member_count.short_description = 'Members'


class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 0
    fields = ['user', 'role', 'can_invite_members', 'can_create_projects', 'is_active']
    readonly_fields = ['joined_at']


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'team', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'can_create_projects', 'can_review_work']
    search_fields = ['user__username', 'user__email', 'team__name']
    readonly_fields = ['joined_at']
    
    fieldsets = (
        ('Membership', {
            'fields': ('team', 'user', 'role', 'is_active')
        }),
        ('Permissions', {
            'fields': ('can_invite_members', 'can_create_projects', 'can_manage_projects', 
                      'can_review_work', 'can_export_data')
        }),
        ('Details', {
            'fields': ('invited_by', 'joined_at')
        })
    )


@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'team', 'status', 'invited_by', 'created_at', 'expires_at']
    list_filter = ['status', 'role', 'created_at']
    search_fields = ['email', 'team__name', 'invited_by__username']
    readonly_fields = ['id', 'created_at', 'responded_at']
    
    fieldsets = (
        ('Invitation Details', {
            'fields': ('id', 'team', 'email', 'invited_user', 'invited_by')
        }),
        ('Role & Status', {
            'fields': ('role', 'status', 'message')
        }),
        ('Timing', {
            'fields': ('created_at', 'expires_at', 'responded_at')
        })
    )


@admin.register(SharedProject)
class SharedProjectAdmin(admin.ModelAdmin):
    list_display = ['project', 'team', 'sharing_type', 'shared_by', 'is_active', 'shared_at']
    list_filter = ['sharing_type', 'is_active', 'shared_at']
    search_fields = ['project__name', 'team__name', 'shared_by__username']
    readonly_fields = ['shared_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'comment_type', 'content_preview', 'is_public', 'is_resolved', 'created_at']
    list_filter = ['comment_type', 'is_public', 'is_resolved', 'created_at']
    search_fields = ['author__username', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'requested_by', 'review_type', 'status', 'decision', 'overall_score', 'requested_at']
    list_filter = ['review_type', 'status', 'decision', 'requested_at']
    search_fields = ['reviewer__username', 'requested_by__username']
    readonly_fields = ['requested_at', 'submitted_at', 'average_score']
    
    fieldsets = (
        ('Review Details', {
            'fields': ('reviewer', 'requested_by', 'review_type', 'status', 'decision')
        }),
        ('Content', {
            'fields': ('summary', 'detailed_feedback')
        }),
        ('Scores', {
            'fields': ('methodology_score', 'clarity_score', 'significance_score', 
                      'overall_score', 'average_score')
        }),
        ('Timing', {
            'fields': ('requested_at', 'deadline', 'submitted_at')
        })
    )
    
    def average_score(self, obj):
        avg = obj.get_average_score()
        return f"{avg:.1f}" if avg else "N/A"
    average_score.short_description = 'Average Score'


@admin.register(ActivityFeed)
class ActivityFeedAdmin(admin.ModelAdmin):
    list_display = ['actor', 'activity_type', 'team', 'description', 'is_public', 'created_at']
    list_filter = ['activity_type', 'is_public', 'created_at']
    search_fields = ['actor__username', 'description', 'team__name']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        return False  # Activity feeds are created automatically


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'priority', 'is_read', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'title', 'message']
    readonly_fields = ['created_at', 'read_at']
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        for notification in queryset:
            notification.mark_as_read()
        self.message_user(request, f"Marked {queryset.count()} notifications as read.")
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False, read_at=None)
        self.message_user(request, f"Marked {queryset.count()} notifications as unread.")
    mark_as_unread.short_description = "Mark selected notifications as unread"


@admin.register(CollaborativeEdit)
class CollaborativeEditAdmin(admin.ModelAdmin):
    list_display = ['user', 'edit_type', 'field_name', 'change_summary', 'is_minor', 'created_at']
    list_filter = ['edit_type', 'is_minor', 'created_at']
    search_fields = ['user__username', 'field_name', 'change_summary']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        return False  # Edits are tracked automatically