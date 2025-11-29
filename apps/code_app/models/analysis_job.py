"""
Data Analysis Job Model

Specialized model for data analysis tasks using MNGS.
"""

import uuid

from django.db import models
from django.contrib.auth.models import User


class DataAnalysisJob(models.Model):
    """Specialized model for data analysis tasks using MNGS."""

    ANALYSIS_TYPES = [
        ("time_series", "Time Series Analysis"),
        ("statistics", "Statistical Analysis"),
        ("signal_processing", "Signal Processing"),
        ("machine_learning", "Machine Learning"),
        ("visualization", "Data Visualization"),
        ("custom", "Custom Analysis"),
    ]

    # Job identification
    analysis_id = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="analysis_jobs"
    )
    code_job = models.OneToOneField(
        "code_app.CodeExecutionJob", on_delete=models.CASCADE, null=True, blank=True
    )

    # Analysis details
    analysis_type = models.CharField(max_length=30, choices=ANALYSIS_TYPES)
    input_data_path = models.CharField(max_length=500, blank=True)
    parameters = models.JSONField(default=dict)

    # Results
    results = models.JSONField(default=dict)
    summary = models.TextField(blank=True)
    figures_generated = models.IntegerField(default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Analysis {self.analysis_id} ({self.analysis_type})"
