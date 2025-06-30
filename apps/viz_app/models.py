import uuid
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class VisualizationType(models.Model):
    """Different types of visualizations available in the system"""
    
    CATEGORY_CHOICES = [
        ('basic', 'Basic Charts'),
        ('statistical', 'Statistical Plots'),
        ('scientific', 'Scientific Visualization'),
        ('3d', '3D Visualization'),
        ('network', 'Network Graphs'),
        ('temporal', 'Time Series'),
        ('geospatial', 'Geospatial'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)  # Icon class name
    default_config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'display_name']
    
    def __str__(self):
        return self.display_name


class ColorScheme(models.Model):
    """Custom color schemes for visualizations"""
    
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='color_schemes')
    colors = models.JSONField()  # List of hex colors
    is_public = models.BooleanField(default=False)
    category = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'owner']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} by {self.owner.username}"


class DataSource(models.Model):
    """Data sources for visualizations"""
    
    SOURCE_TYPE_CHOICES = [
        ('file', 'File Upload'),
        ('database', 'Database Connection'),
        ('api', 'API Endpoint'),
        ('realtime', 'Real-time Stream'),
        ('computed', 'Computed/Derived'),
        ('code_execution', 'Code Execution Results'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('error', 'Error'),
        ('updating', 'Updating'),
        ('inactive', 'Inactive'),
    ]
    
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_sources')
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    connection_config = models.JSONField()  # Connection details, encrypted sensitive data
    schema = models.JSONField(null=True, blank=True)  # Data schema/structure
    refresh_interval = models.IntegerField(null=True, blank=True, help_text="Refresh interval in seconds")
    last_updated = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} ({self.source_type})"


