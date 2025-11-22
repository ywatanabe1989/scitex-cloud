#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-12 18:49:15 (ywatanabe)"


"""
Django signals for Project app - Gitea integration

Automatically creates Gitea repositories when Django projects are created.
Automatically deletes Gitea repositories when Django projects are deleted.
"""

import logging
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver
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
        import requests.exceptions

        # Initialize Gitea client
        try:
            client = GiteaClient()
        except (
            requests.exceptions.ConnectionError,
            ConnectionRefusedError,
        ) as e:
            logger.warning(
                f"Gitea unavailable during project creation for {instance.slug}: {e}"
            )
            logger.info(
                "Project created without Gitea repository. Repository will be created when Gitea becomes available."
            )
            return

        # Prepare repository data
        repo_name = instance.slug
        description = instance.description or f"SciTeX project: {instance.name}"
        is_private = instance.visibility == "private"

        # Check if repository already exists
        try:
            existing_repo = client.get_repository(
                owner=instance.owner.username, repo=repo_name
            )
            logger.info(
                f"Gitea repository already exists: {instance.owner.username}/{repo_name}"
            )

            # Update project with Gitea info
            instance.gitea_repo_url = existing_repo.get("html_url", "")
            instance.gitea_clone_url = existing_repo.get("clone_url", "")
            instance.save(update_fields=["gitea_repo_url", "gitea_clone_url"])
            return

        except (
            requests.exceptions.ConnectionError,
            ConnectionRefusedError,
        ) as e:
            logger.warning(
                f"Gitea unavailable when checking existing repo for {repo_name}: {e}"
            )
            return
        except GiteaAPIError:
            # Repository doesn't exist, create it
            pass

        # Ensure Gitea user exists before creating repository
        from apps.gitea_app.services.gitea_sync_service import (
            ensure_gitea_user_exists,
        )
        from apps.gitea_app.exceptions import (
            GiteaUserCreationError,
            GiteaConnectionError,
        )

        try:
            ensure_gitea_user_exists(instance.owner)
        except GiteaConnectionError as e:
            logger.warning(f"Gitea unavailable when creating user: {e}")
            logger.info(
                "Project created without Gitea repository. Repository will be created when Gitea becomes available."
            )
            return
        except GiteaUserCreationError as e:
            logger.error(f"Failed to create Gitea user {instance.owner.username}: {e}")
            logger.error(f"Cannot create repository without Gitea user account")
            return

        # Create repository in Gitea under the project owner
        logger.info(
            f"Creating Gitea repository: {instance.owner.username}/{repo_name} (private={is_private})"
        )

        repo = client.create_repository(
            name=repo_name,
            description=description,
            private=is_private,
            auto_init=True,  # Initialize with README
            gitignores="Python",  # Add Python .gitignore
            license="MIT",  # Default license
            readme="Default",
            owner=instance.owner.username,  # Create under specific user
        )

        # Update Django project with Gitea repository information
        instance.gitea_repo_url = repo.get("html_url", "")
        instance.gitea_clone_url = repo.get("clone_url", "")
        instance.gitea_ssh_url = repo.get("ssh_url", "")
        instance.gitea_repo_id = repo.get("id")
        instance.gitea_repo_name = repo.get("name", repo_name)
        instance.git_url = repo.get("clone_url", "")  # HTTPS URL for cloning
        instance.gitea_enabled = True
        instance.save(
            update_fields=[
                "gitea_repo_url",
                "gitea_clone_url",
                "gitea_ssh_url",
                "gitea_repo_id",
                "gitea_repo_name",
                "git_url",
                "gitea_enabled",
            ]
        )

        logger.info(f"✓ Gitea repository created: {instance.gitea_repo_url}")

        # Clone repository to Django data directory
        _clone_gitea_repo_to_data_dir(instance)

    except (requests.exceptions.ConnectionError, ConnectionRefusedError):
        # Gitea unavailable - log warning but don't fail project creation
        logger.warning(f"Gitea unavailable for {instance.slug}: Connection refused")
        logger.info(
            "Project created without Gitea repository. Repository will be created when Gitea becomes available."
        )
    except Exception as e:
        # Log error but don't fail project creation
        logger.error(f"Failed to create Gitea repository for {instance.slug}: {e}")
        logger.exception("Full traceback:")


