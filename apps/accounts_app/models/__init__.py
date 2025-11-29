"""
Accounts App Models Package

Exports all account-related models for backward compatibility.
"""

from .academic import JAPANESE_ACADEMIC_DOMAINS, is_japanese_academic_email
from .profile import UserProfile
from .ssh_key import WorkspaceSSHKey
from .api_key import APIKey

__all__ = [
    # Academic utilities
    "JAPANESE_ACADEMIC_DOMAINS",
    "is_japanese_academic_email",
    # Models
    "UserProfile",
    "WorkspaceSSHKey",
    "APIKey",
]
