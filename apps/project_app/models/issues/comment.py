"""
Issue Comment Model

Model for comments on issues.
"""

from django.db import models
from django.contrib.auth.models import User


class IssueComment(models.Model):
    """
    Model for issue comments.

    Represents a comment on an issue (similar to GitHub issue comments).
    """

    issue = models.ForeignKey(
        "project_app.Issue",
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="Issue this comment belongs to",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="issue_comments",
        help_text="User who wrote the comment",
    )
    content = models.TextField(help_text="Comment content (supports Markdown)")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Editing information
    is_edited = models.BooleanField(
        default=False, help_text="Whether comment has been edited"
    )

    # Reactions
    reactions_count = models.JSONField(
        default=dict, blank=True, help_text="Reaction counts"
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["issue", "created_at"]),
            models.Index(fields=["author", "created_at"]),
        ]
        verbose_name = "Issue Comment"
        verbose_name_plural = "Issue Comments"

    def __str__(self):
        return f"Comment on {self.issue} by {self.author.username}"
