#!/usr/bin/env python3
"""
Sync Django users to Gitea.

This script ensures that all Django users have corresponding Gitea accounts.
It does NOT create test users - only syncs existing Django users.

This script should be run from within the Docker container:
  docker-compose -f docker-compose.dev.yml exec -T web python /app/scripts/sync_django_gitea_users.py
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.settings_dev")

# Load environment before Django setup
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

django.setup()

import requests
from django.contrib.auth import get_user_model

User = get_user_model()


def get_gitea_config():
    """Get Gitea configuration from environment."""
    gitea_url = os.environ.get("SCITEX_CLOUD_GITEA_URL_DEV", "http://127.0.0.1:3000")
    gitea_token = os.environ.get("SCITEX_CLOUD_GITEA_TOKEN_DEV", "")

    if not gitea_token:
        print("ERROR: SCITEX_CLOUD_GITEA_TOKEN_DEV not set in .env")
        sys.exit(1)

    return gitea_url, gitea_token


def check_gitea_user_exists(username, gitea_url, gitea_token):
    """Check if a user exists in Gitea."""
    try:
        headers = {"Authorization": f"token {gitea_token}"}
        response = requests.get(
            f"{gitea_url}/api/v1/users/{username}",
            headers=headers,
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"  ✗ Error checking user: {e}")
        return False


def create_gitea_user(django_user, gitea_url, gitea_token):
    """Create a Gitea user from a Django user."""
    try:
        headers = {
            "Authorization": f"token {gitea_token}",
            "Content-Type": "application/json"
        }

        # Use a default password (user should change it in Gitea)
        default_password = os.environ.get(
            "SCITEX_CLOUD_TEST_USER_PASSWORD",
            "ChangeMe123!"
        )

        data = {
            "username": django_user.username,
            "email": django_user.email,
            "password": default_password,
            "must_change_password": True,
            "send_notify": False
        }

        response = requests.post(
            f"{gitea_url}/api/v1/admin/users",
            headers=headers,
            json=data,
            timeout=5
        )

        if response.status_code == 201:
            return True, "Created successfully"
        else:
            error_msg = response.json().get("message", response.text)
            return False, f"HTTP {response.status_code}: {error_msg}"

    except Exception as e:
        return False, str(e)


def sync_users():
    """Sync all Django users to Gitea."""
    gitea_url, gitea_token = get_gitea_config()

    print("=" * 60)
    print("Django to Gitea User Sync")
    print("=" * 60)
    print(f"Gitea URL: {gitea_url}")
    print()

    # Get all active Django users
    django_users = User.objects.filter(is_active=True).order_by("username")

    if not django_users.exists():
        print("No active Django users found.")
        return

    print(f"Found {django_users.count()} active Django users")
    print()

    created_count = 0
    exists_count = 0
    failed_count = 0

    for user in django_users:
        print(f"Checking user: {user.username}")

        # Check if user exists in Gitea
        if check_gitea_user_exists(user.username, gitea_url, gitea_token):
            print(f"  ✓ Already exists in Gitea")
            exists_count += 1
            continue

        # Try to create user
        print(f"  → Creating in Gitea...")
        success, message = create_gitea_user(user, gitea_url, gitea_token)

        if success:
            print(f"  ✓ Created: {user.username}")
            created_count += 1
        else:
            print(f"  ✗ Failed: {message}")
            if "token does not have" in message.lower():
                print(f"     Note: Token needs 'write:admin' scope")
                print(f"     You can create users manually in Gitea web UI")
            failed_count += 1

    print()
    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    print(f"  Already existed: {exists_count}")
    print(f"  Created: {created_count}")
    print(f"  Failed: {failed_count}")
    print("=" * 60)

    if failed_count > 0:
        print()
        print("To create users manually:")
        print(f"1. Go to {gitea_url}")
        print("2. Login as admin (scitex)")
        print("3. Site Administration → User Accounts → Create User Account")
        print()


if __name__ == "__main__":
    try:
        sync_users()
    except KeyboardInterrupt:
        print("\nSync cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
