"""
Pull Requests Feature Views

Exports all pull request-related view functions.

Refactored from monolithic detail.py into focused modules:
- detail.py: Main PR detail view
- actions.py: PR state changes (merge, close, reopen)
- reviews.py: PR feedback (reviews, comments)
- helpers.py: Shared helper functions
"""

from .list import pr_list
from .detail import pr_detail
from .actions import pr_merge, pr_close, pr_reopen
from .reviews import pr_review_submit, pr_comment_create
from .form import pr_create, pr_compare

__all__ = [
    # List
    "pr_list",
    # Detail
    "pr_detail",
    # Actions
    "pr_merge",
    "pr_close",
    "pr_reopen",
    # Reviews
    "pr_review_submit",
    "pr_comment_create",
    # Form
    "pr_create",
    "pr_compare",
]