def _setup_project_venv(project, project_dir):
    """
    Create lightweight Python virtual environment for project-specific dependencies.

    Strategy:
    - Create .venv with --system-site-packages to access shared scitex installation
    - This avoids reinstalling heavy dependencies (PyTorch, etc.) in every project
    - Users can install project-specific packages in .venv/bin/pip
    """
    import subprocess
    from pathlib import Path

    try:
        venv_path = Path(project_dir) / ".venv"

        # Skip if .venv already exists
        if venv_path.exists():
            logger.info(f"Virtual environment already exists for {project.slug}")
            return

        logger.info(f"Creating virtual environment for {project.slug}")

        # Create venv with --system-site-packages to access shared scitex
        result = subprocess.run(
            ["python3", "-m", "venv", "--system-site-packages", str(venv_path)],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            logger.error(f"Failed to create venv: {result.stderr}")
            return

        # Create requirements.txt template
        requirements_file = Path(project_dir) / "requirements.txt"
        if not requirements_file.exists():
            requirements_file.write_text("""# Project-specific dependencies
# scitex is available via --system-site-packages (shared installation)
# Add your project-specific packages here
""")

        logger.info(f"✓ Virtual environment created for {project.slug} (with system packages)")

    except subprocess.TimeoutExpired:
        logger.error(f"Timeout creating venv for {project.slug}")
    except Exception as e:
        logger.error(f"Failed to setup venv for {project.slug}: {e}")


def _initialize_writer_structure(project, project_dir):
    """
    Initialize scitex writer structure using Writer() with parent git strategy.

    Flow:
    1. Project root already has .git (from Gitea clone)
    2. Create scitex/writer/ subdirectory
    3. Writer() with git_strategy='parent' creates full structure
    4. Commit and push to Gitea

    Args:
        project: Project model instance
        project_dir: Path to project root (with .git from Gitea)
    """
    import subprocess

    try:
        # Writer goes in scitex/writer subdirectory
        scitex_dir = project_dir / "scitex"
        writer_dir = scitex_dir / "writer"

        # Let Writer() handle structure validation - don't check manually
        # Writer() will either create new or attach to existing structure
        logger.info(f"Initializing scitex writer structure for {project.slug}")
        logger.info(f"  Project root: {project_dir}")
        logger.info(f"  Writer dir: {writer_dir}")
        logger.info(f"  Has git: {(project_dir / '.git').exists()}")

        # Initialize Writer with parent git strategy
        # This will use the project root's .git repository
        # Don't pass name parameter - let it use directory name 'writer'
        from scitex.writer import Writer
        from django.conf import settings

        # Get branch and tag from settings
        # In development: tag=v2.0.0-beta, branch=None
        # In production: tag=None, branch=main
        template_branch = getattr(settings, "SCITEX_WRITER_TEMPLATE_BRANCH", None)
        template_tag = getattr(settings, "SCITEX_WRITER_TEMPLATE_TAG", None)

        writer = Writer(
            project_dir=writer_dir,
            git_strategy="parent",  # Use project root's git repo
            branch=template_branch,  # Use env-specific branch (or None)
            tag=template_tag,  # Use env-specific tag (or None)
        )

        logger.success(f"✓ Scitex writer structure created for {project.slug}")
        logger.info(f"  - Manuscript: {writer.manuscript.root}")
        logger.info(f"  - Supplementary: {writer.supplementary.root}")
        logger.info(f"  - Git root: {writer.git_root}")

        # Commit the new structure
        subprocess.run(["git", "add", "-A"], cwd=project_dir, capture_output=True)
        result = subprocess.run(
            ["git", "commit", "-m", "Initialize scitex writer structure"],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            logger.info("✓ Committed writer structure")

            # Push to Gitea
            result = subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=project_dir,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logger.success(f"✓ Pushed to Gitea: {project.slug}")
            else:
                logger.warning(f"Could not push to Gitea: {result.stderr}")
        else:
            logger.info("No changes to commit (structure may already exist)")

    except Exception as e:
        logger.error(f"Failed to initialize writer structure for {project.slug}: {e}")
        logger.exception("Full traceback:")


def _clone_gitea_repo_to_data_dir(project):
    """
    Clone Gitea repository to Django's data directory.

    Creates a working tree at: /data/users/{username}/proj/{project_slug}/
    """
    import subprocess
    from pathlib import Path
    from django.conf import settings

    try:
        # Get user data directory - must match ProjectFilesystemManager structure
        user_data_dir = (
            Path(settings.BASE_DIR) / "data" / "users" / project.owner.username / "proj"
        )
        user_data_dir.mkdir(parents=True, exist_ok=True)

        project_dir = user_data_dir / project.slug

        # Skip if directory already exists and is a git repo
        if project_dir.exists() and (project_dir / ".git").exists():
            logger.info(f"Project directory already exists as git repo: {project_dir}")
            return

        # Remove directory if exists but not a git repo
        if project_dir.exists():
            import shutil

            shutil.rmtree(project_dir)

        # Clone from Gitea using HTTP with embedded token for authentication
        # Format: http://{token}@gitea:3000/{owner}/{repo}.git
        clone_url = project.gitea_clone_url

        # Inject Gitea admin token into URL for authentication
        # Clone URL format from Gitea: http://gitea:3000/owner/repo.git
        # Authenticated format needed: http://{token}@gitea:3000/owner/repo.git
        from django.conf import settings

        gitea_token = settings.GITEA_TOKEN

        if gitea_token and clone_url:
            # Parse and inject token: http://gitea:3000/... → http://{token}@gitea:3000/...
            if "://" in clone_url:
                protocol, rest = clone_url.split("://", 1)
                authenticated_clone_url = f"{protocol}://{gitea_token}@{rest}"
            else:
                authenticated_clone_url = clone_url
        else:
            authenticated_clone_url = clone_url

        logger.info(f"Cloning Gitea repo to: {project_dir}")
        logger.info(f"  From: {clone_url}")  # Log original URL (without token)

        result = subprocess.run(
            ["git", "clone", authenticated_clone_url, str(project_dir)],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            logger.info(f"✓ Gitea repo cloned to: {project_dir}")

            # Set git config for this repo
            subprocess.run(
                [
                    "git",
                    "config",
                    "user.name",
                    project.owner.get_full_name() or project.owner.username,
                ],
                cwd=project_dir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.email", project.owner.email],
                cwd=project_dir,
                capture_output=True,
            )

            # Configure git credentials for push (embed token in URL)
            from apps.project_app.services.git_service import (
                configure_git_credentials,
            )

            configure_git_credentials(
                project_dir=project_dir,
                username=project.owner.username,
                token=settings.GITEA_TOKEN,
            )

            # Update project model with clone path
            project.git_clone_path = str(project_dir)
            project.directory_created = True
            project.save(update_fields=["git_clone_path", "directory_created"])

            # Setup Python virtual environment with scitex (DISABLED - use shared scitex)
            # _setup_project_venv(project, project_dir)

            # Initialize scitex writer structure in scitex/writer subdirectory
            _initialize_writer_structure(project, project_dir)

        else:
            logger.error(f"Failed to clone repo: {result.stderr}")

    except subprocess.TimeoutExpired:
        logger.error(f"Git clone timeout for {project.slug}")
    except Exception as e:
        logger.error(f"Failed to clone Gitea repo for {project.slug}: {e}")
        logger.exception("Full traceback:")


@receiver(post_save, sender=Project)
def ensure_bibliography_structure(sender, instance, created, **kwargs):
    """
    Ensure bibliography directory structure exists after project creation.

    This creates the basic directory structure and symlinks for bibliography
    management, but does NOT parse or merge files (that's opt-in).
    """
    # Only run for newly created projects with git clone path
    if not created or not instance.git_clone_path:
        return

    try:
        from pathlib import Path
        from .services.bibliography_manager import (
            ensure_bibliography_structure as ensure_structure,
        )

        project_path = Path(instance.git_clone_path)
        if project_path.exists():
            results = ensure_structure(project_path)
            if results["success"]:
                logger.info(f"✓ Bibliography structure initialized for {instance.slug}")
            else:
                logger.warning(
                    f"Bibliography structure initialization had errors: {results['errors']}"
                )

    except Exception as e:
        # Non-critical error, log and continue
        logger.warning(
            f"Failed to initialize bibliography structure for {instance.slug}: {e}"
        )


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
    if not hasattr(instance, "_old_visibility"):
        return

    if instance._old_visibility == instance.visibility:
        return

    try:
        from apps.gitea_app.api_client import GiteaClient

        client = GiteaClient()
        is_private = instance.visibility == "private"

        # Update Gitea repository visibility
        # Note: Gitea API uses PATCH /repos/{owner}/{repo}
        endpoint = f"/repos/{instance.owner.username}/{instance.slug}"
        client._request("PATCH", endpoint, json={"private": is_private})

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


@receiver(post_delete, sender=Project)
def delete_gitea_repository(sender, instance, **kwargs):
    """
    Automatically delete Gitea repository when a Django Project is deleted.

    Ensures that deleting a project from SciTeX Cloud also removes the
    corresponding repository from Gitea to maintain consistency.

    Args:
        sender: The model class (Project)
        instance: The Project instance being deleted
        **kwargs: Additional keyword arguments
    """
    # Skip if no Gitea repo associated
    if not instance.gitea_repo_url or not instance.gitea_repo_id:
        logger.info(
            f"No Gitea repository associated with project {instance.slug}, skipping deletion"
        )
        return

    try:
        from apps.gitea_app.api_client import GiteaClient, GiteaAPIError
        import requests.exceptions

        logger.info(f"Deleting Gitea repository for project {instance.slug}")

        # Initialize Gitea client
        try:
            client = GiteaClient()
        except (
            requests.exceptions.ConnectionError,
            ConnectionRefusedError,
        ) as e:
            logger.warning(
                f"Gitea unavailable during project deletion for {instance.slug}: {e}"
            )
            logger.warning(
                "Gitea repository was NOT deleted. Please manually delete it or use cleanup command."
            )
            return

        # Delete repository in Gitea
        try:
            client.delete_repository(owner=instance.owner.username, repo=instance.slug)
            logger.info(
                f"✓ Gitea repository deleted: {instance.owner.username}/{instance.slug}"
            )
        except GiteaAPIError as e:
            logger.warning(
                f"Gitea repository may not exist or was already deleted: {instance.owner.username}/{instance.slug}"
            )
            logger.debug(f"Error details: {e}")

    except (requests.exceptions.ConnectionError, ConnectionRefusedError):
        logger.warning(f"Gitea unavailable for {instance.slug}: Connection refused")
        logger.warning(
            "Gitea repository was NOT deleted. Please manually delete it or use cleanup command."
        )
    except Exception as e:
        logger.error(f"Failed to delete Gitea repository for {instance.slug}: {e}")
        logger.exception("Full traceback:")


# EOF
