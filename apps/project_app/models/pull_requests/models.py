"""
Pull Request models for GitHub-style code review and collaboration.

Provides comprehensive PR functionality including reviews, inline comments,
commit tracking, and merge strategies.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class PullRequest(models.Model):
    """
    Model for Pull Requests - GitHub-style code review workflow.

    Represents a request to merge changes from source_branch into target_branch.
    """

    STATE_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
        ("merged", "Merged"),
        ("draft", "Draft"),
    ]

    # Core fields
    project = models.ForeignKey(
        "Project",
        on_delete=models.CASCADE,
        related_name="pull_requests",
        help_text="Project this PR belongs to",
    )
    number = models.IntegerField(help_text="PR number (auto-incremented per project)")
    title = models.CharField(
        max_length=255, help_text="PR title (e.g., 'Add neural decoder model')"
    )
    description = models.TextField(
        blank=True, help_text="PR description (supports Markdown)"
    )

    # Author
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="authored_pull_requests",
        help_text="User who created the PR",
    )

    # Branch information
    source_branch = models.CharField(
        max_length=255, help_text="Branch to merge from (e.g., 'feature/add-decoder')"
    )
    target_branch = models.CharField(
        max_length=255,
        default="main",
        help_text="Branch to merge into (e.g., 'main', 'develop')",
    )

    # State
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default="open",
        db_index=True,
        help_text="Current state of the PR",
    )
    is_draft = models.BooleanField(
        default=False, help_text="Whether this is a draft PR (work in progress)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    merged_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    # Merge information
    merged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="merged_pull_requests",
        help_text="User who merged the PR",
    )
    merge_commit_sha = models.CharField(
        max_length=40, blank=True, help_text="SHA of the merge commit"
    )
    merge_strategy = models.CharField(
        max_length=20,
        blank=True,
        help_text="Merge strategy used (merge, squash, rebase)",
    )

    # Merge conflict detection
    has_conflicts = models.BooleanField(
        default=False, help_text="Whether PR has merge conflicts"
    )
    conflict_files = models.JSONField(
        default=list, blank=True, help_text="List of files with conflicts"
    )

    # Review requirements
    reviewers = models.ManyToManyField(
        User,
        related_name="review_requested_prs",
        blank=True,
        help_text="Users requested to review this PR",
    )
    required_approvals = models.IntegerField(
        default=0, help_text="Number of approvals required before merge"
    )

    # Labels and assignees
    labels = models.JSONField(
        default=list, blank=True, help_text="PR labels (e.g., ['bug', 'enhancement'])"
    )
    assignees = models.ManyToManyField(
        User,
        related_name="assigned_prs",
        blank=True,
        help_text="Users assigned to work on this PR",
    )

    # CI/CD status
    ci_status = models.CharField(
        max_length=20,
        blank=True,
        help_text="CI/CD check status (pending, success, failure)",
    )

    class Meta:
        unique_together = ("project", "number")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "state"]),
            models.Index(fields=["project", "number"]),
            models.Index(fields=["author", "created_at"]),
        ]
        verbose_name = "Pull Request"
        verbose_name_plural = "Pull Requests"

    def __str__(self):
        return f"PR #{self.number}: {self.title}"

    def save(self, *args, **kwargs):
        # Auto-increment PR number per project
        if not self.number:
            last_pr = (
                PullRequest.objects.filter(project=self.project)
                .order_by("-number")
                .first()
            )
            self.number = (last_pr.number + 1) if last_pr else 1
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        """Check if PR is open"""
        return self.state == "open"

    @property
    def is_merged(self):
        """Check if PR is merged"""
        return self.state == "merged"

    @property
    def is_closed(self):
        """Check if PR is closed (but not merged)"""
        return self.state == "closed"

    def get_approval_status(self):
        """
        Get approval status for this PR.

        Returns:
            dict: {
                'approved_count': int,
                'changes_requested_count': int,
                'commented_count': int,
                'is_approved': bool
            }
        """
        reviews = self.reviews.all()

        # Get latest review from each reviewer
        latest_reviews = {}
        for review in reviews.order_by("created_at"):
            latest_reviews[review.reviewer_id] = review

        approved = sum(1 for r in latest_reviews.values() if r.state == "approved")
        changes_requested = sum(
            1 for r in latest_reviews.values() if r.state == "changes_requested"
        )
        commented = sum(1 for r in latest_reviews.values() if r.state == "commented")

        return {
            "approved_count": approved,
            "changes_requested_count": changes_requested,
            "commented_count": commented,
            "is_approved": approved >= self.required_approvals
            and changes_requested == 0,
        }

    def can_merge(self, user):
        """
        Check if user can merge this PR.

        Args:
            user: User attempting to merge

        Returns:
            tuple: (can_merge: bool, reason: str)
        """
        # Check if PR is open
        if not self.is_open:
            return False, "PR is not open"

        # Check if user has permission
        if not self.project.can_edit(user):
            return False, "User does not have permission to merge"

        # Check if PR has conflicts
        if self.has_conflicts:
            return False, "PR has merge conflicts"

        # Check approval status
        approval_status = self.get_approval_status()
        if not approval_status["is_approved"]:
            return False, f"PR requires {self.required_approvals} approval(s)"

        # Check if CI/CD passed
        if self.ci_status == "failure":
            return False, "CI/CD checks failed"

        if self.ci_status == "pending":
            return False, "CI/CD checks are still running"

        return True, "OK"

    def merge(self, user, strategy="merge", commit_message=None):
        """
        Merge this PR using the specified strategy.

        Args:
            user: User performing the merge
            strategy: Merge strategy ('merge', 'squash', 'rebase')
            commit_message: Optional custom commit message

        Returns:
            tuple: (success: bool, message: str)
        """
        # Check if merge is allowed
        can_merge, reason = self.can_merge(user)
        if not can_merge:
            return False, reason

        # TODO: Implement actual git merge logic here
        # This would use GitPython or subprocess to:
        # 1. git checkout target_branch
        # 2. git merge/squash/rebase source_branch
        # 3. git push

        # For now, just update the model
        self.state = "merged"
        self.merged_at = timezone.now()
        self.merged_by = user
        self.merge_strategy = strategy
        # self.merge_commit_sha = <actual_commit_sha>
        self.save()

        return True, "PR merged successfully"

    def close(self, user):
        """
        Close this PR without merging.

        Args:
            user: User closing the PR

        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.is_open:
            return False, "PR is not open"

        if not self.project.can_edit(user):
            return False, "User does not have permission to close"

        self.state = "closed"
        self.closed_at = timezone.now()
        self.save()

        return True, "PR closed successfully"

    def reopen(self, user):
        """
        Reopen a closed PR.

        Args:
            user: User reopening the PR

        Returns:
            tuple: (success: bool, message: str)
        """
        if self.is_merged:
            return False, "Cannot reopen merged PR"

        if not self.is_closed:
            return False, "PR is not closed"

        if not self.project.can_edit(user):
            return False, "User does not have permission to reopen"

        self.state = "open"
        self.closed_at = None
        self.save()

        return True, "PR reopened successfully"

    def get_absolute_url(self):
        """Get URL for this PR"""
        from django.urls import reverse

        return reverse(
            "user_projects:pr_detail",
            kwargs={
                "username": self.project.owner.username,
                "slug": self.project.slug,
                "pr_number": self.number,
            },
        )


