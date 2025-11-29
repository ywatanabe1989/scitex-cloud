"""arXiv API response model."""

from django.db import models


class ArxivApiResponse(models.Model):
    """Log arXiv API responses for debugging and monitoring."""

    submission = models.ForeignKey(
        "writer_app.ArxivSubmission", on_delete=models.CASCADE, related_name="api_responses"
    )

    # Request details
    api_endpoint = models.CharField(max_length=200)
    request_method = models.CharField(max_length=10)
    request_data = models.JSONField(default=dict)

    # Response details
    response_status = models.IntegerField()
    response_data = models.JSONField(default=dict)
    response_headers = models.JSONField(default=dict)

    # Timing
    request_time = models.DateTimeField()
    response_time = models.DateTimeField()
    duration_ms = models.IntegerField()  # Duration in milliseconds

    # Error tracking
    is_error = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.request_method} {self.api_endpoint} - {self.response_status}"
