from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

# Import Organization models from dedicated app
from apps.organizations_app.models import Organization, ResearchGroup


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


# Organization and ResearchGroup models moved to apps.organizations_app
# Import them at the top of this file


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

    # Gitea Integration fields
    gitea_repo_id = models.IntegerField(null=True, blank=True, help_text="Gitea repository ID")
    gitea_repo_name = models.CharField(max_length=200, blank=True, help_text="Gitea repository name")
    gitea_repo_url = models.URLField(blank=True, help_text="Gitea repository web URL")
    gitea_clone_url = models.URLField(blank=True, help_text="Gitea HTTPS clone URL")
    gitea_ssh_url = models.CharField(max_length=500, blank=True, help_text="Gitea SSH clone URL")
    git_url = models.URLField(blank=True, help_text="Git clone URL (SSH or HTTPS)")
    git_clone_path = models.CharField(max_length=500, blank=True, help_text="Local git clone path")
    gitea_enabled = models.BooleanField(default=False, help_text="Gitea integration enabled")

    # Source tracking (where did this project come from?)
    SOURCE_CHOICES = [
        ('scitex', 'Created in SciTeX'),
        ('github', 'Imported from GitHub'),
        ('gitlab', 'Imported from GitLab'),
        ('bitbucket', 'Imported from Bitbucket'),
        ('git', 'Cloned from Git URL'),
    ]
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='scitex', help_text="Project source")
    source_url = models.URLField(blank=True, help_text="Original source URL (if imported)")

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
        """
        Generate a globally unique slug from project name

        Follows GitHub repository naming rules:
        - Only alphanumeric, hyphens, underscores, periods
        - Cannot start or end with special characters
        - Max 100 characters
        """
        import re
        from django.utils.text import slugify

        # Use Django's slugify (handles unicode, converts to ASCII)
        base_slug = slugify(name)

        # Further sanitize for GitHub compatibility
        # GitHub allows: alphanumeric, hyphens, underscores, periods
        base_slug = re.sub(r'[^a-z0-9._-]', '-', base_slug.lower())

        # Remove leading/trailing special chars
        base_slug = re.sub(r'^[._-]+|[._-]+$', '', base_slug)

        # Ensure not empty
        if not base_slug:
            base_slug = 'project'

        # Limit to 100 chars (GitHub limit)
        base_slug = base_slug[:100]

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

    @classmethod
    def validate_repository_name(cls, name):
        """
        Validate repository name according to GitHub/Gitea naming rules

        Returns:
            Tuple of (is_valid: bool, error_message: str or None)

        Rules:
        - Cannot contain spaces
        - Must be 1-100 characters
        - Can only contain: alphanumeric, hyphens, underscores, periods
        - Cannot start or end with special characters (-, _, .)
        - Cannot be empty or whitespace only
        """
        import re

        # Check if empty or whitespace only
        if not name or not name.strip():
            return False, "Repository name cannot be empty"

        # Check length
        if len(name) > 100:
            return False, "Repository name must be 100 characters or less"

        # Check for spaces
        if ' ' in name:
            return False, "Repository name cannot contain spaces. Use hyphens (-) or underscores (_) instead."

        # Check for valid characters (alphanumeric, hyphens, underscores, periods)
        if not re.match(r'^[a-zA-Z0-9._-]+$', name):
            return False, "Repository name can only contain letters, numbers, hyphens (-), underscores (_), and periods (.)"

        # Check that it doesn't start or end with special characters
        if re.match(r'^[._-]', name) or re.match(r'[._-]$', name):
            return False, "Repository name cannot start or end with hyphens, underscores, or periods"

        return True, None
    
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

    @staticmethod
    def extract_repo_name_from_url(git_url: str) -> str:
        """
        Extract repository name from Git URL, preserving the original name.

        Examples:
            https://github.com/user/my-repo.git -> my-repo
            https://github.com/user/MyRepo -> MyRepo
            git@github.com:user/awesome_project.git -> awesome_project

        Args:
            git_url: Git repository URL

        Returns:
            Repository name extracted from URL (preserves original case and valid characters)
        """
        git_url = git_url.strip()

        # Remove .git suffix if present
        if git_url.endswith('.git'):
            git_url = git_url[:-4]

        # Extract repo name (last part of path)
        # Works for both HTTPS and SSH formats
        repo_name = git_url.rstrip('/').split('/')[-1]

        # Only decode URL encoding if present, but keep original name otherwise
        try:
            from urllib.parse import unquote
            repo_name = unquote(repo_name)
        except:
            pass

        return repo_name or 'imported-repo'

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

    # ----------------------------------------
    # Gitea Integration Methods
    # ----------------------------------------

    def create_gitea_repository(self, user_token: str = None):
        """
        Create repository in Gitea

        Args:
            user_token: User's Gitea API token (optional, uses default if not provided)

        Returns:
            Gitea repository object
        """
        from apps.gitea_app.api_client import GiteaClient

        client = GiteaClient(token=user_token) if user_token else GiteaClient()

        repo = client.create_repository(
            name=self.slug,
            description=self.description,
            private=(self.visibility == 'private'),
            auto_init=True,
            gitignores='Python',
            readme='Default'
        )

        # Update project with Gitea info
        self.gitea_repo_id = repo['id']
        self.gitea_repo_name = repo['name']
        self.git_url = repo['clone_url']  # HTTPS URL
        self.gitea_enabled = True
        self.save()

        return repo

    def clone_gitea_to_local(self):
        """
        Clone Gitea repository to local working directory

        Returns:
            Tuple of (success, path or error_message)
        """
        import subprocess
        from pathlib import Path
        from apps.workspace_app.services.directory_service import get_user_directory_manager

        if not self.git_url:
            return False, "No git URL configured"

        manager = get_user_directory_manager(self.owner)
        clone_path = manager.base_path / self.slug

        # Remove existing directory if empty
        if clone_path.exists():
            if any(clone_path.iterdir()):
                return False, "Directory already exists and is not empty"
            else:
                clone_path.rmdir()

        try:
            result = subprocess.run(
                ['git', 'clone', self.git_url, str(clone_path)],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                self.git_clone_path = str(clone_path)
                self.directory_created = True
                self.data_location = str(clone_path.relative_to(manager.base_path))
                self.save()
                return True, str(clone_path)
            else:
                return False, result.stderr

        except subprocess.TimeoutExpired:
            return False, "Clone operation timed out"
        except Exception as e:
            return False, str(e)

    def import_from_github(self, github_url: str, github_token: str = '',
                          import_issues: bool = True, import_pulls: bool = True):
        """
        Import project from GitHub repository

        Args:
            github_url: GitHub repository URL
            github_token: GitHub personal access token (for private repos)
            import_issues: Import issues
            import_pulls: Import pull requests

        Returns:
            Tuple of (success, repo_object or error_message)
        """
        from apps.gitea_app.api_client import GiteaClient

        client = GiteaClient()

        try:
            repo = client.migrate_repository(
                clone_addr=github_url,
                repo_name=self.slug,
                service='github',
                auth_token=github_token,
                mirror=False,
                private=(self.visibility == 'private'),
                description=self.description,
                issues=import_issues,
                pull_requests=import_pulls
            )

            # Update project with Gitea info
            self.gitea_repo_id = repo['id']
            self.gitea_repo_name = repo['name']
            self.git_url = repo['clone_url']
            self.gitea_enabled = True
            self.source = 'github'
            self.source_url = github_url
            self.save()

            # Clone to local directory
            success, result = self.clone_gitea_to_local()

            return True, repo

        except Exception as e:
            return False, str(e)


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