class PullRequestReview(models.Model):
    """
    Model for PR reviews - allows reviewers to approve, request changes, or comment.
    """

    STATE_CHOICES = [
        ("approved", "Approved"),
        ("changes_requested", "Changes Requested"),
        ("commented", "Commented"),
    ]

    pull_request = models.ForeignKey(
        PullRequest,
        on_delete=models.CASCADE,
        related_name="reviews",
        help_text="PR being reviewed",
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pr_reviews",
        help_text="User submitting the review",
    )
    state = models.CharField(
        max_length=20, choices=STATE_CHOICES, help_text="Review state"
    )
    content = models.TextField(
        blank=True, help_text="Review comments (supports Markdown)"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["pull_request", "created_at"]),
            models.Index(fields=["reviewer", "created_at"]),
        ]
        verbose_name = "Pull Request Review"
        verbose_name_plural = "Pull Request Reviews"

    def __str__(self):
        return f"{self.reviewer.username} {self.state} PR #{self.pull_request.number}"


class PullRequestComment(models.Model):
    """
    Model for PR comments - supports both general and inline code comments.
    """

    pull_request = models.ForeignKey(
        PullRequest,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="PR this comment belongs to",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pr_comments",
        help_text="User who wrote the comment",
    )
    content = models.TextField(help_text="Comment content (supports Markdown)")

    # Inline comment fields (optional - null for general comments)
    file_path = models.CharField(
        max_length=500, blank=True, help_text="File path for inline comments"
    )
    line_number = models.IntegerField(
        null=True, blank=True, help_text="Line number for inline comments"
    )
    commit_sha = models.CharField(
        max_length=40, blank=True, help_text="Commit SHA for inline comments"
    )

    # Comment threading
    parent_comment = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        help_text="Parent comment for threaded discussions",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited = models.BooleanField(default=False)

    # Review association
    review = models.ForeignKey(
        PullRequestReview,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comments",
        help_text="Review this comment is part of (optional)",
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["pull_request", "created_at"]),
            models.Index(fields=["author", "created_at"]),
            models.Index(fields=["file_path", "line_number"]),
        ]
        verbose_name = "Pull Request Comment"
        verbose_name_plural = "Pull Request Comments"

    def __str__(self):
        if self.file_path:
            return f"Comment by {self.author.username} on {self.file_path}:{self.line_number}"
        return f"Comment by {self.author.username} on PR #{self.pull_request.number}"

    @property
    def is_inline(self):
        """Check if this is an inline code comment"""
        return bool(self.file_path and self.line_number)

    @property
    def is_general(self):
        """Check if this is a general comment"""
        return not self.is_inline


class PullRequestCommit(models.Model):
    """
    Model to track commits included in a PR.
    """

    pull_request = models.ForeignKey(
        PullRequest,
        on_delete=models.CASCADE,
        related_name="commits",
        help_text="PR this commit belongs to",
    )
    commit_hash = models.CharField(max_length=40, help_text="Git commit SHA")
    commit_message = models.TextField(help_text="Commit message")
    author_name = models.CharField(max_length=255, help_text="Git author name")
    author_email = models.CharField(max_length=255, help_text="Git author email")
    committed_at = models.DateTimeField(help_text="Git commit timestamp")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("pull_request", "commit_hash")
        ordering = ["committed_at"]
        indexes = [
            models.Index(fields=["pull_request", "committed_at"]),
            models.Index(fields=["commit_hash"]),
        ]
        verbose_name = "Pull Request Commit"
        verbose_name_plural = "Pull Request Commits"

    def __str__(self):
        return f"{self.commit_hash[:7]} - {self.commit_message[:50]}"


class PullRequestLabel(models.Model):
    """
    Model for PR labels (e.g., 'bug', 'enhancement', 'documentation').
    """

    project = models.ForeignKey(
        "Project",
        on_delete=models.CASCADE,
        related_name="pr_labels",
        help_text="Project this label belongs to",
    )
    name = models.CharField(
        max_length=50, help_text="Label name (e.g., 'bug', 'enhancement')"
    )
    color = models.CharField(
        max_length=7, default="#0969da", help_text="Label color (hex code)"
    )
    description = models.TextField(blank=True, help_text="Label description")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "name")
        ordering = ["name"]
        verbose_name = "Pull Request Label"
        verbose_name_plural = "Pull Request Labels"

    def __str__(self):
        return self.name


class PullRequestEvent(models.Model):
    """
    Model to track PR events (opened, closed, merged, reviewed, etc.).
    """

    EVENT_CHOICES = [
        ("opened", "Opened"),
        ("closed", "Closed"),
        ("reopened", "Reopened"),
        ("merged", "Merged"),
        ("reviewed", "Reviewed"),
        ("comment", "Comment Added"),
        ("commit", "Commit Added"),
        ("label", "Label Changed"),
        ("assignee", "Assignee Changed"),
        ("reviewer", "Reviewer Changed"),
    ]

    pull_request = models.ForeignKey(
        PullRequest,
        on_delete=models.CASCADE,
        related_name="events",
        help_text="PR this event belongs to",
    )
    event_type = models.CharField(
        max_length=20, choices=EVENT_CHOICES, help_text="Type of event"
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="pr_events",
        help_text="User who triggered the event",
    )
    metadata = models.JSONField(
        default=dict, blank=True, help_text="Additional event metadata"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["pull_request", "created_at"]),
            models.Index(fields=["event_type", "created_at"]),
        ]
        verbose_name = "Pull Request Event"
        verbose_name_plural = "Pull Request Events"

    def __str__(self):
        return f"{self.event_type} - PR #{self.pull_request.number} by {self.actor}"
