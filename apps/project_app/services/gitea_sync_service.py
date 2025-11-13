#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-20 20:10:00 (ywatanabe)"
# File: ./apps/workspace_app/gitea_sync.py

"""
Gitea synchronization utilities for SciTeX Cloud

Provides helper functions for syncing Django users and projects with Gitea.
"""

import logging
from typing import Optional
from django.contrib.auth.models import User
from django.conf import settings
from apps.gitea_app.api_client import GiteaClient, GiteaAPIError

logger = logging.getLogger(__name__)


def sync_user_to_gitea(user: User, password: Optional[str] = None) -> bool:
    """
    Create or update a Gitea user account for a Django user.

    Args:
        user: Django User instance
        password: User's password (required for new user creation)

    Returns:
        True if successful, False otherwise
    """
    try:
        client = GiteaClient()

        # Check if user exists in Gitea
        try:
            gitea_user = client._request("GET", f"/users/{user.username}").json()
            logger.info(f"Gitea user already exists: {user.username}")
            return True
        except GiteaAPIError:
            # User doesn't exist, create it
            pass

        # Create new Gitea user (requires admin token)
        if not password:
            logger.warning(
                f"Cannot create Gitea user {user.username}: password required"
            )
            return False

        user_data = {
            "username": user.username,
            "email": user.email,
            "password": password,
            "full_name": user.get_full_name() or user.username,
            "send_notify": False,
            "must_change_password": False,
        }

        response = client._request("POST", "/admin/users", json=user_data)
        gitea_user = response.json()

        logger.info(f"✓ Created Gitea user: {user.username}")
        return True

    except Exception as e:
        logger.error(f"Failed to sync user {user.username} to Gitea: {e}")
        return False


def sync_all_users_to_gitea():
    """
    Sync all Django users to Gitea.

    Note: Cannot sync passwords (they're hashed in Django).
    Users will need to set Gitea passwords separately or use OAuth.
    """
    from django.contrib.auth.models import User

    users = User.objects.filter(is_active=True)
    success_count = 0
    failed_count = 0

    for user in users:
        # Try to sync (will fail for password, but creates user record)
        if sync_user_to_gitea(user):
            success_count += 1
        else:
            failed_count += 1

    logger.info(f"User sync complete: {success_count} succeeded, {failed_count} failed")
    return success_count, failed_count


def ensure_gitea_user_exists(user: User) -> bool:
    """
    Ensure a Gitea user exists before creating repositories.

    For production, we'll use OAuth so users authenticate with Gitea directly.
    For development, we check if user exists.

    Args:
        user: Django User instance

    Returns:
        True if user exists in Gitea
    """
    try:
        client = GiteaClient()
        gitea_user = client._request("GET", f"/users/{user.username}").json()
        return True
    except GiteaAPIError:
        logger.warning(f"Gitea user not found: {user.username}")
        logger.warning(f"User should register at: {settings.GITEA_URL}/user/sign_up")
        return False


# EOF
