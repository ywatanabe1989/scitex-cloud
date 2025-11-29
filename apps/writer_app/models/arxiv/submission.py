"""arXiv submission model."""

from django.db import models
from django.contrib.auth.models import User
import uuid


class ArxivSubmission(models.Model):
    """Track arXiv submission records."""

    SUBMISSION_STATUS = [
        ("draft", "Draft"),
        ("validating", "Validating"),
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("published", "Published"),
        ("rejected", "Rejected"),
        ("withdrawn", "Withdrawn"),
        ("replaced", "Replaced"),
    ]

    SUBMISSION_TYPE = [
        ("new", "New Submission"),
        ("replacement", "Replacement"),
        ("withdrawal", "Withdrawal"),
        ("cross_list", "Cross-list"),
    ]

    # Core relationships
    manuscript = models.ForeignKey(
        "writer_app.Manuscript", on_delete=models.CASCADE, related_name="arxiv_submissions"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="arxiv_submissions"
    )
    arxiv_account = models.ForeignKey(
        "writer_app.ArxivAccount", on_delete=models.CASCADE, related_name="submissions"
    )

    # Submission identification
    submission_id = models.UUIDField(default=uuid.uuid4, unique=True)
    arxiv_id = models.CharField(max_length=50, blank=True)  # e.g., '2312.12345'
    arxiv_url = models.URLField(blank=True)

    # Submission metadata
    submission_type = models.CharField(
        max_length=20, choices=SUBMISSION_TYPE, default="new"
    )
    status = models.CharField(max_length=20, choices=SUBMISSION_STATUS, default="draft")

    # Categories
    primary_category = models.ForeignKey(
        "writer_app.ArxivCategory", on_delete=models.PROTECT, related_name="primary_submissions"
    )
    secondary_categories = models.ManyToManyField(
        "writer_app.ArxivCategory", blank=True, related_name="secondary_submissions"
    )

    # Manuscript details for submission
    title = models.CharField(max_length=500)
    abstract = models.TextField()
    authors = models.TextField()  # Formatted author list

    # Files
    latex_source = models.FileField(
        upload_to="arxiv_submissions/latex/", blank=True, null=True
    )
    pdf_file = models.FileField(
        upload_to="arxiv_submissions/pdfs/", blank=True, null=True
    )
    supplementary_files = models.JSONField(
        default=list
    )  # List of additional file paths

    # Submission comments and journal reference
    comments = models.TextField(blank=True)  # e.g., "28 pages, 15 figures"
    journal_reference = models.CharField(max_length=500, blank=True)
    doi = models.CharField(max_length=100, blank=True)

    # arXiv specific fields
    arxiv_comments = models.TextField(blank=True)  # Comments from arXiv moderators
    moderation_reason = models.TextField(blank=True)  # Reason for rejection/hold

    # Version management
    version = models.IntegerField(default=1)
    replaces_submission = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replacements",
    )

    # Status tracking
    submitted_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    last_status_check = models.DateTimeField(null=True, blank=True)

    # Administrative
    admin_notes = models.TextField(blank=True)
    is_test_submission = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["manuscript", "version"]

    def __str__(self):
        arxiv_display = f" ({self.arxiv_id})" if self.arxiv_id else ""
        return f"arXiv Submission: {self.title[:50]}...{arxiv_display}"

    def get_status_display_with_details(self):
        """Get detailed status display."""
        status_map = {
            "draft": "Draft - Not yet submitted",
            "validating": "Validating - Checking submission requirements",
            "submitted": "Submitted - Awaiting arXiv processing",
            "under_review": "Under Review - Being reviewed by arXiv moderators",
            "approved": "Approved - Will be published in next announcement",
            "published": f"Published - Available at {self.arxiv_url}"
            if self.arxiv_url
            else "Published",
            "rejected": f"Rejected - {self.moderation_reason}"
            if self.moderation_reason
            else "Rejected",
            "withdrawn": "Withdrawn - Submission withdrawn by author",
            "replaced": "Replaced - Superseded by newer version",
        }
        return status_map.get(self.status, self.get_status_display())

    def can_be_replaced(self):
        """Check if submission can be replaced with a new version."""
        return (
            self.status in ["published", "approved"] and not self.replacements.exists()
        )

    def can_be_withdrawn(self):
        """Check if submission can be withdrawn."""
        return self.status in ["submitted", "under_review", "approved", "published"]
