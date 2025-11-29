"""Git status operations."""

import logging
from typing import Dict

from git import GitCommandError

logger = logging.getLogger(__name__)


class GitStatusMixin:
    """Mixin for Git status operations."""

    def get_status(self) -> Dict:
        """
        Get current repository status.

        Returns:
            Dictionary with status information
        """
        if not self.repo:
            return {"clean": True, "files": []}

        try:
            status = {
                "branch": self.repo.active_branch.name,
                "clean": not self.repo.is_dirty(),
                "files": {
                    "modified": [item.a_path for item in self.repo.index.diff(None)],
                    "staged": [item.a_path for item in self.repo.index.diff("HEAD")],
                    "untracked": self.repo.untracked_files,
                },
            }
            return status

        except GitCommandError as e:
            logger.error(f"[Git] Failed to get status: {e}")
            return {"clean": True, "files": []}
