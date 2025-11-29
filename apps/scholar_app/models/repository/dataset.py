"""
Dataset model - Research datasets stored in repositories.
"""

from django.db import models
from django.contrib.auth.models import User
import uuid


class Dataset(models.Model):
    """Research datasets stored in repositories"""

    DATASET_TYPES = [
        ("raw_data", "Raw Data"),
        ("processed_data", "Processed Data"),
        ("analysis_results", "Analysis Results"),
        ("code_output", "Code Execution Output"),
        ("supplementary", "Supplementary Materials"),
        ("replication_data", "Replication Data"),
        ("metadata", "Metadata Only"),
    ]

    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("private", "Private"),
        ("restricted", "Restricted Access"),
        ("embargoed", "Embargoed"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("published", "Published"),
        ("updated", "Updated"),
        ("deprecated", "Deprecated"),
        ("deleted", "Deleted"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic metadata
    title = models.CharField(max_length=500)
    description = models.TextField()
    dataset_type = models.CharField(max_length=30, choices=DATASET_TYPES)
    keywords = models.CharField(max_length=500, blank=True)

    # Ownership and collaboration
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_datasets"
    )
    collaborators = models.ManyToManyField(
        User, related_name="shared_datasets", blank=True
    )

    # Repository information
    repository_connection = models.ForeignKey(
        "scholar_app.RepositoryConnection", on_delete=models.CASCADE, related_name="datasets"
    )
    repository_id = models.CharField(
        max_length=200, blank=True
    )  # ID in the external repository
    repository_url = models.URLField(blank=True)
    repository_doi = models.CharField(max_length=100, blank=True)

    # Version and status
    version = models.CharField(max_length=50, default="1.0")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    visibility = models.CharField(
        max_length=20, choices=VISIBILITY_CHOICES, default="private"
    )

    # File information
    file_count = models.IntegerField(default=0)
    total_size_bytes = models.BigIntegerField(default=0)
    file_formats = models.JSONField(default=list)  # List of file extensions

    # Licensing and access
    license = models.CharField(max_length=200, blank=True)
    access_conditions = models.TextField(blank=True)
    embargo_until = models.DateTimeField(null=True, blank=True)

    # Research context
    related_papers = models.ManyToManyField(
        "scholar_app.SearchIndex", related_name="associated_datasets", blank=True
    )
    project = models.ForeignKey(
        "project_app.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="datasets",
    )

    # Code integration
    generated_by_job = models.ForeignKey(
        "code_app.CodeExecutionJob",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_datasets",
    )
    associated_notebooks = models.ManyToManyField(
        "code_app.Notebook", related_name="associated_datasets", blank=True
    )

    # Manuscript integration
    cited_in_manuscripts = models.ManyToManyField(
        "writer_app.Manuscript", related_name="cited_datasets", blank=True
    )

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
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["repository_connection", "status"]),
            models.Index(fields=["dataset_type"]),
            models.Index(fields=["visibility"]),
            models.Index(fields=["-published_at"]),
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
        return user == self.owner or user in self.collaborators.all() or user.is_staff
