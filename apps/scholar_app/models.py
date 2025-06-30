from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings
import uuid
import base64


class Author(models.Model):
    """Author information for research papers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    orcid = models.CharField(max_length=19, blank=True, db_index=True)  # ORCID format: 0000-0000-0000-0000
    email = models.EmailField(blank=True)
    affiliation = models.CharField(max_length=500, blank=True)
    h_index = models.IntegerField(null=True, blank=True)
    total_citations = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['orcid']),
        ]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    @property
    def full_name(self):
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return ' '.join(parts)


class Journal(models.Model):
    """Journal metadata"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=500, unique=True)
    abbreviation = models.CharField(max_length=100, blank=True)
    issn = models.CharField(max_length=9, blank=True, db_index=True)  # Format: 0000-0000
    eissn = models.CharField(max_length=9, blank=True)  # Electronic ISSN
    publisher = models.CharField(max_length=200, blank=True)
    impact_factor = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    website = models.URLField(blank=True)
    open_access = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['issn']),
        ]

    def __str__(self):
        return self.name


class Topic(models.Model):
    """Research topics/keywords"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    description = models.TextField(blank=True)
    paper_count = models.IntegerField(default=0)  # Denormalized for performance
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


class SearchIndex(models.Model):
    """Main search index for documents and research papers"""
    SOURCE_CHOICES = [
        ('pubmed', 'PubMed'),
        ('arxiv', 'arXiv'),
        ('doi', 'DOI'),
        ('google_scholar', 'Google Scholar'),
        ('internal', 'Internal'),
        ('manual', 'Manual Entry'),
    ]

    DOCUMENT_TYPE_CHOICES = [
        ('article', 'Journal Article'),
        ('preprint', 'Preprint'),
        ('book', 'Book'),
        ('chapter', 'Book Chapter'),
        ('conference', 'Conference Paper'),
        ('thesis', 'Thesis/Dissertation'),
        ('report', 'Technical Report'),
        ('dataset', 'Dataset'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('retracted', 'Retracted'),
        ('pending', 'Pending Review'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic metadata
    title = models.TextField(db_index=True)
    abstract = models.TextField(blank=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='article')
    publication_date = models.DateField(null=True, blank=True, db_index=True)
    
    # Authors and affiliations
    authors = models.ManyToManyField(Author, through='AuthorPaper')
    journal = models.ForeignKey(Journal, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Identifiers
    doi = models.CharField(max_length=100, blank=True, unique=True, null=True, db_index=True)
    pmid = models.CharField(max_length=20, blank=True, unique=True, null=True, db_index=True)  # PubMed ID
    arxiv_id = models.CharField(max_length=20, blank=True, unique=True, null=True, db_index=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='manual')
    external_url = models.URLField(blank=True)
    
    # Content
    full_text = models.TextField(blank=True)
    pdf_url = models.URLField(blank=True)
    pdf_file = models.FileField(upload_to='scholar/pdfs/', blank=True, null=True)
    bibtex_file = models.FileField(upload_to='scholar/bibtex/', blank=True, null=True)
    bibtex_content = models.TextField(blank=True, help_text="BibTeX citation content")
    
    # Search optimization
    # search_vector = SearchVectorField(null=True)  # PostgreSQL full-text search - commented for compatibility
    keywords = models.TextField(blank=True)  # Store as comma-separated values for SQLite compatibility
    topics = models.ManyToManyField(Topic, blank=True)
    
    # Metrics
    citation_count = models.IntegerField(default=0)
    citation_source = models.CharField(max_length=50, blank=True, help_text="Source of citation data (semantic_scholar, crossref, etc.)")
    citation_last_updated = models.DateTimeField(null=True, blank=True, help_text="When citation count was last updated")
    view_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    relevance_score = models.FloatField(default=0.0)  # Custom relevance scoring
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_open_access = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    indexed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-publication_date', '-relevance_score']
        indexes = [
            models.Index(fields=['publication_date', 'relevance_score']),
            models.Index(fields=['doi']),
            models.Index(fields=['pmid']),
            models.Index(fields=['arxiv_id']),
            # GinIndex(fields=['search_vector']),  # PostgreSQL specific - commented for compatibility
        ]

    def __str__(self):
        return self.title[:100]


class AuthorPaper(models.Model):
    """Through model for Author-Paper relationship with ordering"""
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    paper = models.ForeignKey(SearchIndex, on_delete=models.CASCADE)
    author_order = models.IntegerField(default=1)
    is_corresponding = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['author_order']
        unique_together = ['author', 'paper']


class Citation(models.Model):
    """Paper citations and references"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    citing_paper = models.ForeignKey(SearchIndex, on_delete=models.CASCADE, related_name='citations_made')
    cited_paper = models.ForeignKey(SearchIndex, on_delete=models.CASCADE, related_name='citations_received')
    citation_context = models.TextField(blank=True)  # Text around the citation
    section = models.CharField(max_length=50, blank=True)  # Section where citation appears
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['citing_paper', 'cited_paper']
        indexes = [
            models.Index(fields=['citing_paper', 'cited_paper']),
        ]

    def __str__(self):
        return f"{self.citing_paper.title[:50]} cites {self.cited_paper.title[:50]}"


