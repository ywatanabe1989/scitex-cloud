"""
Demo Project Pool Manager

Manages temporary demo projects for anonymous users across all SciTeX apps.
This is a shared infrastructure service used by Writer, Scholar, Code, etc.

Each visitor gets their own isolated workspace that behaves identically to authenticated users.
"""

import logging
import secrets
from datetime import timedelta
from typing import Optional, Tuple
from django.utils import timezone
from django.contrib.auth.models import User
from apps.project_app.models import Project
from pathlib import Path

logger = logging.getLogger(__name__)


class DemoProjectPool:
    """
    Manages a pool of demo projects for anonymous visitors across all SciTeX apps.

    Features:
    - Session-based allocation (each visitor gets isolated workspace)
    - Automatic cleanup of expired projects
    - Same code paths as authenticated users
    - Reusable across Writer, Scholar, Code, and other apps

    Architecture:
    - Each session gets one demo user + one demo project
    - Apps (writer, scholar, etc.) use the same project infrastructure
    - Cleanup happens automatically via management command
    """

    DEMO_USER_PREFIX = "demo-visitor-"
    DEMO_PROJECT_PREFIX = "demo-project-"
    DEMO_PROJECT_LIFETIME_HOURS = 24  # Projects expire after 24 hours
    SESSION_KEY_PROJECT_ID = 'demo_project_id'
    SESSION_KEY_DEMO_USER_ID = 'demo_user_id'

    @classmethod
    def get_or_create_demo_user(cls, session) -> User:
        """
        Get or create a demo user for the session.

        Args:
            session: Django session object

        Returns:
            User: Demo user instance
        """
        # Check if session already has a demo user
        demo_user_id = session.get(cls.SESSION_KEY_DEMO_USER_ID)

        if demo_user_id:
            try:
                user = User.objects.get(id=demo_user_id, username__startswith=cls.DEMO_USER_PREFIX)
                logger.info(f"[DemoPool] Reusing demo user: {user.username}")
                return user
            except User.DoesNotExist:
                logger.warning(f"[DemoPool] Demo user {demo_user_id} not found, creating new one")

        # Create new demo user
        username = f"{cls.DEMO_USER_PREFIX}{secrets.token_hex(8)}"
        user = User.objects.create(
            username=username,
            email=f"{username}@demo.scitex.local",
            is_active=True,
        )
        user.set_unusable_password()  # No password login
        user.save()

        # Store in session
        session[cls.SESSION_KEY_DEMO_USER_ID] = user.id
        session.save()

        logger.info(f"[DemoPool] Created demo user: {username} (id={user.id})")
        return user

    @classmethod
    def get_or_create_demo_project(cls, session) -> Tuple[Project, bool]:
        """
        Get or create a demo project for the current session.

        This is the main entry point for apps needing demo project infrastructure.

        Args:
            session: Django session object

        Returns:
            tuple: (Project, created: bool)
                - Project: Demo project instance
                - created: True if newly created, False if reused
        """
        # Check if session already has a demo project
        demo_project_id = session.get(cls.SESSION_KEY_PROJECT_ID)

        if demo_project_id:
            try:
                project = Project.objects.get(
                    id=demo_project_id,
                    slug__startswith=cls.DEMO_PROJECT_PREFIX
                )
                logger.info(f"[DemoPool] Reusing demo project: {project.slug} (id={project.id})")
                return project, False
            except Project.DoesNotExist:
                logger.warning(f"[DemoPool] Demo project {demo_project_id} not found, creating new one")

        # Create new demo project
        demo_user = cls.get_or_create_demo_user(session)
        project_slug = f"{cls.DEMO_PROJECT_PREFIX}{secrets.token_hex(6)}"

        project = Project.objects.create(
            name="Demo Project",
            slug=project_slug,
            description="Temporary demo workspace - try out SciTeX!",
            owner=demo_user,
            visibility='private',
        )

        # Initialize project directory structure
        from apps.project_app.services.project_filesystem import get_project_filesystem_manager
        manager = get_project_filesystem_manager(demo_user)
        success, project_path = manager.create_empty_project_directory(project)

        if not success:
            logger.error(f"[DemoPool] Failed to create directory for demo project {project.id}")
            project.delete()
            raise RuntimeError("Failed to create demo project directory")

        # Store in session
        session[cls.SESSION_KEY_PROJECT_ID] = project.id
        session.save()

        logger.info(f"[DemoPool] Created demo project: {project_slug} (id={project.id}, user={demo_user.username}, path={project_path})")

        return project, True

    @classmethod
    def get_demo_project_id(cls, session) -> Optional[int]:
        """
        Get demo project ID from session without creating one.

        Args:
            session: Django session object

        Returns:
            Optional[int]: Project ID if exists, None otherwise
        """
        return session.get(cls.SESSION_KEY_PROJECT_ID)

    @classmethod
    def get_demo_user_id(cls, session) -> Optional[int]:
        """
        Get demo user ID from session without creating one.

        Args:
            session: Django session object

        Returns:
            Optional[int]: User ID if exists, None otherwise
        """
        return session.get(cls.SESSION_KEY_DEMO_USER_ID)

    @classmethod
    def is_demo_project(cls, project: Project) -> bool:
        """
        Check if a project is a demo project.

        Args:
            project: Project instance

        Returns:
            bool: True if demo project
        """
        return project.slug.startswith(cls.DEMO_PROJECT_PREFIX)

    @classmethod
    def is_demo_user(cls, user: User) -> bool:
        """
        Check if a user is a demo user.

        Args:
            user: User instance

        Returns:
            bool: True if demo user
        """
        return user.username.startswith(cls.DEMO_USER_PREFIX)

    @classmethod
    def cleanup_expired_projects(cls, older_than_hours: Optional[int] = None, dry_run: bool = False) -> int:
        """
        Clean up expired demo projects.

        Args:
            older_than_hours: Projects older than this many hours (default: DEMO_PROJECT_LIFETIME_HOURS)
            dry_run: If True, only report what would be deleted without actually deleting

        Returns:
            int: Number of projects cleaned up
        """
        if older_than_hours is None:
            older_than_hours = cls.DEMO_PROJECT_LIFETIME_HOURS

        expiry_date = timezone.now() - timedelta(hours=older_than_hours)

        # Find expired demo projects
        expired_projects = Project.objects.filter(
            slug__startswith=cls.DEMO_PROJECT_PREFIX,
            created_at__lt=expiry_date
        )

        count = expired_projects.count()

        if dry_run:
            logger.info(f"[DemoPool] DRY RUN: Would clean up {count} expired projects")
            for project in expired_projects:
                logger.info(f"[DemoPool] DRY RUN: Would delete: {project.slug} (created: {project.created_at})")
            return count

        deleted = 0
        for project in expired_projects:
            try:
                # Delete project directories
                from apps.project_app.services.project_filesystem import get_project_filesystem_manager
                manager = get_project_filesystem_manager(project.owner)
                project_root = manager.get_project_root_path(project)

                if project_root and project_root.exists():
                    import shutil
                    shutil.rmtree(project_root)
                    logger.info(f"[DemoPool] Deleted directory: {project_root}")

                # Delete demo user if they have no other projects
                demo_user = project.owner
                if demo_user.username.startswith(cls.DEMO_USER_PREFIX):
                    other_projects = Project.objects.filter(owner=demo_user).exclude(id=project.id)
                    if not other_projects.exists():
                        demo_user.delete()
                        logger.info(f"[DemoPool] Deleted demo user: {demo_user.username}")

                # Delete project (cascades to manuscripts, etc.)
                project_slug = project.slug
                project.delete()
                deleted += 1
                logger.info(f"[DemoPool] Cleaned up expired project: {project_slug}")

            except Exception as e:
                logger.error(f"[DemoPool] Error cleaning up project {project.id}: {e}")

        logger.info(f"[DemoPool] Cleanup complete: {deleted}/{count} projects removed")
        return deleted

    @classmethod
    def cleanup_orphaned_users(cls, dry_run: bool = False) -> int:
        """
        Clean up demo users that have no associated projects.

        Args:
            dry_run: If True, only report what would be deleted

        Returns:
            int: Number of users cleaned up
        """
        # Find demo users with no projects
        demo_users = User.objects.filter(username__startswith=cls.DEMO_USER_PREFIX)
        orphaned = []

        for user in demo_users:
            if not Project.objects.filter(owner=user).exists():
                orphaned.append(user)

        count = len(orphaned)

        if dry_run:
            logger.info(f"[DemoPool] DRY RUN: Would clean up {count} orphaned demo users")
            for user in orphaned:
                logger.info(f"[DemoPool] DRY RUN: Would delete user: {user.username}")
            return count

        deleted = 0
        for user in orphaned:
            try:
                username = user.username
                user.delete()
                deleted += 1
                logger.info(f"[DemoPool] Deleted orphaned demo user: {username}")
            except Exception as e:
                logger.error(f"[DemoPool] Error deleting user {user.id}: {e}")

        logger.info(f"[DemoPool] Cleanup complete: {deleted}/{count} orphaned users removed")
        return deleted
