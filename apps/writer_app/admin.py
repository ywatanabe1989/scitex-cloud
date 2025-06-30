from django.contrib import admin
from .models import (
    DocumentTemplate, Manuscript, ManuscriptSection, Figure, Table, Citation,
    CompilationJob, AIAssistanceLog, CollaborativeSession, DocumentChange,
    ManuscriptVersion, ManuscriptBranch, DiffResult, MergeRequest,
    ArxivAccount, ArxivCategory, ArxivSubmission, ArxivSubmissionHistory,
    ArxivValidationResult, ArxivApiResponse
)


# Writer App Admin
@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'journal_name', 'is_public', 'usage_count', 'created_at']
    list_filter = ['template_type', 'is_public', 'created_at']
    search_fields = ['name', 'journal_name', 'description']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']


@admin.register(Manuscript)
class ManuscriptAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'status', 'project', 'is_modular', 'word_count_total', 'updated_at']
    list_filter = ['status', 'is_modular', 'is_public', 'created_at']
    search_fields = ['title', 'abstract', 'keywords']
    readonly_fields = ['slug', 'word_count_total', 'citation_count', 'created_at', 'updated_at', 'last_compiled']
    filter_horizontal = ['collaborators']


@admin.register(ManuscriptSection)
class ManuscriptSectionAdmin(admin.ModelAdmin):
    list_display = ['manuscript', 'section_type', 'title', 'order', 'updated_at']
    list_filter = ['section_type', 'created_at']
    search_fields = ['title', 'content']


@admin.register(CompilationJob)
class CompilationJobAdmin(admin.ModelAdmin):
    list_display = ['manuscript', 'status', 'compilation_type', 'initiated_by', 'compilation_time', 'created_at']
    list_filter = ['status', 'compilation_type', 'created_at']
    readonly_fields = ['job_id', 'compilation_time', 'page_count', 'created_at', 'started_at', 'completed_at']


@admin.register(AIAssistanceLog)
class AIAssistanceLogAdmin(admin.ModelAdmin):
    list_display = ['manuscript', 'user', 'assistance_type', 'accepted', 'tokens_used', 'created_at']
    list_filter = ['assistance_type', 'accepted', 'created_at']
    readonly_fields = ['response_time', 'created_at']


# arXiv Integration Admin
@admin.register(ArxivAccount)
class ArxivAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'arxiv_username', 'arxiv_email', 'is_verified', 'is_active', 'submissions_today', 'daily_submission_limit']
    list_filter = ['is_verified', 'is_active', 'created_at']
    search_fields = ['user__username', 'arxiv_username', 'arxiv_email', 'affiliation']
    readonly_fields = ['verification_token', 'verified_at', 'submissions_today', 'last_submission_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('user', 'arxiv_username', 'arxiv_email', 'orcid_id', 'affiliation')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_token', 'verified_at')
        }),
        ('Submission Limits', {
            'fields': ('daily_submission_limit', 'submissions_today', 'last_submission_date')
        }),
        ('Status', {
            'fields': ('is_active', 'suspension_reason', 'suspended_until')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ArxivCategory)
class ArxivCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'parent_category', 'is_active', 'submission_count']
    list_filter = ['is_active', 'parent_category', 'created_at']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['submission_count', 'created_at', 'updated_at']


@admin.register(ArxivSubmission)
class ArxivSubmissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'arxiv_id', 'status', 'primary_category', 'version', 'submitted_at']
    list_filter = ['status', 'submission_type', 'primary_category', 'is_test_submission', 'created_at']
    search_fields = ['title', 'abstract', 'authors', 'arxiv_id']
    readonly_fields = ['submission_id', 'arxiv_id', 'arxiv_url', 'submitted_at', 'published_at', 'last_status_check', 'created_at', 'updated_at']
    filter_horizontal = ['secondary_categories']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('manuscript', 'user', 'arxiv_account', 'submission_id')
        }),
        ('Submission Details', {
            'fields': ('title', 'abstract', 'authors', 'submission_type', 'version')
        }),
        ('Categories', {
            'fields': ('primary_category', 'secondary_categories')
        }),
        ('arXiv Information', {
            'fields': ('arxiv_id', 'arxiv_url', 'status')
        }),
        ('Files', {
            'fields': ('latex_source', 'pdf_file', 'supplementary_files')
        }),
        ('Additional Information', {
            'fields': ('comments', 'journal_reference', 'doi', 'arxiv_comments', 'moderation_reason')
        }),
        ('Version Control', {
            'fields': ('replaces_submission',)
        }),
        ('Status Tracking', {
            'fields': ('submitted_at', 'published_at', 'last_status_check')
        }),
        ('Administrative', {
            'fields': ('admin_notes', 'is_test_submission'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ArxivSubmissionHistory)
class ArxivSubmissionHistoryAdmin(admin.ModelAdmin):
    list_display = ['submission', 'previous_status', 'new_status', 'changed_by', 'is_automatic', 'created_at']
    list_filter = ['previous_status', 'new_status', 'is_automatic', 'created_at']
    search_fields = ['submission__title', 'change_reason']
    readonly_fields = ['created_at']


@admin.register(ArxivValidationResult)
class ArxivValidationResultAdmin(admin.ModelAdmin):
    list_display = ['submission', 'status', 'overall_score', 'is_ready_for_submission', 'validation_started']
    list_filter = ['status', 'latex_compilation', 'pdf_generation', 'metadata_validation', 'validation_started']
    readonly_fields = ['validation_started', 'validation_completed']
    
    fieldsets = (
        ('General', {
            'fields': ('submission', 'status', 'overall_score')
        }),
        ('Validation Checks', {
            'fields': ('latex_compilation', 'pdf_generation', 'metadata_validation', 'category_validation', 'file_format_check')
        }),
        ('Detailed Results', {
            'fields': ('validation_details', 'error_messages', 'warning_messages'),
            'classes': ('collapse',)
        }),
        ('LaTeX Specific', {
            'fields': ('latex_log', 'bibtex_issues', 'missing_figures'),
            'classes': ('collapse',)
        }),
        ('arXiv Requirements', {
            'fields': ('title_length_check', 'abstract_length_check', 'author_format_check')
        }),
        ('File Validation', {
            'fields': ('total_file_size', 'max_file_size_exceeded', 'unsupported_files')
        }),
        ('Timestamps', {
            'fields': ('validation_started', 'validation_completed'),
            'classes': ('collapse',)
        })
    )


@admin.register(ArxivApiResponse)
class ArxivApiResponseAdmin(admin.ModelAdmin):
    list_display = ['submission', 'api_endpoint', 'request_method', 'response_status', 'is_error', 'duration_ms', 'created_at']
    list_filter = ['request_method', 'response_status', 'is_error', 'created_at']
    search_fields = ['submission__title', 'api_endpoint', 'error_message']
    readonly_fields = ['request_time', 'response_time', 'duration_ms', 'created_at']