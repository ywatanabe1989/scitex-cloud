"""
Pull Request Git Operations

Handles commit sync and conflict detection for PRs.
"""

from __future__ import annotations

import logging
import subprocess

from django.utils import timezone

logger = logging.getLogger(__name__)


def sync_pr_commits(pr):
    """
    Sync commits from git to PR.

    Args:
        pr: PullRequest instance
    """
    try:
        from apps.project_app.services.project_filesystem import (
            get_project_filesystem_manager,
        )
        from apps.project_app.models import PullRequestCommit

        manager = get_project_filesystem_manager(pr.project.owner)
        project_path = manager.get_project_root_path(pr.project)

        if not project_path or not project_path.exists():
            return

        # Get commits between base and head
        result = subprocess.run(
            [
                "git",
                "log",
                f"{pr.target_branch}..{pr.source_branch}",
                "--format=%H|%an|%ae|%at|%s",
            ],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return

        # Parse and create commit records
        for line in result.stdout.split("\n"):
            if not line.strip():
                continue

            parts = line.split("|")
            if len(parts) >= 5:
                commit_hash, author_name, author_email, timestamp, message = parts[:5]

                # Create or update commit
                PullRequestCommit.objects.get_or_create(
                    pull_request=pr,
                    commit_hash=commit_hash,
                    defaults={
                        "commit_message": message,
                        "author_name": author_name,
                        "author_email": author_email,
                        "committed_at": timezone.datetime.fromtimestamp(int(timestamp)),
                    },
                )

    except Exception as e:
        logger.error(f"Failed to sync PR commits: {e}")


def check_pr_conflicts(pr):
    """
    Check if PR has merge conflicts.

    Args:
        pr: PullRequest instance
    """
    try:
        from apps.project_app.services.project_filesystem import (
            get_project_filesystem_manager,
        )

        manager = get_project_filesystem_manager(pr.project.owner)
        project_path = manager.get_project_root_path(pr.project)

        if not project_path or not project_path.exists():
            return

        # Try to merge (dry run)
        result = subprocess.run(
            ["git", "merge-tree", pr.target_branch, pr.source_branch],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Check for conflicts in output
        has_conflicts = "CONFLICT" in result.stdout

        # Update PR
        pr.has_conflicts = has_conflicts
        if has_conflicts:
            # Parse conflict files
            conflict_files = []
            for line in result.stdout.split("\n"):
                if "CONFLICT" in line:
                    # Extract filename from conflict message
                    parts = line.split()
                    if len(parts) > 2:
                        conflict_files.append(parts[-1])
            pr.conflict_files = conflict_files

        pr.save(update_fields=["has_conflicts", "conflict_files"])

    except Exception as e:
        logger.error(f"Failed to check PR conflicts: {e}")
