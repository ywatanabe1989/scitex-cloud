from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid
import json


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


class ABTest(models.Model):
    """A/B Testing framework for feature experimentation"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Test configuration
    feature_flag = models.CharField(max_length=50)  # Feature flag name
    traffic_allocation = models.FloatField(default=50.0)  # Percentage for variant A
    target_metric = models.CharField(max_length=50)  # Primary metric to measure
    
    # Test variants
    control_name = models.CharField(max_length=50, default='control')
    variant_name = models.CharField(max_length=50, default='variant')
    control_config = models.JSONField(default=dict)  # Configuration for control
    variant_config = models.JSONField(default=dict)  # Configuration for variant
    
    # Targeting
    target_users = models.JSONField(default=dict)  # User targeting criteria
    exclusion_criteria = models.JSONField(default=dict)  # Users to exclude
    
    # Timeline
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Results tracking
    total_participants = models.IntegerField(default=0)
    control_participants = models.IntegerField(default=0)
    variant_participants = models.IntegerField(default=0)
    
    # Statistical significance
    confidence_level = models.FloatField(default=95.0)
    statistical_significance = models.BooleanField(default=False)
    p_value = models.FloatField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tests')
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['feature_flag']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    def is_active(self):
        """Check if test is currently active"""
        now = timezone.now()
        return (
            self.status == 'active' and
            (self.start_date is None or self.start_date <= now) and
            (self.end_date is None or self.end_date >= now)
        )
    
    def get_user_variant(self, user):
        """Determine which variant a user should see"""
        if not self.is_active():
            return None
        
        # Use user ID for consistent assignment
        import hashlib
        hash_input = f"{self.id}:{user.id if user.is_authenticated else 'anonymous'}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        percentage = (hash_value % 100) + 1
        
        if percentage <= self.traffic_allocation:
            return 'variant'
        else:
            return 'control'


class ABTestParticipant(models.Model):
    """Track users participating in A/B tests"""
    
    test = models.ForeignKey(ABTest, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=40, null=True, blank=True)  # For anonymous users
    variant = models.CharField(max_length=20)  # 'control' or 'variant'
    
    # Participant metadata
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_type = models.CharField(max_length=50, null=True, blank=True)
    
    # Participation tracking
    first_exposure = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    conversion_achieved = models.BooleanField(default=False)
    conversion_date = models.DateTimeField(null=True, blank=True)
    
    # Custom metrics
    metrics_data = models.JSONField(default=dict)  # Store custom metrics
    
    class Meta:
        unique_together = ['test', 'user', 'session_id']
        indexes = [
            models.Index(fields=['test', 'variant']),
            models.Index(fields=['first_exposure']),
            models.Index(fields=['conversion_achieved']),
        ]
    
    def __str__(self):
        user_id = self.user.username if self.user else f"session:{self.session_id}"
        return f"{self.test.name} - {user_id} ({self.variant})"


class ConversionFunnel(models.Model):
    """Define conversion funnels for analysis"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    # Funnel configuration
    steps = models.JSONField()  # List of funnel steps with conditions
    time_window = models.IntegerField(default=86400)  # Seconds (default: 24 hours)
    
    # Targeting
    target_users = models.JSONField(default=dict)  # User criteria
    
    # Settings
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return self.name


class ConversionEvent(models.Model):
    """Track individual conversion events"""
    
    funnel = models.ForeignKey(ConversionFunnel, on_delete=models.CASCADE, related_name='events')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=40, null=True, blank=True)
    
    step_index = models.IntegerField()  # Which step in the funnel (0-based)
    step_name = models.CharField(max_length=100)
    
    # Event metadata
    properties = models.JSONField(default=dict)  # Event-specific data
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Context
    page_url = models.URLField(null=True, blank=True)
    referrer = models.URLField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['funnel', 'user', 'timestamp']),
            models.Index(fields=['funnel', 'step_index', 'timestamp']),
            models.Index(fields=['session_id', 'timestamp']),
        ]
    
    def __str__(self):
        user_id = self.user.username if self.user else f"session:{self.session_id}"
        return f"{self.funnel.name} - {user_id} - Step {self.step_index}"


