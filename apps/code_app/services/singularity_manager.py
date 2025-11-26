#!/usr/bin/env python3
"""
Singularity Container Manager for SciTeX-Code
Superior security alternative to Docker for user code execution.

Security Benefits:
- No root daemon required
- No Docker socket mounting
- User runs as themselves (UID preserved)
- Designed for multi-user HPC environments
"""

import subprocess
import logging
import time
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache

logger = logging.getLogger(__name__)


class SingularityError(Exception):
    """Raised when Singularity operations fail."""
    pass


class SingularityManager:
    """
    Manage Singularity containers for user code execution

    This provides a secure alternative to Docker with:
    - No daemon requirement
    - UID preservation (no mapping complexity)
    - HPC integration (SLURM, PBS)
    - Resource efficiency (single shared image)
    """

    def __init__(self):
        # Get configuration from Django settings
        self.image_path = Path(settings.SINGULARITY_IMAGE_PATH)
        self.max_concurrent = settings.SINGULARITY_MAX_CONCURRENT_JOBS
        self.default_timeout = settings.SINGULARITY_DEFAULT_TIMEOUT
        self.max_timeout = settings.SINGULARITY_MAX_TIMEOUT

        # Cache keys
        self.cache_key_active = 'singularity_active_jobs'
        self.cache_key_stats = 'singularity_stats'
        self.cache_ttl = 300  # 5 minutes

        # Verify Singularity is installed
        self._verify_singularity()

        # Verify image exists
        if not self.image_path.exists():
            logger.error(f"Singularity image not found: {self.image_path}")
            raise FileNotFoundError(
                f"Singularity image not found: {self.image_path}\n"
                f"Build it with: sudo singularity build {self.image_path} {self.image_path.with_suffix('.def')}"
            )

    def _verify_singularity(self):
        """Verify Singularity is installed and accessible"""
        try:
            result = subprocess.run(
                ["singularity", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"Singularity version: {result.stdout.strip()}")
            else:
                raise SingularityError("Singularity not found or not working")
        except FileNotFoundError:
            raise SingularityError(
                "Singularity not installed. Install with: "
                "sudo apt-get install singularity-container"
            )
        except subprocess.TimeoutExpired:
            raise SingularityError("Singularity command timed out")

    def get_active_job_count(self) -> int:
        """Get current number of active Singularity jobs"""
        return cache.get(self.cache_key_active, 0)

    def _increment_job_count(self):
        """Increment active job counter"""
        count = self.get_active_job_count()
        cache.set(self.cache_key_active, count + 1, self.cache_ttl)

    def _decrement_job_count(self):
        """Decrement active job counter"""
        count = self.get_active_job_count()
        cache.set(self.cache_key_active, max(0, count - 1), self.cache_ttl)

    def can_execute(self) -> Tuple[bool, str]:
        """
        Check if resources are available for execution

        Returns:
            (can_execute, reason)
        """
        active = self.get_active_job_count()

        if active >= self.max_concurrent:
            return False, f"Maximum concurrent jobs reached ({self.max_concurrent})"

        return True, "Resources available"

    def execute_code(
        self,
        user: User,
        script_path: Path,
        timeout: Optional[int] = None,
        bind_workspace: bool = True,
        capture_output: bool = True
    ) -> Dict[str, Any]:
        """
        Execute user code in Singularity container

        Args:
            user: Django user object
            script_path: Path to Python script to execute
            timeout: Execution timeout in seconds (None = default)
            bind_workspace: Whether to bind user workspace directory
            capture_output: Whether to capture stdout/stderr

        Returns:
            Dict with stdout, stderr, returncode, execution_time

        Security Features:
            - No root daemon required
            - Runs as invoking user (preserves UID)
            - Isolated /tmp and /var/tmp (--contain)
            - Clean environment variables (--cleanenv)
            - No home directory mounted (--no-home)
            - Resource limits via cgroups

        Raises:
            ResourceWarning: If resources unavailable
            SingularityError: On execution errors
        """
        # Use default timeout if not specified
        if timeout is None:
            timeout = self.default_timeout
        elif timeout > self.max_timeout:
            logger.warning(
                f"Requested timeout {timeout}s exceeds max {self.max_timeout}s, capping"
            )
            timeout = self.max_timeout

        # Check resource availability
        can_run, reason = self.can_execute()
        if not can_run:
            raise ResourceWarning(f"Cannot execute: {reason}")

        # Prepare workspace binding
        workspace_dir = Path(settings.MEDIA_ROOT) / "users" / str(user.id) / "workspace"
        workspace_dir.mkdir(parents=True, exist_ok=True)

        # Verify script exists
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        # Build Singularity command with security options
        cmd = [
            "singularity", "exec",
            "--contain",     # Isolated /tmp, /var/tmp
            "--cleanenv",    # Clean environment
            "--no-home",     # Don't mount home directory
        ]

        # Bind workspace if requested
        if bind_workspace:
            cmd.extend([
                "--bind", f"{workspace_dir}:/workspace:rw",
                "--pwd", "/workspace",
            ])

        # Apply resource limits (cgroups)
        # Note: Requires Singularity 3.8+ and cgroups v2
        try:
            cgroup_config = self._create_cgroup_config(user.id)
            cmd.extend([
                "--apply-cgroups", str(cgroup_config),
            ])
        except Exception as e:
            logger.warning(f"Could not apply cgroups (running without limits): {e}")

        # Add image and command
        cmd.extend([
            str(self.image_path),
            "python", str(script_path)
        ])

        # Execute with timeout
        start_time = time.time()

        try:
            # Increment active job counter
            self._increment_job_count()

            logger.info(
                f"Executing Singularity job for user {user.username}: {script_path.name}"
            )
            logger.debug(f"Command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                check=False,
                cwd=workspace_dir,
            )

            execution_time = time.time() - start_time

            logger.info(
                f"Singularity job completed for user {user.username}: "
                f"exit_code={result.returncode}, duration={execution_time:.2f}s"
            )

            # Update statistics
            self._update_stats(user.id, execution_time, result.returncode == 0)

            return {
                'stdout': result.stdout if capture_output else '',
                'stderr': result.stderr if capture_output else '',
                'returncode': result.returncode,
                'execution_time': execution_time,
                'timeout': timeout,
                'success': result.returncode == 0,
            }

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            logger.warning(
                f"Singularity job timeout for user {user.username} after {timeout}s"
            )

            self._update_stats(user.id, execution_time, False)

            return {
                'stdout': '',
                'stderr': f'Execution timed out after {timeout} seconds',
                'returncode': -1,
                'execution_time': execution_time,
                'timeout': timeout,
                'success': False,
            }

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Singularity execution error for user {user.username}: {e}")

            self._update_stats(user.id, execution_time, False)

            return {
                'stdout': '',
                'stderr': f'Execution error: {str(e)}',
                'returncode': -1,
                'execution_time': execution_time,
                'timeout': timeout,
                'success': False,
            }

        finally:
            # Decrement active job counter
            self._decrement_job_count()

    def _create_cgroup_config(self, user_id: int) -> Path:
        """
        Create cgroup configuration file for resource limits

        Resource Limits (aligned with NAS allocation):
        - CPU: 0.35 cores (35% of 1 core)
        - Memory: 2GB
        - PIDs: 256 processes (prevent fork bombs)

        Args:
            user_id: User ID for unique config file

        Returns:
            Path to cgroup config file
        """
        cgroup_dir = Path(settings.MEDIA_ROOT) / "cgroups"
        cgroup_dir.mkdir(parents=True, exist_ok=True)

        cgroup_file = cgroup_dir / f"user_{user_id}.toml"

        # Singularity cgroup config format (TOML)
        # See: https://sylabs.io/guides/3.8/user-guide/cgroups.html
        config = """# Singularity cgroup configuration for user workspace
# Generated automatically - do not edit manually

[cpu]
    # CPU shares: 350 = 35% of 1 core (out of 1024)
    shares = 350

[memory]
    # Memory limit: 2GB in bytes
    limit = 2147483648
    # Swap limit: same as memory (no swap)
    swap = 2147483648

[pids]
    # Process limit: prevent fork bombs
    limit = 256
"""

        cgroup_file.write_text(config)
        return cgroup_file

    def _update_stats(self, user_id: int, execution_time: float, success: bool):
        """Update execution statistics"""
        try:
            stats = cache.get(self.cache_key_stats, {})

            user_key = f"user_{user_id}"
            if user_key not in stats:
                stats[user_key] = {
                    'total_jobs': 0,
                    'successful_jobs': 0,
                    'failed_jobs': 0,
                    'total_time': 0.0,
                }

            stats[user_key]['total_jobs'] += 1
            if success:
                stats[user_key]['successful_jobs'] += 1
            else:
                stats[user_key]['failed_jobs'] += 1
            stats[user_key]['total_time'] += execution_time

            cache.set(self.cache_key_stats, stats, 3600 * 24)  # 24 hours

        except Exception as e:
            logger.error(f"Failed to update stats: {e}")

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get execution statistics for a user"""
        stats = cache.get(self.cache_key_stats, {})
        user_key = f"user_{user_id}"
        return stats.get(user_key, {
            'total_jobs': 0,
            'successful_jobs': 0,
            'failed_jobs': 0,
            'total_time': 0.0,
        })

    def submit_to_hpc(
        self,
        user: User,
        script_path: Path,
        hpc_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Submit job to HPC cluster (e.g., Spartan) via SLURM

        Args:
            user: Django user object
            script_path: Path to Python script
            hpc_config: HPC configuration (partition, time, cpus, mem)

        Returns:
            SLURM job ID

        Raises:
            SingularityError: On submission failure
        """
        # Default HPC configuration
        if hpc_config is None:
            hpc_config = {
                'partition': 'compute',
                'time': '01:00:00',
                'cpus': 1,
                'mem': '4G',
            }

        # Prepare directories
        hpc_workspace = f"/data/projects/scitex/users/{user.id}/workspace"
        hpc_logs = f"/data/projects/scitex/users/{user.id}/logs"

        # Create SLURM submission script
        slurm_script = f"""#!/bin/bash
#SBATCH --job-name=scitex_{user.id}
#SBATCH --partition={hpc_config['partition']}
#SBATCH --time={hpc_config['time']}
#SBATCH --cpus-per-task={hpc_config['cpus']}
#SBATCH --mem={hpc_config['mem']}
#SBATCH --output={hpc_logs}/slurm-%j.out
#SBATCH --error={hpc_logs}/slurm-%j.err

# Load Singularity module (HPC-specific)
module load singularity/3.8.0

# Execute code in Singularity container
singularity exec \\
    --contain \\
    --cleanenv \\
    --bind {hpc_workspace}:/workspace \\
    --pwd /workspace \\
    /data/projects/scitex/containers/scitex-user-workspace.sif \\
    python {script_path}
"""

        # Submit to SLURM
        try:
            result = subprocess.run(
                ["sbatch", "-"],
                input=slurm_script.encode(),
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )

            # Parse job ID from SLURM output: "Submitted batch job 12345"
            job_id = result.stdout.strip().split()[-1]

            logger.info(f"Submitted HPC job {job_id} for user {user.username}")
            return job_id

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to submit HPC job: {e.stderr}"
            logger.error(error_msg)
            raise SingularityError(error_msg)

        except subprocess.TimeoutExpired:
            error_msg = "HPC job submission timed out"
            logger.error(error_msg)
            raise SingularityError(error_msg)

    def get_hpc_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get SLURM job status

        Args:
            job_id: SLURM job ID

        Returns:
            Dict with status, runtime, node
        """
        try:
            result = subprocess.run(
                ["squeue", "-j", job_id, "-o", "%T,%M,%R"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )

            # Parse output: "RUNNING,00:15:32,node123"
            parts = result.stdout.strip().split(',')

            if len(parts) >= 3:
                status, runtime, node = parts[:3]
                return {
                    'status': status,
                    'runtime': runtime,
                    'node': node,
                    'found': True,
                }
            else:
                return {
                    'status': 'UNKNOWN',
                    'runtime': '',
                    'node': '',
                    'found': False,
                }

        except subprocess.CalledProcessError:
            # Job not found or completed
            return {
                'status': 'NOT_FOUND',
                'runtime': '',
                'node': '',
                'found': False,
            }

        except subprocess.TimeoutExpired:
            return {
                'status': 'TIMEOUT',
                'runtime': '',
                'node': '',
                'found': False,
            }


# Global instance (singleton pattern)
# Initialize on first import
try:
    singularity_manager = SingularityManager()
    logger.info("SingularityManager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize SingularityManager: {e}")
    singularity_manager = None

# EOF
