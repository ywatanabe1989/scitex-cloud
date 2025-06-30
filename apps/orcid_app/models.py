from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid
import json


class OrcidOAuth2Token(models.Model):
    """Store ORCID OAuth2 tokens for authenticated users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='orcid_token')
    access_token = models.CharField(max_length=255, help_text="ORCID access token")
    refresh_token = models.CharField(max_length=255, blank=True, help_text="ORCID refresh token")
    token_type = models.CharField(max_length=50, default='bearer')
    scope = models.CharField(max_length=255, help_text="OAuth scope granted")
    expires_at = models.DateTimeField(help_text="Token expiration time")
    orcid_id = models.CharField(max_length=19, help_text="ORCID iD (e.g., 0000-0000-0000-0000)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "ORCID OAuth2 Token"
        verbose_name_plural = "ORCID OAuth2 Tokens"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['orcid_id']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"ORCID Token for {self.user.username} ({self.orcid_id})"
    
    def is_expired(self):
        """Check if the token has expired"""
        return timezone.now() >= self.expires_at
    
    def is_expiring_soon(self, hours=24):
        """Check if token expires within specified hours"""
        return timezone.now() + timedelta(hours=hours) >= self.expires_at
    
    def get_authorization_header(self):
        """Get formatted authorization header"""
        return f"Bearer {self.access_token}"


class OrcidProfile(models.Model):
    """ORCID profile information for users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='orcid_profile')
    orcid_id = models.CharField(max_length=19, unique=True, help_text="ORCID iD (e.g., 0000-0000-0000-0000)")
    
    # Basic profile information
    given_name = models.CharField(max_length=255, blank=True)
    family_name = models.CharField(max_length=255, blank=True)
    credit_name = models.CharField(max_length=255, blank=True, help_text="Published/Credit name")
    biography = models.TextField(blank=True)
    
    # Contact information
    researcher_urls = models.JSONField(default=list, blank=True, help_text="List of researcher URLs")
    keywords = models.JSONField(default=list, blank=True, help_text="Research keywords")
    
    # Affiliation information
    current_affiliation = models.CharField(max_length=500, blank=True)
    affiliations = models.JSONField(default=list, blank=True, help_text="List of all affiliations")
    
    # Sync settings
    is_synced = models.BooleanField(default=False, help_text="Profile has been synced with ORCID")
    last_sync_at = models.DateTimeField(null=True, blank=True)
    sync_publications = models.BooleanField(default=True, help_text="Auto-sync publications from ORCID")
    auto_sync_enabled = models.BooleanField(default=True, help_text="Enable automatic periodic sync")
    
    # Privacy settings
    public_profile = models.BooleanField(default=True, help_text="Make ORCID profile visible to other users")
    show_publications = models.BooleanField(default=True, help_text="Show ORCID publications in Scholar")
    
    # Metadata
    orcid_record = models.JSONField(default=dict, blank=True, help_text="Raw ORCID record data")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "ORCID Profile"
        verbose_name_plural = "ORCID Profiles"
        ordering = ['family_name', 'given_name']
        indexes = [
            models.Index(fields=['orcid_id']),
            models.Index(fields=['user']),
            models.Index(fields=['last_sync_at']),
        ]
    
    def __str__(self):
        name = self.get_display_name()
        return f"{name} ({self.orcid_id})"
    
    def get_display_name(self):
        """Get the best display name for this profile"""
        if self.credit_name:
            return self.credit_name
        elif self.given_name and self.family_name:
            return f"{self.given_name} {self.family_name}"
        elif self.family_name:
            return self.family_name
        return self.user.get_full_name() or self.user.username
    
    def get_orcid_url(self):
        """Get the full ORCID profile URL"""
        return f"https://orcid.org/{self.orcid_id}"
    
    def needs_sync(self, hours=24):
        """Check if profile needs syncing (hasn't been synced in X hours)"""
        if not self.last_sync_at:
            return True
        return timezone.now() - self.last_sync_at > timedelta(hours=hours)
    
    def get_publication_count(self):
        """Get the count of ORCID publications"""
        return self.orcid_publications.count()
    
    def get_recent_publications(self, limit=5):
        """Get recent ORCID publications"""
        return self.orcid_publications.order_by('-publication_year', '-created_at')[:limit]


