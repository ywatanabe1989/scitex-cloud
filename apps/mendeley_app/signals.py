from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import MendeleyProfile, MendeleyDocument
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_mendeley_profile_if_needed(sender, instance, created, **kwargs):
    """
    Optionally create a Mendeley profile when a user is created.
    This is disabled by default - profiles are created when users connect to Mendeley.
    """
    # Uncomment the following lines if you want to auto-create profiles
    # if created:
    #     MendeleyProfile.objects.get_or_create(
    #         user=instance,
    #         defaults={
    #             'mendeley_id': f'user_{instance.id}',
    #         }
    #     )
    pass


@receiver(post_save, sender=MendeleyDocument)
def log_document_creation(sender, instance, created, **kwargs):
    """Log when a new document is created"""
    if created:
        logger.info(f"New Mendeley document created: {instance.title} for user {instance.profile.user.username}")


@receiver(post_delete, sender=MendeleyDocument)
def log_document_deletion(sender, instance, **kwargs):
    """Log when a document is deleted"""
    logger.info(f"Mendeley document deleted: {instance.title} for user {instance.profile.user.username}")


@receiver(post_save, sender=MendeleyProfile)
def log_profile_sync(sender, instance, created, **kwargs):
    """Log when a profile is synced"""
    if not created and instance.is_synced:
        logger.info(f"Mendeley profile synced for user {instance.user.username}")