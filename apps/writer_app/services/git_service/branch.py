"""Git branch operations."""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from git import GitCommandError

logger = logging.getLogger(__name__)


class GitBranchMixin:
    """Mixin for Git branch operations."""

    def get_branches(self) -> List[Dict]:
        """
        Get list of branches for visualization.

        Returns:
            List of branch dictionaries
        """
        if not self.repo:
            return []

        try:
            branches = []
            for branch in self.repo.branches:
                is_current = branch == self.repo.active_branch

                branches.append({
                    "name": branch.name,
                    "is_current": is_current,
                    "commit_sha": branch.commit.hexsha,
                    "commit_sha_short": branch.commit.hexsha[:8],
                    "commit_message": branch.commit.message.strip(),
                    "last_commit_date": datetime.fromtimestamp(branch.commit.committed_date),
                })

            return branches

        except GitCommandError as e:
            logger.error(f"[Git] Failed to get branches: {e}")
            return []

    def create_branch(self, branch_name: str, from_commit: Optional[str] = None) -> bool:
        """
        Create a new branch.

        Args:
            branch_name: Name of new branch
            from_commit: Commit to branch from (default: current HEAD)

        Returns:
            True if successful
        """
        if not self.repo:
            return False

        try:
            if from_commit:
                start_point = self.repo.commit(from_commit)
                self.repo.create_head(branch_name, start_point)
            else:
                self.repo.create_head(branch_name)

            logger.info(f"[Git] Created branch '{branch_name}'")
            return True

        except GitCommandError as e:
            logger.error(f"[Git] Failed to create branch: {e}")
            return False

    def switch_branch(self, branch_name: str) -> bool:
        """
        Switch to a different branch.

        Args:
            branch_name: Name of branch to switch to

        Returns:
            True if successful
        """
        if not self.repo:
            return False

        try:
            # Check for uncommitted changes
            if self.repo.is_dirty():
                logger.warning("[Git] Working directory has uncommitted changes")
                return False

            # Switch branch
            self.repo.git.checkout(branch_name)
            logger.info(f"[Git] Switched to branch '{branch_name}'")
            return True

        except GitCommandError as e:
            logger.error(f"[Git] Failed to switch branch: {e}")
            return False
