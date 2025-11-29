"""
Notebook Model

Jupyter notebook management.
"""

import uuid

from django.db import models
from django.contrib.auth.models import User


class Notebook(models.Model):
    """Jupyter notebook management."""

    NOTEBOOK_STATUS = [
        ("draft", "Draft"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("shared", "Shared"),
    ]

    # Notebook identification
    notebook_id = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notebooks")

    # Notebook metadata
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=NOTEBOOK_STATUS, default="draft")

    # Content
    content = models.JSONField(default=dict)  # Jupyter notebook JSON
    file_path = models.CharField(max_length=500, blank=True)

    # Sharing and collaboration
    is_public = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(
        User, related_name="shared_notebooks", blank=True
    )

    # Execution tracking
    last_executed = models.DateTimeField(null=True, blank=True)
    execution_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = ["user", "title"]

    def __str__(self):
        return f"{self.title} - {self.user.username}"
