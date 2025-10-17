from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone


class ProjectMembership(models.Model):
    """Enhanced membership model for project collaboration"""
    
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('collaborator', 'Collaborator'),
        ('viewer', 'Viewer'),
    ]
    
    PERMISSION_CHOICES = [
        ('read', 'Read Only'),
        ('write', 'Read/Write'),
        ('admin', 'Full Admin'),
    ]
    
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='collaborator')
    permission_level = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='read')
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='project_invitations_sent')
    
    class Meta:
        unique_together = ('project', 'user')
        
    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"


class Organization(models.Model):
    """Model for research organizations"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class ResearchGroup(models.Model):
    """Model for research groups/labs within organizations"""
    name = models.CharField(max_length=200)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='research_groups')
    leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='project_app_led_groups')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class Project(models.Model):
    """Model for research projects with enhanced collaboration"""

    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, default='project')
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_app_owned_projects')

    # Privacy settings
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='public',
        help_text="Repository visibility: public (anyone can see) or private (only collaborators)"
    )

    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
    research_group = models.ForeignKey(ResearchGroup, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='projects', help_text="Associated research group/lab")

    # Enhanced collaboration through ProjectMembership
    collaborators = models.ManyToManyField(User, through='ProjectMembership', through_fields=('project', 'user'), related_name='project_app_collaborative_projects')
    progress = models.IntegerField(default=0, help_text="Project progress percentage (0-100)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True)
    
    # Research data - Core SciTeX workflow fields
    hypotheses = models.TextField(blank=True, help_text="Research hypotheses (optional)")
    source_code_url = models.URLField(blank=True, help_text="GitHub/GitLab repository URL")
    data_location = models.CharField(max_length=500, blank=True, help_text="Relative path to project directory")
    # manuscript_draft = models.ForeignKey('document_app.Document', on_delete=models.SET_NULL, null=True, blank=True,  # Removed - document_app not installed
    #                                    related_name='project_app_manuscripts',
    #                                    help_text="Associated manuscript document")
    
    # Enhanced GitHub Integration fields
    github_token = models.CharField(max_length=255, blank=True, help_text="GitHub OAuth token")
    github_repo_id = models.IntegerField(null=True, blank=True, help_text="GitHub repository ID")
    github_repo_name = models.CharField(max_length=200, blank=True, help_text="GitHub repository name")
    github_owner = models.CharField(max_length=100, blank=True, help_text="GitHub repository owner")
    current_branch = models.CharField(max_length=100, default='main', help_text="Current git branch")
    last_sync_at = models.DateTimeField(null=True, blank=True, help_text="Last GitHub sync timestamp")
    github_integration_enabled = models.BooleanField(default=False, help_text="GitHub integration status")
    
    # Directory management fields
    directory_created = models.BooleanField(default=False, help_text="Whether project directory has been created")
    storage_used = models.BigIntegerField(default=0, help_text="Storage used by project in bytes")
    last_activity = models.DateTimeField(auto_now=True, help_text="Last activity in project directory")
    
    # SciTeX Engine Integration Status
    search_completed = models.BooleanField(default=False, help_text="Literature search completed")
    knowledge_gap_identified = models.TextField(blank=True, help_text="Identified knowledge gaps")
    analysis_completed = models.BooleanField(default=False, help_text="Code analysis completed")
    figures_generated = models.BooleanField(default=False, help_text="Visualizations generated")
    manuscript_generated = models.BooleanField(default=False, help_text="Manuscript generated")
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ('name', 'owner')  # Ensure unique project names per user
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.name)
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_unique_slug(cls, name):
        """Generate a globally unique slug from project name"""
        from django.utils.text import slugify
        base_slug = slugify(name)
        if not base_slug:
            base_slug = 'project'
        
        # Check if slug is unique
        if not cls.objects.filter(slug=base_slug).exists():
            return base_slug
        
        # If base slug exists, try with numbers
        counter = 1
        while True:
            unique_slug = f"{base_slug}-{counter}"
            if not cls.objects.filter(slug=unique_slug).exists():
                return unique_slug
            counter += 1
    
    @classmethod
    def generate_unique_name(cls, base_name, owner):
        """Generate a unique project name for the given owner"""
        # First try the base name
        if not cls.objects.filter(name=base_name, owner=owner).exists():
            return base_name
        
        # If base name exists, try with numbers
        counter = 1
        while True:
            unique_name = f"{base_name}_{counter}"
            if not cls.objects.filter(name=unique_name, owner=owner).exists():
                return unique_name
            counter += 1
    
    @classmethod
    def validate_name_uniqueness(cls, name, owner, exclude_id=None):
        """Validate that project name is unique for the user"""
        queryset = cls.objects.filter(name=name, owner=owner)
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
        return not queryset.exists()
    
    def get_github_safe_name(self):
        """Get a GitHub-safe repository name"""
        import re
        # GitHub repo names: alphanumeric, hyphens, underscores, periods
        # Cannot start/end with special chars, max 100 chars
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', self.name.lower())
        safe_name = re.sub(r'^[._-]+|[._-]+$', '', safe_name)
        safe_name = safe_name[:100]  # GitHub limit
        return safe_name or 'scitex_project'
    
    def get_filesystem_safe_name(self):
        """Get a filesystem-safe directory name"""
        import re
        # Remove/replace characters that are problematic for filesystems
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', self.name)
        safe_name = re.sub(r'\s+', '_', safe_name)  # Replace spaces with underscores
        safe_name = safe_name[:255]  # Filesystem limit
        return safe_name or 'scitex_project'
    
    def get_absolute_url(self):
        """Get project detail URL using GitHub-style username/project pattern"""
        from django.urls import reverse
        try:
            # Use the new user_projects namespace
            return reverse('user_projects:detail', kwargs={
                'username': self.owner.username,
                'slug': self.slug
            })
        except:
            # Fallback to direct URL construction
            return f'/{self.owner.username}/{self.slug}/'

    def is_public(self):
        """Check if repository is public"""
        return self.visibility == 'public'

    def is_private(self):
        """Check if repository is private"""
        return self.visibility == 'private'

    def can_view(self, user):
        """Check if user can view this repository"""
        # Public repositories are viewable by anyone
        if self.is_public():
            return True

        # Private repositories require authentication
        if not user or not user.is_authenticated:
            return False

        # Owner can always view
        if user == self.owner:
            return True

        # Check if user is a collaborator
        return self.memberships.filter(user=user).exists()

    def can_edit(self, user):
        """Check if user can edit this repository"""
        if not user or not user.is_authenticated:
            return False

        # Owner can always edit
        if user == self.owner:
            return True

        # Check collaborator permissions
        try:
            membership = self.memberships.get(user=user)
            return membership.permission_level in ['write', 'admin']
        except ProjectMembership.DoesNotExist:
            return False


class ProjectPermission(models.Model):
    """Granular permissions for project resources"""
    
    RESOURCE_CHOICES = [
        ('files', 'Files'),
        ('documents', 'Documents'),
        ('code', 'Code'),
        ('data', 'Data'),
        ('settings', 'Settings'),
    ]
    
    PERMISSION_CHOICES = [
        ('view', 'View'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
        ('admin', 'Admin'),
    ]
    
    membership = models.ForeignKey(ProjectMembership, on_delete=models.CASCADE, related_name='project_permissions')
    resource_type = models.CharField(max_length=20, choices=RESOURCE_CHOICES)
    permission_level = models.CharField(max_length=20, choices=PERMISSION_CHOICES)
    
    class Meta:
        unique_together = ('membership', 'resource_type')
        
    def __str__(self):
        return f"{self.membership.user.username} - {self.resource_type}: {self.permission_level}"