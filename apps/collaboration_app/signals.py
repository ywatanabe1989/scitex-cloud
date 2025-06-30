from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from .models import (
    Team, TeamMembership, TeamInvitation, SharedProject, 
    Comment, Review, ActivityFeed, Notification
)
from apps.document_app.models import Document
from apps.project_app.models import Project
from apps.auth_app.models import UserProfile


@receiver(post_save, sender=Team)
def create_team_activity(sender, instance, created, **kwargs):
    """Create activity feed entry when team is created"""
    if created:
        ActivityFeed.objects.create(
            team=instance,
            actor=instance.owner,
            activity_type='team_created',
            description=f"Created team '{instance.name}'",
            content_object=instance,
            metadata={'team_type': instance.team_type}
        )


@receiver(post_save, sender=TeamMembership)
def handle_team_membership_changes(sender, instance, created, **kwargs):
    """Handle team membership changes"""
    if created and instance.is_active:
        # Create activity for member joining
        ActivityFeed.objects.create(
            team=instance.team,
            actor=instance.user,
            activity_type='member_joined',
            description=f"{instance.user.get_full_name() or instance.user.username} joined the team",
            content_object=instance.team,
            metadata={'role': instance.role}
        )
        
        # Create notification for team owner
        if instance.user != instance.team.owner:
            Notification.objects.create(
                recipient=instance.team.owner,
                notification_type='system',
                title=f'New Team Member',
                message=f'{instance.user.get_full_name() or instance.user.username} has joined your team "{instance.team.name}"',
                content_object=instance.team,
                action_url=f'/collaboration/teams/{instance.team.id}/'
            )
    
    elif not created and not instance.is_active:
        # Member left or was removed
        ActivityFeed.objects.create(
            team=instance.team,
            actor=instance.user,
            activity_type='member_left',
            description=f"{instance.user.get_full_name() or instance.user.username} left the team",
            content_object=instance.team,
            metadata={'role': instance.role}
        )


@receiver(post_save, sender=TeamInvitation)
def handle_team_invitation(sender, instance, created, **kwargs):
    """Handle team invitation notifications"""
    if created:
        # Try to find existing user by email
        try:
            user = User.objects.get(email=instance.email)
            Notification.objects.create(
                recipient=user,
                notification_type='team_invitation',
                title=f'Team Invitation',
                message=f'You have been invited to join "{instance.team.name}" by {instance.invited_by.get_full_name() or instance.invited_by.username}',
                content_object=instance,
                action_url=f'/collaboration/invitations/{instance.id}/',
                priority='high'
            )
        except User.DoesNotExist:
            # User doesn't exist yet, invitation will be processed when they sign up
            pass


@receiver(post_save, sender=SharedProject)
def handle_project_sharing(sender, instance, created, **kwargs):
    """Handle project sharing activities and notifications"""
    if created:
        # Create activity entry
        ActivityFeed.objects.create(
            team=instance.team,
            actor=instance.shared_by,
            activity_type='project_shared',
            description=f"Shared project '{instance.project.name}' with the team",
            content_object=instance.project,
            metadata={'sharing_type': instance.sharing_type}
        )
        
        # Notify team members
        for member in instance.team.get_all_members():
            if member != instance.shared_by:
                Notification.objects.create(
                    recipient=member,
                    notification_type='project_shared',
                    title=f'Project Shared',
                    message=f'{instance.shared_by.get_full_name() or instance.shared_by.username} shared project "{instance.project.name}" with your team',
                    content_object=instance.project,
                    action_url=f'/core/projects/{instance.project.id}/'
                )


@receiver(post_save, sender=Comment)
def handle_comment_notifications(sender, instance, created, **kwargs):
    """Handle comment notifications and activities"""
    if created:
        # Create activity entry if comment is on a shared object
        if hasattr(instance.content_object, 'associated_teams'):
            for team in instance.content_object.associated_teams.all():
                ActivityFeed.objects.create(
                    team=team,
                    actor=instance.author,
                    activity_type='comment_added',
                    description=f"Added a comment on {instance.content_object}",
                    content_object=instance.content_object,
                    metadata={'comment_type': instance.comment_type}
                )
        
        # Handle reply notifications
        if instance.parent_comment:
            # Notify parent comment author
            if instance.parent_comment.author != instance.author:
                Notification.objects.create(
                    recipient=instance.parent_comment.author,
                    notification_type='comment_reply',
                    title=f'Comment Reply',
                    message=f'{instance.author.get_full_name() or instance.author.username} replied to your comment',
                    content_object=instance,
                    action_url=f'/collaboration/comments/{instance.id}/'
                )


@receiver(post_save, sender=Review)
def handle_review_notifications(sender, instance, created, **kwargs):
    """Handle review request and completion notifications"""
    if created:
        # Notify reviewer about new review request
        Notification.objects.create(
            recipient=instance.reviewer,
            notification_type='review_request',
            title=f'Review Request',
            message=f'{instance.requested_by.get_full_name() or instance.requested_by.username} has requested your review',
            content_object=instance,
            action_url=f'/collaboration/reviews/{instance.id}/',
            priority='high'
        )
        
        # Create activity entry
        ActivityFeed.objects.create(
            actor=instance.requested_by,
            activity_type='review_requested',
            description=f"Requested review from {instance.reviewer.get_full_name() or instance.reviewer.username}",
            content_object=instance.content_object,
            metadata={'review_type': instance.review_type}
        )
    
    elif instance.status == 'completed' and instance.submitted_at:
        # Review was completed
        Notification.objects.create(
            recipient=instance.requested_by,
            notification_type='review_completed',
            title=f'Review Completed',
            message=f'{instance.reviewer.get_full_name() or instance.reviewer.username} has completed their review',
            content_object=instance,
            action_url=f'/collaboration/reviews/{instance.id}/',
            priority='high'
        )
        
        # Create activity entry
        ActivityFeed.objects.create(
            actor=instance.reviewer,
            activity_type='review_completed',
            description=f"Completed review for {instance.content_object}",
            content_object=instance.content_object,
            metadata={'decision': instance.decision, 'overall_score': instance.overall_score}
        )


@receiver(post_save, sender=Project)
def handle_project_creation_for_teams(sender, instance, created, **kwargs):
    """Handle project creation activities for teams"""
    if created:
        # Check if project is associated with any teams
        for team in instance.associated_teams.all():
            ActivityFeed.objects.create(
                team=team,
                actor=instance.owner,
                activity_type='project_created',
                description=f"Created project '{instance.name}'",
                content_object=instance,
                metadata={'status': instance.status}
            )


@receiver(post_save, sender=Document)
def handle_document_activities(sender, instance, created, **kwargs):
    """Handle document creation and update activities"""
    if instance.project:
        activity_type = 'document_created' if created else 'document_updated'
        description = f"{'Created' if created else 'Updated'} document '{instance.title}'"
        
        # Create activities for associated teams
        for team in instance.project.associated_teams.all():
            ActivityFeed.objects.create(
                team=team,
                actor=instance.owner,
                activity_type=activity_type,
                description=description,
                content_object=instance,
                metadata={'document_type': instance.document_type}
            )