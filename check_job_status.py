#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.scholar_app.models import BibTeXEnrichmentJob

job = BibTeXEnrichmentJob.objects.order_by('-created_at').first()

print(f"Job ID: {job.id}")
print(f"Status: {job.status}")
print(f"Total papers: {job.total_papers}")
print(f"Processed papers: {job.processed_papers}")
print(f"Failed papers: {job.failed_papers}")
print(f"Error message: {job.error_message}")
print(f"\nOutput file exists: {bool(job.output_file)}")
if job.output_file:
    print(f"Output file: {job.output_file.name if hasattr(job.output_file, 'name') else job.output_file}")
print(f"\nProcessing Log:")
print(job.processing_log)
