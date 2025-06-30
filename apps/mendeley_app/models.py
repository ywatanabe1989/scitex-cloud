from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid
import json


class MendeleyOAuth2Token(models.Model):
    """Store Mendeley OAuth2 tokens for authenticated users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mendeley_token')
    access_token = models.CharField(max_length=500, help_text="Mendeley access token")
    refresh_token = models.CharField(max_length=500, blank=True, help_text="Mendeley refresh token")
    token_type = models.CharField(max_length=50, default='bearer')
    scope = models.CharField(max_length=255, help_text="OAuth scope granted")
    expires_at = models.DateTimeField(help_text="Token expiration time")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'mendeley_app'
        verbose_name = "Mendeley OAuth2 Token"
        verbose_name_plural = "Mendeley OAuth2 Tokens"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Mendeley Token for {self.user.username}"
    
    def is_expired(self):
        """Check if the token has expired"""
        return timezone.now() >= self.expires_at
    
    def is_expiring_soon(self, hours=24):
        """Check if token expires within specified hours"""
        return timezone.now() + timedelta(hours=hours) >= self.expires_at
    
    def get_authorization_header(self):
        """Get formatted authorization header"""
        return f"Bearer {self.access_token}"


class MendeleyProfile(models.Model):
    """Mendeley profile information for users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mendeley_profile')
    mendeley_id = models.CharField(max_length=100, unique=True, help_text="Mendeley user ID")
    
    # Basic profile information
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    display_name = models.CharField(max_length=255, blank=True, help_text="Display name")
    email = models.EmailField(blank=True)
    
    # Academic information
    academic_status = models.CharField(max_length=100, blank=True, help_text="Academic status (e.g., Professor, Student)")
    discipline = models.CharField(max_length=255, blank=True, help_text="Research discipline")
    institution = models.CharField(max_length=500, blank=True, help_text="Current institution")
    
    # Profile metadata
    link = models.URLField(blank=True, help_text="Mendeley profile URL")
    
    # Sync settings
    is_synced = models.BooleanField(default=False, help_text="Profile has been synced with Mendeley")
    last_sync_at = models.DateTimeField(null=True, blank=True)
    sync_documents = models.BooleanField(default=True, help_text="Auto-sync documents from Mendeley")
    auto_sync_enabled = models.BooleanField(default=True, help_text="Enable automatic periodic sync")
    
    # Privacy settings
    public_profile = models.BooleanField(default=True, help_text="Make Mendeley profile visible to other users")
    show_documents = models.BooleanField(default=True, help_text="Show Mendeley documents in Scholar")
    
    # Metadata
    mendeley_record = models.JSONField(default=dict, blank=True, help_text="Raw Mendeley profile data")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'mendeley_app'
        verbose_name = "Mendeley Profile"
        verbose_name_plural = "Mendeley Profiles"
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['mendeley_id']),
            models.Index(fields=['user']),
            models.Index(fields=['last_sync_at']),
        ]
    
    def __str__(self):
        name = self.get_display_name()
        return f"{name} ({self.mendeley_id})"
    
    def get_display_name(self):
        """Get the best display name for this profile"""
        if self.display_name:
            return self.display_name
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.last_name:
            return self.last_name
        return self.user.get_full_name() or self.user.username
    
    def needs_sync(self, hours=24):
        """Check if profile needs syncing (hasn't been synced in X hours)"""
        if not self.last_sync_at:
            return True
        return timezone.now() - self.last_sync_at > timedelta(hours=hours)
    
    def get_document_count(self):
        """Get the count of Mendeley documents"""
        return self.mendeley_documents.count()
    
    def get_recent_documents(self, limit=5):
        """Get recent Mendeley documents"""
        return self.mendeley_documents.order_by('-created', '-created_at')[:limit]


