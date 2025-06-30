"""
API serializers for reference manager synchronization.
"""

from rest_framework import serializers
from django.contrib.auth.models import User

from .models import (
    ReferenceManagerAccount,
    SyncProfile,
    SyncSession,
    ReferenceMapping,
    ConflictResolution,
    SyncLog,
    SyncStatistics,
    WebhookEndpoint
)
from apps.scholar_app.models import SearchIndex


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user information."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ReferenceManagerAccountSerializer(serializers.ModelSerializer):
    """Serializer for reference manager accounts."""
    
    user = UserSerializer(read_only=True)
    is_token_valid = serializers.SerializerMethodField()
    can_make_api_call = serializers.SerializerMethodField()
    mappings_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReferenceManagerAccount
        fields = [
            'id', 'user', 'service', 'account_name', 'account_email',
            'external_user_id', 'status', 'is_active', 'last_sync',
            'sync_count', 'api_calls_today', 'api_quota_reset',
            'created_at', 'updated_at', 'is_token_valid',
            'can_make_api_call', 'mappings_count'
        ]
        read_only_fields = [
            'id', 'user', 'external_user_id', 'last_sync', 'sync_count',
            'api_calls_today', 'api_quota_reset', 'created_at', 'updated_at'
        ]
    
    def get_is_token_valid(self, obj):
        """Check if the OAuth token is still valid."""
        return obj.is_token_valid()
    
    def get_can_make_api_call(self, obj):
        """Check if we can make an API call."""
        return obj.can_make_api_call()
    
    def get_mappings_count(self, obj):
        """Get count of reference mappings."""
        return obj.mappings.count()


