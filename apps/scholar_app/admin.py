from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Author, Journal, Topic, SearchIndex, AuthorPaper, Citation, SearchQuery,
    SearchResult, SearchFilter, SavedSearch, Collection, UserLibrary,
    LibraryExport, RecommendationLog, Annotation, AnnotationReply, AnnotationVote,
    CollaborationGroup, GroupMembership, AnnotationTag,
    # Repository models
    Repository, RepositoryConnection, Dataset, DatasetFile, DatasetVersion,
    RepositorySync
)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'orcid', 'affiliation', 'h_index', 'total_citations']
    list_filter = ['created_at', 'h_index']
    search_fields = ['first_name', 'last_name', 'orcid', 'email', 'affiliation']
    ordering = ['last_name', 'first_name']


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'issn', 'publisher', 'impact_factor', 'open_access']
    list_filter = ['open_access', 'publisher', 'impact_factor']
    search_fields = ['name', 'abbreviation', 'issn', 'publisher']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'paper_count']
    list_filter = ['parent']
    search_fields = ['name', 'description']


@admin.register(SearchIndex)
class SearchIndexAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'publication_date', 'citation_count', 'view_count', 'status']
    list_filter = ['document_type', 'status', 'source', 'is_open_access', 'publication_date']
    search_fields = ['title', 'abstract', 'doi', 'pmid', 'arxiv_id']
    date_hierarchy = 'publication_date'
    ordering = ['-publication_date']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_public', 'paper_count_display', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    
    def paper_count_display(self, obj):
        return obj.paper_count()
    paper_count_display.short_description = 'Paper Count'


@admin.register(UserLibrary)
class UserLibraryAdmin(admin.ModelAdmin):
    list_display = ['user', 'paper_title', 'reading_status', 'importance_rating', 'saved_at']
    list_filter = ['reading_status', 'importance_rating', 'saved_at']
    search_fields = ['user__username', 'paper__title', 'project', 'tags']
    
    def paper_title(self, obj):
        return obj.paper.title[:50] + '...' if len(obj.paper.title) > 50 else obj.paper.title
    paper_title.short_description = 'Paper'


# Repository Administration
@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'repository_type', 'status', 'supports_doi', 'is_default', 'total_deposits', 'active_connections']
    list_filter = ['repository_type', 'status', 'supports_doi', 'is_open_access', 'is_default']
    search_fields = ['name', 'description', 'api_base_url']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'repository_type', 'description', 'status')
        }),
        ('API Configuration', {
            'fields': ('api_base_url', 'api_version', 'api_documentation_url', 'website_url')
        }),
        ('Features & Capabilities', {
            'fields': (
                'supports_doi', 'supports_versioning', 'supports_private_datasets',
                'max_file_size_mb', 'max_dataset_size_mb', 'requires_authentication'
            )
        }),
        ('Metadata & Formats', {
            'fields': ('supports_metadata_formats', 'supported_file_formats', 'license_options'),
            'classes': ('collapse',)
        }),
        ('Repository Settings', {
            'fields': ('is_open_access', 'is_default')
        }),
        ('Statistics', {
            'fields': ('total_deposits', 'active_connections'),
            'classes': ('collapse',)
        })
    )


