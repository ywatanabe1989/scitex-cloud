"""Git history and diff operations."""

import logging
from datetime import datetime
from typing import Dict, List, Optional

import git
from git import GitCommandError

logger = logging.getLogger(__name__)


class GitHistoryMixin:
    """Mixin for Git history and diff operations."""

    def get_commit_history(self, max_count: int = 50, branch: str = "HEAD") -> List[Dict]:
        """
        Get commit history for visualization.

        Args:
            max_count: Maximum number of commits to retrieve
            branch: Branch name (default: current branch)

        Returns:
            List of commit dictionaries with user-friendly info
        """
        if not self.repo:
            return []

        try:
            commits = []
            for commit in self.repo.iter_commits(branch, max_count=max_count):
                commits.append({
                    "sha": commit.hexsha,
                    "sha_short": commit.hexsha[:8],
                    "message": commit.message.strip(),
                    "author_name": commit.author.name,
                    "author_email": commit.author.email,
                    "date": datetime.fromtimestamp(commit.committed_date),
                    "date_relative": self._get_relative_time(commit.committed_date),
                    "parent_shas": [p.hexsha for p in commit.parents],
                    "stats": {
                        "files_changed": len(commit.stats.files),
                        "insertions": commit.stats.total["insertions"],
                        "deletions": commit.stats.total["deletions"],
                    },
                })

            logger.info(f"[Git] Retrieved {len(commits)} commits")
            return commits

        except GitCommandError as e:
            logger.error(f"[Git] Failed to get history: {e}")
            return []

    def get_diff(
        self,
        commit_sha: Optional[str] = None,
        compare_to: Optional[str] = None,
    ) -> Dict:
        """
        Get diff for visualization.

        Args:
            commit_sha: Commit to show diff for (default: working directory)
            compare_to: Commit to compare against (default: previous commit)

        Returns:
            Dictionary with diff information
        """
        if not self.repo:
            return {"files": [], "stats": {"files": 0, "insertions": 0, "deletions": 0}}

        try:
            if commit_sha:
                # Diff for specific commit
                commit = self.repo.commit(commit_sha)
                if compare_to:
                    diff_index = commit.diff(compare_to)
                else:
                    # Diff against parent
                    if commit.parents:
                        diff_index = commit.diff(commit.parents[0])
                    else:
                        # Initial commit
                        diff_index = commit.diff(git.NULL_TREE)
            else:
                # Diff for working directory
                diff_index = self.repo.head.commit.diff(None)

            files = []
            total_insertions = 0
            total_deletions = 0

            for diff_item in diff_index:
                # Get file path
                file_path = diff_item.a_path or diff_item.b_path

                # Get change type
                if diff_item.new_file:
                    change_type = "added"
                elif diff_item.deleted_file:
                    change_type = "deleted"
                elif diff_item.renamed_file:
                    change_type = "renamed"
                else:
                    change_type = "modified"

                # Get diff content
                try:
                    diff_text = diff_item.diff.decode("utf-8", errors="replace")
                except AttributeError:
                    diff_text = ""

                # Count insertions/deletions
                insertions = diff_text.count("\n+") - 1  # -1 for header
                deletions = diff_text.count("\n-") - 1

                files.append({
                    "path": file_path,
                    "change_type": change_type,
                    "diff": diff_text,
                    "insertions": insertions,
                    "deletions": deletions,
                })

                total_insertions += insertions
                total_deletions += deletions

            return {
                "files": files,
                "stats": {
                    "files": len(files),
                    "insertions": total_insertions,
                    "deletions": total_deletions,
                },
            }

        except (GitCommandError, ValueError) as e:
            logger.error(f"[Git] Failed to get diff: {e}")
            return {"files": [], "stats": {"files": 0, "insertions": 0, "deletions": 0}}
