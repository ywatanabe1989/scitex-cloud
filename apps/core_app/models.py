from django.db import models
from django.contrib.auth.models import User
import random
import string
from datetime import timedelta
from django.utils import timezone


# Japanese Academic domains to recognize
JAPANESE_ACADEMIC_DOMAINS = [
    # Japanese Academic (.ac.jp) - All academic institutions
    '.ac.jp',
    '.u-tokyo.ac.jp', '.kyoto-u.ac.jp', '.osaka-u.ac.jp',
    '.tohoku.ac.jp', '.nagoya-u.ac.jp', '.kyushu-u.ac.jp',
    '.hokudai.ac.jp', '.tsukuba.ac.jp', '.hiroshima-u.ac.jp',
    '.kobe-u.ac.jp', '.waseda.jp', '.keio.ac.jp',
    
    # Government Research Institutions (.go.jp)
    '.go.jp',  # Broader government research support
    '.riken.jp', '.aist.go.jp', '.nict.go.jp', '.jaxa.jp',
    '.jst.go.jp', '.nims.go.jp', '.nies.go.jp'
]


def is_japanese_academic_email(email):
    """Check if email belongs to Japanese academic institution"""
    if not email:
        return False
    try:
        domain = email.lower().split('@')[1]
        # Check if domain matches exactly or ends with the academic domain
        for academic_domain in JAPANESE_ACADEMIC_DOMAINS:
            # Remove leading dot for exact matching
            clean_domain = academic_domain.lstrip('.')
            if domain == clean_domain or domain.endswith(academic_domain):
                return True
        return False
    except (IndexError, AttributeError):
        return False


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
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
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
            from .directory_manager import get_user_directory_manager
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
            'revision': '.tex',
            'draft': '.md',
            'hypothesis': '.md'
        }
        return extensions.get(self.document_type, '.txt')
    
    def save_to_directory(self):
        """Save document content to the directory structure"""
        from .directory_manager import get_user_directory_manager
        manager = get_user_directory_manager(self.owner)
        
        if self.project:
            # Determine document category for directory placement
            category = 'manuscripts' if self.document_type in ['manuscript', 'draft', 'revision'] else 'notes'
            success, file_path = manager.store_document(self, self.content, category)
            return success
        return False


