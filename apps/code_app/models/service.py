"""
ProjectService model - Track services running for projects.
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ProjectService(models.Model):
    """Track services (TensorBoard, Jupyter, etc.) running for projects."""

    SERVICE_TYPES = [
        ("tensorboard", "TensorBoard"),
        ("jupyter", "Jupyter Lab"),
        ("mlflow", "MLflow"),
        ("streamlit", "Streamlit"),
        ("custom", "Custom Service"),
    ]

    SERVICE_STATUS = [
        ("starting", "Starting"),
        ("running", "Running"),
        ("stopped", "Stopped"),
        ("error", "Error"),
    ]

    # Service identification
    service_id = models.UUIDField(default=uuid.uuid4, unique=True)
    project = models.ForeignKey(
        "project_app.Project",
        on_delete=models.CASCADE,
        related_name="services"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="project_services"
    )

    # Service details
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    port = models.IntegerField()
    process_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=SERVICE_STATUS, default="starting")

    # Optional configuration
    config = models.JSONField(default=dict, blank=True)  # Custom service config

    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(default=timezone.now)
    stopped_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["port"]),
            models.Index(fields=["last_accessed"]),
        ]

    def __str__(self):
        return f"{self.service_type} on port {self.port} ({self.status})"
