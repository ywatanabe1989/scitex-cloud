"""
Issue Assignment Model

Model for tracking issue assignments.
"""

from django.db import models
from django.contrib.auth.models import User


class IssueAssignment(models.Model):
    """
    Model for issue assignments.

    Tracks when users are assigned to issues.
    """

    issue = models.ForeignKey(
        "project_app.Issue", on_delete=models.CASCADE, related_name="assignments"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="issue_assignments"
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issue_assignments_made",
        help_text="User who made the assignment",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("issue", "user")
        ordering = ["assigned_at"]
        verbose_name = "Issue Assignment"
        verbose_name_plural = "Issue Assignments"

    def __str__(self):
        return f"{self.user.username} assigned to {self.issue}"