class SearchQuery(models.Model):
    """Track user searches"""
    SEARCH_TYPE_CHOICES = [
        ('simple', 'Simple Search'),
        ('advanced', 'Advanced Search'),
        ('author', 'Author Search'),
        ('citation', 'Citation Search'),
        ('semantic', 'Semantic Search'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_queries')
    query_text = models.TextField()
    search_type = models.CharField(max_length=20, choices=SEARCH_TYPE_CHOICES, default='simple')
    filters = models.JSONField(default=dict, blank=True)  # Store applied filters
    result_count = models.IntegerField(default=0)
    execution_time = models.FloatField(null=True, blank=True)  # in seconds
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.query_text[:50]}"


class SearchResult(models.Model):
    """Store search results"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    search_query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, related_name='results')
    paper = models.ForeignKey(SearchIndex, on_delete=models.CASCADE)
    rank = models.IntegerField()
    score = models.FloatField()  # Relevance score
    snippet = models.TextField(blank=True)  # Highlighted snippet
    clicked = models.BooleanField(default=False)
    click_timestamp = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['search_query', 'rank']
        indexes = [
            models.Index(fields=['search_query', 'rank']),
        ]

    def __str__(self):
        return f"Result {self.rank} for query {self.search_query.id}"


class SearchFilter(models.Model):
    """Advanced search filters"""
    FILTER_TYPE_CHOICES = [
        ('date_range', 'Date Range'),
        ('author', 'Author'),
        ('journal', 'Journal'),
        ('topic', 'Topic'),
        ('citation_count', 'Citation Count'),
        ('document_type', 'Document Type'),
        ('open_access', 'Open Access'),
        ('language', 'Language'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    filter_type = models.CharField(max_length=20, choices=FILTER_TYPE_CHOICES)
    description = models.TextField(blank=True)
    configuration = models.JSONField(default=dict)  # Store filter-specific config
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['filter_type', 'name']

    def __str__(self):
        return f"{self.filter_type}: {self.name}"


class SavedSearch(models.Model):
    """User's saved searches"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('never', 'Never'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=200)
    query_text = models.TextField()
    search_type = models.CharField(max_length=20, choices=SearchQuery.SEARCH_TYPE_CHOICES)
    filters = models.JSONField(default=dict, blank=True)
    email_alerts = models.BooleanField(default=False)
    alert_frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='never')
    last_run = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.user.username}: {self.name}"


