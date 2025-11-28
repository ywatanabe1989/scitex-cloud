"""
Visitor Pool Manager

Pre-allocated visitor accounts for visitor users.
Each visitor gets a default project that can be claimed on signup.

Architecture:
- Configurable pool size via SCITEX_VISITOR_POOL_SIZE env var (default: 4)
- Allocation: Session-based with security token (1h lifetime)
- Signup: Transfer project ownership (visitor → real user)
- Reset: Clear workspace, free slot back to pool
"""

import os

import logging
import secrets
from datetime import timedelta
from typing import Optional, Tuple
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from apps.project_app.models import Project, VisitorAllocation

logger = logging.getLogger(__name__)


class VisitorPool:
    """
    Manages fixed pool of visitor accounts and default projects.

    Pool Size: 4 concurrent visitors (rotated with 1h session lifetime)
    Naming: visitor-001 to visitor-004

    With 1-hour sessions, 4 slots support up to 96 visitors per day.
    When visitors sign up, their data is automatically migrated to their new account.
    Slots are automatically freed and reused when sessions expire.
    """

    VISITOR_USER_PREFIX = "visitor-"
    DEFAULT_PROJECT_PREFIX = "default-project-"
    POOL_SIZE = int(os.environ.get("SCITEX_VISITOR_POOL_SIZE", 4))  # Configurable via env
    SESSION_LIFETIME_HOURS = 1  # 1-hour sessions with data migration on signup
    SESSION_KEY_PROJECT_ID = "visitor_project_id"
    SESSION_KEY_VISITOR_ID = "visitor_user_id"
    SESSION_KEY_ALLOCATION_TOKEN = "visitor_allocation_token"

    @classmethod
    def initialize_pool(cls, pool_size: int = None) -> int:
        """
        Create visitor pool (visitor-001 to visitor-004 by default).

        Run once during deployment: python manage.py create_visitor_pool

        Returns:
            int: Number of visitor accounts created
        """
        if pool_size is None:
            pool_size = cls.POOL_SIZE

        # Fast-path: Check if pool is already fully initialized
        # This avoids expensive writer workspace checks on every restart
        all_ready = True
        for i in range(1, pool_size + 1):
            visitor_num = f"{i:03d}"
            username = f"{cls.VISITOR_USER_PREFIX}{visitor_num}"
            project_slug = "default-project"

            try:
                user = User.objects.get(username=username)
                project = Project.objects.get(slug=project_slug, owner=user)

                # Check directory exists
                from apps.project_app.services.project_filesystem import (
                    get_project_filesystem_manager,
                )
                manager = get_project_filesystem_manager(user)
                project_root = manager.get_project_root_path(project)

                if not (project_root and project_root.exists()):
                    all_ready = False
                    break
            except (User.DoesNotExist, Project.DoesNotExist):
                all_ready = False
                break

        if all_ready:
            logger.info(
                f"[VisitorPool] Pool already initialized: {pool_size}/{pool_size} visitor accounts ready"
            )
            # Still ensure Gitea users exist (idempotent)
            cls._ensure_gitea_users_exist(pool_size)
            return 0

        created_count = 0

        for i in range(1, pool_size + 1):
            visitor_num = f"{i:03d}"
            username = f"{cls.VISITOR_USER_PREFIX}{visitor_num}"
            # Project slug is just "default-project" (same as logged-in users)
            # Uniqueness is provided by the username (visitor-001, visitor-002, etc.)
            project_slug = "default-project"

            # Create visitor user if doesn't exist
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@visitor.scitex.local",
                    "is_active": True,
                },
            )
            if user_created:
                user.set_unusable_password()
                user.save()
                logger.info(f"[VisitorPool] Created user: {username}")

            # Ensure visitor user exists in Gitea for Git SSH access
            try:
                from apps.gitea_app.api_client import GiteaClient
                client = GiteaClient()

                # Check if user exists in Gitea
                try:
                    client._request("GET", f"/users/{username}")
                    logger.debug(f"[VisitorPool] Gitea user already exists: {username}")
                except:
                    # User doesn't exist, create it
                    visitor_password = secrets.token_urlsafe(32)  # Random password, never to be used
                    user_data = {
                        "username": username,
                        "email": f"{username}@visitor.scitex.local",
                        "password": visitor_password,
                        "full_name": f"Visitor {visitor_num}",
                        "send_notify": False,
                        "must_change_password": False,
                    }
                    client._request("POST", "/admin/users", json=user_data)
                    logger.info(f"[VisitorPool] Created Gitea user: {username}")
            except Exception as e:
                logger.warning(f"[VisitorPool] Failed to ensure Gitea user {username}: {e}")

            # Create default project if doesn't exist
            # Name and slug match logged-in user convention: "default-project"
            project, project_created = Project.objects.get_or_create(
                slug=project_slug,
                owner=user,
                defaults={
                    "name": "default-project",
                    "description": "Try SciTeX features - sign up to save permanently!",
                    "visibility": "private",
                    "data_location": f"{username}/{project_slug}",
                },
            )

            # Initialize project directory
            # Always ensure directory exists, not just for new projects
            from apps.project_app.services.project_filesystem import (
                get_project_filesystem_manager,
            )

            manager = get_project_filesystem_manager(user)
            project_root = manager.get_project_root_path(project)

            # Create directory if project is new OR directory doesn't exist
            if project_created or not (project_root and project_root.exists()):
                import shutil
                import subprocess
                from django.conf import settings

                project_path = manager.base_path / project_slug

                # Ensure directory doesn't exist before copying
                if project_path.exists():
                    shutil.rmtree(project_path)
                    logger.info(f"[VisitorPool] Removed existing directory before template copy")

                # Copy master template (fast, offline, reliable)
                from pathlib import Path
                template_master = Path(getattr(
                    settings,
                    "VISITOR_TEMPLATE_PATH",
                    "/app/templates/research-master"
                ))

                try:
                    if not template_master.exists():
                        logger.warning(f"[VisitorPool] Master template not found at {template_master}, using basic directory")
                        success, project_path = manager.create_project_directory(project)
                    else:
                        logger.info(f"[VisitorPool] Copying template from {template_master}")

                        # Use shutil.copytree for reliable copying
                        shutil.copytree(template_master, project_path, symlinks=True)

                        success = True
                        logger.info(f"[VisitorPool] Template copied successfully")

                except Exception as e:
                    logger.error(f"[VisitorPool] Template copy error: {e}, using basic directory")
                    success, project_path = manager.create_project_directory(project)

                if success:
                    # Set git_clone_path for file operations (critical for Code workspace)
                    project.git_clone_path = str(project_path)
                    project.directory_created = True
                    project.save(update_fields=["git_clone_path", "directory_created"])

                    logger.info(
                        f"[VisitorPool] Created project: {project_slug} at {project_path}"
                    )

                    # Initialize writer workspace for visitor projects
                    from pathlib import Path

                    _initialize_visitor_writer_workspace(project, Path(project_path))

                    created_count += 1
                else:
                    logger.error(
                        f"[VisitorPool] Failed to create directory for {project_slug}"
                    )
                    if project_created:
                        project.delete()
            else:
                logger.info(
                    f"[VisitorPool] Project directory already exists: {project_root}"
                )

                # Set git_clone_path if not already set (critical for Code workspace)
                if not project.git_clone_path:
                    project.git_clone_path = str(project_root)
                    project.save(update_fields=["git_clone_path"])
                    logger.info(f"[VisitorPool] Set git_clone_path for existing project: {project_root}")

                # Initialize writer workspace - let Writer() handle structure validation
                from pathlib import Path

                logger.info(
                    f"[VisitorPool] Ensuring writer workspace for {project_slug}..."
                )
                _initialize_visitor_writer_workspace(project, project_root)

        # Get actual pool status
        existing_users = 0
        for i in range(1, pool_size + 1):
            visitor_num = f"{i:03d}"
            username = f"{cls.VISITOR_USER_PREFIX}{visitor_num}"
            if User.objects.filter(username=username).exists():
                existing_users += 1

        if created_count > 0:
            logger.info(
                f"[VisitorPool] Pool initialization complete: {created_count} new projects created"
            )
        else:
            logger.info(
                f"[VisitorPool] Pool already initialized: {existing_users}/{pool_size} visitor accounts ready"
            )

        return created_count

    @classmethod
    @transaction.atomic
    def allocate_visitor(cls, session) -> Tuple[Optional[Project], Optional[User]]:
        """
        Allocate a free visitor slot to the session.

        Uses database locking to prevent race conditions.
        Falls back to DemoProjectPool if VisitorAllocation table not created yet.

        Returns:
            tuple: (Project, User) or (None, None) if pool exhausted
        """
        # Check if VisitorAllocation table exists (migration may not have run yet)
        try:
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'project_app_visitorallocation'"
                )
                table_exists = cursor.fetchone()[0] > 0
        except Exception:
            table_exists = False

        if not table_exists:
            # Fallback to old DemoProjectPool until migration runs
            logger.warning(
                "[VisitorPool] VisitorAllocation table not found, using DemoProjectPool fallback"
            )
            from apps.project_app.services.demo_project_pool import DemoProjectPool

            project, created = DemoProjectPool.get_or_create_demo_project(session)
            return project, project.owner if project else None

        # Check if session already has allocation
        existing_token = session.get(cls.SESSION_KEY_ALLOCATION_TOKEN)
        if existing_token:
            try:
                allocation = VisitorAllocation.objects.get(
                    allocation_token=existing_token,
                    is_active=True,
                    expires_at__gt=timezone.now(),
                )
                visitor_num = allocation.visitor_number
                user = User.objects.get(
                    username=f"{cls.VISITOR_USER_PREFIX}{visitor_num:03d}"
                )
                # Project slug is just "default-project" (not numbered)
                project = Project.objects.get(slug="default-project", owner=user)
                logger.info(
                    f"[VisitorPool] Reusing allocation: visitor-{visitor_num:03d}"
                )
                # Note: Caller should handle login() if needed, as we don't have access to request here
                return project, user
            except (
                VisitorAllocation.DoesNotExist,
                User.DoesNotExist,
                Project.DoesNotExist,
            ):
                logger.warning(
                    f"[VisitorPool] Invalid allocation token, clearing session and reallocating"
                )
                # Clear stale session data before reallocating
                session.pop(cls.SESSION_KEY_PROJECT_ID, None)
                session.pop(cls.SESSION_KEY_VISITOR_ID, None)
                session.pop(cls.SESSION_KEY_ALLOCATION_TOKEN, None)
                session.save()

        # Find free visitor slot
        for i in range(1, cls.POOL_SIZE + 1):
            visitor_num = i

            # Check if slot is free or expired
            allocation = VisitorAllocation.objects.filter(
                visitor_number=visitor_num
            ).first()

            # Slot is free if: no allocation, expired, or inactive
            if (
                allocation is None
                or not allocation.is_active
                or allocation.expires_at < timezone.now()
            ):
                # Allocate this slot
                allocation_token = secrets.token_hex(32)
                expires_at = timezone.now() + timedelta(
                    hours=cls.SESSION_LIFETIME_HOURS
                )

                # Delete old allocation if exists
                if allocation:
                    allocation.delete()

                # Create new allocation
                VisitorAllocation.objects.create(
                    visitor_number=visitor_num,
                    session_key=session.session_key or "",
                    allocation_token=allocation_token,
                    expires_at=expires_at,
                    is_active=True,
                )

                # Get visitor user and project
                username = f"{cls.VISITOR_USER_PREFIX}{visitor_num:03d}"
                # Project slug is always "default-project" (not numbered)
                project_slug = "default-project"

                try:
                    user = User.objects.get(username=username)
                    project = Project.objects.get(slug=project_slug, owner=user)

                    # Store in session
                    session[cls.SESSION_KEY_PROJECT_ID] = project.id
                    session[cls.SESSION_KEY_VISITOR_ID] = user.id
                    session[cls.SESSION_KEY_ALLOCATION_TOKEN] = allocation_token
                    session.save()

                    logger.info(
                        f"[VisitorPool] Allocated visitor-{visitor_num:03d} to session"
                    )
                    return project, user

                except (User.DoesNotExist, Project.DoesNotExist):
                    logger.error(
                        f"[VisitorPool] Visitor slot {visitor_num} exists in allocations but user/project not found"
                    )
                    continue

        # Pool exhausted
        logger.warning(
            f"[VisitorPool] Pool exhausted - all {cls.POOL_SIZE} slots in use"
        )
        return None, None

    @classmethod
    def deallocate_visitor(cls, session):
        """
        Free visitor slot (called when session expires or user signs up).

        Args:
            session: Django session object
        """
        allocation_token = session.get(cls.SESSION_KEY_ALLOCATION_TOKEN)
        if not allocation_token:
            return

        try:
            allocation = VisitorAllocation.objects.get(
                allocation_token=allocation_token
            )
            allocation.is_active = False
            allocation.save()

            # Clear session
            session.pop(cls.SESSION_KEY_PROJECT_ID, None)
            session.pop(cls.SESSION_KEY_VISITOR_ID, None)
            session.pop(cls.SESSION_KEY_ALLOCATION_TOKEN, None)
            session.save()

            logger.info(
                f"[VisitorPool] Deallocated visitor-{allocation.visitor_number:03d}"
            )

        except VisitorAllocation.DoesNotExist:
            logger.warning(
                f"[VisitorPool] Allocation not found for token: {allocation_token[:8]}..."
            )

    @classmethod
    @transaction.atomic
    def claim_project_on_signup(cls, session, new_user: User) -> Optional[Project]:
        """
        Transfer visitor's default project to newly signed-up user.

        Called during signup to preserve visitor's work.

        Args:
            session: Django session with visitor allocation
            new_user: Newly created user account

        Returns:
            Optional[Project]: Transferred project or None
        """
        visitor_project_id = session.get(cls.SESSION_KEY_PROJECT_ID)
        allocation_token = session.get(cls.SESSION_KEY_ALLOCATION_TOKEN)

        if not visitor_project_id or not allocation_token:
            logger.warning(
                f"[VisitorPool] No visitor project to claim for user {new_user.username}"
            )
            return None

        try:
            # Get visitor project
            project = Project.objects.get(id=visitor_project_id)
            old_owner = project.owner

            # Verify it's a default project (slug is "default-project")
            if project.slug != "default-project":
                logger.error(
                    f"[VisitorPool] Project {project.id} is not a default project (slug: {project.slug})"
                )
                return None

            # Transfer ownership - keep the same name/slug, just change owner
            project.owner = new_user
            # Keep name as "default-project" for consistency
            # Slug stays "default-project" but now scoped under new user
            project.save()

            # Update filesystem ownership
            from apps.project_app.services.project_filesystem import (
                get_project_filesystem_manager,
            )

            old_manager = get_project_filesystem_manager(old_owner)
            new_manager = get_project_filesystem_manager(new_user)

            old_path = old_manager.get_project_root_path(project)
            if old_path and old_path.exists():
                # Move directory from visitor space to user space
                new_path = new_manager.base_path / new_user.username / project.slug
                new_path.parent.mkdir(parents=True, exist_ok=True)

                import shutil

                shutil.move(str(old_path), str(new_path))

                # Update data_location
                project.data_location = str(new_path.relative_to(new_manager.base_path))
                project.save()

                logger.info(
                    f"[VisitorPool] Moved project from {old_path} to {new_path}"
                )

            # Deallocate visitor slot
            cls.deallocate_visitor(session)

            # Reset visitor workspace for next user
            cls._reset_visitor_workspace(old_owner)

            logger.info(
                f"[VisitorPool] Claimed project {project.slug} for user {new_user.username}"
            )
            return project

        except Project.DoesNotExist:
            logger.error(f"[VisitorPool] Project {visitor_project_id} not found")
            return None
        except Exception as e:
            logger.error(f"[VisitorPool] Error claiming project: {e}", exc_info=True)
            return None

    @classmethod
    def _reset_visitor_workspace(cls, visitor_user: User):
        """
        Reset visitor's workspace (clear content, keep structure).

        Called after visitor signs up and claims project.
        """
        try:
            # Recreate default project for this visitor
            project_slug = "default-project"

            # Delete old project if exists
            Project.objects.filter(slug=project_slug, owner=visitor_user).delete()

            # Create fresh default project (consistent naming with logged-in users)
            project = Project.objects.create(
                name="default-project",
                slug=project_slug,
                description="Try SciTeX features - sign up to save permanently!",
                owner=visitor_user,
                visibility="private",
                data_location=f"{visitor_user.username}/{project_slug}",
            )

            # Initialize directory
            from apps.project_app.services.project_filesystem import (
                get_project_filesystem_manager,
            )

            manager = get_project_filesystem_manager(visitor_user)
            project_path = manager.base_path / project_slug

            # Ensure directory doesn't exist before copying template
            import shutil
            from django.conf import settings
            from pathlib import Path

            if project_path.exists():
                shutil.rmtree(project_path)
                logger.info(f"[VisitorPool] Removed existing directory before template copy")

            # Copy master template
            template_master = Path(getattr(
                settings,
                "VISITOR_TEMPLATE_PATH",
                "/app/templates/research-master"
            ))

            try:
                if not template_master.exists():
                    logger.warning(f"[VisitorPool] Master template not found at {template_master}, using basic directory")
                    success, project_path = manager.create_project_directory(project)
                else:
                    logger.info(f"[VisitorPool] Resetting workspace from {template_master}")

                    # Use shutil.copytree for reliable copying
                    shutil.copytree(template_master, project_path, symlinks=True)

                    success = True
                    logger.info(f"[VisitorPool] Template copied successfully for reset")

            except Exception as e:
                logger.error(f"[VisitorPool] Template copy error during reset: {e}")
                success, project_path = manager.create_project_directory(project)

            if success:
                # Set git_clone_path for file operations (critical for Code workspace)
                project.git_clone_path = str(project_path)
                project.directory_created = True
                project.save(update_fields=["git_clone_path", "directory_created"])

                logger.info(f"[VisitorPool] Reset visitor workspace: {project_slug}")

                # Initialize writer workspace for the fresh visitor project
                from pathlib import Path

                _initialize_visitor_writer_workspace(project, Path(project_path))
            else:
                logger.error(
                    f"[VisitorPool] Failed to reset visitor workspace: {project_slug}"
                )

        except Exception as e:
            logger.error(
                f"[VisitorPool] Error resetting visitor workspace: {e}", exc_info=True
            )

    @classmethod
    def cleanup_expired_allocations(cls) -> int:
        """
        Free visitor slots with expired sessions.

        Returns:
            int: Number of slots freed
        """
        expired = VisitorAllocation.objects.filter(
            is_active=True, expires_at__lt=timezone.now()
        )

        count = 0
        for allocation in expired:
            allocation.is_active = False
            allocation.save()
            count += 1
            logger.info(
                f"[VisitorPool] Freed expired slot: visitor-{allocation.visitor_number:03d}"
            )

        return count

    @classmethod
    def _ensure_gitea_users_exist(cls, pool_size: int = None):
        """
        Ensure all visitor users exist in Gitea for Git SSH access.

        This is idempotent - safe to call multiple times.
        """
        if pool_size is None:
            pool_size = cls.POOL_SIZE

        try:
            from apps.gitea_app.api_client import GiteaClient
            client = GiteaClient()

            for i in range(1, pool_size + 1):
                visitor_num = f"{i:03d}"
                username = f"{cls.VISITOR_USER_PREFIX}{visitor_num}"

                try:
                    # Check if user exists in Gitea
                    client._request("GET", f"/users/{username}")
                    logger.debug(f"[VisitorPool] Gitea user already exists: {username}")
                except:
                    # User doesn't exist, create it
                    visitor_password = secrets.token_urlsafe(32)  # Random password, never to be used
                    user_data = {
                        "username": username,
                        "email": f"{username}@visitor.scitex.local",
                        "password": visitor_password,
                        "full_name": f"Visitor {visitor_num}",
                        "send_notify": False,
                        "must_change_password": False,
                    }
                    client._request("POST", "/admin/users", json=user_data)
                    logger.info(f"[VisitorPool] Created Gitea user: {username}")
        except Exception as e:
            logger.warning(f"[VisitorPool] Failed to ensure Gitea users: {e}")

    @classmethod
    def get_pool_status(cls) -> dict:
        """
        Get current pool status.

        Returns:
            dict: {total, allocated, free, expired}
        """
        total = cls.POOL_SIZE
        active_allocations = VisitorAllocation.objects.filter(
            is_active=True, expires_at__gt=timezone.now()
        ).count()

        expired = VisitorAllocation.objects.filter(
            is_active=True, expires_at__lte=timezone.now()
        ).count()

        return {
            "total": total,
            "allocated": active_allocations,
            "free": total - active_allocations,
            "expired": expired,
        }


