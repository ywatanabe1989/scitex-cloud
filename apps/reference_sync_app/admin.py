from django.contrib import admin
from .models import (
    ReferenceManagerAccount,
    SyncProfile,
    SyncSession,
    ReferenceMapping,
    ConflictResolution,
    SyncLog
)


@admin.register(ReferenceManagerAccount)
class ReferenceManagerAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'account_name', 'is_active', 'last_sync']
    list_filter = ['service', 'is_active', 'created_at']
    search_fields = ['user__username', 'account_name', 'service']
    readonly_fields = ['created_at', 'updated_at', 'last_sync']


@admin.register(SyncProfile)
class SyncProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'auto_sync', 'sync_frequency', 'last_sync']
    list_filter = ['auto_sync', 'sync_frequency', 'conflict_resolution', 'created_at']
    search_fields = ['user__username', 'name']
    readonly_fields = ['created_at', 'updated_at', 'last_sync']


@admin.register(SyncSession)
class SyncSessionAdmin(admin.ModelAdmin):
    list_display = ['profile', 'status', 'started_at', 'completed_at', 'items_processed', 'conflicts_found']
    list_filter = ['status', 'started_at']
    search_fields = ['profile__name', 'profile__user__username']
    readonly_fields = ['started_at', 'completed_at']


@admin.register(ReferenceMapping)
class ReferenceMappingAdmin(admin.ModelAdmin):
    list_display = ['local_paper', 'service', 'external_id', 'last_synced']
    list_filter = ['service', 'last_synced']
    search_fields = ['local_paper__title', 'external_id']
    readonly_fields = ['created_at', 'last_synced']


@admin.register(ConflictResolution)
class ConflictResolutionAdmin(admin.ModelAdmin):
    list_display = ['sync_session', 'reference_mapping', 'conflict_type', 'resolution', 'resolved_at']
    list_filter = ['conflict_type', 'resolution', 'resolved_at']
    search_fields = ['reference_mapping__external_id']
    readonly_fields = ['created_at', 'resolved_at']


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['sync_session', 'level', 'operation', 'created_at']
    list_filter = ['level', 'operation', 'created_at']
    search_fields = ['message']
    readonly_fields = ['created_at']