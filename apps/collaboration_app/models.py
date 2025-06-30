from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from apps.project_app.models import Project
from apps.core_app.models import ResearchGroup
import uuid


class Team(models.Model):
    """Model for research teams with collaborative workspaces"""
    
    TEAM_TYPES = [
        ('research', 'Research Team'),
        ('project', 'Project Team'),
        ('department', 'Department Team'),
        ('lab', 'Laboratory Team'),
        ('collaboration', 'Collaboration Team'),
    ]
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('institution', 'Institution Only'),
        ('private', 'Private'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Team name")
    description = models.TextField(blank=True, help_text="Team description and objectives")
    team_type = models.CharField(max_length=20, choices=TEAM_TYPES, default='research')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    
    # Team leadership
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_teams')
    admins = models.ManyToManyField(User, related_name='admin_teams', blank=True)
    
    # Team settings
    allow_member_invites = models.BooleanField(default=False, help_text="Allow members to invite others")
    require_approval = models.BooleanField(default=True, help_text="Require approval for new members")
    max_members = models.IntegerField(default=50, help_text="Maximum number of team members")
    
    # Integration with existing models
    research_group = models.ForeignKey(ResearchGroup, on_delete=models.SET_NULL, null=True, blank=True)
    associated_projects = models.ManyToManyField(Project, related_name='associated_teams', blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['owner', 'is_active']),
            models.Index(fields=['team_type', 'visibility']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_all_members(self):
        """Get all team members including owner and admins"""
        member_ids = set(self.memberships.filter(is_active=True).values_list('user_id', flat=True))
        member_ids.add(self.owner.id)
        member_ids.update(self.admins.values_list('id', flat=True))
        return User.objects.filter(id__in=member_ids)
    
    def get_member_count(self):
        """Get total number of active members"""
        return self.get_all_members().count()
    
    def is_full(self):
        """Check if team has reached maximum capacity"""
        return self.get_member_count() >= self.max_members
    
    def can_user_join(self, user):
        """Check if user can join this team"""
        if not self.is_active or self.is_full():
            return False
        if self.is_member(user):
            return False
        return True
    
    def is_member(self, user):
        """Check if user is a member of this team"""
        return (user == self.owner or 
                self.admins.filter(id=user.id).exists() or
                self.memberships.filter(user=user, is_active=True).exists())
    
    def is_admin(self, user):
        """Check if user is an admin of this team"""
        return user == self.owner or self.admins.filter(id=user.id).exists()
    
    def get_user_role(self, user):
        """Get user's role in this team"""
        if user == self.owner:
            return 'owner'
        elif self.admins.filter(id=user.id).exists():
            return 'admin'
        else:
            try:
                membership = self.memberships.get(user=user, is_active=True)
                return membership.role
            except TeamMembership.DoesNotExist:
                return None
    
    def add_member(self, user, role='member', invited_by=None):
        """Add a member to the team"""
        if not self.can_user_join(user):
            return None, "User cannot join this team"
        
        membership, created = TeamMembership.objects.get_or_create(
            team=self,
            user=user,
            defaults={
                'role': role,
                'invited_by': invited_by,
                'is_active': True
            }
        )
        
        if not created and not membership.is_active:
            membership.is_active = True
            membership.role = role
            membership.save()
        
        return membership, "Member added successfully" if created else "Member reactivated"
    
    def remove_member(self, user):
        """Remove a member from the team"""
        try:
            membership = self.memberships.get(user=user)
            membership.is_active = False
            membership.save()
            return True
        except TeamMembership.DoesNotExist:
            return False


class TeamMembership(models.Model):
    """Model for team membership with roles and permissions"""
    
    ROLES = [
        ('member', 'Member'),
        ('contributor', 'Contributor'),
        ('editor', 'Editor'),
        ('reviewer', 'Reviewer'),
        ('guest', 'Guest'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=20, choices=ROLES, default='member')
    
    # Permissions
    can_invite_members = models.BooleanField(default=False)
    can_create_projects = models.BooleanField(default=True)
    can_manage_projects = models.BooleanField(default=False)
    can_review_work = models.BooleanField(default=False)
    can_export_data = models.BooleanField(default=True)
    
    # Membership details
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_team_invitations')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('team', 'user')
        ordering = ['joined_at']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.team.name} ({self.role})"
    
    def get_effective_permissions(self):
        """Get effective permissions based on role"""
        role_permissions = {
            'guest': {
                'can_invite_members': False,
                'can_create_projects': False,
                'can_manage_projects': False,
                'can_review_work': False,
                'can_export_data': False,
            },
            'member': {
                'can_invite_members': False,
                'can_create_projects': True,
                'can_manage_projects': False,
                'can_review_work': False,
                'can_export_data': True,
            },
            'contributor': {
                'can_invite_members': False,
                'can_create_projects': True,
                'can_manage_projects': True,
                'can_review_work': False,
                'can_export_data': True,
            },
            'editor': {
                'can_invite_members': True,
                'can_create_projects': True,
                'can_manage_projects': True,
                'can_review_work': True,
                'can_export_data': True,
            },
            'reviewer': {
                'can_invite_members': False,
                'can_create_projects': False,
                'can_manage_projects': False,
                'can_review_work': True,
                'can_export_data': True,
            },
        }
        
        defaults = role_permissions.get(self.role, role_permissions['member'])
        effective = {}
        
        for perm in defaults.keys():
            individual_value = getattr(self, perm, defaults[perm])
            effective[perm] = defaults[perm] and individual_value
        
        return effective


class TeamInvitation(models.Model):
    """Model for team invitations"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='team_invitations')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    
    role = models.CharField(max_length=20, choices=TeamMembership.ROLES, default='member')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    message = models.TextField(blank=True, help_text="Personal message with invitation")
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'status']),
            models.Index(fields=['team', 'status']),
        ]
    
    def __str__(self):
        return f"Invitation to {self.email} for {self.team.name}"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def can_accept(self):
        return self.status == 'pending' and not self.is_expired()
    
    def accept(self, user=None):
        """Accept the invitation"""
        if not self.can_accept():
            return False, "Invitation cannot be accepted"
        
        # If user is not specified, try to find by email
        if not user:
            try:
                user = User.objects.get(email=self.email)
            except User.DoesNotExist:
                return False, "User not found"
        
        # Add user to team
        membership, message = self.team.add_member(user, self.role, self.invited_by)
        if membership:
            self.status = 'accepted'
            self.responded_at = timezone.now()
            self.invited_user = user
            self.save()
            return True, "Invitation accepted successfully"
        else:
            return False, message
    
    def reject(self):
        """Reject the invitation"""
        if self.status != 'pending':
            return False
        
        self.status = 'rejected'
        self.responded_at = timezone.now()
        self.save()
        return True


class SharedProject(models.Model):
    """Model for projects shared across teams with collaborative features"""
    
    SHARING_TYPES = [
        ('view', 'View Only'),
        ('comment', 'Comment Only'),
        ('edit', 'Edit Access'),
        ('collaborate', 'Full Collaboration'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='shared_instances')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='shared_projects')
    sharing_type = models.CharField(max_length=20, choices=SHARING_TYPES, default='view')
    
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_projects')
    shared_at = models.DateTimeField(auto_now_add=True)
    
    # Access control
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('project', 'team')
        ordering = ['-shared_at']
    
    def __str__(self):
        return f"{self.project.name} shared with {self.team.name}"
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def is_accessible(self):
        return self.is_active and not self.is_expired()


class Comment(models.Model):
    """Model for comments on projects, documents, and other content"""
    
    COMMENT_TYPES = [
        ('general', 'General Comment'),
        ('suggestion', 'Suggestion'),
        ('review', 'Review Comment'),
        ('question', 'Question'),
        ('approval', 'Approval'),
        ('concern', 'Concern'),
    ]
    
    # Generic foreign key setup for commenting on different models
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    comment_type = models.CharField(max_length=20, choices=COMMENT_TYPES, default='general')
    
    content = models.TextField()
    
    # Threading for replies
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Status and metadata
    is_resolved = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['author', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.content_object}"
    
    def get_replies(self):
        """Get all replies to this comment"""
        return self.replies.filter(is_public=True).order_by('created_at')
    
    def is_thread_starter(self):
        """Check if this is a top-level comment"""
        return self.parent_comment is None


class Review(models.Model):
    """Model for formal reviews of projects and documents"""
    
    REVIEW_TYPES = [
        ('peer', 'Peer Review'),
        ('supervisor', 'Supervisor Review'),
        ('external', 'External Review'),
        ('self', 'Self Review'),
    ]
    
    REVIEW_STATUS = [
        ('requested', 'Review Requested'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
    ]
    
    REVIEW_DECISIONS = [
        ('approve', 'Approved'),
        ('approve_with_changes', 'Approved with Changes'),
        ('revision_required', 'Revision Required'),
        ('reject', 'Rejected'),
    ]
    
    # What is being reviewed
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_conducted')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_requested')
    
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPES, default='peer')
    status = models.CharField(max_length=20, choices=REVIEW_STATUS, default='requested')
    decision = models.CharField(max_length=30, choices=REVIEW_DECISIONS, null=True, blank=True)
    
    # Review content
    summary = models.TextField(blank=True, help_text="Overall review summary")
    detailed_feedback = models.TextField(blank=True, help_text="Detailed feedback and suggestions")
    
    # Criteria scores (1-5 scale)
    methodology_score = models.IntegerField(null=True, blank=True, help_text="Methodology quality (1-5)")
    clarity_score = models.IntegerField(null=True, blank=True, help_text="Clarity and presentation (1-5)")
    significance_score = models.IntegerField(null=True, blank=True, help_text="Scientific significance (1-5)")
    overall_score = models.IntegerField(null=True, blank=True, help_text="Overall quality (1-5)")
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['reviewer', 'status']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.content_object}"
    
    def clean(self):
        """Validate score ranges"""
        score_fields = ['methodology_score', 'clarity_score', 'significance_score', 'overall_score']
        for field in score_fields:
            score = getattr(self, field)
            if score is not None and (score < 1 or score > 5):
                raise ValidationError(f"{field} must be between 1 and 5")
    
    def is_overdue(self):
        """Check if review is overdue"""
        if self.deadline and self.status in ['requested', 'in_progress']:
            return timezone.now() > self.deadline
        return False
    
    def get_average_score(self):
        """Calculate average score from all criteria"""
        scores = [s for s in [self.methodology_score, self.clarity_score, 
                             self.significance_score] if s is not None]
        if scores:
            return sum(scores) / len(scores)
        return None


class ActivityFeed(models.Model):
    """Model for tracking team and project activities"""
    
    ACTIVITY_TYPES = [
        ('team_created', 'Team Created'),
        ('member_joined', 'Member Joined'),
        ('member_left', 'Member Left'),
        ('project_shared', 'Project Shared'),
        ('project_created', 'Project Created'),
        ('document_created', 'Document Created'),
        ('document_updated', 'Document Updated'),
        ('comment_added', 'Comment Added'),
        ('review_requested', 'Review Requested'),
        ('review_completed', 'Review Completed'),
        ('file_uploaded', 'File Uploaded'),
        ('milestone_reached', 'Milestone Reached'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    
    # Generic foreign key for the object that was acted upon
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)  # Support both UUID and integer IDs
    content_object = GenericForeignKey('content_type', 'object_id')
    
    description = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional activity data")
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['team', 'created_at']),
            models.Index(fields=['actor', 'created_at']),
            models.Index(fields=['activity_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.actor.username}: {self.description}"


class Notification(models.Model):
    """Model for user notifications"""
    
    NOTIFICATION_TYPES = [
        ('team_invitation', 'Team Invitation'),
        ('project_shared', 'Project Shared'),
        ('comment_reply', 'Comment Reply'),
        ('review_request', 'Review Request'),
        ('review_completed', 'Review Completed'),
        ('mention', 'Mentioned'),
        ('deadline_reminder', 'Deadline Reminder'),
        ('system', 'System Notification'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='normal')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Link to related object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)  # Support both UUID and integer IDs
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Action URL
    action_url = models.URLField(blank=True, help_text="URL for notification action")
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', 'created_at']),
        ]
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class CollaborativeEdit(models.Model):
    """Model for tracking collaborative editing sessions"""
    
    EDIT_TYPES = [
        ('document', 'Document Edit'),
        ('code', 'Code Edit'),
        ('manuscript', 'Manuscript Edit'),
        ('data', 'Data Edit'),
    ]
    
    # What is being edited
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collaborative_edits')
    edit_type = models.CharField(max_length=20, choices=EDIT_TYPES, default='document')
    
    # Edit details
    field_name = models.CharField(max_length=100, help_text="Field being edited")
    old_value = models.TextField(blank=True, help_text="Previous value")
    new_value = models.TextField(blank=True, help_text="New value")
    
    # Change metadata
    change_summary = models.CharField(max_length=255, blank=True)
    is_minor = models.BooleanField(default=False, help_text="Minor edit (e.g., typo fix)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"Edit by {self.user.username} on {self.content_object} ({self.field_name})"