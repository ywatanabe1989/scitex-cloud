#!/usr/bin/env python3
"""Test SSH clone functionality"""

import os
import sys
import subprocess
import tempfile
import shutil
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.settings_dev")
sys.path.insert(0, "/home/ywatanabe/proj/scitex-cloud")
django.setup()

from django.contrib.auth.models import User
from apps.gitea_app.api_client import GiteaClient

# Get test user
username = "ywatanabe"
try:
    user = User.objects.get(username=username)
    print(f"✓ Found user: {username}")
except User.DoesNotExist:
    print(f"✗ User not found: {username}")
    sys.exit(1)

# Create a test repository in Gitea
print(f"\n1. Creating test repository in Gitea...")
repo_name = "test-ssh-clone"
try:
    client = GiteaClient()

    # Delete if exists
    try:
        client.delete_repository(username, repo_name)
        print(f"   Deleted existing repository: {repo_name}")
    except:
        pass

    # Create new repository
    repo = client.create_repository(
        name=repo_name,
        description="Test SSH clone functionality",
        private=False,
        auto_init=True,
        owner=username,
    )
    print(f"   ✓ Created repository: {repo.get('full_name')}")
    print(f"   Clone URL (HTTPS): {repo.get('clone_url')}")
    print(f"   Clone URL (SSH): {repo.get('ssh_url')}")
except Exception as e:
    print(f"   ✗ Failed to create repository: {e}")
    sys.exit(1)

# Test SSH clone
print(f"\n2. Testing SSH clone...")
ssh_url = f"ssh://git@127.0.0.1:2222/{username}/{repo_name}.git"
print(f"   SSH URL: {ssh_url}")

# Create temp directory for clone
temp_dir = tempfile.mkdtemp()
clone_path = os.path.join(temp_dir, repo_name)

try:
    # Get SSH key path
    ssh_key_path = f"/app/data/ssh_keys/user_{user.id}/id_rsa"
    print(f"   SSH key: {ssh_key_path}")

    # Set up SSH command with the user's key
    env = os.environ.copy()
    env["GIT_SSH_COMMAND"] = (
        f"ssh -i {ssh_key_path} "
        f"-o StrictHostKeyChecking=no "
        f"-o UserKnownHostsFile=/dev/null"
    )

    # Try to clone
    print(f"   Cloning to: {clone_path}")
    result = subprocess.run(
        ["git", "clone", ssh_url, clone_path],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode == 0:
        print(f"   ✓ SSH clone successful!")
        print(f"\n3. Verifying cloned repository...")

        # Check if .git directory exists
        if os.path.exists(os.path.join(clone_path, ".git")):
            print(f"   ✓ .git directory exists")

        # Check if README exists
        if os.path.exists(os.path.join(clone_path, "README.md")):
            print(f"   ✓ README.md exists")
            with open(os.path.join(clone_path, "README.md"), "r") as f:
                content = f.read()
                print(f"   Content preview: {content[:100]}...")

        print(f"\n✓ SSH clone test completed successfully!")
        print(f"\nSSH clone is working! Users can now clone using:")
        print(f"  git clone ssh://git@127.0.0.1:2222/{username}/{repo_name}.git")
    else:
        print(f"   ✗ SSH clone failed!")
        print(f"   Exit code: {result.returncode}")
        print(f"   STDOUT: {result.stdout}")
        print(f"   STDERR: {result.stderr}")
        sys.exit(1)

finally:
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"\n✓ Cleaned up temp directory")
