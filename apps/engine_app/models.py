from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class EngineConfiguration(models.Model):
    """Configuration for SciTeX Engine instances."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='engine_configs')
    name = models.CharField(max_length=100, default='Default Configuration')
    
    # Emacs Integration Settings
    emacs_version = models.CharField(max_length=50, blank=True)
    init_file_path = models.CharField(max_length=255, default='~/.emacs.d/init.el')
    
    # Claude AI Settings
    api_key_encrypted = models.TextField(blank=True)  # Encrypted API key
    model_version = models.CharField(max_length=50, default='claude-3-opus-20240229')
    max_tokens = models.IntegerField(default=4000)
    temperature = models.FloatField(default=0.7)
    
    # Feature Flags
    enable_code_completion = models.BooleanField(default=True)
    enable_org_mode_assistance = models.BooleanField(default=True)
    enable_latex_support = models.BooleanField(default=True)
    enable_shell_integration = models.BooleanField(default=True)
    enable_project_awareness = models.BooleanField(default=True)
    
    # Usage Tracking
    total_requests = models.IntegerField(default=0)
    total_tokens_used = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class EngineSession(models.Model):
    """Track SciTeX Engine sessions for analytics and history."""
    SESSION_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='engine_sessions')
    configuration = models.ForeignKey(EngineConfiguration, on_delete=models.CASCADE)
    session_id = models.UUIDField(default=uuid.uuid4, unique=True)
    
    # Session Details
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='active')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Context
    buffer_mode = models.CharField(max_length=50, blank=True)
    project_path = models.CharField(max_length=255, blank=True)
    
    # Metrics
    request_count = models.IntegerField(default=0)
    tokens_used = models.IntegerField(default=0)
    response_time_avg = models.FloatField(default=0)
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def complete_session(self):
        """Mark session as completed."""
        self.status = 'completed'
        self.end_time = timezone.now()
        self.save()


class EngineRequest(models.Model):
    """Individual requests made to SciTeX Engine."""
    REQUEST_TYPES = [
        ('code_complete', 'Code Completion'),
        ('analyze_region', 'Analyze Region'),
        ('help_buffer', 'Help with Buffer'),
        ('org_assist', 'Org-mode Assistance'),
        ('latex_help', 'LaTeX Help'),
        ('shell_command', 'Shell Command'),
        ('custom', 'Custom Query'),
    ]
    
    session = models.ForeignKey(EngineSession, on_delete=models.CASCADE, related_name='requests')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    
    # Request Content
    prompt = models.TextField()
    context = models.TextField(blank=True)  # Buffer content, project info, etc.
    
    # Response
    response = models.TextField()
    tokens_used = models.IntegerField(default=0)
    response_time = models.FloatField()  # in seconds
    
    # Metadata
    buffer_name = models.CharField(max_length=255, blank=True)
    file_path = models.CharField(max_length=255, blank=True)
    language_mode = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.request_type} - {self.created_at.strftime('%H:%M:%S')}"


class EngineSnippet(models.Model):
    """Saved code snippets and templates from SciTeX Engine."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='engine_snippets')
    
    # Snippet Details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=50)
    code = models.TextField()
    
    # Organization
    tags = models.CharField(max_length=255, blank=True)
    is_public = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False)
    
    # Usage
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} ({self.language})"


class EngineWorkflow(models.Model):
    """Research workflows orchestrated by SciTeX Engine."""
    WORKFLOW_STATUS = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='engine_workflows')
    
    # Workflow Details
    name = models.CharField(max_length=200)
    description = models.TextField()
    workflow_definition = models.JSONField()  # Stores the workflow steps
    
    # Status
    status = models.CharField(max_length=20, choices=WORKFLOW_STATUS, default='draft')
    current_step = models.IntegerField(default=0)
    progress = models.IntegerField(default=0)  # 0-100
    
    # Results
    results = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.status}"


class EngineIntegration(models.Model):
    """External tool integrations for SciTeX Engine."""
    INTEGRATION_TYPES = [
        ('jupyter', 'Jupyter Notebook'),
        ('git', 'Git'),
        ('docker', 'Docker'),
        ('conda', 'Conda/Mamba'),
        ('slurm', 'SLURM'),
        ('aws', 'AWS'),
        ('gcp', 'Google Cloud'),
        ('custom', 'Custom'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='engine_integrations')
    
    # Integration Details
    integration_type = models.CharField(max_length=20, choices=INTEGRATION_TYPES)
    name = models.CharField(max_length=100)
    configuration = models.JSONField()  # Stores integration-specific config
    
    # Status
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'integration_type', 'name']
        ordering = ['integration_type', 'name']
    
    def __str__(self):
        return f"{self.user.username} - {self.integration_type}: {self.name}"