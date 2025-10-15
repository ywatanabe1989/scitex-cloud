"""
SciTeX Cloud - Model Signals for Directory Management

This module contains Django signals to automatically manage user directories
and project directory structures when models are created or updated.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Project, UserProfile
# from apps.document_app.models import Document  # Removed - document_app not installed
from .directory_manager import get_user_directory_manager, ensure_project_directory
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_workspace(sender, instance, created, **kwargs):
    """Create user workspace when a new user is created."""
    if created:
        try:
            # Create user profile if it doesn't exist
            profile, profile_created = UserProfile.objects.get_or_create(user=instance)
            
            # Initialize user workspace
            manager = get_user_directory_manager(instance)
            success = manager.initialize_user_workspace()
            
            if success:
                logger.info(f"User workspace created for {instance.username}")
            else:
                logger.error(f"Failed to create user workspace for {instance.username}")
                
        except Exception as e:
            logger.error(f"Error creating user workspace for {instance.username}: {e}")


@receiver(post_save, sender=Project)
def handle_project_directory(sender, instance, created, **kwargs):
    """Handle project directory creation and updates."""
    try:
        if created and not instance.directory_created:
            # Create project directory for new projects (avoid recursion)
            manager = get_user_directory_manager(instance.owner)
            success, path = manager.create_project_directory(instance)
            if success:
                # Update directory_created flag without triggering signal
                Project.objects.filter(id=instance.id).update(directory_created=True)
                logger.info(f"Project directory created for {instance.name}")
            else:
                logger.error(f"Failed to create project directory for {instance.name}")
        elif not created and instance.directory_created:
            # Update project directory if already created
            try:
                instance.update_storage_usage()
            except Exception as storage_error:
                logger.warning(f"Failed to update storage for {instance.name}: {storage_error}")
                
    except Exception as e:
        logger.error(f"Error handling project directory for {instance.name}: {e}")


# @receiver(post_save, sender=Document)
# def handle_document_storage(sender, instance, created, **kwargs):
#     """Handle document file storage in project directories."""
#     try:
#         # Only save to directory if document has a project and content
#         if instance.project and instance.content and not instance.file_location:
#             success = instance.save_to_directory()
#             if success:
#                 logger.info(f"Document saved to directory: {instance.title}")
#             else:
#                 logger.warning(f"Failed to save document to directory: {instance.title}")
#
#     except Exception as e:
#         logger.error(f"Error handling document storage for {instance.title}: {e}")


@receiver(post_delete, sender=Project)
def cleanup_project_directory(sender, instance, **kwargs):
    """Clean up project directory when project is deleted."""
    try:
        if instance.directory_created:
            manager = get_user_directory_manager(instance.owner)
            success = manager.delete_project_directory(instance)
            if success:
                logger.info(f"Project directory deleted for {instance.name}")
            else:
                logger.warning(f"Failed to delete project directory for {instance.name}")
                
    except Exception as e:
        logger.error(f"Error deleting project directory for {instance.name}: {e}")


# @receiver(post_delete, sender=Document)
# def cleanup_document_file(sender, instance, **kwargs):
#     """Clean up document file when document is deleted."""
#     try:
#         if instance.file_location:
#             file_path = instance.get_file_path()
#             if file_path and file_path.exists():
#                 file_path.unlink()
#                 logger.info(f"Document file deleted: {instance.title}")
#
#                 # Update project storage usage if applicable
#                 if instance.project:
#                     instance.project.update_storage_usage()
#
#     except Exception as e:
#         logger.error(f"Error deleting document file for {instance.title}: {e}")


# @receiver(pre_save, sender=Document)
# def update_document_metadata(sender, instance, **kwargs):
#     """Update document metadata before saving."""
#     try:
#         # Calculate file size if content changed
#         if instance.content:
#             instance.file_size = len(instance.content.encode('utf-8'))
#
#         # Generate file hash for integrity checking
#         if instance.content:
#             import hashlib
#             instance.file_hash = hashlib.sha256(instance.content.encode('utf-8')).hexdigest()
#
#     except Exception as e:
#         logger.error(f"Error updating document metadata for {instance.title}: {e}")


@receiver(post_save, sender=UserProfile)
def handle_profile_updates(sender, instance, created, **kwargs):
    """Handle user profile updates that might affect directory structure."""
    try:
        if not created:
            # Update academic status
            instance.update_academic_status()
            
            # If user workspace doesn't exist, create it
            manager = get_user_directory_manager(instance.user)
            if not manager.base_path.exists():
                manager.initialize_user_workspace()
                logger.info(f"User workspace initialized for existing user {instance.user.username}")
                
    except Exception as e:
        logger.error(f"Error handling profile updates for {instance.user.username}: {e}")


# Custom signal for bulk operations
from django.dispatch import Signal

# Define custom signals
project_directory_created = Signal()
document_saved_to_directory = Signal()
storage_usage_updated = Signal()


@receiver(project_directory_created)
def log_project_directory_creation(sender, project, directory_path, **kwargs):
    """Log when a project directory is successfully created."""
    logger.info(f"Project directory created: {project.name} at {directory_path}")


@receiver(document_saved_to_directory)
def log_document_storage(sender, document, file_path, **kwargs):
    """Log when a document is saved to the directory structure."""
    logger.info(f"Document stored: {document.title} at {file_path}")


@receiver(storage_usage_updated)
def log_storage_update(sender, project, old_size, new_size, **kwargs):
    """Log when project storage usage is updated."""
    if old_size != new_size:
        change = new_size - old_size
        logger.info(f"Storage updated for {project.name}: {change:+d} bytes (total: {new_size} bytes)")


# Periodic cleanup functions (to be called by management commands)
def cleanup_orphaned_files():
    """Clean up files that don't have corresponding database records."""
    from pathlib import Path
    from django.conf import settings
    
    users_dir = Path(settings.MEDIA_ROOT) / 'users'
    if not users_dir.exists():
        return
    
    cleaned_count = 0
    
    for user_dir in users_dir.iterdir():
        if not user_dir.is_dir():
            continue
            
        try:
            user_id = int(user_dir.name)
            user = User.objects.get(id=user_id)
            
            # Check projects directory
            projects_dir = user_dir / 'projects'
            if projects_dir.exists():
                for project_dir in projects_dir.iterdir():
                    if project_dir.is_dir():
                        # Check if project exists in database
                        project_slug = project_dir.name
                        project_exists = Project.objects.filter(
                            owner=user,
                            data_location__contains=project_slug
                        ).exists()
                        
                        if not project_exists:
                            import shutil
                            shutil.rmtree(project_dir)
                            cleaned_count += 1
                            logger.info(f"Cleaned orphaned project directory: {project_dir}")
                            
        except (ValueError, User.DoesNotExist):
            # Invalid user directory or user doesn't exist
            continue
        except Exception as e:
            logger.error(f"Error cleaning up directory {user_dir}: {e}")
    
    return cleaned_count


def update_all_storage_usage():
    """Update storage usage for all projects."""
    updated_count = 0
    
    for project in Project.objects.filter(directory_created=True):
        try:
            old_size = project.storage_used
            new_size = project.update_storage_usage()
            
            # Send signal for logging
            storage_usage_updated.send(
                sender=Project,
                project=project,
                old_size=old_size,
                new_size=new_size
            )
            
            updated_count += 1
            
        except Exception as e:
            logger.error(f"Error updating storage for project {project.name}: {e}")
    
    return updated_count