from django.contrib import admin
from .models import Project, ProjectMembership, Organization, ResearchGroup, ProjectPermission


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)


@admin.register(ResearchGroup)
class ResearchGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'leader', 'created_at')
    search_fields = ('name', 'description', 'organization__name')
    list_filter = ('organization', 'created_at')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'progress', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'owner__username')
    list_filter = ('created_at', 'updated_at', 'organization')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'owner', 'progress')
        }),
        ('Organization', {
            'fields': ('organization', 'research_group'),
            'classes': ('collapse',)
        }),
        ('Research Data', {
            'fields': ('hypotheses', 'source_code_url', 'data_location', 'manuscript_draft'),
            'classes': ('collapse',)
        }),
        ('GitHub Integration', {
            'fields': ('github_integration_enabled', 'github_repo_name', 'github_owner', 'current_branch'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'role', 'permission_level', 'joined_at')
    search_fields = ('project__name', 'user__username')
    list_filter = ('role', 'permission_level', 'joined_at')


@admin.register(ProjectPermission)
class ProjectPermissionAdmin(admin.ModelAdmin):
    list_display = ('membership', 'resource_type', 'permission_level')
    search_fields = ('membership__project__name', 'membership__user__username')
    list_filter = ('resource_type', 'permission_level')
