"""
Git Service for Writer Operations.

Provides visual Git interface for non-technical users:
- Auto-commit on save
- Commit history visualization
- Diff display
- Branch management

Modular structure:
- base.py: Initialization and utilities
- commit.py: Commit operations
- history.py: History and diff operations
- branch.py: Branch operations
- status.py: Status operations
"""

import logging
from pathlib import Path
from typing import Optional

from git import Repo

from .base import GitBaseMixin
from .commit import GitCommitMixin
from .history import GitHistoryMixin
from .branch import GitBranchMixin
from .status import GitStatusMixin

logger = logging.getLogger(__name__)


class GitService(
    GitBaseMixin,
    GitCommitMixin,
    GitHistoryMixin,
    GitBranchMixin,
    GitStatusMixin,
):
    """Git operations for writer manuscripts with user-friendly interface."""

    def __init__(
        self,
        writer_dir: Path,
        user_name: str = "SciTeX Writer",
        user_email: str = "writer@scitex.app",
    ):
        """
        Initialize Git service for a writer directory.

        Args:
            writer_dir: Path to writer directory (scitex/writer/)
            user_name: Git author name
            user_email: Git author email
        """
        self.writer_dir = Path(writer_dir)
        self.user_name = user_name
        self.user_email = user_email
        self.repo: Optional[Repo] = None

        # Initialize or load repository
        self._init_or_load_repo()


__all__ = ["GitService"]