def _initialize_visitor_writer_workspace(project, project_path):
    """
    Initialize writer workspace for visitor projects (Gitea-independent).

    This is called during visitor pool initialization to ensure writer workspaces
    are created even though visitors don't have Gitea accounts.

    Args:
        project: Project model instance
        project_path: Path to project root directory
    """
    try:
        writer_dir = project_path / "scitex" / "writer"

        # Let Writer() handle structure validation and initialization
        # Writer will either create new or attach to existing workspace
        logger.info(f"[VisitorPool] Initializing writer workspace for {project.slug}")

        # Initialize Writer with git_strategy='none' for visitor projects
        # Visitors don't have Gitea repos, so we don't use git
        from scitex.writer import Writer
        from django.conf import settings

        template_branch = getattr(settings, "SCITEX_WRITER_TEMPLATE_BRANCH", None)
        template_tag = getattr(settings, "SCITEX_WRITER_TEMPLATE_TAG", None)

        # branch and tag are mutually exclusive - only pass the one that's set
        writer_kwargs = {
            "project_dir": writer_dir,
            "git_strategy": None,  # No git for visitor projects
        }
        if template_tag:
            writer_kwargs["tag"] = template_tag
        elif template_branch:
            writer_kwargs["branch"] = template_branch

        writer = Writer(**writer_kwargs)

        # Verify creation
        manuscript_dir = writer_dir / "01_manuscript"
        if manuscript_dir.exists():
            logger.info(
                f"[VisitorPool] Writer workspace initialized for {project.slug}"
            )

            # Create manuscript record (writer_initialized is a computed property, not a field)
            from apps.writer_app.models import Manuscript

            # Since project is OneToOneField, only use project for lookup
            Manuscript.objects.get_or_create(
                project=project,
                defaults={
                    "owner": project.owner,
                    "title": f"{project.name} Manuscript"
                },
            )
        else:
            logger.warning(
                f"[VisitorPool] Writer workspace incomplete for {project.slug}"
            )

    except Exception as e:
        logger.error(
            f"[VisitorPool] Failed to initialize writer workspace for {project.slug}: {e}"
        )
        logger.exception("Full traceback:")


# For backward compatibility during migration
DemoProjectPool = VisitorPool
