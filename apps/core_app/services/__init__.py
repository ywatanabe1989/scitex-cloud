#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core App Services Layer

This package contains business logic and domain services for the Core application.

Services are organized by domain:
    - directory_service: User directory and file management
    - git_service: Git operations and version control
    - ssh_service: SSH key management
    - gitea_sync_service: Gitea repository synchronization
    - anonymous_storage: Anonymous user session storage
    - filesystem_utils: File system utilities
"""

# Import EmailService for backward compatibility through services package
from ..email_service import EmailService

__all__ = ['EmailService']

# EOF