class MendeleyDocument(models.Model):
    """Documents from Mendeley library"""
    
    DOCUMENT_TYPES = [
        ('journal', 'Journal Article'),
        ('book', 'Book'),
        ('book_section', 'Book Section'),
        ('conference_proceedings', 'Conference Proceedings'),
        ('working_paper', 'Working Paper'),
        ('report', 'Report'),
        ('web_page', 'Web Page'),
        ('thesis', 'Thesis'),
        ('magazine_article', 'Magazine Article'),
        ('statute', 'Statute'),
        ('patent', 'Patent'),
        ('newspaper_article', 'Newspaper Article'),
        ('computer_program', 'Computer Program'),
        ('hearing', 'Hearing'),
        ('television_broadcast', 'Television Broadcast'),
        ('encyclopedia_article', 'Encyclopedia Article'),
        ('case', 'Case'),
        ('film', 'Film'),
        ('bill', 'Bill'),
        ('generic', 'Generic'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(MendeleyProfile, on_delete=models.CASCADE, related_name='mendeley_documents')
    
    # Mendeley document ID
    mendeley_id = models.CharField(max_length=100, help_text="Mendeley document ID")
    
    # Basic document information
    title = models.TextField(help_text="Document title")
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES, default='journal')
    year = models.IntegerField(null=True, blank=True, help_text="Publication year")
    month = models.IntegerField(null=True, blank=True, help_text="Publication month")
    day = models.IntegerField(null=True, blank=True, help_text="Publication day")
    
    # Publication details
    source = models.CharField(max_length=500, blank=True, help_text="Journal or publication source")
    volume = models.CharField(max_length=50, blank=True)
    issue = models.CharField(max_length=50, blank=True)
    pages = models.CharField(max_length=100, blank=True)
    
    # Content
    abstract = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="User notes from Mendeley")
    
    # Authors (stored as JSON list)
    authors = models.JSONField(default=list, blank=True, help_text="List of authors")
    editors = models.JSONField(default=list, blank=True, help_text="List of editors")
    
    # Identifiers
    doi = models.CharField(max_length=255, blank=True, db_index=True)
    pmid = models.CharField(max_length=20, blank=True, help_text="PubMed ID")
    isbn = models.CharField(max_length=20, blank=True)
    issn = models.CharField(max_length=9, blank=True)
    arxiv = models.CharField(max_length=50, blank=True, help_text="ArXiv ID")
    
    # URLs and links
    website = models.URLField(blank=True)
    mendeley_url = models.URLField(blank=True, help_text="Mendeley document URL")
    
    # Tags and categories
    tags = models.JSONField(default=list, blank=True, help_text="Document tags")
    keywords = models.JSONField(default=list, blank=True, help_text="Keywords")
    
    # File information
    file_attached = models.BooleanField(default=False, help_text="Document has attached file")
    
    # Mendeley metadata
    created = models.DateTimeField(null=True, blank=True, help_text="Created date in Mendeley")
    last_modified = models.DateTimeField(null=True, blank=True, help_text="Last modified date in Mendeley")
    mendeley_raw_data = models.JSONField(default=dict, blank=True, help_text="Raw Mendeley API response")
    
    # Integration with Scholar module
    is_imported = models.BooleanField(default=False, help_text="Imported into Scholar module")
    scholar_paper = models.ForeignKey(
        'scholar_app.SearchIndex', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='mendeley_documents',
        help_text="Linked Scholar paper"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'mendeley_app'
        verbose_name = "Mendeley Document"
        verbose_name_plural = "Mendeley Documents"
        ordering = ['-year', '-created', '-created_at']
        unique_together = ['profile', 'mendeley_id']
        indexes = [
            models.Index(fields=['profile', '-year']),
            models.Index(fields=['doi']),
            models.Index(fields=['pmid']),
            models.Index(fields=['document_type']),
            models.Index(fields=['is_imported']),
            models.Index(fields=['created']),
        ]
    
    def __str__(self):
        return f"{self.title[:100]} ({self.year or 'Unknown year'})"
    
    def get_authors_display(self):
        """Get formatted author string"""
        if not self.authors:
            return "Unknown authors"
        
        author_names = []
        for author in self.authors:
            if isinstance(author, dict):
                parts = []
                if author.get('first_name'):
                    parts.append(author['first_name'])
                if author.get('last_name'):
                    parts.append(author['last_name'])
                if parts:
                    author_names.append(' '.join(parts))
            elif isinstance(author, str):
                author_names.append(author)
        
        if len(author_names) <= 3:
            return ', '.join(author_names)
        else:
            return f"{', '.join(author_names[:3])}, et al."
    
    def get_citation_format(self, style='apa'):
        """Generate citation in specified format"""
        authors = self.get_authors_display()
        year = f"({self.year})" if self.year else "(n.d.)"
        title = self.title
        
        if style == 'apa':
            citation = f"{authors} {year}. {title}."
            if self.source:
                citation += f" {self.source}"
                if self.volume:
                    citation += f", {self.volume}"
                    if self.issue:
                        citation += f"({self.issue})"
                if self.pages:
                    citation += f", {self.pages}"
            citation += "."
            if self.doi:
                citation += f" https://doi.org/{self.doi}"
            return citation
        
        return f"{authors} {year}. {title}."
    
    def can_import_to_scholar(self):
        """Check if document can be imported to Scholar module"""
        return (
            not self.is_imported and 
            self.title and 
            self.document_type in ['journal', 'conference_proceedings', 'book', 'book_section']
        )
    
    def get_publication_date(self):
        """Get the publication date as a readable string"""
        if self.year:
            if self.month and self.day:
                try:
                    from datetime import date
                    return date(self.year, self.month, self.day).strftime("%B %d, %Y")
                except ValueError:
                    pass
            if self.month:
                try:
                    from datetime import date
                    return date(self.year, self.month, 1).strftime("%B %Y")
                except ValueError:
                    pass
            return str(self.year)
        return "Unknown date"


class MendeleyGroup(models.Model):
    """Mendeley groups that the user belongs to"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(MendeleyProfile, on_delete=models.CASCADE, related_name='mendeley_groups')
    
    # Group information
    mendeley_group_id = models.CharField(max_length=100, help_text="Mendeley group ID")
    name = models.CharField(max_length=255, help_text="Group name")
    description = models.TextField(blank=True)
    
    # Group metadata
    group_type = models.CharField(max_length=50, blank=True, help_text="Type of group (private, public, etc.)")
    role = models.CharField(max_length=50, blank=True, help_text="User's role in group")
    access_level = models.CharField(max_length=50, blank=True, help_text="Access level")
    
    # Sync settings
    sync_enabled = models.BooleanField(default=True, help_text="Sync documents from this group")
    
    # Mendeley metadata
    mendeley_raw_data = models.JSONField(default=dict, blank=True, help_text="Raw Mendeley group data")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'mendeley_app'
        verbose_name = "Mendeley Group"
        verbose_name_plural = "Mendeley Groups"
        ordering = ['name']
        unique_together = ['profile', 'mendeley_group_id']
        indexes = [
            models.Index(fields=['profile']),
            models.Index(fields=['mendeley_group_id']),
        ]
    
    def __str__(self):
        return f"{self.name} (Group)"


class MendeleyFolder(models.Model):
    """Mendeley folders for organizing documents"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(MendeleyProfile, on_delete=models.CASCADE, related_name='mendeley_folders')
    
    # Folder information
    mendeley_folder_id = models.CharField(max_length=100, help_text="Mendeley folder ID")
    name = models.CharField(max_length=255, help_text="Folder name")
    
    # Hierarchy support
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    
    # Documents in this folder (many-to-many relationship)
    documents = models.ManyToManyField(MendeleyDocument, blank=True, related_name='folders')
    
    # Mendeley metadata
    mendeley_raw_data = models.JSONField(default=dict, blank=True, help_text="Raw Mendeley folder data")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'mendeley_app'
        verbose_name = "Mendeley Folder"
        verbose_name_plural = "Mendeley Folders"
        ordering = ['name']
        unique_together = ['profile', 'mendeley_folder_id']
        indexes = [
            models.Index(fields=['profile']),
            models.Index(fields=['mendeley_folder_id']),
            models.Index(fields=['parent_folder']),
        ]
    
    def __str__(self):
        return f"{self.name} (Folder)"
    
    def get_full_path(self):
        """Get the full path of the folder"""
        if self.parent_folder:
            return f"{self.parent_folder.get_full_path()}/{self.name}"
        return self.name


class MendeleySyncLog(models.Model):
    """Log Mendeley synchronization activities"""
    
    SYNC_TYPES = [
        ('profile', 'Profile Sync'),
        ('documents', 'Documents Sync'),
        ('groups', 'Groups Sync'),
        ('folders', 'Folders Sync'),
        ('full', 'Full Sync'),
    ]
    
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(MendeleyProfile, on_delete=models.CASCADE, related_name='sync_logs')
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    
    # Sync results
    items_processed = models.IntegerField(default=0)
    items_created = models.IntegerField(default=0)
    items_updated = models.IntegerField(default=0)
    items_skipped = models.IntegerField(default=0)
    
    # Error information
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    class Meta:
        app_label = 'mendeley_app'
        verbose_name = "Mendeley Sync Log"
        verbose_name_plural = "Mendeley Sync Logs"
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['profile', '-started_at']),
            models.Index(fields=['status']),
            models.Index(fields=['sync_type']),
        ]
    
    def __str__(self):
        return f"{self.sync_type} sync for {self.profile.get_display_name()} - {self.status}"
    
    def mark_completed(self, status='success'):
        """Mark sync as completed with status"""
        self.completed_at = timezone.now()
        self.status = status
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.save()
    
    def add_error(self, message, details=None):
        """Add error information to the sync log"""
        self.error_message = message
        if details:
            self.error_details = details
        self.status = 'failed'
        self.save()
    
    def get_success_rate(self):
        """Calculate success rate for this sync"""
        if self.items_processed == 0:
            return 0.0
        return (self.items_created + self.items_updated) / self.items_processed * 100