class UserProfile(models.Model):
    """Extended user profile for researchers"""
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('restricted', 'Restricted'), 
        ('private', 'Private'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, help_text="Brief description of your research background")
    institution = models.CharField(max_length=200, blank=True, help_text="Your current institution")
    research_interests = models.TextField(max_length=500, blank=True, help_text="Your research areas and interests")
    website = models.URLField(blank=True, help_text="Your personal or professional website")
    
    # Academic information
    orcid = models.CharField(max_length=19, blank=True, help_text="Your ORCID identifier (e.g., 0000-0000-0000-0000)")
    academic_title = models.CharField(max_length=100, blank=True, help_text="Your academic title (e.g., PhD, Professor)")
    department = models.CharField(max_length=200, blank=True, help_text="Your department or faculty")
    
    # Professional links
    google_scholar = models.URLField(blank=True, help_text="Your Google Scholar profile")
    linkedin = models.URLField(blank=True, help_text="Your LinkedIn profile")
    researchgate = models.URLField(blank=True, help_text="Your ResearchGate profile")
    twitter = models.CharField(max_length=50, blank=True, help_text="Your Twitter handle (without @)")
    
    # Privacy settings
    profile_visibility = models.CharField(
        max_length=20, 
        choices=VISIBILITY_CHOICES, 
        default='public',
        help_text="Who can view your profile"
    )
    is_public = models.BooleanField(default=True, help_text="Make profile public")
    show_email = models.BooleanField(default=False, help_text="Show email in public profile")
    allow_collaboration = models.BooleanField(default=True, help_text="Allow collaboration requests")
    allow_messages = models.BooleanField(default=True, help_text="Allow messages from other users")
    
    # Academic institution recognition
    is_academic_ja = models.BooleanField(
        default=False, 
        help_text="Automatically detected: User belongs to Japanese academic institution"
    )
    
    # Account deletion
    deletion_scheduled_at = models.DateTimeField(null=True, blank=True, help_text="When account deletion was scheduled")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"Profile for {self.user.get_full_name() or self.user.username}"
    
    def get_display_name(self):
        """Get the best display name for the user"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username
    
    def get_full_title(self):
        """Get full academic title and name"""
        name = self.get_display_name()
        if self.academic_title:
            return f"{self.academic_title} {name}"
        return name
    
    def is_complete(self):
        """Check if profile has essential information"""
        return bool(
            self.bio and 
            self.institution and 
            self.research_interests
        )
    
    @property
    def total_documents(self):
        """Get total number of documents created by the user"""
        return self.user.documents.count()
    
    @property
    def total_projects(self):
        """Get total number of projects owned by the user"""
        return self.user.owned_projects.count()
    
    @property
    def total_collaborations(self):
        """Get total number of collaborations"""
        # Count projects where user is a member (not owner)
        return ProjectPermission.objects.filter(user=self.user).count()
    
    def get_social_links(self):
        """Get available social/professional links"""
        links = []
        if self.website:
            links.append(('Website', self.website))
        if self.google_scholar:
            links.append(('Google Scholar', self.google_scholar))
        if self.linkedin:
            links.append(('LinkedIn', self.linkedin))
        if self.researchgate:
            links.append(('ResearchGate', self.researchgate))
        if self.twitter:
            links.append(('Twitter', f"https://twitter.com/{self.twitter}"))
        return links
    
    def update_academic_status(self):
        """Update is_academic_ja flag based on user's email"""
        self.is_academic_ja = is_japanese_academic_email(self.user.email)
        return self.is_academic_ja
    
    def get_academic_status_display(self):
        """Get display text for academic status"""
        if self.is_academic_ja:
            return "Japanese Academic Institution"
        return "General User"
    
    def save(self, *args, **kwargs):
        """Override save to automatically update academic status"""
        # Update academic status before saving
        self.update_academic_status()
        super().save(*args, **kwargs)


class Organization(models.Model):
    """Model for research organizations"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(User, through='OrganizationMembership')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class OrganizationMembership(models.Model):
    """Model for organization membership with roles"""
    ROLES = [
        ('admin', 'Administrator'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'organization')
        
    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"


class ResearchGroup(models.Model):
    """Model for research groups/labs with hierarchical structure"""
    
    name = models.CharField(max_length=200, help_text="Research group/lab name (e.g., 'Ikegaya Lab')")
    description = models.TextField(blank=True, help_text="Description of research focus and goals")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='research_groups')
    
    # Group leadership
    principal_investigator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_groups', 
                                             help_text="PI/Lab head with full administrative control")
    admins = models.ManyToManyField(User, related_name='administered_groups', blank=True,
                                   help_text="Additional admins (senior postdocs, co-PIs)")
    
    # Group membership
    members = models.ManyToManyField(User, through='ResearchGroupMembership', related_name='research_groups')
    
    # Group settings
    is_public = models.BooleanField(default=False, help_text="Public group visibility")
    allow_external_collaborators = models.BooleanField(default=True, help_text="Allow external collaborators")
    auto_approve_internal = models.BooleanField(default=True, help_text="Auto-approve same organization members")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ('name', 'organization')
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"
    
    def get_all_members(self):
        """Get all members including PI and admins"""
        member_ids = set(self.members.values_list('id', flat=True))
        member_ids.add(self.principal_investigator.id)
        member_ids.update(self.admins.values_list('id', flat=True))
        return User.objects.filter(id__in=member_ids)
    
    def is_member(self, user):
        """Check if user is a member of this group"""
        return (user == self.principal_investigator or 
                self.admins.filter(id=user.id).exists() or
                self.members.filter(id=user.id).exists())
    
    def get_user_role(self, user):
        """Get user's role in this group"""
        if user == self.principal_investigator:
            return 'pi'
        elif self.admins.filter(id=user.id).exists():
            return 'admin'
        else:
            try:
                membership = ResearchGroupMembership.objects.get(group=self, user=user)
                return membership.role
            except ResearchGroupMembership.DoesNotExist:
                return None


