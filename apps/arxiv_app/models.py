#!/usr/bin/env python3
"""
Models for arXiv submission and integration system.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.files.storage import default_storage
import uuid
import json
import logging

logger = logging.getLogger(__name__)


class ArxivCategory(models.Model):
    """arXiv subject categories."""
    
    code = models.CharField(max_length=20, primary_key=True, help_text="arXiv category code (e.g., cs.AI)")
    name = models.CharField(max_length=200, help_text="Full category name")
    description = models.TextField(blank=True, help_text="Category description")
    parent_category = models.CharField(max_length=10, blank=True, help_text="Parent category code")
    is_active = models.BooleanField(default=True)
    
    # Submission guidelines
    guidelines = models.TextField(blank=True, help_text="Submission guidelines for this category")
    requirements = models.JSONField(default=dict, blank=True, help_text="Category-specific requirements")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
        verbose_name = "arXiv Category"
        verbose_name_plural = "arXiv Categories"
    
    def __str__(self):
        return f"{self.code}: {self.name}"


class ArxivSubmission(models.Model):
    """Track arXiv submissions from SciTeX Writer."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('preparing', 'Preparing'),
        ('validating', 'Validating'),
        ('submitting', 'Submitting'),
        ('submitted', 'Submitted'),
        ('processing', 'Processing on arXiv'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
        ('error', 'Error'),
    ]
    
    SUBMISSION_TYPE_CHOICES = [
        ('new', 'New Submission'),
        ('replacement', 'Replacement'),
        ('withdrawal', 'Withdrawal'),
        ('cross_list', 'Cross-list'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # User and project info
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='arxiv_submissions')
    writer_project = models.ForeignKey('writer_app.WriterProject', on_delete=models.CASCADE, related_name='arxiv_submissions', null=True, blank=True)
    
    # Basic submission info
    title = models.CharField(max_length=500, help_text="Paper title")
    abstract = models.TextField(help_text="Paper abstract")
    authors = models.JSONField(help_text="List of authors with affiliations")
    
    # arXiv metadata
    primary_category = models.ForeignKey(ArxivCategory, on_delete=models.PROTECT, related_name='primary_submissions')
    secondary_categories = models.ManyToManyField(ArxivCategory, blank=True, related_name='secondary_submissions')
    
    # Comments and journal reference
    comments = models.TextField(blank=True, help_text="Comments field (e.g., '5 pages, 3 figures')")
    journal_ref = models.CharField(max_length=200, blank=True, help_text="Journal reference if published")
    doi = models.CharField(max_length=100, blank=True, help_text="DOI if available")
    
    # Submission details
    submission_type = models.CharField(max_length=20, choices=SUBMISSION_TYPE_CHOICES, default='new')
    replaces_arxiv_id = models.CharField(max_length=50, blank=True, help_text="arXiv ID this replaces")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    arxiv_id = models.CharField(max_length=50, blank=True, help_text="Assigned arXiv ID")
    version = models.IntegerField(default=1, help_text="Version number")
    
    # File management
    source_files_path = models.CharField(max_length=500, blank=True, help_text="Path to source files")
    compiled_pdf_path = models.CharField(max_length=500, blank=True, help_text="Path to compiled PDF")
    submission_package_path = models.CharField(max_length=500, blank=True, help_text="Path to submission package")
    
    # Validation results
    validation_status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('valid', 'Valid'),
        ('warnings', 'Warnings'),
        ('errors', 'Errors'),
    ])
    validation_log = models.TextField(blank=True, help_text="Validation output")
    
    # Submission tracking
    submitted_at = models.DateTimeField(null=True, blank=True)
    arxiv_submission_id = models.CharField(max_length=100, blank=True, help_text="Internal arXiv submission ID")
    
    # Publication info
    published_at = models.DateTimeField(null=True, blank=True)
    announcement_date = models.DateField(null=True, blank=True)
    
    # Error handling
    last_error = models.TextField(blank=True, help_text="Last error message")
    retry_count = models.IntegerField(default=0)
    
    # Metadata
    submission_metadata = models.JSONField(default=dict, blank=True, help_text="Additional submission metadata")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['arxiv_id']),
        ]
    
    def __str__(self):
        return f"{self.title[:50]} ({self.status})"
    
    def get_arxiv_url(self):
        """Get the arXiv URL for this submission."""
        if self.arxiv_id:
            return f"https://arxiv.org/abs/{self.arxiv_id}"
        return None
    
    def get_pdf_url(self):
        """Get the arXiv PDF URL."""
        if self.arxiv_id:
            return f"https://arxiv.org/pdf/{self.arxiv_id}.pdf"
        return None
    
    def can_submit(self):
        """Check if submission is ready for arXiv."""
        return (self.status == 'draft' and 
                self.validation_status == 'valid' and 
                self.compiled_pdf_path and 
                self.source_files_path)
    
    def is_published(self):
        """Check if submission is published on arXiv."""
        return self.status == 'published' and self.arxiv_id


