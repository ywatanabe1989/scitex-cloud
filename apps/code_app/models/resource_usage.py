"""
ResourceUsage model - Track resource usage for billing and monitoring.
"""

from django.db import models
from django.contrib.auth.models import User


class ResourceUsage(models.Model):
    """Track resource usage for billing and monitoring."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="resource_usage"
    )

    # Resource metrics
    cpu_seconds = models.FloatField(default=0.0)
    memory_mb_hours = models.FloatField(default=0.0)
    storage_gb = models.FloatField(default=0.0)
    network_gb = models.FloatField(default=0.0)

    # Job counts
    code_executions = models.IntegerField(default=0)
    analysis_jobs = models.IntegerField(default=0)
    notebook_runs = models.IntegerField(default=0)

    # Time period
    date = models.DateField()
    month = models.CharField(max_length=7)  # YYYY-MM format

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "date"]
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["user", "month"]),
            models.Index(fields=["date"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date}"
