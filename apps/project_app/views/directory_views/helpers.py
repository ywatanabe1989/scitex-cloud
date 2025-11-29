"""
Helper Functions for Directory and File Views

This module provides shared utility functions used across directory browsing,
file viewing, and git integration views.

Modular structure:
- helpers_access.py: Access control validation
- helpers_breadcrumb.py: Breadcrumb navigation builders
- helpers_git.py: Git metadata and parsing
"""

from __future__ import annotations

# Re-export all helpers for backward compatibility
from .helpers_access import (
    check_project_access,
    get_project_filesystem,
    validate_path_security,
)
from .helpers_breadcrumb import (
    build_breadcrumbs,
    build_directory_breadcrumb,
)
from .helpers_git import (
    get_git_file_info,
    calculate_time_ago,
    parse_git_blame_porcelain,
    parse_unified_diff,
)

# Underscore-prefixed aliases for backward compatibility
_check_project_access = check_project_access
_get_project_filesystem = get_project_filesystem
_validate_path_security = validate_path_security
_build_file_breadcrumb = build_breadcrumbs
_build_directory_breadcrumb = build_directory_breadcrumb
_get_git_file_info = get_git_file_info
_calculate_time_ago = calculate_time_ago
_parse_git_blame_porcelain = parse_git_blame_porcelain
_parse_unified_diff = parse_unified_diff

__all__ = [
    # Public API
    "check_project_access",
    "get_project_filesystem",
    "validate_path_security",
    "build_breadcrumbs",
    "build_directory_breadcrumb",
    "get_git_file_info",
    "calculate_time_ago",
    "parse_git_blame_porcelain",
    "parse_unified_diff",
    # Backward compatibility aliases
    "_check_project_access",
    "_get_project_filesystem",
    "_validate_path_security",
    "_build_file_breadcrumb",
    "_build_directory_breadcrumb",
    "_get_git_file_info",
    "_calculate_time_ago",
    "_parse_git_blame_porcelain",
    "_parse_unified_diff",
]