class VisualizationTemplate(models.Model):
    """Reusable templates for visualizations"""
    
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viz_templates')
    visualization_type = models.ForeignKey(VisualizationType, on_delete=models.CASCADE)
    configuration = models.JSONField()
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    tags = models.JSONField(default=list)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'owner']
        ordering = ['-usage_count', '-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.visualization_type.name})"


class Visualization(models.Model):
    """Main visualization model"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visualizations')
    visualization_type = models.ForeignKey(VisualizationType, on_delete=models.PROTECT)
    data_source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True)
    template = models.ForeignKey(VisualizationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Visualization data and configuration
    data = models.JSONField(null=True, blank=True)  # Embedded data if not using DataSource
    configuration = models.JSONField(default=dict)  # Chart-specific configuration
    layout = models.JSONField(default=dict)  # Layout configuration
    color_scheme = models.ForeignKey(ColorScheme, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_public = models.BooleanField(default=False)
    is_interactive = models.BooleanField(default=True)
    allow_download = models.BooleanField(default=True)
    
    # Versioning
    version = models.IntegerField(default=1)
    parent_version = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Analytics
    view_count = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['is_public', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.owner.username}"
    
    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class ChartConfiguration(models.Model):
    """Detailed configuration for specific chart types"""
    
    visualization = models.OneToOneField(Visualization, on_delete=models.CASCADE, related_name='chart_config')
    
    # Axes configuration
    x_axis_label = models.CharField(max_length=200, blank=True)
    y_axis_label = models.CharField(max_length=200, blank=True)
    z_axis_label = models.CharField(max_length=200, blank=True)
    x_axis_type = models.CharField(max_length=20, default='linear')  # linear, log, category, datetime
    y_axis_type = models.CharField(max_length=20, default='linear')
    
    # Display options
    show_grid = models.BooleanField(default=True)
    show_legend = models.BooleanField(default=True)
    legend_position = models.CharField(max_length=20, default='right')
    
    # Scientific options
    error_bars = models.JSONField(null=True, blank=True)
    confidence_intervals = models.JSONField(null=True, blank=True)
    regression_lines = models.JSONField(null=True, blank=True)
    annotations = models.JSONField(default=list)
    
    # Advanced configuration
    custom_script = models.TextField(blank=True)  # Custom JavaScript for advanced interactivity
    plugins = models.JSONField(default=list)  # List of enabled plugins
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Config for {self.visualization.title}"


class InteractiveElement(models.Model):
    """Interactive elements within visualizations"""
    
    ELEMENT_TYPE_CHOICES = [
        ('filter', 'Filter'),
        ('slider', 'Slider'),
        ('dropdown', 'Dropdown'),
        ('button', 'Button'),
        ('tooltip', 'Tooltip'),
        ('zoom', 'Zoom Control'),
        ('pan', 'Pan Control'),
    ]
    
    visualization = models.ForeignKey(Visualization, on_delete=models.CASCADE, related_name='interactive_elements')
    element_type = models.CharField(max_length=20, choices=ELEMENT_TYPE_CHOICES)
    element_id = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    configuration = models.JSONField()  # Element-specific configuration
    target_data = models.CharField(max_length=200, blank=True)  # Data field this element affects
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'element_id']
        unique_together = ['visualization', 'element_id']
    
    def __str__(self):
        return f"{self.element_type}: {self.label}"


class Dashboard(models.Model):
    """Collection of visualizations"""
    
    title = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    description = models.TextField(blank=True)
    visualizations = models.ManyToManyField(Visualization, through='DashboardVisualization')
    
    # Layout
    layout_type = models.CharField(max_length=20, default='grid')  # grid, masonry, custom
    layout_config = models.JSONField(default=dict)
    
    # Access control
    is_public = models.BooleanField(default=False)
    password_protected = models.BooleanField(default=False)
    password_hash = models.CharField(max_length=128, blank=True)
    
    # Theming
    theme = models.CharField(max_length=50, default='light')
    custom_css = models.TextField(blank=True)
    
    # Auto-refresh
    auto_refresh = models.BooleanField(default=False)
    refresh_interval = models.IntegerField(default=300)  # seconds
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} by {self.owner.username}"


class DashboardVisualization(models.Model):
    """Through model for Dashboard-Visualization relationship"""
    
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE)
    visualization = models.ForeignKey(Visualization, on_delete=models.CASCADE)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=6, validators=[MinValueValidator(1), MaxValueValidator(12)])
    height = models.IntegerField(default=4, validators=[MinValueValidator(1), MaxValueValidator(12)])
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'position_y', 'position_x']
        unique_together = ['dashboard', 'visualization']
    
    def __str__(self):
        return f"{self.visualization.title} in {self.dashboard.title}"


class VisualizationShare(models.Model):
    """Sharing visualizations with other users"""
    
    PERMISSION_CHOICES = [
        ('view', 'View Only'),
        ('comment', 'View and Comment'),
        ('edit', 'Edit'),
    ]
    
    visualization = models.ForeignKey(Visualization, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_visualizations')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_visualizations', null=True, blank=True)
    email = models.EmailField(blank=True)  # For sharing with non-users
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='view')
    share_token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    message = models.TextField(blank=True)
    accessed = models.BooleanField(default=False)
    accessed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['visualization', 'shared_with', 'email']
    
    def __str__(self):
        recipient = self.shared_with.username if self.shared_with else self.email
        return f"{self.visualization.title} shared with {recipient}"


class ExportJob(models.Model):
    """Export visualization jobs"""
    
    FORMAT_CHOICES = [
        ('png', 'PNG Image'),
        ('svg', 'SVG Vector'),
        ('pdf', 'PDF Document'),
        ('html', 'Interactive HTML'),
        ('json', 'JSON Data'),
        ('csv', 'CSV Data'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    visualization = models.ForeignKey(Visualization, on_delete=models.CASCADE, related_name='export_jobs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_jobs')
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    options = models.JSONField(default=dict)  # Format-specific options (DPI, size, etc.)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Export {self.visualization.title} as {self.format}"


class VisualizationComment(models.Model):
    """Comments on visualizations"""
    
    visualization = models.ForeignKey(Visualization, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Annotations
    annotation_data = models.JSONField(null=True, blank=True)  # Coordinates, element references
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.visualization.title}"


class VisualizationAnalytics(models.Model):
    """Analytics for visualization usage"""
    
    visualization = models.ForeignKey(Visualization, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    views = models.IntegerField(default=0)
    unique_viewers = models.IntegerField(default=0)
    exports = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    avg_view_duration = models.FloatField(default=0)  # in seconds
    interactions = models.JSONField(default=dict)  # Detailed interaction data
    
    class Meta:
        ordering = ['-date']
        unique_together = ['visualization', 'date']
        indexes = [
            models.Index(fields=['visualization', 'date']),
        ]
    
    def __str__(self):
        return f"Analytics for {self.visualization.title} on {self.date}"