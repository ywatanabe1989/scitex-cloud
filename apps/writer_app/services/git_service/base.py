"""Base Git service initialization and utilities."""

import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

import git
from git import Repo

logger = logging.getLogger(__name__)


class GitBaseMixin:
    """Base mixin for Git initialization and utilities."""

    def _init_or_load_repo(self) -> None:
        """Initialize new Git repo or load existing one."""
        try:
            # Try to load existing repo
            self.repo = Repo(self.writer_dir)
            logger.info(f"[Git] Loaded existing repository at {self.writer_dir}")
        except (git.InvalidGitRepositoryError, git.NoSuchPathError):
            # Initialize new repository
            self.repo = Repo.init(self.writer_dir)
            logger.info(f"[Git] Initialized new repository at {self.writer_dir}")

            # Configure user
            with self.repo.config_writer() as config:
                config.set_value("user", "name", self.user_name)
                config.set_value("user", "email", self.user_email)

            # Create .gitignore
            self._create_gitignore()

            # Initial commit
            self.commit("Initial commit", auto_stage=True)

    def _create_gitignore(self) -> None:
        """Create .gitignore file for writer directory."""
        gitignore_content = """# Compiled PDFs (temporary)
.preview/
*.aux
*.log
*.out
*.toc
*.synctex.gz
*.fls
*.fdb_latexmk

# System files
.DS_Store
Thumbs.db
*.swp
*.swo
*~

# IDE
.vscode/
.idea/
*.code-workspace
"""
        gitignore_path = self.writer_dir / ".gitignore"
        gitignore_path.write_text(gitignore_content)
        logger.info("[Git] Created .gitignore")

    def _get_relative_time(self, timestamp: int) -> str:
        """Convert timestamp to relative time string."""
        now = datetime.now()
        commit_time = datetime.fromtimestamp(timestamp)
        delta = now - commit_time

        if delta.days > 365:
            years = delta.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif delta.days > 30:
            months = delta.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"
