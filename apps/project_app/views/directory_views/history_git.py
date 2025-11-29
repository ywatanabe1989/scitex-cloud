"""
History Git Operations

Git operations for file history and commit details.
"""

from __future__ import annotations

import logging
import subprocess
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def get_file_commits(project_path, file_path, author_filter=None):
    """
    Get commit history for a specific file.

    Args:
        project_path: Path to project root
        file_path: Relative file path
        author_filter: Optional author name filter

    Returns:
        list: Commit dictionaries
    """
    commits = []

    try:
        # Build git log command
        git_cmd = [
            "git", "log", "--follow",
            "--format=%H|%an|%ae|%at|%ar|%s",
            "--", file_path,
        ]

        if author_filter:
            git_cmd.insert(3, f"--author={author_filter}")

        result = subprocess.run(
            git_cmd, cwd=project_path, capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0 or not result.stdout.strip():
            return []

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            parts = line.split("|", 5)
            if len(parts) < 6:
                continue

            commit_hash, author_name, author_email, timestamp, relative_time, subject = parts

            # Get file-specific stats
            additions, deletions = _get_file_stats(project_path, commit_hash, file_path)

            commits.append({
                "hash": commit_hash,
                "short_hash": commit_hash[:7],
                "author_name": author_name,
                "author_email": author_email,
                "timestamp": int(timestamp),
                "relative_time": relative_time,
                "subject": subject,
                "additions": additions,
                "deletions": deletions,
            })

    except subprocess.TimeoutExpired:
        logger.error(f"Git log timeout for {file_path}")
    except Exception as e:
        logger.error(f"Error getting file history for {file_path}: {e}")

    return commits


def _get_file_stats(project_path, commit_hash, file_path):
    """Get additions/deletions for a file in a commit."""
    try:
        result = subprocess.run(
            ["git", "show", "--numstat", "--format=", commit_hash, "--", file_path],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0 and result.stdout.strip():
            stat_line = result.stdout.strip().split("\n")[0]
            parts = stat_line.split("\t")
            if len(parts) >= 2:
                additions = int(parts[0]) if parts[0] != "-" else 0
                deletions = int(parts[1]) if parts[1] != "-" else 0
                return additions, deletions
    except (ValueError, subprocess.TimeoutExpired):
        pass

    return 0, 0


def get_commit_info(project_path, commit_hash):
    """
    Get commit metadata.

    Returns:
        dict: Commit info or None if not found
    """
    try:
        result = subprocess.run(
            ["git", "show", "--no-patch",
             "--format=%an|%ae|%aI|%s|%b|%P|%H", commit_hash],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return None

        parts = result.stdout.strip().split("|", 6)
        return {
            "author_name": parts[0],
            "author_email": parts[1],
            "date": datetime.fromisoformat(parts[2].replace("Z", "+00:00")),
            "subject": parts[3],
            "body": parts[4] if len(parts) > 4 else "",
            "parent_hash": parts[5].split()[0] if len(parts) > 5 and parts[5] else None,
            "full_hash": parts[6] if len(parts) > 6 else commit_hash,
            "short_hash": commit_hash[:7],
        }

    except subprocess.TimeoutExpired:
        logger.error(f"Git show timeout for {commit_hash}")
    except Exception as e:
        logger.error(f"Error getting commit info: {e}")

    return None


def get_commit_files(project_path, commit_hash):
    """
    Get changed files with diffs for a commit.

    Returns:
        list: Changed file dictionaries
    """
    changed_files = []

    try:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--numstat", "-r", commit_hash],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return []

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) < 3:
                continue

            added, deleted, filepath = parts[0], parts[1], parts[2]
            diff_lines = _get_file_diff(project_path, commit_hash, filepath)

            changed_files.append({
                "path": filepath,
                "additions": added if added != "-" else 0,
                "deletions": deleted if deleted != "-" else 0,
                "diff": diff_lines,
                "extension": Path(filepath).suffix.lower(),
            })

    except subprocess.TimeoutExpired:
        logger.error(f"Git diff-tree timeout for {commit_hash}")
    except Exception as e:
        logger.error(f"Error getting commit files: {e}")

    return changed_files


def _get_file_diff(project_path, commit_hash, filepath):
    """Get parsed diff lines for a file."""
    diff_lines = []

    try:
        result = subprocess.run(
            ["git", "show", "--format=", commit_hash, "--", filepath],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return []

        for line in result.stdout.split("\n"):
            line_type = "context"
            if line.startswith("+++") or line.startswith("---"):
                line_type = "header"
            elif line.startswith("@@"):
                line_type = "hunk"
            elif line.startswith("+"):
                line_type = "addition"
            elif line.startswith("-"):
                line_type = "deletion"

            diff_lines.append({"content": line, "type": line_type})

    except subprocess.TimeoutExpired:
        pass

    return diff_lines


def get_current_branch(project_path):
    """Get current branch name."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip() or "main"
    except subprocess.TimeoutExpired:
        pass

    return "main"
