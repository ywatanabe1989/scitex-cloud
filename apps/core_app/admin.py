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

# ProjectMembership now managed in project_app
# UserProfile now managed in profile_app
from apps.profile_app.models import UserProfile
# Organization models now managed in organizations_app
from apps.organizations_app.models import (
    Organization, OrganizationMembership,
    ResearchGroup, ResearchGroupMembership,
)
# Git models now managed in gitea_app
from apps.gitea_app.models import GitFileStatus


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


# ProjectMembershipInline classes moved to apps.project_app.admin

# Extended User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, OrganizationMembershipInline, ResearchGroupMembershipInline)
    
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
        return obj.project_app_owned_projects.count()
    total_projects.short_description = 'Projects'


# UserProfile admin moved to apps.profile_app.admin
# Organization and ResearchGroup admin moved to apps.organizations_app.admin
# Project admin moved to apps.project_app.admin
# ProjectMembership admin moved to apps.project_app.admin
# Git File Status admin moved to apps.gitea_app.admin


# Re-register User with custom admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Customize admin site
admin.site.site_header = "SciTeX Cloud Administration"
admin.site.site_title = "SciTeX Admin"
admin.site.index_title = "Welcome to SciTeX Cloud Administration"