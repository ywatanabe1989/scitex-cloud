from django.contrib import admin
from .models import OrcidProfile, OrcidPublication, OrcidWork, OrcidOAuth2Token


@admin.register(OrcidProfile)
class OrcidProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'orcid_id', 'given_name', 'family_name', 'is_synced', 'last_sync_at')
    list_filter = ('is_synced', 'last_sync_at', 'created_at')
    search_fields = ('user__username', 'user__email', 'orcid_id', 'given_name', 'family_name')
    readonly_fields = ('orcid_id', 'created_at', 'updated_at', 'last_sync_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'orcid_id')
        }),
        ('Profile Data', {
            'fields': ('given_name', 'family_name', 'credit_name', 'biography', 'researcher_urls')
        }),
        ('Sync Information', {
            'fields': ('is_synced', 'last_sync_at', 'sync_publications', 'auto_sync_enabled')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(OrcidPublication)
class OrcidPublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'publication_type', 'publication_year', 'journal', 'is_imported')
    list_filter = ('publication_type', 'publication_year', 'is_imported', 'created_at')
    search_fields = ('title', 'journal', 'doi', 'profile__user__username')
    readonly_fields = ('orcid_put_code', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('profile', 'title', 'publication_type', 'publication_year')
        }),
        ('Publication Details', {
            'fields': ('journal', 'doi', 'url', 'abstract')
        }),
        ('Authors', {
            'fields': ('authors',)
        }),
        ('ORCID Data', {
            'fields': ('orcid_put_code', 'orcid_raw_data')
        }),
        ('Import Status', {
            'fields': ('is_imported', 'scholar_paper')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(OrcidWork)
class OrcidWorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'work_type', 'publication_date', 'is_imported')
    list_filter = ('work_type', 'is_imported', 'created_at')
    search_fields = ('title', 'journal_title', 'profile__user__username')
    readonly_fields = ('put_code', 'created_at', 'updated_at')


@admin.register(OrcidOAuth2Token)
class OrcidOAuth2TokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'access_token_preview', 'expires_at', 'is_expired')
    list_filter = ('expires_at', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('access_token', 'refresh_token', 'created_at', 'updated_at')
    
    def access_token_preview(self, obj):
        if obj.access_token:
            return f"{obj.access_token[:10]}..."
        return "No token"
    access_token_preview.short_description = 'Access Token'
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Is Expired'