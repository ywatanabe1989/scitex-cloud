#!/usr/bin/env python3
"""
Check Gitea API connectivity and configuration.
This script tests the Gitea API connection and helps diagnose repository creation issues.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


def check_gitea_connection():
    """Check Gitea API connectivity and authentication."""

    # Get configuration from environment
    gitea_url = os.environ.get("SCITEX_CLOUD_GITEA_URL_DEV", "http://127.0.0.1:3000")
    gitea_token = os.environ.get("SCITEX_CLOUD_GITEA_TOKEN_DEV", "")

    print("=" * 60)
    print("Gitea API Connectivity Check")
    print("=" * 60)
    print(f"Gitea URL: {gitea_url}")
    print(f"Token configured: {'Yes' if gitea_token else 'No'}")
    print(f"Token: {gitea_token[:10]}..." if gitea_token else "Token: [Not set]")
    print()

    # Test 1: Basic connectivity
    print("Test 1: Basic connectivity...")
    try:
        response = requests.get(f"{gitea_url}/api/v1/version", timeout=5)
        print(f"✓ Connected to Gitea (HTTP {response.status_code})")
        print(f"  Version: {response.json()['version']}")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False
    print()

    # Test 2: Authentication
    print("Test 2: Authentication...")
    if not gitea_token:
        print("✗ No token configured")
        return False

    try:
        headers = {"Authorization": f"token {gitea_token}"}
        response = requests.get(f"{gitea_url}/api/v1/user", headers=headers, timeout=5)

        if response.status_code == 200:
            user_data = response.json()
            print(f"✓ Authenticated successfully")
            print(f"  User: {user_data.get('login', 'unknown')}")
            print(f"  Email: {user_data.get('email', 'unknown')}")
        else:
            print(f"✗ Authentication failed (HTTP {response.status_code})")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Authentication test failed: {e}")
        return False
    print()

    # Test 3: List user repositories
    print("Test 3: List user repositories...")
    try:
        headers = {"Authorization": f"token {gitea_token}"}
        response = requests.get(
            f"{gitea_url}/api/v1/user/repos",
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            repos = response.json()
            print(f"✓ Successfully retrieved repositories")
            print(f"  Total repositories: {len(repos)}")
            if repos:
                print("  Recent repositories:")
                for repo in repos[:5]:
                    print(f"    - {repo['full_name']}")
        else:
            print(f"✗ Failed to list repositories (HTTP {response.status_code})")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Repository listing failed: {e}")
    print()

    # Test 4: Test repository creation (with cleanup)
    print("Test 4: Test repository creation endpoint...")
    test_repo_name = "_connectivity_test"
    repo_created = False

    try:
        headers = {
            "Authorization": f"token {gitea_token}",
            "Content-Type": "application/json"
        }

        # Check if test repo exists
        response = requests.get(
            f"{gitea_url}/api/v1/repos/{user_data['login']}/{test_repo_name}",
            headers=headers,
            timeout=5
        )

        if response.status_code == 404:
            # Create test repository
            test_data = {
                "name": test_repo_name,
                "description": "Temporary test repository for connectivity check",
                "private": True,
                "auto_init": False
            }

            response = requests.post(
                f"{gitea_url}/api/v1/user/repos",
                headers=headers,
                json=test_data,
                timeout=5
            )

            if response.status_code == 201:
                print("✓ Repository creation successful")
                repo_created = True
            else:
                print(f"✗ Repository creation failed (HTTP {response.status_code})")
                print(f"  Response: {response.text}")

        elif response.status_code == 200:
            print("✓ Repository creation endpoint accessible")
            print("  (Test repository already exists, will clean up)")
            repo_created = True
        else:
            print(f"? Unexpected response (HTTP {response.status_code})")

        # Cleanup: Delete test repository
        if repo_created:
            response = requests.delete(
                f"{gitea_url}/api/v1/repos/{user_data['login']}/{test_repo_name}",
                headers=headers,
                timeout=5
            )

            if response.status_code == 204:
                print("✓ Test repository cleaned up")
            else:
                print(f"? Failed to clean up test repository (HTTP {response.status_code})")

    except Exception as e:
        print(f"✗ Repository creation test failed: {e}")
    print()

    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    print("If all tests passed, Gitea API is properly configured.")
    print("If repository creation fails in the app, check:")
    print("  1. Django settings.py GITEA_TOKEN matches .env token")
    print("  2. User has permission to create repositories")
    print("  3. Check Django logs for detailed error messages")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = check_gitea_connection()
    sys.exit(0 if success else 1)