class UserJourney(models.Model):
    """Track complete user journeys and touchpoints"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journeys')
    session_id = models.CharField(max_length=40)
    journey_id = models.UUIDField(default=uuid.uuid4, unique=True)
    
    # Journey metadata
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_duration = models.IntegerField(null=True, blank=True)  # Seconds
    
    # Entry and exit points
    entry_point = models.CharField(max_length=200)  # First page/action
    exit_point = models.CharField(max_length=200, null=True, blank=True)  # Last page/action
    entry_referrer = models.URLField(null=True, blank=True)
    
    # Journey characteristics
    total_pages_viewed = models.IntegerField(default=0)
    total_actions = models.IntegerField(default=0)
    goal_achieved = models.BooleanField(default=False)
    goal_type = models.CharField(max_length=50, null=True, blank=True)
    
    # Technical context
    device_type = models.CharField(max_length=50, null=True, blank=True)
    browser = models.CharField(max_length=50, null=True, blank=True)
    platform = models.CharField(max_length=50, null=True, blank=True)
    
    # Journey path (simplified)
    path_summary = models.JSONField(default=list)  # List of key touchpoints
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'start_time']),
            models.Index(fields=['session_id']),
            models.Index(fields=['goal_achieved', 'goal_type']),
            models.Index(fields=['start_time']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Journey {self.journey_id.hex[:8]}"


class UserCohort(models.Model):
    """Define and track user cohorts for analysis"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    # Cohort definition
    criteria = models.JSONField()  # Conditions for cohort membership
    time_period = models.CharField(max_length=50)  # 'weekly', 'monthly', etc.
    
    # Cohort metadata
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Members
    users = models.ManyToManyField(User, through='CohortMembership')
    
    # Analytics
    initial_size = models.IntegerField(default=0)
    current_size = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['start_date', 'time_period']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.start_date})"


class CohortMembership(models.Model):
    """Track user membership in cohorts"""
    
    cohort = models.ForeignKey(UserCohort, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Membership details
    joined_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # Cohort-specific metrics
    metrics = models.JSONField(default=dict)
    
    class Meta:
        unique_together = ['cohort', 'user']
    
    def __str__(self):
        return f"{self.user.username} in {self.cohort.name}"


class DataExportRequest(models.Model):
    """Track data export requests for analytics"""
    
    EXPORT_TYPES = [
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('excel', 'Excel'),
        ('pdf', 'PDF Report'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_requests')
    
    # Export configuration
    export_type = models.CharField(max_length=20, choices=EXPORT_TYPES)
    data_source = models.CharField(max_length=50)  # 'user_activity', 'feature_usage', etc.
    filters = models.JSONField(default=dict)  # Date range, user filters, etc.
    
    # Request metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # File information
    file_path = models.CharField(max_length=500, null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)  # Bytes
    download_count = models.IntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.data_source} ({self.export_type})"


class AlertRule(models.Model):
    """Define automated alert rules for monitoring"""
    
    SEVERITY_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    CONDITION_TYPES = [
        ('threshold', 'Threshold'),
        ('percentage', 'Percentage'),
        ('trend', 'Trend'),
        ('anomaly', 'Anomaly'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    # Rule configuration
    metric_name = models.CharField(max_length=50)  # What to monitor
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPES)
    threshold_value = models.FloatField()
    time_window = models.IntegerField(default=300)  # Seconds
    
    # Alert settings
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='warning')
    is_active = models.BooleanField(default=True)
    
    # Notification settings
    notification_emails = models.JSONField(default=list)
    notification_slack = models.CharField(max_length=200, null=True, blank=True)
    
    # Rate limiting
    cooldown_period = models.IntegerField(default=900)  # Seconds between alerts
    last_triggered = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'metric_name']),
            models.Index(fields=['last_triggered']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.severity})"


class AlertInstance(models.Model):
    """Track triggered alerts"""
    
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, related_name='instances')
    
    # Alert details
    triggered_at = models.DateTimeField(auto_now_add=True)
    metric_value = models.FloatField()
    threshold_value = models.FloatField()
    
    # Context
    context_data = models.JSONField(default=dict)
    message = models.TextField()
    
    # Resolution
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)
    
    # Notification status
    email_sent = models.BooleanField(default=False)
    slack_sent = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['rule', 'triggered_at']),
            models.Index(fields=['resolved_at']),
        ]
    
    def __str__(self):
        return f"{self.rule.name} - {self.triggered_at.strftime('%Y-%m-%d %H:%M')}"


class PrivacyConsent(models.Model):
    """Track user privacy consent for GDPR compliance"""
    
    CONSENT_TYPES = [
        ('analytics', 'Analytics & Performance'),
        ('marketing', 'Marketing & Communications'),
        ('functional', 'Functional Cookies'),
        ('personalization', 'Personalization'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='privacy_consents')
    consent_type = models.CharField(max_length=20, choices=CONSENT_TYPES)
    
    # Consent details
    granted = models.BooleanField()
    granted_at = models.DateTimeField(auto_now_add=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    
    # Legal basis
    legal_basis = models.CharField(max_length=100, null=True, blank=True)
    purpose = models.TextField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'consent_type']
        indexes = [
            models.Index(fields=['user', 'granted']),
            models.Index(fields=['granted_at']),
        ]
    
    def __str__(self):
        status = 'granted' if self.granted else 'withdrawn'
        return f"{self.user.username} - {self.consent_type} ({status})"