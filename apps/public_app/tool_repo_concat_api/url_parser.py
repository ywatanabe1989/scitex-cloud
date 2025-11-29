"""
URL parsing utilities for Git repository URLs.
"""

from __future__ import annotations

import re
from typing import Optional, Tuple


def parse_github_url(url: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Parse GitHub URL to extract repo URL, branch, and subdirectory.

    Examples:
    - https://github.com/user/repo -> (https://github.com/user/repo.git, None, None)
    - https://github.com/user/repo/tree/main/path -> (https://github.com/user/repo.git, main, path)
    - git@github.com:user/repo.git -> (git@github.com:user/repo.git, None, None)

    Returns: (git_url, branch, subdirectory)
    """
    # Handle SSH URLs
    if url.startswith('git@'):
        return (url, None, None)

    # Handle HTTPS URLs with subdirectory
    # Pattern: https://github.com/user/repo/tree/branch/path/to/dir
    pattern = r'https?://github\.com/([^/]+)/([^/]+)(?:/tree/([^/]+)/(.+))?'
    match = re.match(pattern, url)

    if match:
        user, repo, branch, subdir = match.groups()
        # Remove .git if present
        repo = repo.replace('.git', '')
        git_url = f'https://github.com/{user}/{repo}.git'
        return (git_url, branch, subdir)

    # GitLab pattern
    pattern_gitlab = r'https?://gitlab\.com/([^/]+)/([^/]+)(?:/-/tree/([^/]+)/(.+))?'
    match = re.match(pattern_gitlab, url)
    if match:
        user, repo, branch, subdir = match.groups()
        repo = repo.replace('.git', '')
        git_url = f'https://gitlab.com/{user}/{repo}.git'
        return (git_url, branch, subdir)

    # Simple URL without subdirectory
    if url.endswith('.git'):
        return (url, None, None)
    else:
        return (url + '.git' if not url.endswith('.git') else url, None, None)
