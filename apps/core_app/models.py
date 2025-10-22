from django.db import models
from django.contrib.auth.models import User
import random
import string
from datetime import timedelta
from django.utils import timezone


# UserProfile model moved to apps.profile_app.models
# Import here for backwards compatibility
from apps.profile_app.models import UserProfile  # noqa

# Japanese Academic utilities moved to apps.profile_app.models
from apps.profile_app.models import JAPANESE_ACADEMIC_DOMAINS, is_japanese_academic_email  # noqa

# Organization and ResearchGroup models moved to apps.organizations_app.models
# Import here for backwards compatibility
from apps.organizations_app.models import (  # noqa
    Organization,
    OrganizationMembership,
    ResearchGroup,
    ResearchGroupMembership,
)

# Document model moved to apps.document_app.models


class ProjectMembership(models.Model):
    """Model for project-specific membership with fine-grained permissions"""
    
    PROJECT_ROLES = [
        ('owner', 'Project Owner'),
        ('admin', 'Project Administrator'),
        ('editor', 'Editor'),
        ('collaborator', 'Collaborator'),
        ('viewer', 'Viewer'),
        ('reviewer', 'External Reviewer'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=PROJECT_ROLES, default='collaborator')
    
    # File and directory permissions
    can_read_files = models.BooleanField(default=True, help_text="Can read project files")
    can_write_files = models.BooleanField(default=False, help_text="Can modify project files")
    can_delete_files = models.BooleanField(default=False, help_text="Can delete project files")
    can_manage_collaborators = models.BooleanField(default=False, help_text="Can add/remove collaborators")
    
    # Research workflow permissions
    can_edit_metadata = models.BooleanField(default=False, help_text="Can edit project description, hypotheses")
    can_run_analysis = models.BooleanField(default=False, help_text="Can execute code and analysis")
    can_export_data = models.BooleanField(default=True, help_text="Can download/export project data")
    can_view_results = models.BooleanField(default=True, help_text="Can view analysis results")
    
    # Administrative permissions
    can_change_settings = models.BooleanField(default=False, help_text="Can modify project settings")
    can_archive_project = models.BooleanField(default=False, help_text="Can archive/delete project")
    
    # Access constraints
    access_expires_at = models.DateTimeField(null=True, blank=True, help_text="Temporary access expiration")
    access_granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                        related_name='granted_accesses', help_text="Who granted this access")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('user', 'project')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.project.name} ({self.role})"
    
    def is_expired(self):
        """Check if access has expired"""
        if self.access_expires_at:
            return timezone.now() > self.access_expires_at
        return False
    
    def get_effective_permissions(self):
        """Get effective permissions based on role and individual settings"""
        # Role-based defaults
        role_permissions = {
            'owner': {
                'can_read_files': True, 'can_write_files': True, 'can_delete_files': True,
                'can_manage_collaborators': True, 'can_edit_metadata': True, 'can_run_analysis': True,
                'can_export_data': True, 'can_view_results': True, 'can_change_settings': True,
                'can_archive_project': True
            },
            'admin': {
                'can_read_files': True, 'can_write_files': True, 'can_delete_files': True,
                'can_manage_collaborators': True, 'can_edit_metadata': True, 'can_run_analysis': True,
                'can_export_data': True, 'can_view_results': True, 'can_change_settings': False,
                'can_archive_project': False
            },
            'editor': {
                'can_read_files': True, 'can_write_files': True, 'can_delete_files': False,
                'can_manage_collaborators': False, 'can_edit_metadata': True, 'can_run_analysis': True,
                'can_export_data': True, 'can_view_results': True, 'can_change_settings': False,
                'can_archive_project': False
            },
            'collaborator': {
                'can_read_files': True, 'can_write_files': True, 'can_delete_files': False,
                'can_manage_collaborators': False, 'can_edit_metadata': False, 'can_run_analysis': True,
                'can_export_data': True, 'can_view_results': True, 'can_change_settings': False,
                'can_archive_project': False
            },
            'viewer': {
                'can_read_files': True, 'can_write_files': False, 'can_delete_files': False,
                'can_manage_collaborators': False, 'can_edit_metadata': False, 'can_run_analysis': False,
                'can_export_data': True, 'can_view_results': True, 'can_change_settings': False,
                'can_archive_project': False
            },
            'reviewer': {
                'can_read_files': True, 'can_write_files': False, 'can_delete_files': False,
                'can_manage_collaborators': False, 'can_edit_metadata': False, 'can_run_analysis': False,
                'can_export_data': False, 'can_view_results': True, 'can_change_settings': False,
                'can_archive_project': False
            }
        }
        
        # Get role defaults
        defaults = role_permissions.get(self.role, role_permissions['viewer'])
        
        # Override with individual settings (more restrictive only)
        effective = {}
        for perm, default_value in defaults.items():
            individual_value = getattr(self, perm, default_value)
            # Individual settings can only restrict, not expand permissions
            effective[perm] = default_value and individual_value
        
        return effective


