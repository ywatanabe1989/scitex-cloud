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

    # SciTeX Integration (scitex.project package)
    scitex_project_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text="Unique identifier linking to scitex/.metadata/ (from scitex.project package)"
    )
    local_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to local project directory (where scitex/.metadata/ lives)"
    )
    
    # SciTeX Engine Integration Status
    search_completed = models.BooleanField(default=False, help_text="Literature search completed")
    knowledge_gap_identified = models.TextField(blank=True, help_text="Identified knowledge gaps")
    analysis_completed = models.BooleanField(default=False, help_text="Code analysis completed")
    figures_generated = models.BooleanField(default=False, help_text="Visualizations generated")
    manuscript_generated = models.BooleanField(default=False, help_text="Manuscript generated")
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ('name', 'owner')  # Ensure unique project names per user
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'gitea_repo_name'],
                condition=models.Q(gitea_enabled=True),
                name='unique_gitea_repo_per_user'
            ),
            models.UniqueConstraint(
                fields=['gitea_repo_id'],
                condition=models.Q(gitea_repo_id__isnull=False),
                name='unique_gitea_repo_id'
            ),
        ]
        
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
        except (ValueError, TypeError, AttributeError):
            pass

        return repo_name or 'imported-repo'

    def get_absolute_url(self):
        """Get project detail URL using GitHub-style username/project pattern"""
        from django.urls import reverse
        from django.urls.exceptions import NoReverseMatch
        try:
            # Use the new user_projects namespace
            return reverse('user_projects:detail', kwargs={
                'username': self.owner.username,
                'slug': self.slug
            })
        except NoReverseMatch:
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
        Create repository in Gitea with one-to-one relationship validation

        Args:
            user_token: User's Gitea API token (optional, uses default if not provided)

        Returns:
            Gitea repository object

        Raises:
            Exception: If repository creation fails (including if it already exists)
        """
        from apps.gitea_app.api_client import GiteaClient
        import logging

        logger = logging.getLogger(__name__)
        client = GiteaClient(token=user_token) if user_token else GiteaClient()

        # 1. Check if this project already has a Gitea repository
        if self.gitea_enabled and self.gitea_repo_id:
            logger.warning(f"Project {self.slug} already has Gitea repository {self.gitea_repo_id}")
            raise Exception(f"Project already has a Gitea repository")

        # 2. Check if another Django project claims this Gitea repository
        from django.db.models import Q
        existing_project = Project.objects.filter(
            Q(owner=self.owner) &
            Q(gitea_repo_name=self.slug) &
            Q(gitea_enabled=True)
        ).exclude(id=self.id).first()

        if existing_project:
            raise Exception(
                f"A project named '{existing_project.name}' already uses Gitea repository '{self.slug}'"
            )

        # 3. Check if repository already exists in Gitea (enforce strict 1:1)
        try:
            existing_repo = client.get_repository(self.owner.username, self.slug)
            if existing_repo:
                # Repository exists - this violates 1:1 mapping
                logger.error(f"Gitea repository {self.owner.username}/{self.slug} already exists (ID: {existing_repo.get('id')})")
                raise Exception(
                    f"The repository '{self.slug}' already exists in Gitea (ID: {existing_repo.get('id')}). "
                    f"This is an orphaned repository. Please delete it manually or contact support."
                )
        except Exception as e:
            # If it's a 404, the repo doesn't exist (which is what we want for strict 1:1)
            if "404" not in str(e) and "not found" not in str(e).lower():
                # Some other error occurred - re-raise
                raise

        # 4. Create the repository in Gitea
        try:
            repo = client.create_repository(
                name=self.slug,
                description=self.description,
                private=(self.visibility == 'private'),
                auto_init=True,
                gitignores='Python',
                readme='Default'
            )
        except Exception as create_error:
            logger.error(f"Failed to create Gitea repository {self.slug}: {create_error}")
            raise Exception(f"Failed to create Gitea repository: {str(create_error)}")

        # 5. Update project with Gitea info (atomic operation)
        try:
            self.gitea_repo_id = repo['id']
            self.gitea_repo_name = repo['name']
            self.gitea_repo_url = repo.get('html_url', '')
            self.gitea_clone_url = repo.get('clone_url', '')
            self.gitea_ssh_url = repo.get('ssh_url', '')
            self.git_url = repo['clone_url']  # HTTPS URL
            self.gitea_enabled = True
            self.save()

            logger.info(f"✓ Gitea repository created: {self.owner.username}/{self.slug} (ID: {repo['id']})")
            return repo

        except Exception as e:
            # Rollback: delete the Gitea repository we just created
            logger.error(f"Failed to save project after Gitea creation: {e}")
            try:
                client.delete_repository(self.owner.username, self.slug)
                logger.info(f"✓ Rolled back Gitea repository {self.slug}")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup Gitea repository {self.slug}: {cleanup_error}")
            raise Exception(f"Failed to link Gitea repository to project: {str(e)}")

    def clone_gitea_to_local(self):
        """
        Clone Gitea repository to local working directory

        Returns:
            Tuple of (success, path or error_message)
        """
        import subprocess
        from pathlib import Path
        from apps.project_app.services.project_filesystem import get_project_filesystem_manager

        if not self.git_url:
            return False, "No git URL configured"

        manager = get_project_filesystem_manager(self.owner)
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

    def delete_gitea_repository(self, user_token: str = None):
        """
        Delete the associated Gitea repository

        Args:
            user_token: User's Gitea API token (optional)

        Returns:
            Tuple of (success: bool, message: str)
        """
        from apps.gitea_app.api_client import GiteaClient
        import logging

        logger = logging.getLogger(__name__)

        if not self.gitea_enabled or not self.gitea_repo_name:
            return False, "No Gitea repository associated with this project"

        try:
            client = GiteaClient(token=user_token) if user_token else GiteaClient()
            client.delete_repository(self.owner.username, self.gitea_repo_name)

            # Clear Gitea integration fields
            self.gitea_repo_id = None
            self.gitea_repo_name = ''
            self.gitea_repo_url = ''
            self.gitea_clone_url = ''
            self.gitea_ssh_url = ''
            self.gitea_enabled = False
            self.save()

            logger.info(f"✓ Deleted Gitea repository: {self.owner.username}/{self.gitea_repo_name}")
            return True, "Gitea repository deleted successfully"

        except Exception as e:
            logger.error(f"Failed to delete Gitea repository {self.gitea_repo_name}: {e}")
            return False, str(e)

    @classmethod
    def cleanup_orphaned_gitea_repos(cls, user, user_token: str = None):
        """
        Find and optionally delete Gitea repositories that don't have corresponding Django projects

        Args:
            user: Django User object
            user_token: User's Gitea API token (optional)

        Returns:
            Dict with lists of orphaned repositories
        """
        from apps.gitea_app.api_client import GiteaClient
        import logging

        logger = logging.getLogger(__name__)
        client = GiteaClient(token=user_token) if user_token else GiteaClient()

        try:
            # Get all Gitea repositories for this user
            gitea_repos = client.list_repositories(user.username)

            # Get all Django projects with Gitea integration
            django_projects = cls.objects.filter(
                owner=user,
                gitea_enabled=True
            ).values_list('gitea_repo_name', 'gitea_repo_id')

            django_repo_names = {name for name, _ in django_projects if name}
            django_repo_ids = {repo_id for _, repo_id in django_projects if repo_id}

            # Find orphaned repositories
            orphaned = []
            for repo in gitea_repos:
                repo_name = repo.get('name')
                repo_id = repo.get('id')

                if repo_name not in django_repo_names and repo_id not in django_repo_ids:
                    orphaned.append({
                        'id': repo_id,
                        'name': repo_name,
                        'url': repo.get('html_url', ''),
                        'created_at': repo.get('created_at', ''),
                    })

            return {
                'orphaned': orphaned,
                'total_gitea': len(gitea_repos),
                'total_django': len(django_repo_names),
            }

        except Exception as e:
            logger.error(f"Failed to check for orphaned repositories: {e}")
            return {'error': str(e)}

    def update_storage_usage(self):
        """
        Calculate and update storage usage for this project

        Returns:
            int: Updated storage size in bytes
        """
        from pathlib import Path
        from apps.project_app.services.project_filesystem import get_project_filesystem_manager

        if not self.directory_created:
            return 0

        try:
            manager = get_project_filesystem_manager(self.owner)
            project_path = manager.get_project_root_path(self)

            if not project_path or not project_path.exists():
                return 0

            # Calculate total size of all files in project directory
            total_size = 0
            for item in project_path.rglob('*'):
                if item.is_file():
                    try:
                        total_size += item.stat().st_size
                    except (OSError, PermissionError):
                        # Skip files we can't access
                        pass

            # Update without triggering signals to avoid recursion
            Project.objects.filter(id=self.id).update(storage_used=total_size)
            self.storage_used = total_size

            return total_size

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating storage for project {self.name}: {e}")
            return self.storage_used

    # ----------------------------------------
    # SciTeX Integration Methods
    # ----------------------------------------

    def get_local_path(self):
        """
        Get Path object for local project directory.

        Returns:
            Path to project directory (e.g., data/users/ywatanabe/neural-decoding/)
        """
        from pathlib import Path

        if not self.local_path:
            # Default location
            from apps.project_app.services.project_filesystem import get_project_filesystem_manager
            manager = get_project_filesystem_manager(self.owner)
            return manager.base_path / self.slug
        return Path(self.local_path)

    def has_scitex_metadata(self):
        """Check if project has scitex/.metadata/ directory."""
        local_path = self.get_local_path()
        return (local_path / 'scitex' / '.metadata').exists()

    def to_scitex_project(self):
        """
        Convert Django model to SciTeXProject dataclass.

        Returns:
            SciTeXProject instance loaded from scitex/.metadata/

        Raises:
            FileNotFoundError: If scitex/.metadata/ doesn't exist
            ImportError: If scitex package is not installed
        """
        try:
            from scitex.project import SciTeXProject
        except ImportError:
            raise ImportError(
                "scitex package is not installed. "
                "Install it with: pip install scitex"
            )

        if not self.has_scitex_metadata():
            raise FileNotFoundError(
                f"Project '{self.name}' has no scitex/.metadata/ directory. "
                f"Call initialize_scitex_metadata() first."
            )

        return SciTeXProject.load_from_directory(self.get_local_path())

    def initialize_scitex_metadata(self):
        """
        Initialize scitex/.metadata/ directory for existing Django project.

        This is used during migration to add scitex/.metadata/ to projects that don't have it yet.

        Returns:
            Newly created SciTeXProject

        Raises:
            FileExistsError: If scitex/.metadata/ already exists
            ImportError: If scitex package is not installed
        """
        try:
            from scitex.project import SciTeXProject
        except ImportError:
            raise ImportError(
                "scitex package is not installed. "
                "Install it with: pip install scitex"
            )

        if self.has_scitex_metadata():
            raise FileExistsError(f"Project '{self.name}' already has scitex/.metadata/")

        local_path = self.get_local_path()

        # Create directory if it doesn't exist
        local_path.mkdir(parents=True, exist_ok=True)

        # Create SciTeXProject
        scitex_project = SciTeXProject.create(
            name=self.name,
            path=local_path,
            owner=self.owner.username,
            description=self.description,
            visibility=self.visibility,
            template=None,  # Unknown for existing projects
            tags=[],  # No tags in current Django model
            init_git=False  # Git might already be initialized
        )

        # Link Django project to SciTeXProject
        self.scitex_project_id = scitex_project.project_id
        self.local_path = str(local_path)
        self.save(update_fields=['scitex_project_id', 'local_path'])

        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Initialized scitex metadata for project '{self.name}' "
            f"(ID: {scitex_project.project_id})"
        )

        return scitex_project

    def sync_from_scitex(self):
        """
        Update Django model from SciTeXProject metadata.

        Use this when scitex/.metadata/ is the source of truth (e.g., after local edits).
        """
        scitex_project = self.to_scitex_project()

        # Update fields from SciTeXProject
        self.name = scitex_project.name
        self.slug = scitex_project.slug
        self.description = scitex_project.description
        self.visibility = scitex_project.visibility
        self.storage_used = scitex_project.storage_used

        self.save()

        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Synced Django project '{self.name}' from scitex metadata")

    def sync_to_scitex(self):
        """
        Update SciTeXProject from Django model.

        Use this when Django model is the source of truth (e.g., after web UI changes).
        """
        scitex_project = self.to_scitex_project()

        # Update SciTeXProject fields
        scitex_project.name = self.name
        scitex_project.slug = self.slug
        scitex_project.description = self.description
        scitex_project.visibility = self.visibility

        # Save to scitex/.metadata/
        scitex_project.save()

        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Synced scitex metadata from Django project '{self.name}'")

    def update_storage_from_scitex(self):
        """
        Calculate storage using SciTeXProject and update Django model.

        Returns:
            Storage size in bytes
        """
        if not self.has_scitex_metadata():
            # Fall back to old method
            return self.update_storage_usage()

        scitex_project = self.to_scitex_project()
        storage = scitex_project.update_storage_usage()

        # Update Django model
        self.storage_used = storage
        self.save(update_fields=['storage_used'])

        return storage

    @classmethod
    def validate_name_using_scitex(cls, name):
        """
        Validate project name using scitex.project validator.

        Raises:
            ValidationError: If name is invalid
            ImportError: If scitex package is not installed
        """
        from django.core.exceptions import ValidationError

        try:
            from scitex.project import validate_name
        except ImportError:
            # Fall back to existing validator
            return cls.validate_repository_name(name)

        is_valid, error = validate_name(name)
        if not is_valid:
            raise ValidationError(error)


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


# =============================================================================
# Social Interaction Models (Watch, Star, Fork)
# =============================================================================

class ProjectWatch(models.Model):
    """
    Model to track users watching a project for notifications
    Similar to GitHub's watch feature
    """
    NOTIFICATION_CHOICES = [
        ('all', 'All Activity'),
        ('participating', 'Participating and @mentions'),
        ('ignoring', 'Ignore'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_watches'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_watchers'
    )
    notification_settings = models.CharField(
        max_length=20,
        choices=NOTIFICATION_CHOICES,
        default='all',
        help_text="Notification preference for this project"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')
        verbose_name = 'Project Watch'
        verbose_name_plural = 'Project Watches'
        indexes = [
            models.Index(fields=['user', 'project']),
            models.Index(fields=['project', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} watches {self.project.name}"


class ProjectStar(models.Model):
    """
    Model to track users starring a project
    Similar to GitHub's star feature - indicates interest/bookmarking
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_stars'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_stars_set'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')
        verbose_name = 'Project Star'
        verbose_name_plural = 'Project Stars'
        indexes = [
            models.Index(fields=['user', 'project']),
            models.Index(fields=['project', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} starred {self.project.name}"


class ProjectFork(models.Model):
    """
    Model to track project forks
    Similar to GitHub's fork feature - creates a copy of a project
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_forks',
        help_text="User who created the fork"
    )
    original_project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_forks_set',
        help_text="The original project that was forked"
    )
    forked_project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='forked_from',
        help_text="The new forked project"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Optional: Track if fork is synced with original
    last_sync_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time fork was synced with original"
    )

    class Meta:
        unique_together = ('user', 'original_project', 'forked_project')
        verbose_name = 'Project Fork'
        verbose_name_plural = 'Project Forks'
        indexes = [
            models.Index(fields=['user', 'original_project']),
            models.Index(fields=['original_project', 'created_at']),
            models.Index(fields=['forked_project']),
        ]

    def __str__(self):
        return f"{self.user.username} forked {self.original_project.name} to {self.forked_project.name}"


# =============================================================================
# Import Issue models from models_issues.py
# =============================================================================
# Note: Issue models are defined in models_issues.py but imported here for consistency
try:
    from apps.project_app.models_issues import (
        Issue,
        IssueComment,
        IssueLabel,
        IssueMilestone,
        IssueAssignment,
        IssueEvent,
    )
except ImportError:
    # models_issues.py hasn't been created yet or has import issues
    pass

# =============================================================================
# Import Pull Request models from models_pull_requests.py
# =============================================================================
# Note: PR models are defined in models_pull_requests.py but imported here for consistency
try:
    from apps.project_app.models_pull_requests import (
        PullRequest,
        PullRequestReview,
        PullRequestComment,
        PullRequestCommit,
        PullRequestLabel,
        PullRequestEvent,
    )
except ImportError:
    # models_pull_requests.py hasn't been created yet or has import issues
    pass