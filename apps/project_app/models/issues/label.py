"""
Issue Label Model

Model for categorizing issues with labels.
"""

from django.db import models


class IssueLabel(models.Model):
    """
    Model for issue labels.

    Labels for categorizing issues (e.g., bug, enhancement, documentation).
    """

    project = models.ForeignKey(
        "project_app.Project",
        on_delete=models.CASCADE,
        related_name="issue_labels",
        help_text="Project this label belongs to",
    )
    name = models.CharField(
        max_length=100, help_text="Label name (e.g., 'bug', 'enhancement')"
    )
    description = models.TextField(blank=True, help_text="Label description")
    color = models.CharField(
        max_length=7,
        default="#0366d6",
        help_text="Label color (hex code, e.g., #0366d6)",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "name")
        ordering = ["name"]
        verbose_name = "Issue Label"
        verbose_name_plural = "Issue Labels"

    def __str__(self):
        return f"{self.name} ({self.project.name})"