class ArxivAuthor(models.Model):
    """Author information for arXiv submissions."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(ArxivSubmission, on_delete=models.CASCADE, related_name='author_details')
    
    # Basic info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    
    # Academic info
    affiliation = models.CharField(max_length=300, blank=True)
    orcid_id = models.CharField(max_length=50, blank=True, help_text="ORCID identifier")
    
    # Author order
    order = models.IntegerField(help_text="Author order in the paper")
    is_corresponding = models.BooleanField(default=False)
    
    # Contact info (for corresponding author)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['submission', 'order']
        unique_together = ['submission', 'order']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class ArxivSubmissionFile(models.Model):
    """Files associated with arXiv submissions."""
    
    FILE_TYPE_CHOICES = [
        ('main_tex', 'Main LaTeX File'),
        ('tex', 'LaTeX File'),
        ('cls', 'Class File'),
        ('sty', 'Style File'),
        ('bst', 'Bibliography Style'),
        ('bib', 'Bibliography'),
        ('pdf', 'PDF Figure'),
        ('eps', 'EPS Figure'),
        ('png', 'PNG Figure'),
        ('jpg', 'JPEG Figure'),
        ('gif', 'GIF Figure'),
        ('readme', 'README'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(ArxivSubmission, on_delete=models.CASCADE, related_name='files')
    
    # File info
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    file_path = models.CharField(max_length=500, help_text="Path to the file")
    file_size = models.IntegerField(help_text="File size in bytes")
    
    # File metadata
    is_main_file = models.BooleanField(default=False, help_text="Is this the main LaTeX file?")
    is_required = models.BooleanField(default=True, help_text="Is this file required for compilation?")
    
    # Content info
    checksum = models.CharField(max_length=64, blank=True, help_text="File checksum for integrity")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['submission', 'filename']
        indexes = [
            models.Index(fields=['submission', 'file_type']),
        ]
    
    def __str__(self):
        return f"{self.filename} ({self.submission.title[:30]})"


class ArxivSubmissionLog(models.Model):
    """Log submission activities and API interactions."""
    
    LOG_TYPE_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('api_call', 'API Call'),
        ('validation', 'Validation'),
        ('compilation', 'Compilation'),
        ('submission', 'Submission'),
        ('status_update', 'Status Update'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(ArxivSubmission, on_delete=models.CASCADE, related_name='logs')
    
    # Log details
    log_type = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True, help_text="Additional log details")
    
    # Context
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['submission', '-created_at']),
            models.Index(fields=['log_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.log_type}: {self.message[:100]}"


class ArxivApiCredentials(models.Model):
    """Store arXiv API credentials for users."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='arxiv_credentials')
    
    # arXiv user info
    arxiv_username = models.CharField(max_length=100, blank=True)
    arxiv_password = models.CharField(max_length=255, blank=True)  # Should be encrypted
    
    # API access
    api_key = models.CharField(max_length=255, blank=True, help_text="arXiv API key if available")
    
    # Preferences
    default_category = models.ForeignKey(ArxivCategory, on_delete=models.SET_NULL, null=True, blank=True)
    auto_submit = models.BooleanField(default=False, help_text="Automatically submit when validation passes")
    
    # Status
    is_verified = models.BooleanField(default=False, help_text="Has the user verified their arXiv account?")
    last_verified = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"arXiv credentials for {self.user.username}"


class ArxivTemplate(models.Model):
    """Pre-defined templates for arXiv submissions."""
    
    TEMPLATE_TYPE_CHOICES = [
        ('article', 'Research Article'),
        ('review', 'Review Article'),
        ('letter', 'Letter/Communication'),
        ('conference', 'Conference Paper'),
        ('thesis', 'Thesis/Dissertation'),
        ('preprint', 'Preprint'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Template info
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES)
    
    # Category associations
    recommended_categories = models.ManyToManyField(ArxivCategory, blank=True)
    
    # Template content
    latex_template = models.TextField(help_text="LaTeX template content")
    required_files = models.JSONField(default=list, blank=True, help_text="List of required files")
    optional_files = models.JSONField(default=list, blank=True, help_text="List of optional files")
    
    # Metadata
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Usage stats
    usage_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"


class ArxivSearchCache(models.Model):
    """Cache arXiv search results for performance."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Search parameters
    query = models.CharField(max_length=500, help_text="Search query")
    category = models.CharField(max_length=50, blank=True, help_text="Category filter")
    search_type = models.CharField(max_length=20, default='all', help_text="Search type (all, title, author, etc.)")
    
    # Results
    results = models.JSONField(help_text="Cached search results")
    total_results = models.IntegerField(default=0)
    
    # Cache metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="When this cache entry expires")
    
    class Meta:
        indexes = [
            models.Index(fields=['query', 'category']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Cache: {self.query[:50]}"
    
    def is_expired(self):
        """Check if cache entry is expired."""
        return timezone.now() > self.expires_at


class ArxivPaperMapping(models.Model):
    """Map local Scholar papers to arXiv papers."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Local paper (from Scholar)
    local_paper = models.ForeignKey('scholar.SearchIndex', on_delete=models.CASCADE, related_name='arxiv_mappings')
    
    # arXiv paper info
    arxiv_id = models.CharField(max_length=50, help_text="arXiv identifier")
    arxiv_version = models.IntegerField(default=1, help_text="arXiv version")
    
    # Mapping metadata
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Confidence in the mapping (0.0-1.0)"
    )
    mapping_source = models.CharField(max_length=50, default='manual', choices=[
        ('manual', 'Manual'),
        ('doi', 'DOI Match'),
        ('title', 'Title Match'),
        ('author', 'Author Match'),
        ('automatic', 'Automatic'),
    ])
    
    # Status
    is_verified = models.BooleanField(default=False, help_text="Has this mapping been verified?")
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['local_paper', 'arxiv_id']
        indexes = [
            models.Index(fields=['arxiv_id']),
            models.Index(fields=['confidence_score']),
        ]
    
    def __str__(self):
        return f"{self.local_paper.title[:50]} -> {self.arxiv_id}"