from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SystemMetric(models.Model):
    """Store system performance metrics"""
    
    METRIC_TYPES = [
        ('response_time', 'Response Time'),
        ('api_call', 'API Call'),
        ('error_rate', 'Error Rate'),
        ('user_action', 'User Action'),
        ('database_query', 'Database Query'),
    ]
    
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    endpoint = models.CharField(max_length=200, null=True, blank=True)
    value = models.FloatField()  # Response time in ms, error count, etc.
    status_code = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)  # Additional context
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_type', 'timestamp']),
            models.Index(fields=['endpoint', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.metric_type} - {self.endpoint} ({self.value}ms)"


class ErrorLog(models.Model):
    """Store system errors and exceptions"""
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='medium')
    error_type = models.CharField(max_length=100)
    message = models.TextField()
    stack_trace = models.TextField(null=True, blank=True)
    endpoint = models.CharField(max_length=200, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['severity', 'timestamp']),
            models.Index(fields=['error_type', 'timestamp']),
            models.Index(fields=['resolved', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.severity.upper()} - {self.error_type}"


class APIUsageMetric(models.Model):
    """Track API usage and performance"""
    
    api_name = models.CharField(max_length=50)  # scholar, semantic_scholar, etc.
    endpoint = models.CharField(max_length=200)
    response_time = models.FloatField()  # in milliseconds
    status_code = models.IntegerField()
    success = models.BooleanField()
    query_params = models.JSONField(default=dict)
    response_size = models.IntegerField(null=True, blank=True)  # in bytes
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['api_name', 'timestamp']),
            models.Index(fields=['success', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.api_name} - {self.status_code} ({self.response_time}ms)"


class UserActivity(models.Model):
    """Track user activity and engagement"""
    
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('search', 'Search'),
        ('document_create', 'Document Create'),
        ('document_edit', 'Document Edit'),
        ('project_create', 'Project Create'),
        ('visualization_create', 'Visualization Create'),
        ('code_execute', 'Code Execute'),
        ('scholar_search', 'Scholar Search'),
        ('scholar_save', 'Scholar Save Paper'),
        ('writer_compile', 'Writer Compile'),
        ('writer_template', 'Writer Template Use'),
        ('viz_create', 'Visualization Create'),
        ('viz_export', 'Visualization Export'),
        ('code_run', 'Code Run'),
        ('dashboard_view', 'Dashboard View'),
        ('profile_update', 'Profile Update'),
        ('feature_use', 'Feature Use'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    details = models.JSONField(default=dict)  # Activity-specific data
    session_id = models.CharField(max_length=40, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # Duration in seconds
    module = models.CharField(max_length=20, null=True, blank=True)  # scholar, writer, viz, code
    feature = models.CharField(max_length=50, null=True, blank=True)  # Specific feature used
    success = models.BooleanField(default=True)  # Whether action was successful
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['activity_type', 'timestamp']),
            models.Index(fields=['session_id', 'timestamp']),
            models.Index(fields=['module', 'timestamp']),
            models.Index(fields=['feature', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"


class UserEngagement(models.Model):
    """Track user engagement metrics and feature adoption"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='engagement')
    
    # Session metrics
    total_sessions = models.IntegerField(default=0)
    total_time_spent = models.IntegerField(default=0)  # Total time in seconds
    avg_session_duration = models.FloatField(default=0.0)  # Average session duration in minutes
    last_activity = models.DateTimeField(auto_now=True)
    
    # Feature adoption tracking
    scholar_searches = models.IntegerField(default=0)
    scholar_saves = models.IntegerField(default=0)
    writer_compiles = models.IntegerField(default=0)
    writer_templates_used = models.IntegerField(default=0)
    viz_created = models.IntegerField(default=0)
    viz_exported = models.IntegerField(default=0)
    code_executions = models.IntegerField(default=0)
    
    # Engagement scoring
    engagement_score = models.FloatField(default=0.0)  # 0-100 engagement score
    feature_adoption_rate = models.FloatField(default=0.0)  # Percentage of features used
    retention_score = models.FloatField(default=0.0)  # User retention probability
    
    # Behavioral insights
    preferred_module = models.CharField(max_length=20, null=True, blank=True)
    peak_usage_hour = models.IntegerField(null=True, blank=True)  # 0-23
    consecutive_days = models.IntegerField(default=0)  # Current streak
    max_consecutive_days = models.IntegerField(default=0)  # Best streak
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['engagement_score']),
            models.Index(fields=['feature_adoption_rate']),
            models.Index(fields=['last_activity']),
            models.Index(fields=['preferred_module']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Score: {self.engagement_score:.1f}"
    
    def calculate_engagement_score(self):
        """Calculate engagement score based on activity patterns"""
        score = 0
        
        # Base activity score (40 points max)
        total_activities = (self.scholar_searches + self.scholar_saves + 
                          self.writer_compiles + self.viz_created + self.code_executions)
        activity_score = min(40, total_activities * 2)
        
        # Session quality score (30 points max)
        if self.avg_session_duration > 0:
            session_score = min(30, self.avg_session_duration * 2)
        else:
            session_score = 0
        
        # Feature diversity score (20 points max)
        features_used = sum([
            1 if self.scholar_searches > 0 else 0,
            1 if self.writer_compiles > 0 else 0,
            1 if self.viz_created > 0 else 0,
            1 if self.code_executions > 0 else 0,
        ])
        diversity_score = features_used * 5
        
        # Retention score (10 points max)
        retention_score = min(10, self.consecutive_days)
        
        self.engagement_score = activity_score + session_score + diversity_score + retention_score
        return self.engagement_score
    
    def update_feature_adoption_rate(self):
        """Calculate feature adoption rate"""
        total_features = 4  # scholar, writer, viz, code
        used_features = sum([
            1 if self.scholar_searches > 0 else 0,
            1 if self.writer_compiles > 0 else 0,
            1 if self.viz_created > 0 else 0,
            1 if self.code_executions > 0 else 0,
        ])
        self.feature_adoption_rate = (used_features / total_features) * 100
        return self.feature_adoption_rate


class FeatureUsage(models.Model):
    """Track individual feature usage patterns"""
    
    MODULES = [
        ('scholar', 'Scholar'),
        ('writer', 'Writer'),
        ('viz', 'Visualization'),
        ('code', 'Code'),
        ('dashboard', 'Dashboard'),
    ]
    
    module = models.CharField(max_length=20, choices=MODULES)
    feature_name = models.CharField(max_length=100)
    usage_count = models.IntegerField(default=0)
    unique_users = models.IntegerField(default=0)
    avg_session_time = models.FloatField(default=0.0)  # Average time spent per session
    success_rate = models.FloatField(default=100.0)  # Percentage of successful uses
    last_used = models.DateTimeField(auto_now=True)
    
    # Trend analysis
    daily_usage = models.JSONField(default=dict)  # {"2025-01-01": 45, ...}
    weekly_growth = models.FloatField(default=0.0)  # Week-over-week growth percentage
    monthly_growth = models.FloatField(default=0.0)  # Month-over-month growth percentage
    
    class Meta:
        unique_together = ['module', 'feature_name']
        indexes = [
            models.Index(fields=['module', 'usage_count']),
            models.Index(fields=['feature_name', 'usage_count']),
            models.Index(fields=['last_used']),
        ]
    
    def __str__(self):
        return f"{self.module}.{self.feature_name} - {self.usage_count} uses"