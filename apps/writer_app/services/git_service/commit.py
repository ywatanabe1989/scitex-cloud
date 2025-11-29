"""Git commit operations."""

import logging
from typing import Optional

from git import GitCommandError, Actor

logger = logging.getLogger(__name__)


class GitCommitMixin:
    """Mixin for Git commit operations."""

    def commit(
        self,
        message: str,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        auto_stage: bool = True,
    ) -> Optional[str]:
        """
        Create a commit with user-friendly message.

        Args:
            message: Commit message
            author_name: Override author name
            author_email: Override author email
            auto_stage: Automatically stage all changes

        Returns:
            Commit SHA if successful, None otherwise
        """
        if not self.repo:
            logger.error("[Git] Repository not initialized")
            return None

        try:
            # Stage changes
            if auto_stage:
                self.repo.git.add(A=True)  # Add all files
                logger.info("[Git] Staged all changes")

            # Check if there are changes to commit
            if not self.repo.is_dirty() and not self.repo.untracked_files:
                logger.info("[Git] No changes to commit")
                return None

            # Create author
            author = Actor(
                author_name or self.user_name,
                author_email or self.user_email,
            )

            # Commit
            commit = self.repo.index.commit(message, author=author, committer=author)
            logger.info(f"[Git] Created commit {commit.hexsha[:8]}: {message}")

            return commit.hexsha

        except GitCommandError as e:
            logger.error(f"[Git] Failed to commit: {e}")
            return None
