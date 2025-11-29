"""
File Operations for Remote Projects

Handles CRUD operations on remote filesystem files and directories.
"""

import logging
import time
from pathlib import Path
from typing import Tuple, Optional, List, Dict

logger = logging.getLogger(__name__)


class FileOperations:
    """
    Manages file operations on remote filesystems.
    """

    def __init__(self, project, mount_manager):
        """
        Initialize file operations.

        Args:
            project: Project instance
            mount_manager: MountManager instance
        """
        self.project = project
        self.mount_manager = mount_manager

    def read_file(self, relative_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Read a file from remote filesystem (mounts if needed).

        Args:
            relative_path: Path relative to remote_path

        Returns:
            (success, content, error_message)
        """
        # Ensure mounted
        success, error = self.mount_manager.ensure_mounted()
        if not success:
            return False, None, error

        # Read file
        file_path = self.mount_manager.mount_point / relative_path

        try:
            content = file_path.read_text()
            self.mount_manager._update_last_accessed()
            return True, content, None

        except FileNotFoundError:
            return False, None, f"File not found: {relative_path}"
        except PermissionError:
            return False, None, f"Permission denied: {relative_path}"
        except Exception as e:
            logger.error(f"Error reading file {relative_path}: {str(e)}")
            return False, None, str(e)

    def write_file(self, relative_path: str, content: str) -> Tuple[bool, Optional[str]]:
        """
        Write a file to remote filesystem.

        Args:
            relative_path: Path relative to remote_path
            content: File content

        Returns:
            (success, error_message)
        """
        # Ensure mounted
        success, error = self.mount_manager.ensure_mounted()
        if not success:
            return False, error

        file_path = self.mount_manager.mount_point / relative_path

        try:
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            file_path.write_text(content)

            self.mount_manager._update_last_accessed()
            return True, None

        except PermissionError:
            return False, f"Permission denied: {relative_path}"
        except Exception as e:
            logger.error(f"Error writing file {relative_path}: {str(e)}")
            return False, str(e)

    def delete_file(self, relative_path: str) -> Tuple[bool, Optional[str]]:
        """
        Delete a file from remote filesystem.

        Args:
            relative_path: Path relative to remote_path

        Returns:
            (success, error_message)
        """
        # Ensure mounted
        success, error = self.mount_manager.ensure_mounted()
        if not success:
            return False, error

        file_path = self.mount_manager.mount_point / relative_path

        try:
            file_path.unlink()
            self.mount_manager._update_last_accessed()
            return True, None

        except FileNotFoundError:
            return False, f"File not found: {relative_path}"
        except PermissionError:
            return False, f"Permission denied: {relative_path}"
        except Exception as e:
            logger.error(f"Error deleting file {relative_path}: {str(e)}")
            return False, str(e)

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
        # Ensure mounted
        success, error = self.mount_manager.ensure_mounted()
        if not success:
            return False, None, error

        dir_path = self.mount_manager.mount_point / relative_path

        try:
            entries = []

            for item in dir_path.iterdir():
                stat = item.stat()

                entries.append({
                    'name': item.name,
                    'path': str(item.relative_to(self.mount_manager.mount_point)),
                    'type': 'directory' if item.is_dir() else 'file',
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                })

            # Sort: directories first, then alphabetically
            entries.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))

            self.mount_manager._update_last_accessed()
            return True, entries, None

        except FileNotFoundError:
            return False, None, f"Directory not found: {relative_path}"
        except PermissionError:
            return False, None, f"Permission denied: {relative_path}"
        except Exception as e:
            logger.error(f"Error listing directory {relative_path}: {str(e)}")
            return False, None, str(e)

    def read_file_with_retry(self, relative_path: str, max_retries=3) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Read file with automatic retry on network errors.

        Args:
            relative_path: Path relative to remote_path
            max_retries: Maximum number of retry attempts

        Returns:
            (success, content, error_message)
        """
        for attempt in range(max_retries):
            try:
                success, content, error = self.read_file(relative_path)

                if success:
                    return True, content, None

                # If mount issue, try remounting
                if error and ("Input/output error" in error or "Transport endpoint" in error):
                    logger.warning(f"Mount error on attempt {attempt+1}, remounting...")
                    self.mount_manager.unmount()
                    self.mount_manager.ensure_mounted()
                    continue

                # Other error, don't retry
                return False, None, error

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Read failed on attempt {attempt+1}: {e}, retrying...")
                    time.sleep(1)  # Wait before retry
                    continue
                else:
                    return False, None, f"Failed after {max_retries} attempts: {str(e)}"

        return False, None, "Max retries exceeded"
