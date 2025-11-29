"""arXiv validation result model."""

from django.db import models


class ArxivValidationResult(models.Model):
    """Store validation results for arXiv submissions."""

    VALIDATION_STATUS = [
        ("pending", "Pending"),
        ("passed", "Passed"),
        ("failed", "Failed"),
        ("warning", "Warning"),
    ]

    submission = models.OneToOneField(
        "writer_app.ArxivSubmission", on_delete=models.CASCADE, related_name="validation"
    )

    # Overall validation status
    status = models.CharField(
        max_length=20, choices=VALIDATION_STATUS, default="pending"
    )
    overall_score = models.FloatField(default=0.0)  # 0-100 validation score

    # Individual validation checks
    latex_compilation = models.CharField(
        max_length=20, choices=VALIDATION_STATUS, default="pending"
    )
    pdf_generation = models.CharField(
        max_length=20, choices=VALIDATION_STATUS, default="pending"
    )
    metadata_validation = models.CharField(
        max_length=20, choices=VALIDATION_STATUS, default="pending"
    )
    category_validation = models.CharField(
        max_length=20, choices=VALIDATION_STATUS, default="pending"
    )
    file_format_check = models.CharField(
        max_length=20, choices=VALIDATION_STATUS, default="pending"
    )

    # Detailed results
    validation_details = models.JSONField(default=dict)
    error_messages = models.JSONField(default=list)
    warning_messages = models.JSONField(default=list)

    # LaTeX specific checks
    latex_log = models.TextField(blank=True)
    bibtex_issues = models.JSONField(default=list)
    missing_figures = models.JSONField(default=list)

    # arXiv specific requirements
    title_length_check = models.BooleanField(default=False)
    abstract_length_check = models.BooleanField(default=False)
    author_format_check = models.BooleanField(default=False)

    # File size and format checks
    total_file_size = models.FloatField(default=0.0)  # in MB
    max_file_size_exceeded = models.BooleanField(default=False)
    unsupported_files = models.JSONField(default=list)

    # Validation timestamps
    validation_started = models.DateTimeField(auto_now_add=True)
    validation_completed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-validation_started"]

    def __str__(self):
        return f"Validation: {self.submission.title[:30]}... - {self.status}"

    def is_ready_for_submission(self):
        """Check if validation passed all required checks."""
        return (
            self.status == "passed"
            and self.latex_compilation == "passed"
            and self.pdf_generation == "passed"
            and self.metadata_validation == "passed"
            and not self.max_file_size_exceeded
        )

    def get_validation_summary(self):
        """Get a summary of validation results."""
        return {
            "status": self.status,
            "score": self.overall_score,
            "checks": {
                "latex": self.latex_compilation,
                "pdf": self.pdf_generation,
                "metadata": self.metadata_validation,
                "category": self.category_validation,
                "file_format": self.file_format_check,
            },
            "errors": len(self.error_messages),
            "warnings": len(self.warning_messages),
            "ready": self.is_ready_for_submission(),
        }
