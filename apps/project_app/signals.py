#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-20 19:30:00 (ywatanabe)"
# File: ./apps/project_app/signals.py

"""
Django signals for Project app - Gitea integration

Automatically creates Gitea repositories when Django projects are created.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Project

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Project)
def create_gitea_repository(sender, instance, created, **kwargs):
    """
    Automatically create Gitea repository when a new Project is created.

    Args:
        sender: The model class (Project)
        instance: The Project instance
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    # Only create repo for new projects
    if not created:
        return

    # Gitea integration is always enabled (core feature)
    try:
        from apps.gitea_app.api_client import GiteaClient, GiteaAPIError

        # Initialize Gitea client
        client = GiteaClient()

        # Prepare repository data
        repo_name = instance.slug
        description = instance.description or f"SciTeX project: {instance.name}"
        is_private = (instance.visibility == 'private')

        # Check if repository already exists
        try:
            existing_repo = client.get_repository(
                owner=instance.owner.username,
                repo=repo_name
            )
            logger.info(f"Gitea repository already exists: {instance.owner.username}/{repo_name}")

            # Update project with Gitea info
            instance.gitea_repo_url = existing_repo.get('html_url', '')
            instance.gitea_clone_url = existing_repo.get('clone_url', '')
            instance.save(update_fields=['gitea_repo_url', 'gitea_clone_url'])
            return

        except GiteaAPIError:
            # Repository doesn't exist, create it
            pass

        # Create repository in Gitea
        logger.info(f"Creating Gitea repository: {repo_name} (private={is_private})")

        repo = client.create_repository(
            name=repo_name,
            description=description,
            private=is_private,
            auto_init=True,  # Initialize with README
            gitignores='Python',  # Add Python .gitignore
            license='MIT',  # Default license
            readme='Default'
        )

        # Update Django project with Gitea repository information
        instance.gitea_repo_url = repo.get('html_url', '')
        instance.gitea_clone_url = repo.get('clone_url', '')
        instance.gitea_ssh_url = repo.get('ssh_url', '')
        instance.gitea_repo_id = repo.get('id')
        instance.gitea_repo_name = repo.get('name', repo_name)
        instance.gitea_enabled = True
        instance.save(update_fields=[
            'gitea_repo_url', 'gitea_clone_url', 'gitea_ssh_url',
            'gitea_repo_id', 'gitea_repo_name', 'gitea_enabled'
        ])

        logger.info(f"✓ Gitea repository created: {instance.gitea_repo_url}")

        # Clone repository to Django data directory
        _clone_gitea_repo_to_data_dir(instance)

    except Exception as e:
        # Log error but don't fail project creation
        logger.error(f"Failed to create Gitea repository for {instance.slug}: {e}")
        logger.exception("Full traceback:")


def _clone_gitea_repo_to_data_dir(project):
    """
    Clone Gitea repository to Django's data directory.

    Creates a working tree at: /data/{username}/{project_slug}/
    """
    import subprocess
    from pathlib import Path
    from django.conf import settings

    try:
        # Get user data directory
        user_data_dir = Path(settings.BASE_DIR) / 'data' / project.owner.username
        user_data_dir.mkdir(parents=True, exist_ok=True)

        project_dir = user_data_dir / project.slug

        # Skip if directory already exists and is a git repo
        if project_dir.exists() and (project_dir / '.git').exists():
            logger.info(f"Project directory already exists as git repo: {project_dir}")
            return

        # Remove directory if exists but not a git repo
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir)

        # Clone from Gitea using HTTP (no auth needed for own repos with token)
        clone_url = project.gitea_clone_url

        logger.info(f"Cloning Gitea repo to: {project_dir}")
        logger.info(f"  From: {clone_url}")

        result = subprocess.run(
            ['git', 'clone', clone_url, str(project_dir)],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            logger.info(f"✓ Gitea repo cloned to: {project_dir}")

            # Set git config for this repo
            subprocess.run(
                ['git', 'config', 'user.name', project.owner.get_full_name() or project.owner.username],
                cwd=project_dir,
                capture_output=True
            )
            subprocess.run(
                ['git', 'config', 'user.email', project.owner.email],
                cwd=project_dir,
                capture_output=True
            )

            # Configure git credentials for push (embed token in URL)
            from apps.workspace_app.git_operations import configure_git_credentials
            configure_git_credentials(
                project_dir=project_dir,
                username=project.owner.username,
                token=settings.GITEA_TOKEN
            )

            # Update project model with clone path
            project.git_clone_path = str(project_dir)
            project.directory_created = True
            project.save(update_fields=['git_clone_path', 'directory_created'])

        else:
            logger.error(f"Failed to clone repo: {result.stderr}")

    except subprocess.TimeoutExpired:
        logger.error(f"Git clone timeout for {project.slug}")
    except Exception as e:
        logger.error(f"Failed to clone Gitea repo for {project.slug}: {e}")
        logger.exception("Full traceback:")


@receiver(post_save, sender=Project)
def sync_project_visibility(sender, instance, created, **kwargs):
    """
    Sync project visibility changes with Gitea repository.

    When a Django project's visibility is changed (public ↔ private),
    update the corresponding Gitea repository.
    """
    # Only sync for existing projects
    if created:
        return

    # Skip if no Gitea repo associated
    if not instance.gitea_repo_url:
        return

    # Check if visibility was changed
    if not hasattr(instance, '_old_visibility'):
        return

    if instance._old_visibility == instance.visibility:
        return

    try:
        from apps.gitea_app.api_client import GiteaClient

        client = GiteaClient()
        is_private = (instance.visibility == 'private')

        # Update Gitea repository visibility
        # Note: Gitea API uses PATCH /repos/{owner}/{repo}
        endpoint = f'/repos/{instance.owner.username}/{instance.slug}'
        client._request('PATCH', endpoint, json={'private': is_private})

        logger.info(f"✓ Synced visibility for {instance.slug}: {instance.visibility}")

    except Exception as e:
        logger.error(f"Failed to sync visibility for {instance.slug}: {e}")


# Hook to track visibility changes
from django.db.models.signals import pre_save

@receiver(pre_save, sender=Project)
def track_visibility_change(sender, instance, **kwargs):
    """Track old visibility value before saving"""
    if instance.pk:
        try:
            old_instance = Project.objects.get(pk=instance.pk)
            instance._old_visibility = old_instance.visibility
        except Project.DoesNotExist:
            pass

# EOF