class Collection(models.Model):
    """User's collections for organizing papers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project = models.ForeignKey('project_app.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='collections', help_text="Associated research project")
    color = models.CharField(max_length=7, default='#1a2332', help_text="Hex color code for collection")
    icon = models.CharField(max_length=50, default='fas fa-folder', help_text="FontAwesome icon class")
    is_public = models.BooleanField(default=False, help_text="Allow others to see this collection")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['user', 'name']
        indexes = [
            models.Index(fields=['user', 'name']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.name}"
    
    def paper_count(self):
        """Get number of papers in this collection"""
        return self.library_papers.count()


class UserLibrary(models.Model):
    """User's personal library of saved papers with files"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='library_papers')
    paper = models.ForeignKey(SearchIndex, on_delete=models.CASCADE, related_name='saved_by_users')
    collections = models.ManyToManyField(Collection, blank=True, related_name='library_papers')
    project = models.ForeignKey('project_app.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='saved_papers', help_text="Associated research project")
    
    # User's personal files for this paper
    personal_pdf = models.FileField(upload_to='user_library/pdfs/', blank=True, null=True)
    personal_bibtex = models.FileField(upload_to='user_library/bibtex/', blank=True, null=True)
    personal_notes = models.TextField(blank=True, help_text="Personal notes about this paper")
    tags = models.CharField(max_length=500, blank=True, help_text="Personal tags, comma-separated")
    
    # Reading status
    READING_STATUS_CHOICES = [
        ('to_read', 'To Read'),
        ('reading', 'Currently Reading'),
        ('read', 'Completed'),
        ('referenced', 'For Reference'),
        ('favorite', 'Favorite'),
    ]
    reading_status = models.CharField(max_length=20, choices=READING_STATUS_CHOICES, default='to_read')
    
    # Rating and importance
    importance_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    
    # Export tracking
    exported_count = models.IntegerField(default=0, help_text="Number of times this paper was exported")
    last_exported = models.DateTimeField(null=True, blank=True)
    
    saved_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-saved_at']
        unique_together = ['user', 'paper']
        indexes = [
            models.Index(fields=['user', '-saved_at']),
            models.Index(fields=['project']),
            models.Index(fields=['reading_status']),
            models.Index(fields=['importance_rating']),
        ]
    
    def __str__(self):
        return f"{self.user.username} saved: {self.paper.title[:50]}"
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def get_collections_display(self):
        """Get formatted collection names"""
        return ', '.join([collection.name for collection in self.collections.all()])


class LibraryExport(models.Model):
    """Track library exports for analytics"""
    EXPORT_FORMAT_CHOICES = [
        ('bibtex', 'BibTeX'),
        ('endnote', 'EndNote'),
        ('ris', 'RIS'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('pdf_bundle', 'PDF Bundle'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='library_exports')
    export_format = models.CharField(max_length=20, choices=EXPORT_FORMAT_CHOICES)
    paper_count = models.IntegerField()
    collection_name = models.CharField(max_length=200, blank=True, help_text="Collection name if exported")
    filter_criteria = models.JSONField(default=dict, blank=True, help_text="Applied filters during export")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['export_format']),
        ]
    
    def __str__(self):
        return f"{self.user.username} exported {self.paper_count} papers as {self.export_format}"


class RecommendationLog(models.Model):
    """Track AI recommendations"""
    RECOMMENDATION_TYPE_CHOICES = [
        ('similar', 'Similar Papers'),
        ('author_based', 'Based on Author'),
        ('citation_based', 'Based on Citations'),
        ('topic_based', 'Based on Topics'),
        ('collaborative', 'Collaborative Filtering'),
        ('trending', 'Trending Papers'),
    ]

    FEEDBACK_CHOICES = [
        ('helpful', 'Helpful'),
        ('not_helpful', 'Not Helpful'),
        ('neutral', 'Neutral'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    source_paper = models.ForeignKey(SearchIndex, on_delete=models.CASCADE, related_name='recommendation_source', null=True, blank=True)
    recommended_paper = models.ForeignKey(SearchIndex, on_delete=models.CASCADE, related_name='recommended_as')
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPE_CHOICES)
    score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    reason = models.TextField(blank=True)  # Explanation for recommendation
    clicked = models.BooleanField(default=False)
    feedback = models.CharField(max_length=20, choices=FEEDBACK_CHOICES, blank=True)
    feedback_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    interacted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['recommendation_type', '-score']),
        ]

    def __str__(self):
        return f"Recommendation for {self.user.username}: {self.recommended_paper.title[:50]}"


