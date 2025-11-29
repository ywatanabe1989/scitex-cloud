"""
Remote Project Manager

Main manager class that coordinates all remote project operations.
"""

import logging
from pathlib import Path
from typing import Tuple, Optional, List, Dict

from .mount_manager import MountManager
from .file_operations import FileOperations
from .connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


class RemoteProjectManager:
    """
    Manage remote filesystem projects with TRAMP-like on-demand access.

    Example usage:
        >>> from apps.project_app.models import Project
        >>> project = Project.objects.get(slug='my-remote-project')
        >>> manager = RemoteProjectManager(project)
        >>>
        >>> # Ensure mounted (automatic on first access)
        >>> success, error = manager.ensure_mounted()
        >>>
        >>> # Read file
        >>> success, content, error = manager.read_file('README.md')
        >>>
        >>> # Write file
        >>> success, error = manager.write_file('test.txt', 'Hello World')
        >>>
        >>> # List directory
        >>> success, entries, error = manager.list_directory('.')
        >>>
        >>> # Unmount
        >>> success, error = manager.unmount()
    """

    def __init__(self, project):
        """
        Initialize remote project manager.

        Args:
            project: Project instance (must be project_type='remote')

        Raises:
            ValueError: If project is not type 'remote'
        """
        if project.project_type != 'remote':
            raise ValueError(f"Project {project.slug} is not a remote project")

        if not hasattr(project, 'remote_config') or not project.remote_config:
            raise ValueError(f"Project {project.slug} has no remote configuration")

        self.project = project
        self.config = project.remote_config

        # Mount point: /tmp/scitex_remote/{user_id}/{project_slug}/
        self.mount_base = Path("/tmp/scitex_remote")
        self.mount_point = self.mount_base / str(project.owner.id) / project.slug

        # Initialize component managers
        self.mount_manager = MountManager(project, self.config, self.mount_point)
        self.file_ops = FileOperations(project, self.mount_manager)
        self.connection_manager = ConnectionManager(project, self.config)

    # ========================================================================
    # Mount Management (delegated to MountManager)
    # ========================================================================

    def ensure_mounted(self) -> Tuple[bool, Optional[str]]:
        """
        Ensure remote filesystem is mounted (mount if not already).

        Returns:
            (success, error_message)
        """
        return self.mount_manager.ensure_mounted()

    def unmount(self) -> Tuple[bool, Optional[str]]:
        """
        Unmount remote filesystem.

        Returns:
            (success, error_message)
        """
        return self.mount_manager.unmount()

    def _is_mounted(self) -> bool:
        """
        Check if filesystem is currently mounted.

        Returns:
            True if mounted, False otherwise
        """
        return self.mount_manager._is_mounted()

    # ========================================================================
    # File Operations (delegated to FileOperations)
    # ========================================================================

    def read_file(self, relative_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Read a file from remote filesystem (mounts if needed).

        Args:
            relative_path: Path relative to remote_path

        Returns:
            (success, content, error_message)
        """
        return self.file_ops.read_file(relative_path)

    def write_file(self, relative_path: str, content: str) -> Tuple[bool, Optional[str]]:
        """
        Write a file to remote filesystem.

        Args:
            relative_path: Path relative to remote_path
            content: File content

        Returns:
            (success, error_message)
        """
        return self.file_ops.write_file(relative_path, content)

    def delete_file(self, relative_path: str) -> Tuple[bool, Optional[str]]:
        """
        Delete a file from remote filesystem.

        Args:
            relative_path: Path relative to remote_path

        Returns:
            (success, error_message)
        """
        return self.file_ops.delete_file(relative_path)

    def list_directory(self, relative_path: str = ".") -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        List directory contents from remote filesystem.

        Args:
            relative_path: Path relative to remote_path

        Returns:
            (success, file_list, error_message)

        Example response:
            success, entries, error = manager.list_directory('.')
            # entries = [
            #     {'name': 'README.md', 'path': 'README.md', 'type': 'file', 'size': 1234, 'modified': 1234567890},
            #     {'name': 'src', 'path': 'src', 'type': 'directory', 'size': 0, 'modified': 1234567890},
            # ]
        """
        return self.file_ops.list_directory(relative_path)

    def read_file_with_retry(self, relative_path: str, max_retries=3) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Read file with automatic retry on network errors.

        Args:
            relative_path: Path relative to remote_path
            max_retries: Maximum number of retry attempts

        Returns:
            (success, content, error_message)
        """
        return self.file_ops.read_file_with_retry(relative_path, max_retries)

    # ========================================================================
    # Connection Testing (delegated to ConnectionManager)
    # ========================================================================

    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """
        Test SSH connection to remote system.

        Returns:
            (success, error_message)
        """
        return self.connection_manager.test_connection()
