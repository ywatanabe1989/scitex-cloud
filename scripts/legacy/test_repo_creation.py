#!/usr/bin/env python3
"""
Test repository creation with the same flow as the Django app.
This helps identify where the repository creation is failing.

This script creates test users and repositories, then cleans them up.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


def test_repo_creation(username="_test_user", repo_name="_test_repo", cleanup=True):
    """Test creating a repository for a specific user."""

    # Get configuration from environment
    gitea_url = os.environ.get("SCITEX_CLOUD_GITEA_URL_DEV", "http://127.0.0.1:3000")
    gitea_token = os.environ.get("SCITEX_CLOUD_GITEA_TOKEN_DEV", "")

    print("=" * 60)
    print("Repository Creation Test")
    print("=" * 60)
    print(f"Gitea URL: {gitea_url}")
    print(f"Target user: {username}")
    print(f"Repository name: {repo_name}")
    print()

    # Step 1: Check authenticated user
    print("Step 1: Check authenticated user...")
    try:
        headers = {"Authorization": f"token {gitea_token}"}
        response = requests.get(f"{gitea_url}/api/v1/user", headers=headers, timeout=5)

        if response.status_code == 200:
            auth_user = response.json()
            print(f"✓ Authenticated as: {auth_user['login']}")
        else:
            print(f"✗ Authentication failed (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    print()

    # Step 2: Check if target user exists
    print(f"Step 2: Check if user '{username}' exists...")
    try:
        response = requests.get(
            f"{gitea_url}/api/v1/users/{username}",
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            user_data = response.json()
            print(f"✓ User exists: {user_data['login']}")
        elif response.status_code == 404:
            print(f"✗ User '{username}' does not exist in Gitea")
            print("  You need to create this user in Gitea first!")
            return False
        else:
            print(f"✗ Failed to check user (HTTP {response.status_code})")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    print()

    # Step 3: Check if repository already exists
    print(f"Step 3: Check if repository '{username}/{repo_name}' exists...")
    try:
        response = requests.get(
            f"{gitea_url}/api/v1/repos/{username}/{repo_name}",
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            print(f"! Repository already exists: {username}/{repo_name}")
            print("  Skipping creation test")
            return True
        elif response.status_code == 404:
            print(f"✓ Repository does not exist (ready to create)")
        else:
            print(f"? Unexpected response (HTTP {response.status_code})")
    except Exception as e:
        print(f"✗ Failed: {e}")
    print()

    # Step 4: Attempt to create repository
    print(f"Step 4: Attempt to create repository '{username}/{repo_name}'...")
    try:
        headers = {
            "Authorization": f"token {gitea_token}",
            "Content-Type": "application/json"
        }

        data = {
            "name": repo_name,
            "description": "Test repository created via API",
            "private": False,
            "auto_init": True,
            "default_branch": "main"
        }

        # If authenticated user is the same as target user, use /user/repos
        if auth_user['login'] == username:
            endpoint = f"{gitea_url}/api/v1/user/repos"
        else:
            # If different user, need admin privileges
            endpoint = f"{gitea_url}/api/v1/admin/users/{username}/repos"

        print(f"  Endpoint: {endpoint}")

        response = requests.post(
            endpoint,
            headers=headers,
            json=data,
            timeout=5
        )

        if response.status_code == 201:
            repo_data = response.json()
            print(f"✓ Repository created successfully!")
            print(f"  Full name: {repo_data['full_name']}")
            print(f"  Clone URL: {repo_data['clone_url']}")
            print(f"  SSH URL: {repo_data['ssh_url']}")
        else:
            print(f"✗ Repository creation failed (HTTP {response.status_code})")
            print(f"  Response: {response.text}")
            return False

    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    print()

    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    print("✓ Repository creation test completed successfully")
    print(f"  Repository: {username}/{repo_name}")
    print(f"  View at: {gitea_url}/{username}/{repo_name}")
    print("=" * 60)
    print()

    # Cleanup if requested
    if cleanup:
        print("Step 5: Cleanup test resources...")

        # Delete repository
        try:
            response = requests.delete(
                f"{gitea_url}/api/v1/repos/{username}/{repo_name}",
                headers=headers,
                timeout=5
            )

            if response.status_code == 204:
                print(f"✓ Deleted test repository: {username}/{repo_name}")
            else:
                print(f"? Failed to delete repository (HTTP {response.status_code})")
        except Exception as e:
            print(f"✗ Failed to delete repository: {e}")

        # Delete user if it's a test user (starts with _test)
        if username.startswith("_test"):
            try:
                response = requests.delete(
                    f"{gitea_url}/api/v1/admin/users/{username}",
                    headers=headers,
                    timeout=5
                )

                if response.status_code == 204:
                    print(f"✓ Deleted test user: {username}")
                else:
                    print(f"? Failed to delete user (HTTP {response.status_code})")
                    print(f"  Note: User deletion requires admin token scope")
            except Exception as e:
                print(f"✗ Failed to delete user: {e}")

        print()
        print("=" * 60)
        print("Cleanup completed")
        print("=" * 60)

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Test Gitea repository creation (creates and cleans up test resources)"
    )
    parser.add_argument(
        "--username",
        default="_test_user",
        help="Target username (use _test prefix for auto-cleanup)"
    )
    parser.add_argument(
        "--repo",
        default="_test_repo",
        help="Repository name"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Skip cleanup of test resources"
    )

    args = parser.parse_args()

    success = test_repo_creation(
        args.username,
        args.repo,
        cleanup=not args.no_cleanup
    )
    sys.exit(0 if success else 1)
