"""
DatasetVersion model - Track versions of datasets.
"""

from django.db import models
import uuid


class DatasetVersion(models.Model):
    """Track versions of datasets for proper versioning"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(
        "scholar_app.Dataset", on_delete=models.CASCADE, related_name="versions"
    )

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
    parent_version = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_versions",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["dataset", "version_number"]
        indexes = [
            models.Index(fields=["dataset", "is_current"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.dataset.title} v{self.version_number}"