class OrcidPublication(models.Model):
    """Publications from ORCID records"""
    
    PUBLICATION_TYPES = [
        ('journal-article', 'Journal Article'),
        ('book', 'Book'),
        ('book-chapter', 'Book Chapter'),
        ('book-review', 'Book Review'),
        ('conference-paper', 'Conference Paper'),
        ('conference-abstract', 'Conference Abstract'),
        ('conference-poster', 'Conference Poster'),
        ('dissertation', 'Dissertation'),
        ('edited-book', 'Edited Book'),
        ('encyclopedia-entry', 'Encyclopedia Entry'),
        ('magazine-article', 'Magazine Article'),
        ('manual', 'Manual'),
        ('newsletter-article', 'Newsletter Article'),
        ('newspaper-article', 'Newspaper Article'),
        ('online-resource', 'Online Resource'),
        ('other', 'Other'),
        ('patent', 'Patent'),
        ('registered-copyright', 'Registered Copyright'),
        ('report', 'Report'),
        ('research-tool', 'Research Tool'),
        ('supervised-student-publication', 'Supervised Student Publication'),
        ('test', 'Test'),
        ('translation', 'Translation'),
        ('website', 'Website'),
        ('working-paper', 'Working Paper'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(OrcidProfile, on_delete=models.CASCADE, related_name='orcid_publications')
    
    # Basic publication information
    title = models.TextField(help_text="Publication title")
    publication_type = models.CharField(max_length=50, choices=PUBLICATION_TYPES, default='journal-article')
    publication_year = models.IntegerField(null=True, blank=True)
    publication_date = models.DateField(null=True, blank=True, help_text="Full publication date if available")
    
    # Publication venue
    journal = models.CharField(max_length=500, blank=True, help_text="Journal or venue name")
    volume = models.CharField(max_length=50, blank=True)
    issue = models.CharField(max_length=50, blank=True)
    pages = models.CharField(max_length=100, blank=True)
    
    # Identifiers
    doi = models.CharField(max_length=255, blank=True, db_index=True)
    pmid = models.CharField(max_length=20, blank=True, help_text="PubMed ID")
    isbn = models.CharField(max_length=20, blank=True)
    issn = models.CharField(max_length=9, blank=True)
    url = models.URLField(blank=True)
    
    # Content
    abstract = models.TextField(blank=True)
    authors = models.JSONField(default=list, blank=True, help_text="List of authors")
    
    # ORCID-specific data
    orcid_put_code = models.CharField(max_length=50, help_text="ORCID put-code for this work")
    orcid_raw_data = models.JSONField(default=dict, blank=True, help_text="Raw ORCID API response")
    
    # Integration with Scholar module
    is_imported = models.BooleanField(default=False, help_text="Imported into Scholar module")
    scholar_paper = models.ForeignKey(
        'scholar_app.SearchIndex', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='orcid_publications',
        help_text="Linked Scholar paper"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "ORCID Publication"
        verbose_name_plural = "ORCID Publications"
        ordering = ['-publication_year', '-created_at']
        unique_together = ['profile', 'orcid_put_code']
        indexes = [
            models.Index(fields=['profile', '-publication_year']),
            models.Index(fields=['doi']),
            models.Index(fields=['pmid']),
            models.Index(fields=['publication_type']),
            models.Index(fields=['is_imported']),
        ]
    
    def __str__(self):
        return f"{self.title[:100]} ({self.publication_year or 'Unknown year'})"
    
    def get_authors_display(self):
        """Get formatted author string"""
        if not self.authors:
            return "Unknown authors"
        
        author_names = []
        for author in self.authors:
            if isinstance(author, dict):
                name_parts = []
                if author.get('given-names'):
                    name_parts.append(author['given-names'])
                if author.get('family-name'):
                    name_parts.append(author['family-name'])
                if name_parts:
                    author_names.append(' '.join(name_parts))
                elif author.get('credit-name'):
                    author_names.append(author['credit-name'])
            elif isinstance(author, str):
                author_names.append(author)
        
        if len(author_names) <= 3:
            return ', '.join(author_names)
        else:
            return f"{', '.join(author_names[:3])}, et al."
    
    def get_citation_format(self, style='apa'):
        """Generate citation in specified format"""
        authors = self.get_authors_display()
        year = f"({self.publication_year})" if self.publication_year else "(n.d.)"
        title = self.title
        
        if style == 'apa':
            citation = f"{authors} {year}. {title}."
            if self.journal:
                citation += f" {self.journal}"
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
        """Check if publication can be imported to Scholar module"""
        return (
            not self.is_imported and 
            self.title and 
            self.publication_type in ['journal-article', 'conference-paper', 'book', 'book-chapter']
        )


class OrcidWork(models.Model):
    """Generic ORCID works (broader than publications)"""
    
    WORK_TYPES = [
        ('artistic-performance', 'Artistic Performance'),
        ('book-chapter', 'Book Chapter'),
        ('book-review', 'Book Review'),
        ('book', 'Book'),
        ('conference-abstract', 'Conference Abstract'),
        ('conference-paper', 'Conference Paper'),
        ('conference-poster', 'Conference Poster'),
        ('data-set', 'Dataset'),
        ('dictionary-entry', 'Dictionary Entry'),
        ('disclosure', 'Disclosure'),
        ('dissertation', 'Dissertation'),
        ('edited-book', 'Edited Book'),
        ('encyclopedia-entry', 'Encyclopedia Entry'),
        ('invention', 'Invention'),
        ('journal-article', 'Journal Article'),
        ('journal-issue', 'Journal Issue'),
        ('lecture-speech', 'Lecture/Speech'),
        ('license', 'License'),
        ('magazine-article', 'Magazine Article'),
        ('manual', 'Manual'),
        ('newsletter-article', 'Newsletter Article'),
        ('newspaper-article', 'Newspaper Article'),
        ('online-resource', 'Online Resource'),
        ('other', 'Other'),
        ('patent', 'Patent'),
        ('registered-copyright', 'Registered Copyright'),
        ('report', 'Report'),
        ('research-technique', 'Research Technique'),
        ('research-tool', 'Research Tool'),
        ('spin-off-company', 'Spin-off Company'),
        ('standards-and-policy', 'Standards and Policy'),
        ('supervised-student-publication', 'Supervised Student Publication'),
        ('technical-standard', 'Technical Standard'),
        ('test', 'Test'),
        ('trademark', 'Trademark'),
        ('translation', 'Translation'),
        ('website', 'Website'),
        ('working-paper', 'Working Paper'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(OrcidProfile, on_delete=models.CASCADE, related_name='orcid_works')
    
    # Basic work information
    title = models.TextField(help_text="Work title")
    work_type = models.CharField(max_length=50, choices=WORK_TYPES)
    publication_date = models.DateField(null=True, blank=True)
    
    # Publication details
    journal_title = models.CharField(max_length=500, blank=True)
    short_description = models.TextField(blank=True)
    
    # External identifiers
    external_ids = models.JSONField(default=list, blank=True, help_text="External identifiers (DOI, etc.)")
    url = models.URLField(blank=True)
    
    # ORCID data
    put_code = models.CharField(max_length=50, help_text="ORCID put-code")
    raw_data = models.JSONField(default=dict, blank=True, help_text="Raw ORCID work data")
    
    # Integration status
    is_imported = models.BooleanField(default=False, help_text="Imported to relevant SciTeX module")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "ORCID Work"
        verbose_name_plural = "ORCID Works"
        ordering = ['-publication_date', '-created_at']
        unique_together = ['profile', 'put_code']
        indexes = [
            models.Index(fields=['profile', '-publication_date']),
            models.Index(fields=['work_type']),
            models.Index(fields=['is_imported']),
        ]
    
    def __str__(self):
        return f"{self.title[:100]} ({self.work_type})"
    
    def get_doi(self):
        """Extract DOI from external identifiers"""
        for ext_id in self.external_ids:
            if ext_id.get('external-id-type') == 'doi':
                return ext_id.get('external-id-value')
        return None


class OrcidSyncLog(models.Model):
    """Log ORCID synchronization activities"""
    
    SYNC_TYPES = [
        ('profile', 'Profile Sync'),
        ('publications', 'Publications Sync'),
        ('works', 'Works Sync'),
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
    profile = models.ForeignKey(OrcidProfile, on_delete=models.CASCADE, related_name='sync_logs')
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
        verbose_name = "ORCID Sync Log"
        verbose_name_plural = "ORCID Sync Logs"
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