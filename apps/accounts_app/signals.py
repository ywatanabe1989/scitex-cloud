from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created (if not already exists)"""
    if created:
        UserProfile.objects.get_or_create(user=instance)
        # Create a default project for the new user
        create_default_project_for_user(instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


def create_default_project_for_user(user):
    """Create a default project for newly created users"""
    from apps.project_app.models import Project

    try:
        # Check if user already has projects
        if Project.objects.filter(owner=user).exists():
            return

        # Create a default project
        default_project_name = f"{user.username}'s Project"
        default_project = Project.objects.create(
            name=default_project_name,
            slug=Project.generate_unique_slug(default_project_name),
            description=f"Default project for {user.username}",
            owner=user,
            visibility='private'
        )

        # Set as last active repository
        user.profile.last_active_repository = default_project
        user.profile.save()

    except Exception as e:
        # Log error but don't break user creation
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating default project for user {user.username}: {str(e)}")
