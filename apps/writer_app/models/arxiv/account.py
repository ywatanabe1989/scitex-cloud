"""arXiv account model."""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ArxivAccount(models.Model):
    """Store arXiv account credentials and verification status."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="arxiv_account"
    )

    # Account credentials
    arxiv_username = models.CharField(max_length=200)
    arxiv_password = models.CharField(max_length=500)  # Will be encrypted
    arxiv_email = models.EmailField()

    # Verification status
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    # Account metadata
    orcid_id = models.CharField(max_length=50, blank=True)
    affiliation = models.CharField(max_length=500, blank=True)

    # Submission limits and status
    daily_submission_limit = models.IntegerField(default=5)
    submissions_today = models.IntegerField(default=0)
    last_submission_date = models.DateField(null=True, blank=True)

    # Account status
    is_active = models.BooleanField(default=True)
    suspension_reason = models.TextField(blank=True)
    suspended_until = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"arXiv Account: {self.arxiv_username} ({'Verified' if self.is_verified else 'Unverified'})"

    def can_submit_today(self):
        """Check if user can submit today based on daily limits."""
        today = timezone.now().date()

        if self.last_submission_date != today:
            self.submissions_today = 0
            self.last_submission_date = today
            self.save()

        return self.submissions_today < self.daily_submission_limit

    def increment_daily_submissions(self):
        """Increment daily submission count."""
        today = timezone.now().date()

        if self.last_submission_date != today:
            self.submissions_today = 0
            self.last_submission_date = today

        self.submissions_today += 1
        self.save()