class Annotation(models.Model):
    """User annotations on research papers"""
    ANNOTATION_TYPE_CHOICES = [
        ('highlight', 'Text Highlight'),
        ('note', 'Margin Note'),
        ('comment', 'General Comment'),
        ('question', 'Question'),
        ('important', 'Important Point'),
        ('critique', 'Critical Analysis'),
        ('summary', 'Summary'),
        ('methodology', 'Methodology Note'),
    ]
    
    PRIVACY_CHOICES = [
        ('private', 'Private (Only Me)'),
        ('shared', 'Shared with Collaborators'),
        ('public', 'Public (Anyone can view)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='annotations')
    paper = models.ForeignKey(SearchIndex, on_delete=models.CASCADE, related_name='annotations')
    
    # Annotation content
    annotation_type = models.CharField(max_length=20, choices=ANNOTATION_TYPE_CHOICES, default='note')
    text_content = models.TextField(help_text="The annotation text/note content")
    highlighted_text = models.TextField(blank=True, help_text="The text that was highlighted (if applicable)")
    
    # Position information (for PDF/document positioning)
    page_number = models.IntegerField(null=True, blank=True, help_text="Page number in document")
    position_data = models.JSONField(default=dict, blank=True, help_text="JSON data for precise positioning")
    
    # Collaboration and sharing
    privacy_level = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='private')
    shared_with = models.ManyToManyField(User, blank=True, related_name='shared_annotations')
    tags = models.ManyToManyField('AnnotationTag', blank=True, related_name='annotations')
    
    # Metadata
    is_resolved = models.BooleanField(default=False, help_text="For questions/issues - mark as resolved")
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['paper', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['annotation_type']),
            models.Index(fields=['privacy_level']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.annotation_type} on {self.paper.title[:50]}"
    
    def get_vote_score(self):
        """Calculate net vote score"""
        return self.upvotes - self.downvotes


class AnnotationReply(models.Model):
    """Replies/responses to annotations for collaborative discussion"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='annotation_replies')
    parent_reply = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='nested_replies')
    
    content = models.TextField(help_text="Reply content")
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['annotation', 'created_at']),
        ]
    
    def __str__(self):
        return f"Reply by {self.user.username} to annotation {self.annotation.id}"
    
    def get_vote_score(self):
        """Calculate net vote score"""
        return self.upvotes - self.downvotes


class AnnotationVote(models.Model):
    """Track user votes on annotations and replies"""
    VOTE_CHOICES = [
        ('up', 'Upvote'),
        ('down', 'Downvote'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='annotation_votes')
    annotation = models.ForeignKey(Annotation, null=True, blank=True, on_delete=models.CASCADE, related_name='votes')
    reply = models.ForeignKey(AnnotationReply, null=True, blank=True, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=5, choices=VOTE_CHOICES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Ensure one vote per user per annotation/reply
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'annotation'],
                condition=models.Q(annotation__isnull=False),
                name='unique_user_annotation_vote'
            ),
            models.UniqueConstraint(
                fields=['user', 'reply'],
                condition=models.Q(reply__isnull=False),
                name='unique_user_reply_vote'
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'annotation']),
            models.Index(fields=['user', 'reply']),
        ]
    
    def __str__(self):
        target = self.annotation or self.reply
        return f"{self.user.username} {self.vote_type}voted {target}"


class CollaborationGroup(models.Model):
    """Groups for collaborative annotation sharing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_groups')
    members = models.ManyToManyField(User, through='GroupMembership', related_name='collaboration_groups')
    
    # Group settings
    is_public = models.BooleanField(default=False, help_text="Allow anyone to join")
    auto_approve_members = models.BooleanField(default=True, help_text="Auto-approve membership requests")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['is_public']),
        ]
    
    def __str__(self):
        return f"Group: {self.name} (owned by {self.owner.username})"
    
    def member_count(self):
        """Get total number of members"""
        return self.members.count()


class GroupMembership(models.Model):
    """Through model for CollaborationGroup membership with roles"""
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('invited', 'Invited'),
        ('requested', 'Requested'),
        ('suspended', 'Suspended'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(CollaborationGroup, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'group']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['group', 'role']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.role} in {self.group.name}"


