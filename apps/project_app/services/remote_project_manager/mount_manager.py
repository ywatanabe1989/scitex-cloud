"""
Mount Management for Remote Projects

Handles SSHFS mounting, unmounting, and health checks for remote filesystems.
"""

import subprocess
import logging
from pathlib import Path
from typing import Tuple, Optional
from django.utils import timezone

logger = logging.getLogger(__name__)


class MountManager:
    """
    Manages SSHFS mount operations for remote projects.
    """

    def __init__(self, project, config, mount_point: Path):
        """
        Initialize mount manager.

        Args:
            project: Project instance
            config: RemoteProjectConfig instance
            mount_point: Path to mount point
        """
        self.project = project
        self.config = config
        self.mount_point = mount_point

    def ensure_mounted(self) -> Tuple[bool, Optional[str]]:
        """
        Ensure remote filesystem is mounted (mount if not already).

        Returns:
            (success, error_message)
        """
        # Health check if already mounted
        if self._is_mounted():
            # Try to access mount point
            try:
                self.mount_point.stat()
                self._update_last_accessed()
                logger.debug(f"Remote project {self.project.slug} already mounted and healthy")
                return True, None
            except OSError:
                # Mount is stale, remount
                logger.warning(f"Stale mount detected, remounting: {self.project.slug}")
                self.unmount()
                # Fall through to mount

        # Mount
        return self._mount()

    def _is_mounted(self) -> bool:
        """
        Check if filesystem is currently mounted.

        Returns:
            True if mounted, False otherwise
        """
        if not self.mount_point.exists():
            return False

        # Check if mount point has FUSE filesystem
        cmd = ["mountpoint", "-q", str(self.mount_point)]
        result = subprocess.run(cmd, capture_output=True)

        is_mounted = result.returncode == 0

        # Update database state if different
        if is_mounted != self.config.is_mounted:
            self.config.is_mounted = is_mounted
            self.config.save(update_fields=['is_mounted'])

        return is_mounted

    def _mount(self) -> Tuple[bool, Optional[str]]:
        """
        Mount remote filesystem via SSHFS.

        Returns:
            (success, error_message)
        """
        # Create mount point
        try:
            self.mount_point.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return False, f"Failed to create mount point: {str(e)}"

        # Get SSH key
        ssh_key_path = self.config.remote_credential.private_key_path

        if not Path(ssh_key_path).exists():
            return False, f"SSH key not found: {ssh_key_path}"

        # SSHFS mount command
        remote_target = f"{self.config.ssh_username}@{self.config.ssh_host}:{self.config.remote_path}"

        cmd = [
            "sshfs",
            remote_target,
            str(self.mount_point),
            "-p", str(self.config.ssh_port),
            "-o", f"IdentityFile={ssh_key_path}",
            "-o", "StrictHostKeyChecking=accept-new",
            "-o", "ServerAliveInterval=15",
            "-o", "ServerAliveCountMax=3",
            "-o", "reconnect",
            "-o", "cache_timeout=20",        # Metadata cache: 20 sec
            "-o", "entry_timeout=20",        # Directory entry cache: 20 sec
            "-o", "attr_timeout=20",         # Attribute cache: 20 sec
            "-o", "kernel_cache",            # Use kernel page cache
            "-o", "auto_cache",              # Automatic cache based on mtime
            "-o", "direct_io",               # Bypass cache for writes (consistency)
            "-o", "Compression=yes",         # Compress traffic
            "-o", "allow_other",             # Allow other users (for Docker)
            "-o", "default_permissions",     # Use file permissions
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )

            # Update database
            self.config.is_mounted = True
            self.config.mount_point = str(self.mount_point)
            self.config.mounted_at = timezone.now()
            self.config.last_accessed = timezone.now()
            self.config.save()

            logger.info(
                f"✅ Mounted remote project: {self.project.owner.username}/{self.project.slug} "
                f"→ {remote_target}"
            )

            return True, None

        except subprocess.CalledProcessError as e:
            error_msg = f"SSHFS mount failed: {e.stderr}"
            logger.error(error_msg)
            return False, error_msg

        except subprocess.TimeoutExpired:
            return False, "SSH connection timeout (30 seconds)"

        except Exception as e:
            logger.error(f"Unexpected mount error: {str(e)}")
            return False, f"Mount failed: {str(e)}"

    def unmount(self) -> Tuple[bool, Optional[str]]:
        """
        Unmount remote filesystem.

        Returns:
            (success, error_message)
        """
        if not self._is_mounted():
            return True, None

        cmd = ["fusermount", "-u", str(self.mount_point)]

        try:
            subprocess.run(cmd, check=True, timeout=10, capture_output=True)

            # Update database
            self.config.is_mounted = False
            self.config.mount_point = None
            self.config.save()

            # Remove mount point directory
            try:
                self.mount_point.rmdir()
            except OSError:
                pass  # Directory not empty or doesn't exist

            logger.info(f"✅ Unmounted remote project: {self.project.slug}")
            return True, None

        except subprocess.CalledProcessError as e:
            error_msg = f"Unmount failed: {e.stderr.decode() if e.stderr else 'Unknown error'}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            logger.error(f"Unexpected unmount error: {str(e)}")
            return False, f"Unmount failed: {str(e)}"

    def _update_last_accessed(self):
        """Update last accessed timestamp."""
        self.config.last_accessed = timezone.now()
        self.config.save(update_fields=['last_accessed'])
