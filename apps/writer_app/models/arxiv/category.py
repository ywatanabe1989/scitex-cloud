"""arXiv category model."""

from django.db import models


class ArxivCategory(models.Model):
    """arXiv subject categories."""

    code = models.CharField(
        max_length=20, unique=True
    )  # e.g., 'cs.AI', 'physics.gen-ph'
    name = models.CharField(max_length=200)
    description = models.TextField()
    parent_category = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )

    # Category metadata
    is_active = models.BooleanField(default=True)
    submission_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        verbose_name_plural = "arXiv Categories"

    def __str__(self):
        return f"{self.code} - {self.name}"
