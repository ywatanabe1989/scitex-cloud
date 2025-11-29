"""
DatasetFile model - Individual files within a dataset.
"""

from django.db import models
import uuid


class DatasetFile(models.Model):
    """Individual files within a dataset"""

    FILE_TYPES = [
        ("data", "Data File"),
        ("code", "Code File"),
        ("documentation", "Documentation"),
        ("metadata", "Metadata"),
        ("readme", "README"),
        ("license", "License"),
        ("figure", "Figure/Image"),
        ("supplementary", "Supplementary"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(
        "scholar_app.Dataset", on_delete=models.CASCADE, related_name="files"
    )

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
    local_file = models.FileField(upload_to="dataset_files/", blank=True, null=True)

    # Usage tracking
    download_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["file_path", "filename"]
        unique_together = ["dataset", "file_path", "filename"]
        indexes = [
            models.Index(fields=["dataset", "file_type"]),
            models.Index(fields=["file_format"]),
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