class ResearchGroupMembership(models.Model):
    """Model for research group membership with roles"""
    
    GROUP_ROLES = [
        ('postdoc', 'Postdoctoral Researcher'),
        ('phd', 'PhD Student'),
        ('masters', 'Masters Student'),
        ('undergrad', 'Undergraduate Student'),
        ('researcher', 'Research Staff'),
        ('visiting', 'Visiting Researcher'),
        ('collaborator', 'External Collaborator'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ResearchGroup, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=GROUP_ROLES, default='researcher')
    
    # Permissions within group
    can_create_projects = models.BooleanField(default=True, help_text="Can create new projects for the group")
    can_invite_collaborators = models.BooleanField(default=False, help_text="Can invite external collaborators")
    
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('user', 'group')
        ordering = ['joined_at']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.group.name} ({self.role})"


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
    """Model for research projects with enhanced collaboration"""
    
    PROJECT_STATUS = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
    research_group = models.ForeignKey(ResearchGroup, on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='projects', help_text="Associated research group/lab")
    
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
    manuscript_draft = models.ForeignKey('Document', on_delete=models.SET_NULL, null=True, blank=True, 
                                       related_name='project_manuscripts', 
                                       help_text="Associated manuscript document")
    
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
        
    def __str__(self):
        return self.name
    
    def get_progress_percentage(self):
        """Return progress as percentage"""
        return min(max(self.progress, 0), 100)
    
    def get_directory_path(self):
        """Get the full directory path for this project"""
        if self.data_location:
            from .directory_manager import get_user_directory_manager
            manager = get_user_directory_manager(self.owner)
            return manager.base_path / self.data_location
        return None
    
    def ensure_directory(self):
        """Ensure project directory exists"""
        from .directory_manager import get_user_directory_manager
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
        from .directory_manager import get_user_directory_manager
        manager = get_user_directory_manager(self.owner)
        return manager.get_project_structure(self)
    
    def list_files(self, category=None):
        """List files in the project directory"""
        from .directory_manager import get_user_directory_manager
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


class EmailVerification(models.Model):
    """Model for email verification with 6-digit OTP"""
    
    VERIFICATION_TYPES = [
        ('signup', 'Signup Verification'),
        ('password_reset', 'Password Reset'),
        ('email_change', 'Email Change'),
    ]
    
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPES, default='signup')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='email_verifications')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'otp_code']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"OTP for {self.email} - {self.otp_code}"
    
    def save(self, *args, **kwargs):
        """Auto-generate OTP and expiration if not set"""
        if not self.otp_code:
            self.otp_code = self.generate_otp()
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)  # 10 minutes expiry
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if OTP is valid (not expired, not exceeded attempts, not verified)"""
        return (
            not self.is_expired() and 
            self.attempts < self.max_attempts and 
            not self.is_verified
        )
    
    def verify(self, provided_otp):
        """Verify the provided OTP against this record"""
        self.attempts += 1
        
        if not self.is_valid():
            self.save()
            return False, "OTP has expired or maximum attempts exceeded"
        
        if self.otp_code == provided_otp:
            self.is_verified = True
            self.save()
            return True, "Email verified successfully"
        
        self.save()
        remaining_attempts = self.max_attempts - self.attempts
        if remaining_attempts > 0:
            return False, f"Invalid OTP. {remaining_attempts} attempts remaining"
        else:
            return False, "Maximum verification attempts exceeded"
    
    @classmethod
    def create_verification(cls, email, verification_type='signup', user=None):
        """Create a new email verification OTP"""
        # Invalidate any existing verifications for this email
        cls.objects.filter(
            email=email, 
            verification_type=verification_type,
            is_verified=False
        ).update(is_verified=True)  # Mark old ones as used
        
        # Create new verification
        verification = cls.objects.create(
            email=email,
            verification_type=verification_type,
            user=user
        )
        return verification
    
    @classmethod
    def cleanup_expired(cls):
        """Clean up expired OTP records (should be run periodically)"""
        expired_count = cls.objects.filter(expires_at__lt=timezone.now()).delete()
        return expired_count