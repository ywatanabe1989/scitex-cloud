"""
SSH utilities for repository cloning.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def get_user_ssh_key(user) -> Optional[Path]:
    """
    Get user's SSH private key path.

    NEW SYSTEM: SSH keys are stored in user's home directory:
    ./data/users/{username}/.ssh/

    This allows:
    - Multiple SSH keys per user
    - Standard Unix-like structure
    - User can manage their own keys (CRUD)

    Returns path to private key if exists, None otherwise.
    """
    from django.conf import settings
    from apps.project_app.services.project_filesystem import get_project_filesystem_manager

    # Get user's home directory
    manager = get_project_filesystem_manager(user)
    # manager.base_path = data/users/{username}/proj/
    # So parent = data/users/{username}/
    user_home = manager.base_path.parent
    ssh_dir = user_home / '.ssh'

    logger.error(f"DEBUG get_user_ssh_key: user={user.username}, user_id={user.id}")
    logger.error(f"DEBUG user_home={user_home}, ssh_dir={ssh_dir}")
    logger.error(f"DEBUG ssh_dir exists: {ssh_dir.exists()}")

    if ssh_dir.exists():
        contents = list(ssh_dir.iterdir())
        logger.error(f"DEBUG ssh_dir contents: {contents}")
    else:
        logger.error(f"DEBUG ssh_dir does NOT exist, creating it...")
        ssh_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(ssh_dir, 0o700)
        logger.error(f"DEBUG Created ssh_dir: {ssh_dir}")

    # Common SSH key types (in order of preference)
    ssh_key_names = ['id_ed25519', 'id_rsa', 'id_ecdsa']

    for key_name in ssh_key_names:
        key_path = ssh_dir / key_name
        logger.error(f"DEBUG checking: {key_path}, exists={key_path.exists()}")
        if key_path.exists():
            logger.error(f"DEBUG Found SSH key: {key_path}")
            return key_path

    # FALLBACK: Check old centralized location for backward compatibility
    old_ssh_dir = Path(settings.BASE_DIR) / "data" / "ssh_keys" / f"user_{user.id}"
    logger.error(f"DEBUG Fallback: checking old location {old_ssh_dir}")

    if old_ssh_dir.exists():
        for key_name in ssh_key_names:
            old_key_path = old_ssh_dir / key_name
            if old_key_path.exists():
                logger.error(f"DEBUG Found key in old location, copying to new location: {old_key_path}")
                # Copy to new location
                import shutil
                new_key_path = ssh_dir / key_name
                new_pub_path = ssh_dir / f"{key_name}.pub"
                old_pub_path = old_ssh_dir / f"{key_name}.pub"

                shutil.copy2(old_key_path, new_key_path)
                if old_pub_path.exists():
                    shutil.copy2(old_pub_path, new_pub_path)

                os.chmod(new_key_path, 0o600)
                if new_pub_path.exists():
                    os.chmod(new_pub_path, 0o644)

                logger.error(f"DEBUG Migrated SSH key to {new_key_path}")
                return new_key_path

    logger.error(f"DEBUG No SSH key found for {user.username} in {ssh_dir} or {old_ssh_dir}")
    return None


def convert_https_to_ssh(https_url: str) -> str:
    """
    Convert HTTPS Git URL to SSH format.

    Examples:
    - https://github.com/user/repo.git -> git@github.com:user/repo.git
    - https://gitlab.com/user/repo.git -> git@gitlab.com:user/repo.git
    """
    # GitHub
    pattern = r'https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?$'
    match = re.match(pattern, https_url)
    if match:
        user, repo = match.groups()
        return f'git@github.com:{user}/{repo}.git'

    # GitLab
    pattern = r'https?://gitlab\.com/([^/]+)/([^/]+?)(?:\.git)?$'
    match = re.match(pattern, https_url)
    if match:
        user, repo = match.groups()
        return f'git@gitlab.com:{user}/{repo}.git'

    # Bitbucket
    pattern = r'https?://bitbucket\.org/([^/]+)/([^/]+?)(?:\.git)?$'
    match = re.match(pattern, https_url)
    if match:
        user, repo = match.groups()
        return f'git@bitbucket.org:{user}/{repo}.git'

    return https_url
