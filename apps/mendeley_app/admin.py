from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    MendeleyOAuth2Token, MendeleyProfile, MendeleyDocument, 
    MendeleyGroup, MendeleyFolder, MendeleySyncLog
)


@admin.register(MendeleyOAuth2Token)
class MendeleyOAuth2TokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_type', 'scope', 'expires_at', 'is_expired_display', 'created_at']
    list_filter = ['token_type', 'expires_at', 'created_at']
    search_fields = ['user__username', 'user__email', 'scope']
    readonly_fields = ['created_at', 'updated_at', 'is_expired_display']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'access_token', 'refresh_token', 'token_type', 'scope')
        }),
        ('Expiration', {
            'fields': ('expires_at', 'is_expired_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_expired_display(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">Expired</span>')
        elif obj.is_expiring_soon():
            return format_html('<span style="color: orange;">Expiring Soon</span>')
        else:
            return format_html('<span style="color: green;">Valid</span>')
    is_expired_display.short_description = 'Token Status'


@admin.register(MendeleyProfile)
class MendeleyProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'get_display_name', 'mendeley_id', 'is_synced', 
        'last_sync_at', 'document_count', 'created_at'
    ]
    list_filter = [
        'is_synced', 'auto_sync_enabled', 'sync_documents', 
        'public_profile', 'academic_status', 'last_sync_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'mendeley_id', 
        'first_name', 'last_name', 'display_name', 'email'
    ]
    readonly_fields = ['mendeley_id', 'created_at', 'updated_at', 'document_count']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'mendeley_id')
        }),
        ('Profile Information', {
            'fields': ('first_name', 'last_name', 'display_name', 'email')
        }),
        ('Academic Information', {
            'fields': ('academic_status', 'discipline', 'institution', 'link')
        }),
        ('Sync Settings', {
            'fields': (
                'is_synced', 'last_sync_at', 'sync_documents', 
                'auto_sync_enabled'
            )
        }),
        ('Privacy Settings', {
            'fields': ('public_profile', 'show_documents')
        }),
        ('Statistics', {
            'fields': ('document_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def document_count(self, obj):
        return obj.get_document_count()
    document_count.short_description = 'Documents'


@admin.register(MendeleyDocument)
class MendeleyDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'title_short', 'document_type', 'year', 'source', 
        'is_imported', 'profile', 'created_at'
    ]
    list_filter = [
        'document_type', 'year', 'is_imported', 'file_attached',
        'profile__user', 'created_at'
    ]
    search_fields = [
        'title', 'source', 'doi', 'pmid', 'isbn', 'abstract',
        'profile__user__username'
    ]
    readonly_fields = [
        'mendeley_id', 'created', 'last_modified', 'created_at', 
        'updated_at', 'scholar_paper_link'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('profile', 'mendeley_id', 'title', 'document_type')
        }),
        ('Publication Details', {
            'fields': ('year', 'month', 'day', 'source', 'volume', 'issue', 'pages')
        }),
        ('Content', {
            'fields': ('abstract', 'notes')
        }),
        ('Authors & Editors', {
            'fields': ('authors', 'editors'),
            'classes': ('collapse',)
        }),
        ('Identifiers', {
            'fields': ('doi', 'pmid', 'isbn', 'issn', 'arxiv'),
            'classes': ('collapse',)
        }),
        ('URLs', {
            'fields': ('website', 'mendeley_url'),
            'classes': ('collapse',)
        }),
        ('Tags & Keywords', {
            'fields': ('tags', 'keywords'),
            'classes': ('collapse',)
        }),
        ('File Information', {
            'fields': ('file_attached',)
        }),
        ('Scholar Integration', {
            'fields': ('is_imported', 'scholar_paper_link')
        }),
        ('Mendeley Metadata', {
            'fields': ('created', 'last_modified'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_short(self, obj):
        return obj.title[:100] + '...' if len(obj.title) > 100 else obj.title
    title_short.short_description = 'Title'
    
    def scholar_paper_link(self, obj):
        if obj.scholar_paper:
            url = reverse('admin:scholar_searchindex_change', args=[obj.scholar_paper.id])
            return format_html('<a href="{}">View Scholar Paper</a>', url)
        return 'Not imported'
    scholar_paper_link.short_description = 'Scholar Paper'


@admin.register(MendeleyGroup)
class MendeleyGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'profile', 'group_type', 'role', 'sync_enabled', 'created_at']
    list_filter = ['group_type', 'role', 'sync_enabled', 'profile__user']
    search_fields = ['name', 'description', 'mendeley_group_id', 'profile__user__username']
    readonly_fields = ['mendeley_group_id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('profile', 'mendeley_group_id', 'name', 'description')
        }),
        ('Group Details', {
            'fields': ('group_type', 'role', 'access_level')
        }),
        ('Sync Settings', {
            'fields': ('sync_enabled',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MendeleyFolder)
class MendeleyFolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'profile', 'parent_folder', 'document_count', 'created_at']
    list_filter = ['profile__user', 'parent_folder']
    search_fields = ['name', 'mendeley_folder_id', 'profile__user__username']
    readonly_fields = ['mendeley_folder_id', 'created_at', 'updated_at', 'document_count']
    filter_horizontal = ['documents']
    
    fieldsets = (
        (None, {
            'fields': ('profile', 'mendeley_folder_id', 'name', 'parent_folder')
        }),
        ('Documents', {
            'fields': ('documents', 'document_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def document_count(self, obj):
        return obj.documents.count()
    document_count.short_description = 'Document Count'


@admin.register(MendeleySyncLog)
class MendeleySyncLogAdmin(admin.ModelAdmin):
    list_display = [
        'profile', 'sync_type', 'status', 'started_at', 'duration_seconds',
        'items_processed', 'items_created', 'items_updated', 'success_rate'
    ]
    list_filter = ['sync_type', 'status', 'started_at', 'profile__user']
    search_fields = ['profile__user__username', 'error_message']
    readonly_fields = [
        'started_at', 'completed_at', 'duration_seconds', 'success_rate'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('profile', 'sync_type', 'status')
        }),
        ('Results', {
            'fields': (
                'items_processed', 'items_created', 'items_updated', 
                'items_skipped', 'success_rate'
            )
        }),
        ('Error Information', {
            'fields': ('error_message', 'error_details'),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'duration_seconds')
        }),
    )
    
    def success_rate(self, obj):
        rate = obj.get_success_rate()
        if rate >= 90:
            color = 'green'
        elif rate >= 70:
            color = 'orange'
        else:
            color = 'red'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, rate)
    success_rate.short_description = 'Success Rate'