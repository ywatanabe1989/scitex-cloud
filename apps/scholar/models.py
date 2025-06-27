from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


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
    project = models.CharField(max_length=200, blank=True, help_text="Project name for organization")
    
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