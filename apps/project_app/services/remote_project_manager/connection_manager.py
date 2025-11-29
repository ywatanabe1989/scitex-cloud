"""
Connection Management for Remote Projects

Handles SSH connection testing for remote projects.
"""

import subprocess
import logging
from pathlib import Path
from typing import Tuple, Optional
from django.utils import timezone

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages SSH connection testing for remote projects.
    """

    def __init__(self, project, config):
        """
        Initialize connection manager.

        Args:
            project: Project instance
            config: RemoteProjectConfig instance
        """
        self.project = project
        self.config = config

    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """
        Test SSH connection to remote system.

        Returns:
            (success, error_message)
        """
        ssh_key_path = self.config.remote_credential.private_key_path

        cmd = [
            "ssh",
            "-p", str(self.config.ssh_port),
            "-i", ssh_key_path,
            "-o", "StrictHostKeyChecking=accept-new",
            "-o", "ConnectTimeout=10",
            f"{self.config.ssh_username}@{self.config.ssh_host}",
            "echo 'OK'"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15,
                check=True
            )

            # Update database
            self.config.last_test_at = timezone.now()
            self.config.last_test_success = True
            self.config.save()

            return True, None

        except subprocess.CalledProcessError as e:
            error_msg = f"SSH connection failed: {e.stderr}"

            self.config.last_test_at = timezone.now()
            self.config.last_test_success = False
            self.config.save()

            return False, error_msg

        except subprocess.TimeoutExpired:
            self.config.last_test_at = timezone.now()
            self.config.last_test_success = False
            self.config.save()

            return False, "Connection timeout"

        except Exception as e:
            logger.error(f"Unexpected test error: {str(e)}")
            return False, str(e)