@admin.register(RepositoryConnection)
class RepositoryConnectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'repository', 'connection_name', 'status', 'last_verified', 'total_deposits']
    list_filter = ['status', 'repository__repository_type', 'is_default', 'auto_sync_enabled']
    search_fields = ['user__username', 'repository__name', 'connection_name', 'username']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Connection Details', {
            'fields': ('user', 'repository', 'connection_name', 'status')
        }),
        ('Authentication', {
            'fields': ('username', 'api_token', 'oauth_token'),
            'description': 'Sensitive credentials are encrypted in storage'
        }),
        ('Settings', {
            'fields': ('is_default', 'auto_sync_enabled', 'notification_enabled')
        }),
        ('Status Information', {
            'fields': ('last_verified', 'expires_at', 'last_activity'),
            'classes': ('collapse',)
        }),
        ('Usage Statistics', {
            'fields': ('total_deposits', 'total_downloads'),
            'classes': ('collapse',)
        }),
        ('Error Tracking', {
            'fields': ('last_error', 'error_count'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['last_verified', 'last_activity', 'error_count']
    
    def save_model(self, request, obj, form, change):
        # Encrypt sensitive fields before saving
        # Note: Implement proper encryption in production
        super().save_model(request, obj, form, change)


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'owner', 'dataset_type', 'status', 'visibility', 
        'file_count', 'size_display', 'repository_name', 'created_at'
    ]
    list_filter = [
        'dataset_type', 'status', 'visibility', 'repository_connection__repository__repository_type',
        'created_at', 'published_at'
    ]
    search_fields = ['title', 'description', 'keywords', 'owner__username', 'repository_id']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'dataset_type', 'keywords')
        }),
        ('Ownership & Collaboration', {
            'fields': ('owner', 'collaborators')
        }),
        ('Repository Information', {
            'fields': (
                'repository_connection', 'repository_id', 'repository_url', 
                'repository_doi', 'version'
            )
        }),
        ('Status & Visibility', {
            'fields': ('status', 'visibility', 'license', 'access_conditions', 'embargo_until')
        }),
        ('Research Context', {
            'fields': ('project', 'related_papers', 'generated_by_job', 'associated_notebooks', 'cited_in_manuscripts'),
            'classes': ('collapse',)
        }),
        ('File Information', {
            'fields': ('file_count', 'total_size_bytes', 'file_formats'),
            'classes': ('collapse',)
        }),
        ('Usage Statistics', {
            'fields': ('download_count', 'citation_count', 'view_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at', 'last_synced'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at', 'updated_at', 'file_count', 'total_size_bytes']
    filter_horizontal = ['collaborators', 'related_papers', 'associated_notebooks', 'cited_in_manuscripts']
    
    def repository_name(self, obj):
        return obj.repository_connection.repository.name
    repository_name.short_description = 'Repository'
    
    def size_display(self, obj):
        return obj.get_file_size_display()
    size_display.short_description = 'Total Size'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'owner', 'repository_connection__repository', 'project', 'generated_by_job'
        ).prefetch_related('collaborators')


class DatasetFileInline(admin.TabularInline):
    model = DatasetFile
    extra = 0
    fields = ['filename', 'file_type', 'file_format', 'size_display', 'download_count']
    readonly_fields = ['size_display']
    
    def size_display(self, obj):
        return obj.get_size_display() if obj.pk else ''
    size_display.short_description = 'Size'


@admin.register(DatasetFile)
class DatasetFileAdmin(admin.ModelAdmin):
    list_display = ['filename', 'dataset_title', 'file_type', 'file_format', 'size_display', 'download_count']
    list_filter = ['file_type', 'file_format', 'created_at']
    search_fields = ['filename', 'dataset__title', 'description']
    ordering = ['-created_at']
    
    def dataset_title(self, obj):
        return obj.dataset.title
    dataset_title.short_description = 'Dataset'
    
    def size_display(self, obj):
        return obj.get_size_display()
    size_display.short_description = 'Size'


@admin.register(DatasetVersion)
class DatasetVersionAdmin(admin.ModelAdmin):
    list_display = ['dataset_title', 'version_number', 'is_current', 'files_added', 'files_modified', 'created_at']
    list_filter = ['is_current', 'created_at']
    search_fields = ['dataset__title', 'version_number', 'version_description']
    ordering = ['-created_at']
    
    def dataset_title(self, obj):
        return obj.dataset.title
    dataset_title.short_description = 'Dataset'


@admin.register(RepositorySync)
class RepositorySyncAdmin(admin.ModelAdmin):
    list_display = [
        'sync_type', 'target_display', 'status', 'progress_display', 
        'started_at', 'completed_at', 'user'
    ]
    list_filter = ['sync_type', 'status', 'repository_connection__repository__repository_type', 'started_at']
    search_fields = ['user__username', 'dataset__title', 'repository_connection__repository__name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Sync Information', {
            'fields': ('user', 'repository_connection', 'dataset', 'sync_type', 'status')
        }),
        ('Progress Tracking', {
            'fields': (
                'total_items', 'completed_items', 'failed_items',
                'total_bytes', 'transferred_bytes'
            )
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'estimated_completion')
        }),
        ('Results & Logs', {
            'fields': ('result_data', 'error_message', 'sync_log'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def target_display(self, obj):
        if obj.dataset:
            return f"Dataset: {obj.dataset.title[:30]}..."
        return f"Repository: {obj.repository_connection.repository.name}"
    target_display.short_description = 'Target'
    
    def progress_display(self, obj):
        if obj.total_items > 0:
            percentage = (obj.completed_items / obj.total_items) * 100
            return f"{obj.completed_items}/{obj.total_items} ({percentage:.1f}%)"
        return "N/A"
    progress_display.short_description = 'Progress'


# Enhanced Dataset admin with file inline
class DatasetAdminWithFiles(DatasetAdmin):
    inlines = [DatasetFileInline]


# Update the registration to use the enhanced version
admin.site.unregister(Dataset)
admin.site.register(Dataset, DatasetAdminWithFiles)


# Add some admin actions
@admin.action(description='Sync selected datasets with repository')
def sync_datasets_with_repository(modeladmin, request, queryset):
    from .repository_services import sync_dataset_with_repository
    
    for dataset in queryset:
        if dataset.repository_id:
            sync_dataset_with_repository(dataset)
    
    modeladmin.message_user(request, f"Started sync for {queryset.count()} datasets.")


@admin.action(description='Test repository connections')
def test_repository_connections(modeladmin, request, queryset):
    from .repository_services import RepositoryServiceFactory
    
    results = []
    for connection in queryset:
        try:
            service = RepositoryServiceFactory.create_service(connection)
            if service.authenticate():
                results.append(f" {connection.connection_name}: Connected")
            else:
                results.append(f" {connection.connection_name}: Failed")
        except Exception as e:
            results.append(f" {connection.connection_name}: Error - {str(e)}")
    
    modeladmin.message_user(request, "\n".join(results))


# Add actions to admin classes
DatasetAdminWithFiles.actions = [sync_datasets_with_repository]
RepositoryConnectionAdmin.actions = [test_repository_connections]