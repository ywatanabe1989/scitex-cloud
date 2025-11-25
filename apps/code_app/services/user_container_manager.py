#!/usr/bin/env python3
"""
User Container Manager for SciTeX-Code
Enables users to customize their Apptainer/Singularity environments using fakeroot.

Features:
- Two-tier system: Base container + user customization
- Fakeroot support for rootless container building
- Web-based package installation
- Definition file upload
- Storage quotas
"""

import subprocess
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache

logger = logging.getLogger(__name__)


class UserContainerError(Exception):
    """Raised when user container operations fail."""
    pass


class UserContainerManager:
    """
    Manage user-customizable Apptainer/Singularity containers

    Allows users to:
    - Build custom containers from the base image
    - Install packages (apt, pip, conda)
    - Use fakeroot for rootless building
    - Stay within storage quotas
    """

    def __init__(self):
        # Configuration from Django settings
        self.base_image = Path(settings.SINGULARITY_IMAGE_PATH)
        self.user_containers_dir = Path(settings.MEDIA_ROOT) / "user_containers"
        self.user_containers_dir.mkdir(parents=True, exist_ok=True)

        # Limits
        self.max_container_size = settings.USER_CONTAINER_MAX_SIZE_GB * 1024**3  # Convert to bytes
        self.max_build_time = settings.USER_CONTAINER_MAX_BUILD_TIME
        self.max_builds_per_day = settings.USER_CONTAINER_MAX_BUILDS_PER_DAY

        # Detect Apptainer vs Singularity
        self.container_cmd = self._detect_container_command()

        # Cache key prefix
        self.cache_prefix = 'user_container_'

    def _detect_container_command(self) -> str:
        """
        Detect whether to use 'apptainer' or 'singularity' command

        Returns:
            'apptainer' or 'singularity'
        """
        # Try apptainer first (newer)
        try:
            result = subprocess.run(
                ["apptainer", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("Using 'apptainer' command")
                return "apptainer"
        except FileNotFoundError:
            pass

        # Fall back to singularity
        try:
            result = subprocess.run(
                ["singularity", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("Using 'singularity' command")
                return "singularity"
        except FileNotFoundError:
            pass

        raise UserContainerError(
            "Neither 'apptainer' nor 'singularity' command found. "
            "Install with: sudo apt-get install apptainer"
        )

    def _check_fakeroot_available(self) -> bool:
        """Check if fakeroot is available for this user"""
        try:
            result = subprocess.run(
                [self.container_cmd, "exec", "--fakeroot", str(self.base_image), "true"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Fakeroot check failed: {e}")
            return False

    def get_user_dir(self, user: User) -> Path:
        """Get user's container directory"""
        user_dir = self.user_containers_dir / str(user.id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def get_user_container_path(self, user: User) -> Path:
        """Get path to user's custom container"""
        return self.get_user_dir(user) / "custom.sif"

    def get_sandbox_path(self, user: User) -> Path:
        """Get path to user's sandbox (writable directory)"""
        return self.get_user_dir(user) / "sandbox"

    def has_custom_container(self, user: User) -> bool:
        """Check if user has custom container"""
        return self.get_user_container_path(user).exists()

    def get_active_container(self, user: User) -> Path:
        """
        Get container to use for execution (custom or base)

        Returns:
            Path to .sif file
        """
        custom = self.get_user_container_path(user)
        return custom if custom.exists() else self.base_image

    def get_container_stats(self, user: User) -> Dict[str, Any]:
        """Get user's container statistics"""
        user_dir = self.get_user_dir(user)
        container_path = self.get_user_container_path(user)
        sandbox_path = self.get_sandbox_path(user)

        stats = {
            'has_custom': container_path.exists(),
            'has_sandbox': sandbox_path.exists(),
            'container_size_mb': 0,
            'sandbox_size_mb': 0,
            'total_size_mb': 0,
            'quota_used_percentage': 0,
        }

        # Container size
        if container_path.exists():
            stats['container_size_mb'] = container_path.stat().st_size / 1024**2

        # Sandbox size
        if sandbox_path.exists():
            total = sum(
                f.stat().st_size
                for f in sandbox_path.rglob('*')
                if f.is_file()
            )
            stats['sandbox_size_mb'] = total / 1024**2

        # Total
        stats['total_size_mb'] = stats['container_size_mb'] + stats['sandbox_size_mb']
        stats['total_size_gb'] = stats['total_size_mb'] / 1024

        # Quota
        quota_gb = self.max_container_size / 1024**3
        stats['quota_gb'] = quota_gb
        stats['quota_used_percentage'] = (stats['total_size_gb'] / quota_gb) * 100

        return stats

    def _check_build_rate_limit(self, user: User) -> tuple[bool, str]:
        """Check if user has exceeded build rate limit"""
        cache_key = f"{self.cache_prefix}builds_{user.id}"
        builds_today = cache.get(cache_key, 0)

        if builds_today >= self.max_builds_per_day:
            return False, f"Build limit reached ({self.max_builds_per_day}/day)"

        return True, "OK"

    def _increment_build_count(self, user: User):
        """Increment user's build count for today"""
        cache_key = f"{self.cache_prefix}builds_{user.id}"
        builds = cache.get(cache_key, 0)
        # Cache for 24 hours
        cache.set(cache_key, builds + 1, 86400)

    def create_sandbox(self, user: User) -> Dict[str, Any]:
        """
        Create writable sandbox for user to customize

        Args:
            user: Django user

        Returns:
            Dict with success status and message
        """
        # Check rate limit
        can_build, reason = self._check_build_rate_limit(user)
        if not can_build:
            return {'success': False, 'message': reason}

        sandbox_path = self.get_sandbox_path(user)

        # Check if sandbox already exists
        if sandbox_path.exists():
            return {
                'success': False,
                'message': 'Sandbox already exists. Finalize or delete it first.'
            }

        # Create sandbox from base image
        cmd = [
            self.container_cmd, "build",
            "--sandbox",
            "--fakeroot",
            str(sandbox_path),
            str(self.base_image)
        ]

        try:
            logger.info(f"Creating sandbox for user {user.username}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.max_build_time,
                check=True
            )

            self._increment_build_count(user)

            return {
                'success': True,
                'sandbox_path': str(sandbox_path),
                'message': 'Sandbox created successfully. You can now customize it.',
                'next_steps': [
                    'Install packages with pip or apt',
                    'Test your changes',
                    'Finalize to create permanent container'
                ]
            }

        except subprocess.CalledProcessError as e:
            logger.error(f"Sandbox creation failed for {user.username}: {e.stderr}")
            # Clean up partial sandbox
            if sandbox_path.exists():
                shutil.rmtree(sandbox_path, ignore_errors=True)

            return {
                'success': False,
                'message': f'Failed to create sandbox: {e.stderr}',
                'stderr': e.stderr
            }

        except subprocess.TimeoutExpired:
            logger.error(f"Sandbox creation timeout for {user.username}")
            if sandbox_path.exists():
                shutil.rmtree(sandbox_path, ignore_errors=True)

            return {
                'success': False,
                'message': f'Build timed out after {self.max_build_time} seconds'
            }

    def install_package(
        self,
        user: User,
        package_manager: str,
        packages: List[str]
    ) -> Dict[str, Any]:
        """
        Install packages to user's sandbox

        Args:
            user: Django user
            package_manager: 'pip', 'apt', or 'conda'
            packages: List of package names

        Returns:
            Dict with success status and output
        """
        sandbox_path = self.get_sandbox_path(user)

        if not sandbox_path.exists():
            return {
                'success': False,
                'message': 'Sandbox does not exist. Create one first.'
            }

        # Build install command
        if package_manager == 'pip':
            packages_str = ' '.join(packages)
            install_cmd = f"pip install --no-cache-dir {packages_str}"
        elif package_manager == 'apt':
            packages_str = ' '.join(packages)
            install_cmd = f"apt-get update && apt-get install -y {packages_str}"
        elif package_manager == 'conda':
            packages_str = ' '.join(packages)
            install_cmd = f"conda install -y {packages_str}"
        else:
            return {
                'success': False,
                'message': f'Invalid package manager: {package_manager}'
            }

        # Execute in sandbox with fakeroot
        cmd = [
            self.container_cmd, "exec",
            "--fakeroot",
            "--writable",
            str(sandbox_path),
            "/bin/bash", "-c",
            install_cmd
        ]

        try:
            logger.info(
                f"Installing {packages} with {package_manager} "
                f"for user {user.username}"
            )

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes for package installation
                check=True
            )

            return {
                'success': True,
                'packages': packages,
                'package_manager': package_manager,
                'stdout': result.stdout,
                'message': f'Successfully installed: {", ".join(packages)}'
            }

        except subprocess.CalledProcessError as e:
            logger.error(
                f"Package installation failed for {user.username}: {e.stderr}"
            )
            return {
                'success': False,
                'packages': packages,
                'stderr': e.stderr,
                'message': f'Installation failed. See stderr for details.'
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'packages': packages,
                'message': 'Installation timed out after 5 minutes'
            }

    def finalize_sandbox(self, user: User) -> Dict[str, Any]:
        """
        Convert sandbox to final .sif container

        Args:
            user: Django user

        Returns:
            Dict with success status
        """
        sandbox_path = self.get_sandbox_path(user)
        output_sif = self.get_user_container_path(user)

        if not sandbox_path.exists():
            return {
                'success': False,
                'message': 'No sandbox to finalize. Create one first.'
            }

        # Check if would exceed size limit
        sandbox_size = sum(
            f.stat().st_size
            for f in sandbox_path.rglob('*')
            if f.is_file()
        )

        if sandbox_size > self.max_container_size:
            size_gb = sandbox_size / 1024**3
            limit_gb = self.max_container_size / 1024**3
            return {
                'success': False,
                'message': f'Sandbox too large ({size_gb:.1f}GB > {limit_gb}GB limit)'
            }

        # Build final container
        cmd = [
            self.container_cmd, "build",
            "--fakeroot",
            str(output_sif),
            str(sandbox_path)
        ]

        try:
            logger.info(f"Finalizing sandbox for user {user.username}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.max_build_time,
                check=True
            )

            # Check final size
            final_size = output_sif.stat().st_size
            if final_size > self.max_container_size:
                output_sif.unlink()
                return {
                    'success': False,
                    'message': f'Container exceeds size limit'
                }

            # Remove sandbox after successful build
            shutil.rmtree(sandbox_path)

            return {
                'success': True,
                'container_path': str(output_sif),
                'size_mb': final_size / 1024**2,
                'message': 'Container finalized successfully. Sandbox removed.'
            }

        except subprocess.CalledProcessError as e:
            logger.error(f"Finalization failed for {user.username}: {e.stderr}")
            return {
                'success': False,
                'message': f'Finalization failed: {e.stderr}',
                'stderr': e.stderr
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': f'Build timed out after {self.max_build_time} seconds'
            }

    def build_from_definition(
        self,
        user: User,
        definition_content: str
    ) -> Dict[str, Any]:
        """
        Build custom container from user's definition file

        Args:
            user: Django user
            definition_content: Singularity/Apptainer definition file content

        Returns:
            Dict with success status
        """
        # Check rate limit
        can_build, reason = self._check_build_rate_limit(user)
        if not can_build:
            return {'success': False, 'message': reason}

        user_dir = self.get_user_dir(user)
        def_file = user_dir / "user-container.def"
        output_sif = self.get_user_container_path(user)

        # Save definition file
        def_file.write_text(definition_content)

        # Build container
        cmd = [
            self.container_cmd, "build",
            "--fakeroot",
            str(output_sif),
            str(def_file)
        ]

        try:
            logger.info(f"Building container from definition for {user.username}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.max_build_time,
                check=True
            )

            # Check size
            size = output_sif.stat().st_size
            if size > self.max_container_size:
                output_sif.unlink()
                return {
                    'success': False,
                    'message': f'Container too large ({size/1024**3:.1f}GB > {self.max_container_size/1024**3}GB limit)'
                }

            self._increment_build_count(user)

            return {
                'success': True,
                'container_path': str(output_sif),
                'size_mb': size / 1024**2,
                'message': 'Custom container built successfully',
                'build_log': result.stdout
            }

        except subprocess.CalledProcessError as e:
            logger.error(f"Build failed for {user.username}: {e.stderr}")
            if output_sif.exists():
                output_sif.unlink()

            return {
                'success': False,
                'message': f'Build failed',
                'stderr': e.stderr,
                'stdout': e.stdout if hasattr(e, 'stdout') else ''
            }

        except subprocess.TimeoutExpired:
            logger.error(f"Build timeout for {user.username}")
            if output_sif.exists():
                output_sif.unlink()

            return {
                'success': False,
                'message': f'Build timed out after {self.max_build_time} seconds'
            }

    def delete_custom_container(self, user: User) -> Dict[str, Any]:
        """Delete user's custom container and sandbox"""
        user_dir = self.get_user_dir(user)
        container_path = self.get_user_container_path(user)
        sandbox_path = self.get_sandbox_path(user)

        deleted = []

        if container_path.exists():
            container_path.unlink()
            deleted.append('container')

        if sandbox_path.exists():
            shutil.rmtree(sandbox_path)
            deleted.append('sandbox')

        if deleted:
            return {
                'success': True,
                'message': f'Deleted: {", ".join(deleted)}',
                'deleted': deleted
            }
        else:
            return {
                'success': False,
                'message': 'No custom container or sandbox found'
            }


# Global instance
user_container_manager = UserContainerManager()

# EOF
