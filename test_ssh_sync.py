#!/usr/bin/env python3
"""Test SSH key sync to Gitea"""

import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.settings_dev")
sys.path.insert(0, "/home/ywatanabe/proj/scitex-cloud")
django.setup()

from django.contrib.auth.models import User
from apps.project_app.services.ssh_service import SSHKeyManager
from apps.project_app.services.gitea_sync_service import (
    sync_ssh_key_to_gitea,
    remove_ssh_key_from_gitea,
)
from apps.gitea_app.api_client import GiteaClient

# Get test user
username = "ywatanabe"
try:
    user = User.objects.get(username=username)
    print(f"✓ Found user: {username}")
except User.DoesNotExist:
    print(f"✗ User not found: {username}")
    sys.exit(1)

# Check SSH key manager
ssh_manager = SSHKeyManager(user)
print(f"\n1. SSH Key Status:")
print(f"   Has SSH key: {ssh_manager.has_ssh_key()}")

# Generate SSH key if not exists
if not ssh_manager.has_ssh_key():
    print(f"\n2. Generating SSH key...")
    success, public_key, error = ssh_manager.get_or_create_user_key()
    if success:
        print(f"   ✓ SSH key generated")
        print(f"   Public key (first 50 chars): {public_key[:50]}...")
    else:
        print(f"   ✗ Failed to generate SSH key: {error}")
        sys.exit(1)
else:
    public_key = ssh_manager.get_public_key()
    print(f"   SSH key already exists")
    print(f"   Public key (first 50 chars): {public_key[:50]}...")

# Check user profile
from apps.accounts_app.models import UserProfile

try:
    profile = UserProfile.objects.get(user=user)
    print(f"\n3. User Profile:")
    print(f"   SSH public key: {profile.ssh_public_key[:50] if profile.ssh_public_key else 'None'}...")
    print(f"   SSH fingerprint: {profile.ssh_key_fingerprint}")
except UserProfile.DoesNotExist:
    print(f"   ✗ User profile not found")
    sys.exit(1)

# Test Gitea connection
print(f"\n4. Testing Gitea connection...")
try:
    client = GiteaClient()
    current_user = client.get_current_user()
    print(f"   ✓ Connected to Gitea as: {current_user.get('login')}")
except Exception as e:
    print(f"   ✗ Failed to connect to Gitea: {e}")
    sys.exit(1)

# List existing SSH keys in Gitea
print(f"\n5. Existing SSH keys in Gitea for user {username}:")
try:
    keys = client.list_ssh_keys(username)
    if keys:
        for key in keys:
            print(f"   - ID: {key.get('id')}, Title: {key.get('title')}")
            print(f"     Fingerprint: {key.get('fingerprint')}")
    else:
        print(f"   No SSH keys found")
except Exception as e:
    print(f"   ✗ Failed to list keys: {e}")

# Sync SSH key to Gitea
print(f"\n6. Syncing SSH key to Gitea...")
success, error = sync_ssh_key_to_gitea(user)
if success:
    print(f"   ✓ SSH key synced successfully!")
else:
    print(f"   ✗ Failed to sync: {error}")
    sys.exit(1)

# List SSH keys again to verify
print(f"\n7. Verifying sync - SSH keys in Gitea after sync:")
try:
    keys = client.list_ssh_keys(username)
    if keys:
        for key in keys:
            print(f"   - ID: {key.get('id')}, Title: {key.get('title')}")
            print(f"     Fingerprint: {key.get('fingerprint')}")
    else:
        print(f"   No SSH keys found")
except Exception as e:
    print(f"   ✗ Failed to list keys: {e}")

print(f"\n✓ SSH key sync test completed successfully!")
print(f"\nYou can now test SSH clone with:")
print(f"  git clone ssh://git@127.0.0.1:2222/{username}/default-project.git")
