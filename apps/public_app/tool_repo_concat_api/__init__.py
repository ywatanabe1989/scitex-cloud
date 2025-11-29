"""
Repository Concatenator Tool - API Endpoints

Handles cloning Git repositories and concatenating files.

Refactored from monolithic tool_repo_concat_api.py into focused modules:
- ssh_utils.py: SSH key handling and URL conversion
- url_parser.py: Git URL parsing
- clone_analyze.py: Clone and analyze endpoint
- concatenate.py: Concatenate files endpoint
- state.py: Global state management
"""

from .clone_analyze import api_clone_and_analyze
from .concatenate import api_concatenate_repo
from .ssh_utils import get_user_ssh_key, convert_https_to_ssh
from .url_parser import parse_github_url
from .state import _temp_repos

__all__ = [
    "api_clone_and_analyze",
    "api_concatenate_repo",
    "get_user_ssh_key",
    "convert_https_to_ssh",
    "parse_github_url",
    "_temp_repos",
]
