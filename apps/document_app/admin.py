from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'owner', 'project', 'created_at', 'updated_at')
    list_filter = ('document_type', 'is_public', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'owner__username', 'tags')
    readonly_fields = ('created_at', 'updated_at', 'file_size', 'file_hash')
    
    fieldsets = (
        ('Document Information', {
            'fields': ('title', 'content', 'document_type', 'owner', 'project')
        }),
        ('Metadata', {
            'fields': ('tags', 'is_public'),
        }),
        ('File Information', {
            'fields': ('file_location', 'file_size', 'file_hash'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )