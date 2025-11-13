#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI/CD Actions Models for SciTeX Projects

GitHub Actions-style workflow system allowing users to define and run
automated workflows on git events.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import yaml


class Workflow(models.Model):
    """
    Workflow definition (similar to .github/workflows/*.yml)
    Stored in .scitex/workflows/ directory of each project
    """

    TRIGGER_EVENT_CHOICES = [
        ("push", "Push"),
        ("pull_request", "Pull Request"),
        ("schedule", "Schedule"),
        ("manual", "Manual"),
        ("issue", "Issue"),
        ("release", "Release"),
    ]

    project = models.ForeignKey(
        "Project",
        on_delete=models.CASCADE,
        related_name="workflows",
        help_text="Associated project",
    )
    name = models.CharField(
        max_length=200, help_text="Workflow name (e.g., 'Python Tests', 'LaTeX Build')"
    )
    file_path = models.CharField(
        max_length=500, help_text="Path to workflow YAML file in .scitex/workflows/"
    )
    description = models.TextField(blank=True, help_text="Workflow description")

    # Workflow configuration
    yaml_content = models.TextField(help_text="YAML workflow definition content")
    trigger_events = models.JSONField(
        default=list, help_text="List of trigger events (push, pull_request, etc.)"
    )
    enabled = models.BooleanField(default=True, help_text="Whether workflow is enabled")

    # Schedule configuration
    schedule_cron = models.CharField(
        max_length=100,
        blank=True,
        help_text="Cron expression for scheduled runs (e.g., '0 0 * * *')",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_workflows",
        help_text="User who created this workflow",
    )

    # Statistics
    total_runs = models.IntegerField(default=0, help_text="Total number of runs")
    successful_runs = models.IntegerField(
        default=0, help_text="Number of successful runs"
    )
    failed_runs = models.IntegerField(default=0, help_text="Number of failed runs")
    last_run_at = models.DateTimeField(
        null=True, blank=True, help_text="Last run timestamp"
    )
    last_run_status = models.CharField(
        max_length=20,
        blank=True,
        help_text="Last run status (success, failure, cancelled)",
    )

    class Meta:
        unique_together = ("project", "name")
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["project", "enabled"]),
            models.Index(fields=["project", "updated_at"]),
        ]

    def __str__(self):
        return f"{self.project.name} - {self.name}"

    def parse_yaml(self):
        """Parse YAML content and return Python dict"""
        try:
            return yaml.safe_load(self.yaml_content)
        except yaml.YAMLError as e:
            return {"error": str(e)}

    def get_absolute_url(self):
        """Get workflow detail URL"""
        from django.urls import reverse

        return reverse(
            "user_projects:workflow_detail",
            kwargs={
                "username": self.project.owner.username,
                "slug": self.project.slug,
                "workflow_id": self.id,
            },
        )


class WorkflowRun(models.Model):
    """
    Single execution of a workflow (similar to GitHub Actions run)
    """

    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("failed", "Failed"),
    ]

    CONCLUSION_CHOICES = [
        ("success", "Success"),
        ("failure", "Failure"),
        ("cancelled", "Cancelled"),
        ("skipped", "Skipped"),
        ("timed_out", "Timed Out"),
    ]

    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name="runs",
        help_text="Associated workflow",
    )
    run_number = models.IntegerField(
        help_text="Sequential run number for this workflow"
    )

    # Trigger information
    trigger_event = models.CharField(
        max_length=50,
        help_text="Event that triggered this run (push, pull_request, manual, etc.)",
    )
    trigger_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triggered_workflow_runs",
        help_text="User who triggered this run (for manual triggers)",
    )
    trigger_data = models.JSONField(
        default=dict, help_text="Additional trigger data (commit SHA, branch, etc.)"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="queued",
        help_text="Current run status",
    )
    conclusion = models.CharField(
        max_length=20,
        choices=CONCLUSION_CHOICES,
        blank=True,
        help_text="Final run conclusion",
    )

    # Timing
    started_at = models.DateTimeField(null=True, blank=True, help_text="Run start time")
    completed_at = models.DateTimeField(
        null=True, blank=True, help_text="Run completion time"
    )
    duration_seconds = models.IntegerField(
        null=True, blank=True, help_text="Run duration in seconds"
    )

    # Git information
    commit_sha = models.CharField(
        max_length=40, blank=True, help_text="Git commit SHA that triggered this run"
    )
    branch = models.CharField(max_length=200, blank=True, help_text="Git branch")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Environment
    environment = models.CharField(
        max_length=100,
        default="default",
        help_text="Environment name (e.g., production, staging, development)",
    )

    class Meta:
        unique_together = ("workflow", "run_number")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workflow", "status"]),
            models.Index(fields=["workflow", "-run_number"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.workflow.name} #{self.run_number}"

    def save(self, *args, **kwargs):
        """Auto-generate run number if not set"""
        if not self.run_number:
            # Get the last run number for this workflow
            last_run = (
                WorkflowRun.objects.filter(workflow=self.workflow)
                .order_by("-run_number")
                .first()
            )
            self.run_number = (last_run.run_number + 1) if last_run else 1

        super().save(*args, **kwargs)

    def calculate_duration(self):
        """Calculate and update duration"""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.duration_seconds = int(delta.total_seconds())
            self.save(update_fields=["duration_seconds"])

    def get_absolute_url(self):
        """Get run detail URL"""
        from django.urls import reverse

        return reverse(
            "user_projects:workflow_run_detail",
            kwargs={
                "username": self.workflow.project.owner.username,
                "slug": self.workflow.project.slug,
                "run_id": self.id,
            },
        )


class WorkflowJob(models.Model):
    """
    Single job within a workflow run
    A workflow can have multiple jobs that run sequentially or in parallel
    """

    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("failed", "Failed"),
        ("skipped", "Skipped"),
    ]

    run = models.ForeignKey(
        WorkflowRun,
        on_delete=models.CASCADE,
        related_name="jobs",
        help_text="Associated workflow run",
    )
    name = models.CharField(max_length=200, help_text="Job name from workflow YAML")
    job_id = models.CharField(
        max_length=100, help_text="Job identifier from workflow YAML"
    )

    # Job configuration
    runs_on = models.CharField(
        max_length=100,
        default="ubuntu-latest",
        help_text="Runner environment (e.g., ubuntu-latest, python:3.11)",
    )
    depends_on = models.JSONField(
        default=list, help_text="List of job IDs that must complete before this job"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="queued",
        help_text="Current job status",
    )
    conclusion = models.CharField(
        max_length=20, blank=True, help_text="Job conclusion (success, failure, etc.)"
    )

    # Timing
    started_at = models.DateTimeField(null=True, blank=True, help_text="Job start time")
    completed_at = models.DateTimeField(
        null=True, blank=True, help_text="Job completion time"
    )
    duration_seconds = models.IntegerField(
        null=True, blank=True, help_text="Job duration in seconds"
    )

    # Execution
    runner_id = models.CharField(
        max_length=100, blank=True, help_text="ID of the runner that executed this job"
    )
    container_id = models.CharField(
        max_length=100, blank=True, help_text="Container ID for this job execution"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Matrix configuration (for matrix jobs)
    matrix_config = models.JSONField(
        default=dict,
        help_text="Matrix configuration for this job (e.g., {python: '3.11', os: 'ubuntu'})",
    )

    class Meta:
        unique_together = ("run", "job_id")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["run", "status"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.run} - {self.name}"

    def calculate_duration(self):
        """Calculate and update duration"""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.duration_seconds = int(delta.total_seconds())
            self.save(update_fields=["duration_seconds"])


class WorkflowStep(models.Model):
    """
    Single step within a job
    Steps execute sequentially within a job
    """

    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("skipped", "Skipped"),
    ]

    job = models.ForeignKey(
        WorkflowJob,
        on_delete=models.CASCADE,
        related_name="steps",
        help_text="Associated job",
    )
    name = models.CharField(max_length=200, help_text="Step name")
    step_number = models.IntegerField(help_text="Step number within job (sequential)")

    # Step configuration
    command = models.TextField(
        help_text="Command to execute (shell command or action reference)"
    )
    working_directory = models.CharField(
        max_length=500, blank=True, help_text="Working directory for this step"
    )
    environment_vars = models.JSONField(
        default=dict, help_text="Environment variables for this step"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="queued",
        help_text="Current step status",
    )
    conclusion = models.CharField(
        max_length=20, blank=True, help_text="Step conclusion (success, failure, etc.)"
    )

    # Execution results
    output = models.TextField(blank=True, help_text="Step output (stdout)")
    error_output = models.TextField(blank=True, help_text="Step error output (stderr)")
    exit_code = models.IntegerField(
        null=True, blank=True, help_text="Process exit code"
    )

    # Timing
    started_at = models.DateTimeField(
        null=True, blank=True, help_text="Step start time"
    )
    completed_at = models.DateTimeField(
        null=True, blank=True, help_text="Step completion time"
    )
    duration_seconds = models.IntegerField(
        null=True, blank=True, help_text="Step duration in seconds"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Conditional execution
    condition = models.CharField(
        max_length=200,
        blank=True,
        help_text="Condition expression (if: always(), if: failure(), etc.)",
    )
    continue_on_error = models.BooleanField(
        default=False, help_text="Continue job execution even if this step fails"
    )

    class Meta:
        unique_together = ("job", "step_number")
        ordering = ["step_number"]
        indexes = [
            models.Index(fields=["job", "step_number"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.job.name} - Step {self.step_number}: {self.name}"

    def calculate_duration(self):
        """Calculate and update duration"""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.duration_seconds = int(delta.total_seconds())
            self.save(update_fields=["duration_seconds"])

    def append_output(self, text):
        """Append text to output (for streaming logs)"""
        self.output = (self.output or "") + text
        self.save(update_fields=["output"])

    def append_error(self, text):
        """Append text to error output"""
        self.error_output = (self.error_output or "") + text
        self.save(update_fields=["error_output"])


class WorkflowSecret(models.Model):
    """
    Encrypted secrets for workflows (similar to GitHub Secrets)
    Secrets can be defined at project or organization level
    """

    SCOPE_CHOICES = [
        ("project", "Project"),
        ("organization", "Organization"),
    ]

    name = models.CharField(
        max_length=100, help_text="Secret name (uppercase, underscores only)"
    )
    encrypted_value = models.TextField(help_text="Encrypted secret value")

    # Scope
    scope = models.CharField(
        max_length=20,
        choices=SCOPE_CHOICES,
        default="project",
        help_text="Secret scope",
    )
    project = models.ForeignKey(
        "Project",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="workflow_secrets",
        help_text="Associated project (for project-scoped secrets)",
    )
    organization = models.ForeignKey(
        "organizations_app.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="workflow_secrets",
        help_text="Associated organization (for org-scoped secrets)",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_workflow_secrets",
        help_text="User who created this secret",
    )
    last_used_at = models.DateTimeField(
        null=True, blank=True, help_text="Last time this secret was used"
    )

    class Meta:
        indexes = [
            models.Index(fields=["project", "name"]),
            models.Index(fields=["organization", "name"]),
        ]

    def __str__(self):
        scope_obj = self.project or self.organization
        return f"{scope_obj} - {self.name}"

    def encrypt_value(self, value):
        """Encrypt secret value"""
        from cryptography.fernet import Fernet
        from django.conf import settings

        # Get encryption key from settings
        key = settings.SCITEX_CLOUD_DJANGO_SECRET_KEY[:32].encode()
        f = Fernet(key)
        self.encrypted_value = f.encrypt(value.encode()).decode()

    def decrypt_value(self):
        """Decrypt and return secret value"""
        from cryptography.fernet import Fernet
        from django.conf import settings

        # Get encryption key from settings
        key = settings.SCITEX_CLOUD_DJANGO_SECRET_KEY[:32].encode()
        f = Fernet(key)
        return f.decrypt(self.encrypted_value.encode()).decode()


class WorkflowArtifact(models.Model):
    """
    Files/artifacts produced by workflow runs
    Similar to GitHub Actions artifacts
    """

    run = models.ForeignKey(
        WorkflowRun,
        on_delete=models.CASCADE,
        related_name="artifacts",
        help_text="Associated workflow run",
    )
    name = models.CharField(max_length=200, help_text="Artifact name")
    file_path = models.CharField(max_length=500, help_text="Path to artifact file")
    file_size = models.BigIntegerField(default=0, help_text="Artifact size in bytes")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="Artifact expiration time")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["run", "created_at"]),
        ]

    def __str__(self):
        return f"{self.run} - {self.name}"

    def is_expired(self):
        """Check if artifact is expired"""
        return timezone.now() > self.expires_at


# EOF