class SyncProfileSerializer(serializers.ModelSerializer):
    """Serializer for sync profiles."""
    
    user = UserSerializer(read_only=True)
    accounts = ReferenceManagerAccountSerializer(many=True, read_only=True)
    account_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=ReferenceManagerAccount.objects.none(),
        source='accounts'
    )
    sessions_count = serializers.SerializerMethodField()
    next_sync_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = SyncProfile
        fields = [
            'id', 'user', 'name', 'description', 'accounts', 'account_ids',
            'auto_sync', 'sync_frequency', 'sync_direction', 'conflict_resolution',
            'sync_collections', 'sync_tags', 'exclude_tags', 'sync_pdfs',
            'sync_notes', 'sync_attachments', 'sync_after_date', 'sync_before_date',
            'is_active', 'last_sync', 'next_sync', 'created_at', 'updated_at',
            'sessions_count', 'next_sync_formatted'
        ]
        read_only_fields = [
            'id', 'user', 'last_sync', 'next_sync', 'created_at', 'updated_at'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Filter accounts to only show user's accounts
            self.fields['account_ids'].queryset = ReferenceManagerAccount.objects.filter(
                user=request.user, is_active=True
            )
    
    def get_sessions_count(self, obj):
        """Get count of sync sessions."""
        return obj.sync_sessions.count()
    
    def get_next_sync_formatted(self, obj):
        """Get formatted next sync time."""
        if obj.next_sync:
            return obj.next_sync.isoformat()
        return None
    
    def validate_account_ids(self, value):
        """Validate that at least one account is selected."""
        if not value:
            raise serializers.ValidationError("At least one account must be selected.")
        return value
    
    def validate(self, data):
        """Validate sync profile data."""
        sync_after = data.get('sync_after_date')
        sync_before = data.get('sync_before_date')
        
        if sync_after and sync_before and sync_after >= sync_before:
            raise serializers.ValidationError(
                "Sync after date must be before sync before date."
            )
        
        return data


class SyncSessionSerializer(serializers.ModelSerializer):
    """Serializer for sync sessions."""
    
    profile = SyncProfileSerializer(read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    conflicts_count = serializers.SerializerMethodField()
    logs_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SyncSession
        fields = [
            'id', 'profile', 'status', 'trigger', 'started_at', 'completed_at',
            'estimated_duration', 'total_items', 'items_processed', 'items_created',
            'items_updated', 'items_deleted', 'items_skipped', 'conflicts_found',
            'conflicts_resolved', 'errors_count', 'last_error', 'api_calls_made',
            'data_transferred_mb', 'result_summary', 'duration_seconds',
            'progress_percentage', 'conflicts_count', 'logs_count'
        ]
        read_only_fields = [
            'id', 'started_at', 'completed_at', 'estimated_duration',
            'total_items', 'items_processed', 'items_created', 'items_updated',
            'items_deleted', 'items_skipped', 'conflicts_found', 'conflicts_resolved',
            'errors_count', 'last_error', 'api_calls_made', 'data_transferred_mb',
            'result_summary'
        ]
    
    def get_duration_seconds(self, obj):
        """Get session duration in seconds."""
        duration = obj.duration()
        return duration.total_seconds() if duration else None
    
    def get_progress_percentage(self, obj):
        """Get progress percentage."""
        return obj.progress_percentage()
    
    def get_conflicts_count(self, obj):
        """Get count of conflicts."""
        return obj.conflicts.count()
    
    def get_logs_count(self, obj):
        """Get count of logs."""
        return obj.logs.count()


class ReferenceSerializer(serializers.ModelSerializer):
    """Serializer for reference (SearchIndex) data."""
    
    authors_list = serializers.SerializerMethodField()
    journal_name = serializers.SerializerMethodField()
    mappings_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SearchIndex
        fields = [
            'id', 'title', 'abstract', 'document_type', 'publication_date',
            'doi', 'pmid', 'arxiv_id', 'external_url', 'keywords',
            'citation_count', 'view_count', 'status', 'is_open_access',
            'created_at', 'updated_at', 'authors_list', 'journal_name',
            'mappings_count'
        ]
        read_only_fields = [
            'id', 'citation_count', 'view_count', 'created_at', 'updated_at'
        ]
    
    def get_authors_list(self, obj):
        """Get list of author names."""
        return [ap.author.full_name for ap in obj.authorpaper_set.all()]
    
    def get_journal_name(self, obj):
        """Get journal name."""
        return obj.journal.name if obj.journal else None
    
    def get_mappings_count(self, obj):
        """Get count of reference mappings."""
        return obj.reference_mappings.count()


class ReferenceMappingSerializer(serializers.ModelSerializer):
    """Serializer for reference mappings."""
    
    local_paper = ReferenceSerializer(read_only=True)
    account = ReferenceManagerAccountSerializer(read_only=True)
    conflicts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReferenceMapping
        fields = [
            'id', 'local_paper', 'service', 'external_id', 'external_group_id',
            'local_hash', 'remote_hash', 'sync_status', 'account',
            'created_at', 'last_synced', 'conflicts_count'
        ]
        read_only_fields = [
            'id', 'local_hash', 'remote_hash', 'created_at', 'last_synced'
        ]
    
    def get_conflicts_count(self, obj):
        """Get count of conflicts."""
        return obj.conflicts.count()


class ConflictResolutionSerializer(serializers.ModelSerializer):
    """Serializer for conflict resolutions."""
    
    sync_session = SyncSessionSerializer(read_only=True)
    reference_mapping = ReferenceMappingSerializer(read_only=True)
    resolved_by = UserSerializer(read_only=True)
    is_resolved = serializers.SerializerMethodField()
    
    class Meta:
        model = ConflictResolution
        fields = [
            'id', 'sync_session', 'reference_mapping', 'conflict_type',
            'local_value', 'remote_value', 'resolution', 'resolved_value',
            'resolution_notes', 'created_at', 'resolved_at', 'resolved_by',
            'is_resolved'
        ]
        read_only_fields = [
            'id', 'sync_session', 'reference_mapping', 'conflict_type',
            'local_value', 'remote_value', 'created_at', 'resolved_at',
            'resolved_by'
        ]
    
    def get_is_resolved(self, obj):
        """Check if conflict is resolved."""
        return obj.is_resolved()


class SyncLogSerializer(serializers.ModelSerializer):
    """Serializer for sync logs."""
    
    sync_session = SyncSessionSerializer(read_only=True)
    reference_mapping = ReferenceMappingSerializer(read_only=True)
    
    class Meta:
        model = SyncLog
        fields = [
            'id', 'sync_session', 'level', 'operation', 'message',
            'reference_mapping', 'extra_data', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SyncStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for sync statistics."""
    
    user = UserSerializer(read_only=True)
    success_rate = serializers.SerializerMethodField()
    average_sync_time = serializers.SerializerMethodField()
    
    class Meta:
        model = SyncStatistics
        fields = [
            'id', 'user', 'date', 'sync_sessions', 'successful_syncs',
            'failed_syncs', 'items_synced', 'items_created', 'items_updated',
            'items_deleted', 'conflicts_found', 'conflicts_resolved',
            'total_sync_time', 'api_calls_made', 'data_transferred_mb',
            'created_at', 'updated_at', 'success_rate', 'average_sync_time'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_success_rate(self, obj):
        """Calculate success rate."""
        if obj.sync_sessions == 0:
            return 0
        return (obj.successful_syncs / obj.sync_sessions) * 100
    
    def get_average_sync_time(self, obj):
        """Calculate average sync time in seconds."""
        if obj.sync_sessions == 0:
            return 0
        return obj.total_sync_time.total_seconds() / obj.sync_sessions


class WebhookEndpointSerializer(serializers.ModelSerializer):
    """Serializer for webhook endpoints."""
    
    account = ReferenceManagerAccountSerializer(read_only=True)
    
    class Meta:
        model = WebhookEndpoint
        fields = [
            'id', 'account', 'service', 'webhook_url', 'secret_key',
            'events', 'is_active', 'last_triggered', 'trigger_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'last_triggered', 'trigger_count', 'created_at', 'updated_at'
        ]


class BulkImportSerializer(serializers.Serializer):
    """Serializer for bulk import requests."""
    
    file = serializers.FileField()
    format = serializers.ChoiceField(
        choices=[
            ('bibtex', 'BibTeX'),
            ('json', 'JSON'),
            ('csv', 'CSV'),
            ('ris', 'RIS'),
        ]
    )
    profile_id = serializers.UUIDField(required=False, allow_null=True)
    create_collections = serializers.BooleanField(default=True)
    overwrite_existing = serializers.BooleanField(default=False)
    
    def validate_file(self, value):
        """Validate uploaded file."""
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        
        # Check file extension
        allowed_extensions = ['.bib', '.json', '.csv', '.ris', '.txt']
        file_extension = '.' + value.name.lower().split('.')[-1]
        
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
            )
        
        return value
    
    def validate_profile_id(self, value):
        """Validate profile exists and belongs to user."""
        if value:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                try:
                    SyncProfile.objects.get(id=value, user=request.user)
                except SyncProfile.DoesNotExist:
                    raise serializers.ValidationError("Invalid sync profile.")
        return value


class BulkExportSerializer(serializers.Serializer):
    """Serializer for bulk export requests."""
    
    format = serializers.ChoiceField(
        choices=[
            ('bibtex', 'BibTeX'),
            ('json', 'JSON'),
            ('csv', 'CSV'),
            ('ris', 'RIS'),
            ('endnote', 'EndNote'),
        ]
    )
    profile_id = serializers.UUIDField(required=False, allow_null=True)
    collection = serializers.CharField(required=False, allow_blank=True)
    include_files = serializers.BooleanField(default=False)
    date_range = serializers.ChoiceField(
        choices=[
            ('all', 'All references'),
            ('last_month', 'Last month'),
            ('last_year', 'Last year'),
            ('custom', 'Custom date range'),
        ],
        default='all'
    )
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    
    def validate(self, data):
        """Validate export parameters."""
        date_range = data.get('date_range')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if date_range == 'custom':
            if not start_date:
                raise serializers.ValidationError("Start date is required for custom range.")
            if not end_date:
                raise serializers.ValidationError("End date is required for custom range.")
            if start_date >= end_date:
                raise serializers.ValidationError("Start date must be before end date.")
        
        return data


class SyncStatusSerializer(serializers.Serializer):
    """Serializer for sync status responses."""
    
    id = serializers.UUIDField()
    status = serializers.CharField()
    progress = serializers.FloatField()
    items_processed = serializers.IntegerField()
    total_items = serializers.IntegerField()
    conflicts_found = serializers.IntegerField()
    errors_count = serializers.IntegerField()
    started_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField(allow_null=True)
    duration_seconds = serializers.FloatField(allow_null=True)
    
    
class SyncActionSerializer(serializers.Serializer):
    """Serializer for sync action requests."""
    
    action = serializers.ChoiceField(
        choices=[
            ('start', 'Start Sync'),
            ('cancel', 'Cancel Sync'),
            ('pause', 'Pause Sync'),
            ('resume', 'Resume Sync'),
        ]
    )
    force = serializers.BooleanField(default=False)
    
    
class OAuthCallbackSerializer(serializers.Serializer):
    """Serializer for OAuth callback data."""
    
    code = serializers.CharField()
    state = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
    error_description = serializers.CharField(required=False)