class AnnotationTag(models.Model):
    """Tags for organizing and categorizing annotations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#1a2332', help_text="Hex color code")
    description = models.TextField(blank=True)
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['-usage_count']),
        ]
    
    def __str__(self):
        return self.name


# Research Data Repository Models
class Repository(models.Model):
    """Research data repositories (Zenodo, Figshare, Dryad, etc.)"""
    REPOSITORY_TYPES = [
        ('zenodo', 'Zenodo'),
        ('figshare', 'Figshare'),
        ('dryad', 'Dryad'),
        ('harvard_dataverse', 'Harvard Dataverse'),
        ('osf', 'Open Science Framework'),
        ('mendeley_data', 'Mendeley Data'),
        ('institutional', 'Institutional Repository'),
        ('custom', 'Custom Repository'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
        ('deprecated', 'Deprecated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    repository_type = models.CharField(max_length=30, choices=REPOSITORY_TYPES)
    description = models.TextField(blank=True)
    
    # API Configuration
    api_base_url = models.URLField()
    api_version = models.CharField(max_length=20, default='v1')
    api_documentation_url = models.URLField(blank=True)
    
    # Repository metadata
    website_url = models.URLField(blank=True)
    supports_doi = models.BooleanField(default=True)
    supports_versioning = models.BooleanField(default=True)
    supports_private_datasets = models.BooleanField(default=True)
    max_file_size_mb = models.IntegerField(default=50000)  # 50GB default
    max_dataset_size_mb = models.IntegerField(default=50000)
    
    # Access and features
    requires_authentication = models.BooleanField(default=True)
    supports_metadata_formats = models.JSONField(default=list)  # ['dublin_core', 'datacite', 'dcat']
    supported_file_formats = models.JSONField(default=list)
    license_options = models.JSONField(default=list)
    
    # Repository status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_open_access = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)  # Default repository for new deposits
    
    # Usage statistics
    total_deposits = models.IntegerField(default=0)
    active_connections = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['repository_type', 'status']),
            models.Index(fields=['is_default']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_repository_type_display()})"


class RepositoryConnection(models.Model):
    """User's connection credentials to research data repositories"""
    CONNECTION_STATUS = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('invalid', 'Invalid'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending Verification'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repository_connections')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='user_connections')
    
    # Authentication credentials (encrypted)
    api_token = models.CharField(max_length=500, blank=True)
    api_secret = models.CharField(max_length=500, blank=True)
    oauth_token = models.CharField(max_length=500, blank=True)
    oauth_refresh_token = models.CharField(max_length=500, blank=True)
    username = models.CharField(max_length=200, blank=True)
    
    # Connection metadata
    connection_name = models.CharField(max_length=200, help_text="User-defined name for this connection")
    status = models.CharField(max_length=20, choices=CONNECTION_STATUS, default='pending')
    last_verified = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # User preferences
    is_default = models.BooleanField(default=False)
    auto_sync_enabled = models.BooleanField(default=True)
    notification_enabled = models.BooleanField(default=True)
    
    # Usage tracking
    total_deposits = models.IntegerField(default=0)
    total_downloads = models.IntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    # Error tracking
    last_error = models.TextField(blank=True)
    error_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'repository', 'connection_name']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['repository', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} -> {self.repository.name} ({self.connection_name})"
    
    def is_active(self):
        """Check if connection is active and not expired"""
        if self.status != 'active':
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True


