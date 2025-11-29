"""arXiv submission history model."""

from django.db import models
from django.contrib.auth.models import User


class ArxivSubmissionHistory(models.Model):
    """Track status changes and updates for arXiv submissions."""

    submission = models.ForeignKey(
        "writer_app.ArxivSubmission", on_delete=models.CASCADE, related_name="history"
    )

    # Status change details
    previous_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    change_reason = models.TextField(blank=True)

    # External data
    arxiv_response = models.JSONField(default=dict)  # Full response from arXiv API
    error_details = models.TextField(blank=True)

    # User action
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_automatic = models.BooleanField(
        default=True
    )  # True for API updates, False for manual changes

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "arXiv Submission Histories"

    def __str__(self):
        return f"{self.submission.title[:30]}... - {self.previous_status} → {self.new_status}"
