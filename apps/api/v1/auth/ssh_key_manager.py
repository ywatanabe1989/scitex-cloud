#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSH Key Management for SciTeX Cloud
Handles user SSH key generation, storage, and Git configuration
"""

import os
import subprocess
import tempfile
from pathlib import Path
from django.conf import settings
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class SSHKeyManager:
    """Manages SSH keys for users"""
    
    def __init__(self, user):
        self.user = user
        self.ssh_dir = self._get_user_ssh_directory()
        
    def _get_user_ssh_directory(self):
        """Get the SSH directory path for the user"""
        ssh_base = getattr(settings, 'SSH_KEYS_DIR', '/home/ywatanabe/proj/SciTeX-Cloud/ssh_keys')
        user_ssh_dir = Path(ssh_base) / f"user_{self.user.id}"
        user_ssh_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        return user_ssh_dir
    
    def generate_ssh_key(self, key_name="scitex_key", key_type="ed25519"):
        """Generate SSH key pair for the user"""
        try:
            private_key_path = self.ssh_dir / f"{key_name}"
            public_key_path = self.ssh_dir / f"{key_name}.pub"
            
            # Remove existing keys
            if private_key_path.exists():
                private_key_path.unlink()
            if public_key_path.exists():
                public_key_path.unlink()
            
            # Generate SSH key
            cmd = [
                'ssh-keygen',
                '-t', key_type,
                '-f', str(private_key_path),
                '-N', '',  # No passphrase
                '-C', f"{self.user.email}@scitex-cloud"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Set proper permissions
                private_key_path.chmod(0o600)
                public_key_path.chmod(0o644)
                
                logger.info(f"SSH key generated for user {self.user.username}")
                return True
            else:
                logger.error(f"SSH key generation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error generating SSH key: {str(e)}")
            return False
    
    def get_public_key(self, key_name="scitex_key"):
        """Get the public key content"""
        try:
            public_key_path = self.ssh_dir / f"{key_name}.pub"
            if public_key_path.exists():
                return public_key_path.read_text().strip()
            return None
        except Exception as e:
            logger.error(f"Error reading public key: {str(e)}")
            return None
    
    def get_private_key_path(self, key_name="scitex_key"):
        """Get the private key file path"""
        private_key_path = self.ssh_dir / f"{key_name}"
        return str(private_key_path) if private_key_path.exists() else None
    
    def has_ssh_key(self, key_name="scitex_key"):
        """Check if user has SSH keys"""
        private_key_path = self.ssh_dir / f"{key_name}"
        public_key_path = self.ssh_dir / f"{key_name}.pub"
        return private_key_path.exists() and public_key_path.exists()
    
    def create_ssh_config(self):
        """Create SSH config for Git operations"""
        try:
            ssh_config_path = self.ssh_dir / "config"
            private_key_path = self.ssh_dir / "scitex_key"
            
            if not private_key_path.exists():
                return False
            
            ssh_config_content = f"""# SciTeX Cloud SSH Configuration
Host github.com
    HostName github.com
    User git
    IdentityFile {private_key_path}
    IdentitiesOnly yes
    StrictHostKeyChecking no

Host gitlab.com
    HostName gitlab.com
    User git
    IdentityFile {private_key_path}
    IdentitiesOnly yes
    StrictHostKeyChecking no

Host bitbucket.org
    HostName bitbucket.org
    User git
    IdentityFile {private_key_path}
    IdentitiesOnly yes
    StrictHostKeyChecking no
"""
            
            ssh_config_path.write_text(ssh_config_content)
            ssh_config_path.chmod(0o600)
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating SSH config: {str(e)}")
            return False
    
    def get_git_env(self):
        """Get environment variables for Git operations with SSH"""
        ssh_config_path = self.ssh_dir / "config"
        if ssh_config_path.exists():
            return {
                'GIT_SSH_COMMAND': f'ssh -F {ssh_config_path}',
                'HOME': str(self.ssh_dir.parent)  # Point to parent of user ssh dir
            }
        return {}
    
    def test_ssh_connection(self, host="github.com"):
        """Test SSH connection to Git host"""
        try:
            env = self.get_git_env()
            cmd = ['ssh', '-T', f"git@{host}"]
            
            if env.get('GIT_SSH_COMMAND'):
                ssh_config_path = self.ssh_dir / "config"
                cmd = ['ssh', '-F', str(ssh_config_path), '-T', f"git@{host}"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, **env}
            )
            
            # GitHub returns exit code 1 for successful auth but shell access denied
            # This is expected behavior
            if host == "github.com" and "successfully authenticated" in result.stderr:
                return True
            elif result.returncode == 0:
                return True
            else:
                logger.warning(f"SSH test failed for {host}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"SSH test to {host} timed out")
            return False
        except Exception as e:
            logger.error(f"Error testing SSH connection: {str(e)}")
            return False
    
    def delete_ssh_key(self, key_name="scitex_key"):
        """Delete SSH key pair"""
        try:
            private_key_path = self.ssh_dir / f"{key_name}"
            public_key_path = self.ssh_dir / f"{key_name}.pub"
            ssh_config_path = self.ssh_dir / "config"
            
            files_deleted = 0
            for path in [private_key_path, public_key_path, ssh_config_path]:
                if path.exists():
                    path.unlink()
                    files_deleted += 1
            
            logger.info(f"Deleted {files_deleted} SSH files for user {self.user.username}")
            return files_deleted > 0
            
        except Exception as e:
            logger.error(f"Error deleting SSH key: {str(e)}")
            return False
    
    def get_ssh_key_info(self):
        """Get SSH key information"""
        if not self.has_ssh_key():
            return {
                'has_key': False,
                'public_key': None,
                'fingerprint': None,
                'created_at': None
            }
        
        try:
            public_key = self.get_public_key()
            private_key_path = self.ssh_dir / "scitex_key"
            
            # Get fingerprint
            fingerprint = None
            if public_key:
                cmd = ['ssh-keygen', '-lf', str(self.ssh_dir / "scitex_key.pub")]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    fingerprint = result.stdout.strip()
            
            # Get creation time
            created_at = None
            if private_key_path.exists():
                created_at = private_key_path.stat().st_mtime
            
            return {
                'has_key': True,
                'public_key': public_key,
                'fingerprint': fingerprint,
                'created_at': created_at
            }
            
        except Exception as e:
            logger.error(f"Error getting SSH key info: {str(e)}")
            return {
                'has_key': False,
                'public_key': None,
                'fingerprint': None,
                'created_at': None
            }


def clone_with_ssh(project, repo_url, ssh_manager):
    """Clone repository using SSH with user's SSH key"""
    try:
        import shutil
        
        # Ensure project directory exists
        project.ensure_directory()
        project_path = project.get_directory_path()
        
        if not project_path:
            logger.error("Failed to create project directory")
            return False
        
        # Clear directory if it exists
        if project_path.exists():
            shutil.rmtree(project_path)
            project_path.mkdir(parents=True, exist_ok=True)
        
        # Get SSH environment
        env = ssh_manager.get_git_env()
        clone_env = {**os.environ, **env}
        
        # Clone the repository
        clone_cmd = ['git', 'clone', repo_url, str(project_path)]
        
        logger.info(f"Cloning repository with SSH: {repo_url} to {project_path}")
        
        result = subprocess.run(
            clone_cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            env=clone_env
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully cloned repository to {project_path}")
            return True
        else:
            logger.error(f"Git clone failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Git clone operation timed out")
        return False
    except Exception as e:
        logger.error(f"Error cloning repository with SSH: {str(e)}")
        return False