class Dataset(models.Model):
    """Research datasets stored in repositories"""
    DATASET_TYPES = [
        ('raw_data', 'Raw Data'),
        ('processed_data', 'Processed Data'),
        ('analysis_results', 'Analysis Results'),
        ('code_output', 'Code Execution Output'),
        ('supplementary', 'Supplementary Materials'),
        ('replication_data', 'Replication Data'),
        ('metadata', 'Metadata Only'),
    ]
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('restricted', 'Restricted Access'),
        ('embargoed', 'Embargoed'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('published', 'Published'),
        ('updated', 'Updated'),
        ('deprecated', 'Deprecated'),
        ('deleted', 'Deleted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic metadata
    title = models.CharField(max_length=500)
    description = models.TextField()
    dataset_type = models.CharField(max_length=30, choices=DATASET_TYPES)
    keywords = models.CharField(max_length=500, blank=True)
    
    # Ownership and collaboration
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_datasets')
    collaborators = models.ManyToManyField(User, related_name='shared_datasets', blank=True)
    
    # Repository information
    repository_connection = models.ForeignKey(RepositoryConnection, on_delete=models.CASCADE, related_name='datasets')
    repository_id = models.CharField(max_length=200, blank=True)  # ID in the external repository
    repository_url = models.URLField(blank=True)
    repository_doi = models.CharField(max_length=100, blank=True)
    
    # Version and status
    version = models.CharField(max_length=50, default='1.0')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    
    # File information
    file_count = models.IntegerField(default=0)
    total_size_bytes = models.BigIntegerField(default=0)
    file_formats = models.JSONField(default=list)  # List of file extensions
    
    # Licensing and access
    license = models.CharField(max_length=200, blank=True)
    access_conditions = models.TextField(blank=True)
    embargo_until = models.DateTimeField(null=True, blank=True)
    
    # Research context
    related_papers = models.ManyToManyField(SearchIndex, related_name='associated_datasets', blank=True)
    project = models.ForeignKey('project_app.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='datasets')
    
    # Code integration
    generated_by_job = models.ForeignKey('code_app.CodeExecutionJob', on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_datasets')
    associated_notebooks = models.ManyToManyField('code_app.Notebook', related_name='associated_datasets', blank=True)
    
    # Manuscript integration  
    cited_in_manuscripts = models.ManyToManyField('writer_app.Manuscript', related_name='cited_datasets', blank=True)
    
    # Usage and impact
    download_count = models.IntegerField(default=0)
    citation_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['repository_connection', 'status']),
            models.Index(fields=['dataset_type']),
            models.Index(fields=['visibility']),
            models.Index(fields=['-published_at']),
        ]
    
    def __str__(self):
        return f"{self.title} (v{self.version})"
    
    def get_file_size_display(self):
        """Return human-readable file size"""
        size_bytes = self.total_size_bytes
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def can_be_edited(self, user):
        """Check if user can edit this dataset"""
        return (user == self.owner or 
                user in self.collaborators.all() or
                user.is_staff)


class DatasetFile(models.Model):
    """Individual files within a dataset"""
    FILE_TYPES = [
        ('data', 'Data File'),
        ('code', 'Code File'),
        ('documentation', 'Documentation'),
        ('metadata', 'Metadata'),
        ('readme', 'README'),
        ('license', 'License'),
        ('figure', 'Figure/Image'),
        ('supplementary', 'Supplementary'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='files')
    
    # File information
    filename = models.CharField(max_length=500)
    file_path = models.CharField(max_length=1000, blank=True)  # Path within dataset
    file_type = models.CharField(max_length=30, choices=FILE_TYPES)
    file_format = models.CharField(max_length=50, blank=True)  # File extension
    
    # File metadata
    size_bytes = models.BigIntegerField()
    checksum_md5 = models.CharField(max_length=32, blank=True)
    checksum_sha256 = models.CharField(max_length=64, blank=True)
    mime_type = models.CharField(max_length=200, blank=True)
    
    # Repository information
    repository_file_id = models.CharField(max_length=200, blank=True)
    download_url = models.URLField(blank=True)
    preview_url = models.URLField(blank=True)
    
    # File content metadata
    description = models.TextField(blank=True)
    encoding = models.CharField(max_length=50, blank=True)
    
    # Local copy (optional)
    local_file = models.FileField(upload_to='dataset_files/', blank=True, null=True)
    
    # Usage tracking
    download_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['file_path', 'filename']
        unique_together = ['dataset', 'file_path', 'filename']
        indexes = [
            models.Index(fields=['dataset', 'file_type']),
            models.Index(fields=['file_format']),
        ]
    
    def __str__(self):
        return f"{self.filename} ({self.get_file_type_display()})"
    
    def get_size_display(self):
        """Return human-readable file size"""
        if self.size_bytes < 1024:
            return f"{self.size_bytes} B"
        elif self.size_bytes < 1024 * 1024:
            return f"{self.size_bytes / 1024:.1f} KB"
        elif self.size_bytes < 1024 * 1024 * 1024:
            return f"{self.size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{self.size_bytes / (1024 * 1024 * 1024):.1f} GB"


class DatasetVersion(models.Model):
    """Track versions of datasets for proper versioning"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='versions')
    
    # Version information
    version_number = models.CharField(max_length=50)
    version_description = models.TextField(blank=True)
    is_current = models.BooleanField(default=False)
    
    # Repository information
    repository_version_id = models.CharField(max_length=200, blank=True)
    repository_version_url = models.URLField(blank=True)
    version_doi = models.CharField(max_length=100, blank=True)
    
    # Changes from previous version
    changes_summary = models.TextField(blank=True)
    files_added = models.IntegerField(default=0)
    files_modified = models.IntegerField(default=0)
    files_deleted = models.IntegerField(default=0)
    
    # Metadata snapshot
    metadata_snapshot = models.JSONField(default=dict)
    file_listing = models.JSONField(default=list)
    
    # Version relationships
    parent_version = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_versions')
    
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['dataset', 'version_number']
        indexes = [
            models.Index(fields=['dataset', 'is_current']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.dataset.title} v{self.version_number}"


class RepositorySync(models.Model):
    """Track synchronization operations with repositories"""
    SYNC_TYPES = [
        ('upload', 'Upload to Repository'),
        ('download', 'Download from Repository'),
        ('metadata_update', 'Update Metadata'),
        ('status_check', 'Status Check'),
        ('full_sync', 'Full Synchronization'),
    ]
    
    SYNC_STATUS = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Sync target
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repository_syncs')
    repository_connection = models.ForeignKey(RepositoryConnection, on_delete=models.CASCADE, related_name='syncs')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='syncs', null=True, blank=True)
    
    # Sync details
    sync_type = models.CharField(max_length=30, choices=SYNC_TYPES)
    status = models.CharField(max_length=20, choices=SYNC_STATUS, default='pending')
    
    # Progress tracking
    total_items = models.IntegerField(default=0)
    completed_items = models.IntegerField(default=0)
    failed_items = models.IntegerField(default=0)
    total_bytes = models.BigIntegerField(default=0)
    transferred_bytes = models.BigIntegerField(default=0)
    
    # Results and logs
    result_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    sync_log = models.TextField(blank=True)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['repository_connection', 'sync_type']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        target = self.dataset.title if self.dataset else "Repository"
        return f"{self.get_sync_type_display()}: {target} ({self.status})"
    
    def get_progress_percentage(self):
        """Calculate progress percentage"""
        if self.total_items == 0:
            return 0
        return (self.completed_items / self.total_items) * 100
    
    def get_transfer_speed(self):
        """Calculate transfer speed in bytes per second"""
        if not self.started_at or self.transferred_bytes == 0:
            return 0
        
        if self.completed_at:
            duration = (self.completed_at - self.started_at).total_seconds()
        else:
            duration = (timezone.now() - self.started_at).total_seconds()
        
        if duration > 0:
            return self.transferred_bytes / duration
        return 0


class UserPreference(models.Model):
    """Store user-specific preferences for Scholar app"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='scholar_preferences')
    
    # Search source preferences
    preferred_sources = models.JSONField(
        default=dict,
        help_text="Dictionary of source preferences: {'pubmed': True, 'arxiv': True, etc.}"
    )
    
    # Search behavior preferences
    default_sort_by = models.CharField(
        max_length=20,
        choices=[
            ('relevance', 'Most Relevant'),
            ('date', 'Most Recent'),
            ('citations', 'Most Cited'),
        ],
        default='relevance'
    )
    
    # Filter preferences
    default_filters = models.JSONField(
        default=dict,
        help_text="Default filter settings: {'open_access': False, 'recent_only': False, etc.}"
    )
    
    # UI preferences
    results_per_page = models.IntegerField(
        default=20,
        validators=[MinValueValidator(10), MaxValueValidator(100)]
    )
    show_abstracts = models.BooleanField(default=True)
    show_preview_images = models.BooleanField(default=True)
    
    # Advanced preferences
    auto_save_searches = models.BooleanField(default=True)
    email_search_alerts = models.BooleanField(default=False)
    
    # API Key Management (encrypted storage)
    pubmed_api_key = models.TextField(blank=True, help_text="Encrypted NCBI API key for PubMed")
    google_scholar_api_key = models.TextField(blank=True, help_text="Encrypted Google Scholar API key")
    semantic_scholar_api_key = models.TextField(blank=True, help_text="Encrypted Semantic Scholar API key")
    crossref_api_key = models.TextField(blank=True, help_text="Encrypted Crossref API key")
    unpaywall_email = models.EmailField(blank=True, help_text="Email for Unpaywall API compliance")
    
    # API usage tracking
    api_usage_count = models.JSONField(
        default=dict,
        help_text="Track API usage by source: {'pubmed': 150, 'arxiv': 75, etc.}"
    )
    api_rate_limit_reset = models.JSONField(
        default=dict,
        help_text="Track rate limit reset times by source"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Preference"
        verbose_name_plural = "User Preferences"
    
    def __str__(self):
        return f"Preferences for {self.user.username}"
    
    def _get_encryption_key(self):
        """Get or create encryption key for this user"""
        # Use user-specific key derived from settings secret key and user ID
        key_material = f"{settings.SECRET_KEY}-{self.user.id}".encode()
        # Create a 32-byte key for Fernet
        key = base64.urlsafe_b64encode(key_material[:32].ljust(32, b'0'))
        return Fernet(key)
    
    def set_api_key(self, source, api_key):
        """Encrypt and store API key for a specific source"""
        if not api_key:
            return
        
        fernet = self._get_encryption_key()
        encrypted_key = fernet.encrypt(api_key.encode()).decode()
        
        if source == 'pubmed':
            self.pubmed_api_key = encrypted_key
        elif source == 'google_scholar':
            self.google_scholar_api_key = encrypted_key
        elif source == 'semantic_scholar':
            self.semantic_scholar_api_key = encrypted_key
        elif source == 'crossref':
            self.crossref_api_key = encrypted_key
        
        self.save()
    
    def get_api_key(self, source):
        """Decrypt and return API key for a specific source"""
        encrypted_key = None
        
        if source == 'pubmed':
            encrypted_key = self.pubmed_api_key
        elif source == 'google_scholar':
            encrypted_key = self.google_scholar_api_key
        elif source == 'semantic_scholar':
            encrypted_key = self.semantic_scholar_api_key
        elif source == 'crossref':
            encrypted_key = self.crossref_api_key
        
        if not encrypted_key:
            return None
        
        try:
            fernet = self._get_encryption_key()
            return fernet.decrypt(encrypted_key.encode()).decode()
        except Exception:
            return None
    
    def has_api_key(self, source):
        """Check if user has a valid API key for the source"""
        return bool(self.get_api_key(source))
    
    def get_missing_api_keys(self):
        """Return list of sources that need API keys for better performance"""
        sources = ['pubmed', 'semantic_scholar', 'crossref']
        missing = []
        
        for source in sources:
            if not self.has_api_key(source):
                missing.append(source)
        
        # Special case for unpaywall (uses email, not API key)
        if not self.unpaywall_email:
            missing.append('unpaywall')
        
        return missing
    
    def increment_api_usage(self, source):
        """Track API usage for rate limiting"""
        if not self.api_usage_count:
            self.api_usage_count = {}
        
        if source not in self.api_usage_count:
            self.api_usage_count[source] = 0
        
        self.api_usage_count[source] += 1
        self.save(update_fields=['api_usage_count'])
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """Get or create preferences for a user with sensible defaults"""
        preference, created = cls.objects.get_or_create(
            user=user,
            defaults={
                'preferred_sources': {
                    'pubmed': True,
                    'google_scholar': True,
                    'arxiv': True,
                    'semantic': True,
                },
                'default_filters': {
                    'open_access': False,
                    'recent_only': False,
                    'high_impact': False,
                },
                'api_usage_count': {},
                'api_rate_limit_reset': {},
            }
        )
        return preference