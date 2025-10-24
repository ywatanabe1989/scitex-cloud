#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project App Services Layer

This package contains business logic and domain services for the Project application.

Services are organized by domain:
    - project_filesystem: Project directory and file management
    - git_service: Git operations and version control
    - ssh_service: SSH key management
    - gitea_sync_service: Gitea repository synchronization
    - anonymous_storage: Anonymous user session storage
    - filesystem_utils: File system utilities
    - email_service: Email sending and verification
"""

# Import EmailService for backward compatibility
from .email_service import EmailService

__all__ = ['EmailService']

# EOF
