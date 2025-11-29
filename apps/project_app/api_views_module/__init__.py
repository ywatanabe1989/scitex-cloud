"""
API Views module for project_app

Refactored from monolithic api_views.py into focused modules:
- social.py: Watch, star, fork, stats endpoints
- branches.py: Branch switching endpoint and helper
"""

from .social import (
    api_project_watch,
    api_project_star,
    api_project_fork,
    api_project_stats,
)
from .branches import api_switch_branch, get_current_branch_from_session

__all__ = [
    # Social interactions
    "api_project_watch",
    "api_project_star",
    "api_project_fork",
    "api_project_stats",
    # Branch switching
    "api_switch_branch",
    "get_current_branch_from_session",
]