class Project(models.Model):
    """
    DEPRECATED: Use apps.project_app.models.Project instead.
    This model is duplicated and will be removed in the next version.

    Model for research projects with enhanced collaboration
    """

    PROJECT_STATUS = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='core_owned_projects')
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name='core_projects')
    research_group = models.ForeignKey(ResearchGroup, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='core_projects', help_text="Associated research group/lab")
    
    # Enhanced collaboration through ProjectMembership
    collaborators = models.ManyToManyField(User, through='ProjectMembership', through_fields=('project', 'user'), related_name='collaborative_projects')
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='planning')
    progress = models.IntegerField(default=0, help_text="Project progress percentage (0-100)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True)
    
    # Research data - Core SciTeX workflow fields
    hypotheses = models.TextField(help_text="Research hypotheses (required)")
    source_code_url = models.URLField(blank=True, help_text="GitHub/GitLab repository URL")
    data_location = models.CharField(max_length=500, blank=True, help_text="Relative path to project directory")
    # manuscript_draft = models.ForeignKey('document_app.Document', on_delete=models.SET_NULL, null=True, blank=True,  # Removed - document_app not installed
    #                                    related_name='project_manuscripts',
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
        managed = False
        db_table = 'project_app_project'
        ordering = ['-updated_at']
        unique_together = ('name', 'owner')  # Ensure unique project names per user
        
    def __str__(self):
        return self.name
    
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
        safe_name = safe_name.strip('.')  # Remove leading/trailing dots
        return safe_name or 'scitex_project'
    
    def get_progress_percentage(self):
        """Return progress as percentage"""
        return min(max(self.progress, 0), 100)
    
    def get_directory_path(self):
        """Get the full directory path for this project"""
        if self.data_location:
            from .services.directory_service import get_user_directory_manager
            manager = get_user_directory_manager(self.owner)
            return manager.base_path / self.data_location
        return None

    def ensure_directory(self):
        """Ensure project directory exists"""
        from .services.directory_service import get_user_directory_manager
        manager = get_user_directory_manager(self.owner)

        if not self.directory_created:
            success, path = manager.create_project_directory(self)
            if success:
                self.directory_created = True
                self.save()
            return success
        return True

    def get_file_structure(self):
        """Get the complete file structure for this project"""
        from .services.directory_service import get_user_directory_manager
        manager = get_user_directory_manager(self.owner)
        return manager.get_project_structure(self)

    def list_files(self, category=None):
        """List files in the project directory"""
        from .services.directory_service import get_user_directory_manager
        manager = get_user_directory_manager(self.owner)
        return manager.list_project_files(self, category)
    
    def update_storage_usage(self):
        """Update storage usage for this project"""
        project_path = self.get_directory_path()
        if project_path and project_path.exists():
            total_size = 0
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            # Update without triggering signals to avoid recursion
            Project.objects.filter(id=self.id).update(storage_used=total_size)
            self.storage_used = total_size  # Update instance too
            return total_size
        return 0
    
    def get_storage_usage_mb(self):
        """Get storage usage in MB"""
        return round(self.storage_used / (1024 * 1024), 2)
    
    def get_github_repo_url(self):
        """Get full GitHub repository URL"""
        if self.github_owner and self.github_repo_name:
            return f"https://github.com/{self.github_owner}/{self.github_repo_name}"
        return self.source_code_url
    
    def is_github_connected(self):
        """Check if project is connected to GitHub"""
        return bool(self.github_integration_enabled and self.github_token and self.github_repo_id)
    
    def get_github_status(self):
        """Get GitHub integration status"""
        if not self.github_integration_enabled:
            return 'disconnected'
        elif not self.github_token:
            return 'auth_required'
    
    # Enhanced permission methods for collaboration
    def has_permission(self, user, permission):
        """Check if user has specific permission for this project"""
        if user == self.owner:
            return True  # Owner has all permissions
        
        try:
            membership = ProjectMembership.objects.get(user=user, project=self, is_active=True)
            if membership.is_expired():
                return False
            
            effective_perms = membership.get_effective_permissions()
            return effective_perms.get(permission, False)
        except ProjectMembership.DoesNotExist:
            return False
    
    def can_read_files(self, user):
        """Check if user can read project files"""
        return self.has_permission(user, 'can_read_files')
    
    def can_write_files(self, user):
        """Check if user can write project files"""
        return self.has_permission(user, 'can_write_files')
    
    def can_delete_files(self, user):
        """Check if user can delete project files"""
        return self.has_permission(user, 'can_delete_files')
    
    def can_manage_collaborators(self, user):
        """Check if user can manage project collaborators"""
        return self.has_permission(user, 'can_manage_collaborators')
    
    def can_edit_metadata(self, user):
        """Check if user can edit project metadata"""
        return self.has_permission(user, 'can_edit_metadata')
    
    def can_run_analysis(self, user):
        """Check if user can run analysis/code"""
        return self.has_permission(user, 'can_run_analysis')
    
    def get_user_role(self, user):
        """Get user's role in this project"""
        if user == self.owner:
            return 'owner'
        
        try:
            membership = ProjectMembership.objects.get(user=user, project=self, is_active=True)
            return membership.role
        except ProjectMembership.DoesNotExist:
            return None
    
    def add_collaborator(self, user, role='collaborator', granted_by=None, **permissions):
        """Add a collaborator to the project with specific role and permissions"""
        membership, created = ProjectMembership.objects.get_or_create(
            user=user,
            project=self,
            defaults={
                'role': role,
                'access_granted_by': granted_by,
                'is_active': True,
                **permissions
            }
        )
        
        if not created:
            # Update existing membership
            membership.role = role
            membership.is_active = True
            if granted_by:
                membership.access_granted_by = granted_by
            
            # Update permissions if provided
            for perm, value in permissions.items():
                if hasattr(membership, perm):
                    setattr(membership, perm, value)
            
            membership.save()
        
        return membership
    
    def remove_collaborator(self, user):
        """Remove a collaborator from the project"""
        try:
            membership = ProjectMembership.objects.get(user=user, project=self)
            membership.is_active = False
            membership.save()
            return True
        except ProjectMembership.DoesNotExist:
            return False
    
    def get_all_collaborators(self):
        """Get all active collaborators including owner"""
        collaborator_ids = set(
            self.memberships.filter(is_active=True).values_list('user_id', flat=True)
        )
        collaborator_ids.add(self.owner.id)
        return User.objects.filter(id__in=collaborator_ids)
    
    def add_research_group(self, research_group, default_role='collaborator'):
        """Add all members of a research group to the project"""
        added_members = []
        
        for member in research_group.get_all_members():
            if member != self.owner:  # Don't add owner as collaborator
                # Determine role based on group hierarchy
                group_role = research_group.get_user_role(member)
                project_role = default_role
                
                # Map group roles to project roles
                if group_role == 'pi':
                    project_role = 'admin'
                elif group_role == 'admin':
                    project_role = 'editor'
                elif group_role in ['postdoc', 'researcher']:
                    project_role = 'collaborator'
                elif group_role in ['phd', 'masters']:
                    project_role = 'collaborator'
                else:
                    project_role = 'viewer'
                
                membership = self.add_collaborator(member, role=project_role)
                added_members.append(membership)
        
        return added_members
    
    def is_accessible_by(self, user):
        """Check if project is accessible by user (any level of access)"""
        if user == self.owner:
            return True
        
        # Check direct project membership
        if self.memberships.filter(user=user, is_active=True).exists():
            membership = self.memberships.get(user=user, is_active=True)
            return not membership.is_expired()
        
        # Check research group membership if project belongs to a group
        if self.research_group and self.research_group.is_member(user):
            return True
        
        return False
    
    def get_github_status_complete(self):
        """Get complete GitHub integration status"""
        if not self.github_integration_enabled:
            return 'disconnected'
        elif not self.github_token:
            return 'auth_required'
        elif not self.github_repo_id:
            return 'repo_required'
        else:
            return 'connected'


class GitFileStatus(models.Model):
    """Model for tracking Git file status within projects"""
    
    GIT_STATUS_CHOICES = [
        ('untracked', 'Untracked'),
        ('modified', 'Modified'),
        ('added', 'Added'),
        ('deleted', 'Deleted'),
        ('renamed', 'Renamed'),
        ('copied', 'Copied'),
        ('staged', 'Staged'),
        ('committed', 'Committed'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='git_files')
    file_path = models.CharField(max_length=500, help_text="Relative path from project root")
    git_status = models.CharField(max_length=20, choices=GIT_STATUS_CHOICES, default='untracked')
    last_commit_hash = models.CharField(max_length=40, blank=True, help_text="SHA of last commit affecting this file")
    last_commit_message = models.CharField(max_length=200, blank=True, help_text="Last commit message")
    last_modified_at = models.DateTimeField(auto_now=True)
    file_size = models.BigIntegerField(default=0, help_text="File size in bytes")
    is_binary = models.BooleanField(default=False, help_text="Whether file is binary")
    
    class Meta:
        unique_together = ('project', 'file_path')
        ordering = ['file_path']
        indexes = [
            models.Index(fields=['project', 'git_status']),
            models.Index(fields=['project', 'file_path']),
        ]
    
    def __str__(self):
        return f"{self.project.name}:{self.file_path} ({self.git_status})"
    
    def get_status_icon(self):
        """Get FontAwesome icon for git status"""
        icons = {
            'untracked': 'fas fa-question-circle text-warning',
            'modified': 'fas fa-edit text-primary',
            'added': 'fas fa-plus-circle text-success',
            'deleted': 'fas fa-trash text-danger',
            'renamed': 'fas fa-exchange-alt text-info',
            'copied': 'fas fa-copy text-info',
            'staged': 'fas fa-check-circle text-success',
            'committed': 'fas fa-check text-muted',
        }
        return icons.get(self.git_status, 'fas fa-file')
    
    def get_status_color(self):
        """Get color class for git status"""
        colors = {
            'untracked': 'warning',
            'modified': 'primary', 
            'added': 'success',
            'deleted': 'danger',
            'renamed': 'info',
            'copied': 'info',
            'staged': 'success',
            'committed': 'muted',
        }
        return colors.get(self.git_status, 'secondary')


class ProjectPermission(models.Model):
    """Model for project-specific permissions"""
    PERMISSIONS = [
        ('admin', 'Administrator'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='permissions')
    permission = models.CharField(max_length=20, choices=PERMISSIONS, default='viewer')
    granted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'project')
        
    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.permission})"


class Manuscript(models.Model):
    """Model for project manuscripts with versioning"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='core_manuscripts')
    version = models.IntegerField(default=1)
    title = models.CharField(max_length=300)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-version']
        unique_together = ('project', 'version')
        
    def __str__(self):
        return f"{self.title} (v{self.version})"
    
    def save(self, *args, **kwargs):
        """Auto-increment version for new manuscripts"""
        if not self.pk:
            last_manuscript = Manuscript.objects.filter(project=self.project).order_by('-version').first()
            if last_manuscript:
                self.version = last_manuscript.version + 1
        super().save(*args, **kwargs)
    
    def get_diff_with_previous(self):
        """Get differences with previous version"""
        previous = Manuscript.objects.filter(
            project=self.project, 
            version=self.version-1
        ).first()
        
        if not previous:
            return None
            
        import difflib
        diff = difflib.unified_diff(
            previous.content.splitlines(keepends=True),
            self.content.splitlines(keepends=True),
            fromfile=f'Version {previous.version}',
            tofile=f'Version {self.version}',
            lineterm=''
        )
        return ''.join(diff)


# EmailVerification model moved to apps.auth_app.models