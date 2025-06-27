"""
SciTeX Cloud - Admin Interface

Administrative interface for managing users, projects, research groups,
and collaboration permissions.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    UserProfile, Organization, OrganizationMembership,
    ResearchGroup, ResearchGroupMembership,
    Project, ProjectMembership, Document, GitFileStatus
)


# Inline admin classes
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'bio', 'institution', 'academic_title', 'department', 'research_interests',
        'orcid', 'website', 'google_scholar', 'linkedin', 'researchgate', 'twitter',
        'profile_visibility', 'is_public', 'show_email', 'allow_collaboration', 'allow_messages',
        'is_academic_ja', 'deletion_scheduled_at'
    )
    readonly_fields = ('is_academic_ja',)


class OrganizationMembershipInline(admin.TabularInline):
    model = OrganizationMembership
    extra = 0
    fields = ('organization', 'role', 'joined_at')
    readonly_fields = ('joined_at',)


class ResearchGroupMembershipInline(admin.TabularInline):
    model = ResearchGroupMembership
    extra = 0
    fields = ('group', 'role', 'can_create_projects', 'can_invite_collaborators', 'joined_at', 'is_active')
    readonly_fields = ('joined_at',)


class ProjectMembershipInlineForUser(admin.TabularInline):
    model = ProjectMembership
    fk_name = 'user'  # For User admin - show projects this user is a member of
    extra = 0
    fields = (
        'project', 'role', 'can_read_files', 'can_write_files', 'can_delete_files',
        'can_manage_collaborators', 'access_expires_at', 'is_active'
    )
    readonly_fields = ('created_at',)


class ProjectMembershipInlineForProject(admin.TabularInline):
    model = ProjectMembership
    fk_name = 'project'  # For Project admin - show users who are members of this project
    extra = 0
    fields = (
        'user', 'role', 'can_read_files', 'can_write_files', 'can_delete_files',
        'can_manage_collaborators', 'access_expires_at', 'is_active'
    )
    readonly_fields = ('created_at',)


# Extended User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, OrganizationMembershipInline, ResearchGroupMembershipInline, ProjectMembershipInlineForUser)
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_academic_ja', 'total_projects', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'profile__is_academic_ja')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'profile__institution')
    
    def is_academic_ja(self, obj):
        """Show Japanese academic status"""
        try:
            return obj.profile.is_academic_ja
        except UserProfile.DoesNotExist:
            return False
    is_academic_ja.boolean = True
    is_academic_ja.short_description = 'Japanese Academic'
    
    def total_projects(self, obj):
        """Show total projects owned"""
        return obj.owned_projects.count()
    total_projects.short_description = 'Projects'


# User Profile admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'academic_title', 'profile_visibility', 'is_academic_ja', 'total_documents', 'total_projects')
    list_filter = ('profile_visibility', 'is_academic_ja', 'allow_collaboration', 'allow_messages', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'institution', 'academic_title')
    readonly_fields = ('is_academic_ja', 'created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'bio', 'institution', 'academic_title', 'department', 'research_interests')
        }),
        ('Academic Identity', {
            'fields': ('orcid', 'is_academic_ja')
        }),
        ('Online Presence', {
            'fields': ('website', 'google_scholar', 'linkedin', 'researchgate', 'twitter'),
            'classes': ('collapse',)
        }),
        ('Privacy Settings', {
            'fields': ('profile_visibility', 'is_public', 'show_email', 'allow_collaboration', 'allow_messages')
        }),
        ('Account Management', {
            'fields': ('deletion_scheduled_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Organization admin
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_members', 'total_groups', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    inlines = (OrganizationMembershipInline,)
    
    def total_members(self, obj):
        return obj.members.count()
    total_members.short_description = 'Members'
    
    def total_groups(self, obj):
        return obj.research_groups.count()
    total_groups.short_description = 'Research Groups'


# Research Group admin  
@admin.register(ResearchGroup)
class ResearchGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'principal_investigator', 'total_members', 'total_projects', 'is_public', 'created_at')
    list_filter = ('organization', 'is_public', 'allow_external_collaborators', 'created_at')
    search_fields = ('name', 'description', 'principal_investigator__username', 'principal_investigator__first_name', 'principal_investigator__last_name')
    filter_horizontal = ('admins',)
    inlines = (ResearchGroupMembershipInline,)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'organization')
        }),
        ('Leadership', {
            'fields': ('principal_investigator', 'admins')
        }),
        ('Settings', {
            'fields': ('is_public', 'allow_external_collaborators', 'auto_approve_internal')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def total_members(self, obj):
        return obj.get_all_members().count()
    total_members.short_description = 'Total Members'
    
    def total_projects(self, obj):
        return obj.projects.count()
    total_projects.short_description = 'Projects'


# Research Group Membership admin
@admin.register(ResearchGroupMembership)
class ResearchGroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'can_create_projects', 'can_invite_collaborators', 'joined_at', 'is_active')
    list_filter = ('role', 'can_create_projects', 'can_invite_collaborators', 'is_active', 'joined_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'group__name')
    list_editable = ('role', 'can_create_projects', 'can_invite_collaborators', 'is_active')


# Project admin
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'research_group', 'status', 'progress_display', 'total_collaborators', 'storage_usage_mb', 'github_status', 'updated_at')
    list_filter = ('status', 'organization', 'research_group', 'github_integration_enabled', 'directory_created', 'created_at')
    search_fields = ('name', 'description', 'owner__username', 'owner__first_name', 'owner__last_name')
    filter_horizontal = ()  # Remove since we use through model
    inlines = (ProjectMembershipInlineForProject,)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'owner', 'organization', 'research_group')
        }),
        ('Project Status', {
            'fields': ('status', 'progress', 'deadline')
        }),
        ('Research Data', {
            'fields': ('hypotheses', 'manuscript_draft'),
            'classes': ('collapse',)
        }),
        ('Directory Management', {
            'fields': ('data_location', 'directory_created', 'storage_used', 'last_activity'),
            'classes': ('collapse',)
        }),
        ('GitHub Integration', {
            'fields': ('github_integration_enabled', 'github_repo_name', 'github_owner', 'current_branch', 'last_sync_at'),
            'classes': ('collapse',)
        }),
        ('SciTeX Workflow Status', {
            'fields': ('search_completed', 'knowledge_gap_identified', 'analysis_completed', 'figures_generated', 'manuscript_generated'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_activity', 'storage_used')
    
    def progress_display(self, obj):
        """Display progress as a colored bar"""
        progress = obj.get_progress_percentage()
        if progress < 30:
            color = '#dc3545'  # Red
        elif progress < 70:
            color = '#ffc107'  # Yellow
        else:
            color = '#28a745'  # Green
        
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 3px;">'
            '<div style="width: {}px; background-color: {}; height: 18px; border-radius: 3px; text-align: center; color: white; font-size: 12px; line-height: 18px;">'
            '{}%</div></div>',
            progress, color, progress
        )
    progress_display.short_description = 'Progress'
    
    def total_collaborators(self, obj):
        return obj.get_all_collaborators().count() - 1  # Exclude owner
    total_collaborators.short_description = 'Collaborators'
    
    def storage_usage_mb(self, obj):
        return f"{obj.get_storage_usage_mb()} MB"
    storage_usage_mb.short_description = 'Storage Used'
    
    def github_status(self, obj):
        status = obj.get_github_status_complete()
        colors = {
            'connected': '#28a745',
            'disconnected': '#6c757d', 
            'auth_required': '#ffc107',
            'repo_required': '#dc3545'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(status, '#6c757d'),
            status.replace('_', ' ').title()
        )
    github_status.short_description = 'GitHub'


# Project Membership admin
@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role', 'permissions_summary', 'access_expires_at', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'can_read_files', 'can_write_files', 'can_delete_files', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'project__name')
    list_editable = ('role', 'is_active')
    
    fieldsets = (
        ('Membership', {
            'fields': ('user', 'project', 'role', 'is_active')
        }),
        ('File Permissions', {
            'fields': ('can_read_files', 'can_write_files', 'can_delete_files')
        }),
        ('Project Permissions', {
            'fields': ('can_manage_collaborators', 'can_edit_metadata', 'can_run_analysis', 'can_export_data', 'can_view_results')
        }),
        ('Administrative Permissions', {
            'fields': ('can_change_settings', 'can_archive_project'),
            'classes': ('collapse',)
        }),
        ('Access Control', {
            'fields': ('access_expires_at', 'access_granted_by'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def permissions_summary(self, obj):
        """Show a summary of key permissions"""
        perms = []
        if obj.can_read_files:
            perms.append('Read')
        if obj.can_write_files:
            perms.append('Write')
        if obj.can_delete_files:
            perms.append('Delete')
        if obj.can_manage_collaborators:
            perms.append('Manage')
        
        return ', '.join(perms) if perms else 'No permissions'
    permissions_summary.short_description = 'Key Permissions'


# Document admin
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'owner', 'project', 'file_size_mb', 'has_file_display', 'updated_at')
    list_filter = ('document_type', 'is_public', 'created_at')
    search_fields = ('title', 'content', 'owner__username', 'project__name', 'tags')
    
    fieldsets = (
        ('Document Information', {
            'fields': ('title', 'document_type', 'content', 'tags')
        }),
        ('Ownership', {
            'fields': ('owner', 'project', 'is_public')
        }),
        ('File Management', {
            'fields': ('file_location', 'file_size', 'file_hash'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'file_size', 'file_hash')
    
    def file_size_mb(self, obj):
        if obj.file_size:
            return f"{obj.file_size / (1024*1024):.2f} MB"
        return "No file"
    file_size_mb.short_description = 'File Size'
    
    def has_file_display(self, obj):
        if obj.has_file():
            return format_html('<span style="color: green;"></span>')
        return format_html('<span style="color: red;"></span>')
    has_file_display.short_description = 'Has File'
    has_file_display.boolean = True


# Git File Status admin
@admin.register(GitFileStatus)
class GitFileStatusAdmin(admin.ModelAdmin):
    list_display = ('project', 'file_path', 'git_status', 'last_modified_at', 'file_size', 'is_binary')
    list_filter = ('git_status', 'is_binary', 'last_modified_at')
    search_fields = ('project__name', 'file_path', 'last_commit_hash')
    readonly_fields = ('last_modified_at',)


# Re-register User with custom admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Customize admin site
admin.site.site_header = "SciTeX Cloud Administration"
admin.site.site_title = "SciTeX Admin"
admin.site.index_title = "Welcome to SciTeX Cloud Administration"