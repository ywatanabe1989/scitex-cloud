from django.db import models
from django.contrib.auth.models import User


class Document(models.Model):
    """Model for user documents"""
    
    DOCUMENT_TYPES = [
        ('hypothesis', 'Hypothesis'),
        ('literature_review', 'Literature Review'),
        ('methodology', 'Methodology'),
        ('results', 'Results'),
        ('manuscript', 'Manuscript'),
        ('revision', 'Revision'),
        ('note', 'General Note'),
        ('draft', 'Draft'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='note')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_app_documents')
    project = models.ForeignKey('project_app.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    
    # Directory management fields
    file_location = models.CharField(max_length=500, blank=True, help_text="Relative path to file in user directory")
    file_size = models.BigIntegerField(default=0, help_text="File size in bytes")
    file_hash = models.CharField(max_length=64, blank=True, help_text="SHA-256 hash for file integrity")
    
    class Meta:
        ordering = ['-updated_at']
        
    def __str__(self):
        return self.title
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def get_file_path(self):
        """Get the full file path for this document"""
        if self.file_location:
            from apps.core_app.directory_manager import get_user_directory_manager
            manager = get_user_directory_manager(self.owner)
            return manager.base_path / self.file_location
        return None
    
    def has_file(self):
        """Check if document has an associated file"""
        return bool(self.file_location)
    
    def get_file_extension(self):
        """Get file extension based on document type"""
        extensions = {
            'note': '.md',
            'manuscript': '.tex',
            'literature_review': '.md',
            'methodology': '.md',
            'results': '.md',
            'hypothesis': '.md',
            'revision': '.tex',
            'draft': '.md',
        }
        return extensions.get(self.document_type, '.txt')