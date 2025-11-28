"""
Real PTY Terminal for Code Workspace
WebSocket-based interactive terminal with full PTY support

Architecture:
    Django WebSocket → srun --pty → Apptainer shell → User workspace

Security:
    - SLURM handles resource isolation (CPU, memory, time)
    - Apptainer provides container isolation (no root, UID preserved)
    - Filesystem quotas at OS level
    - No Docker socket exposure

Resource Fairness:
    - SLURM fair-share scheduling
    - Per-user accounting
    - express partition for interactive (priority)
    - Configurable limits per partition

Maintainability:
    - Single resource management system (SLURM)
    - Same architecture for interactive + batch jobs
    - Dev fallback when SLURM unavailable
"""

import asyncio
import logging
import os
import pty
import select
import shutil
import subprocess
import termios
from pathlib import Path
from typing import Optional

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from apps.project_app.models import Project

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

# Base Apptainer image (shared by all users)
# For direct Apptainer execution inside Docker container
BASE_CONTAINER_PATH = getattr(
    settings,
    'SINGULARITY_IMAGE_PATH',
    '/app/singularity/scitex-user-workspace.sif'
)

# User data directory (inside Docker container)
USER_DATA_ROOT = Path(getattr(settings, 'USER_DATA_ROOT', '/app/data/users'))

# SLURM settings for interactive sessions (from env vars)
SLURM_PARTITION = os.environ.get('SCITEX_QUOTA_SLURM_INTERACTIVE_PARTITION', 'express')
SLURM_TIME_LIMIT = os.environ.get('SCITEX_QUOTA_SLURM_INTERACTIVE_TIME_LIMIT', '04:00:00')
SLURM_CPUS = int(os.environ.get('SCITEX_QUOTA_SLURM_INTERACTIVE_CPUS', 2))
SLURM_MEMORY_GB = int(os.environ.get('SCITEX_QUOTA_SLURM_INTERACTIVE_MEMORY_GB', 4))

# SLURM host paths - jobs run on compute nodes, not inside Docker
# These paths must be accessible from the SLURM compute nodes
SLURM_CONTAINER_PATH = os.environ.get(
    'SCITEX_SLURM_CONTAINER_PATH',
    '/home/ywatanabe/proj/scitex-cloud/deployment/singularity/scitex-user-workspace.sif'
)
SLURM_USER_DATA_ROOT = Path(os.environ.get(
    'SCITEX_SLURM_USER_DATA_ROOT',
    '/home/ywatanabe/proj/scitex-cloud/data/users'
))


# =============================================================================
# Terminal Consumer
# =============================================================================

class TerminalConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for PTY terminal.

    Spawns interactive shell via SLURM + Apptainer for:
    - Security: Container isolation, no root access
    - Fairness: SLURM scheduling, per-user limits
    - Consistency: Same architecture dev/prod/HPC
    """

    async def connect(self):
        """Accept WebSocket connection and spawn PTY"""
        self.user = self.scope['user']
        self.pid = None
        self.fd = None
        self.reader_task = None

        # Get project ID from query params
        query_params = dict(
            (x.split('=') for x in self.scope['query_string'].decode().split('&') if '=' in x)
        )
        project_id = query_params.get('project_id')

        if not project_id:
            await self.close()
            return

        try:
            self.project = await asyncio.to_thread(
                Project.objects.select_related('owner').get,
                id=project_id
            )

            # Check permissions
            if self.user.is_authenticated:
                has_access = (
                    self.user == self.project.owner or
                    await asyncio.to_thread(
                        lambda: self.user in self.project.collaborators.all()
                    )
                )
            else:
                # For visitors, check allocated project
                session = self.scope.get('session', {})
                visitor_project_id = session.get('visitor_project_id')
                has_access = (visitor_project_id and int(project_id) == visitor_project_id)

            if not has_access:
                await self.close()
                return

        except Project.DoesNotExist:
            await self.close()
            return

        await self.accept()
        await self.spawn_pty()

    async def spawn_pty(self):
        """Spawn PTY via SLURM + Apptainer (with dev fallback)"""
        username = self.project.owner.username
        project_slug = self.project.slug

        # User workspace paths
        user_data_dir = USER_DATA_ROOT / username
        project_dir = user_data_dir / "proj" / project_slug

        # Ensure directories exist
        await self._ensure_workspace(user_data_dir, username, project_slug)

        # Select container (priority: project → user → base)
        container_path = await asyncio.to_thread(
            self._select_container, user_data_dir, project_dir
        )

        # Check if SLURM is available
        use_slurm = await asyncio.to_thread(self._is_slurm_available)

        # Create PTY
        self.pid, self.fd = pty.fork()

        if self.pid == 0:
            # Child process
            if use_slurm:
                self._exec_slurm_shell(username, user_data_dir, project_dir, container_path)
            else:
                self._exec_direct_shell(username, user_data_dir, project_dir, container_path)
        else:
            # Parent process - read from PTY
            self.reader_task = asyncio.create_task(self.read_pty())

    def _select_container(self, user_data_dir: Path, project_dir: Path) -> str:
        """
        Select container with priority:
        1. Project-specific: ~/proj/{project}/.singularity/custom.sif
        2. User default: ~/.singularity/default.sif
        3. Base image: /app/singularity/scitex-user-workspace.sif
        """
        # Project-specific container
        project_sif = project_dir / ".singularity" / "custom.sif"
        if project_sif.exists():
            logger.info(f"Using project container: {project_sif}")
            return str(project_sif)

        # User default container
        user_sif = user_data_dir / ".singularity" / "default.sif"
        if user_sif.exists():
            logger.info(f"Using user container: {user_sif}")
            return str(user_sif)

        # Base container
        logger.info(f"Using base container: {BASE_CONTAINER_PATH}")
        return BASE_CONTAINER_PATH

    def _is_slurm_available(self) -> bool:
        """Check if SLURM is available on this system"""
        try:
            result = subprocess.run(
                ["srun", "--version"],
                capture_output=True,
                timeout=5
            )
            available = result.returncode == 0
            if available:
                logger.info("SLURM available - using srun for terminal")
            return available
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.info("SLURM not available - using direct Apptainer")
            return False

    def _exec_slurm_shell(
        self,
        username: str,
        user_data_dir: Path,
        project_dir: Path,
        container_path: str
    ):
        """Execute shell via SLURM (production mode)"""
        # Detect apptainer or singularity on host (SLURM runs on compute nodes)
        # Most HPC systems have apptainer/singularity in standard paths
        container_cmd = "apptainer"  # Assume host has apptainer

        # Convert Docker paths to host paths for SLURM
        # SLURM jobs run on compute nodes, not inside Docker
        host_user_dir = SLURM_USER_DATA_ROOT / username
        host_project_dir = host_user_dir / "proj" / self.project.slug

        # Build srun command with host paths
        cmd = [
            "srun",
            "--pty",
            f"--partition={SLURM_PARTITION}",
            f"--time={SLURM_TIME_LIMIT}",
            f"--cpus-per-task={SLURM_CPUS}",
            f"--mem={SLURM_MEMORY_GB}G",
            f"--job-name=terminal_{username}",
            f"--account=user_{username}",
            # Container execution (using host paths)
            container_cmd, "shell",
            "--containall",
            "--cleanenv",
            "--writable-tmpfs",
            "--hostname", "scitex-cloud",
            "--home", f"{host_user_dir}:/home/{username}",
            "--bind", f"{host_project_dir}:/home/{username}/proj/{self.project.slug}:rw",
            "--pwd", f"/home/{username}/proj/{self.project.slug}",
            SLURM_CONTAINER_PATH,  # Use host path to SIF
        ]

        # Environment
        env = {
            "TERM": "xterm-256color",
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "SCITEX_CLOUD": "true",
            "SCITEX_PROJECT": self.project.slug,
            "SCITEX_USER": username,
        }

        logger.info(f"Spawning SLURM terminal for {username}: srun → {container_cmd}")
        os.execvpe("srun", cmd, env)

    def _exec_direct_shell(
        self,
        username: str,
        user_data_dir: Path,
        project_dir: Path,
        container_path: str
    ):
        """Execute shell directly via Apptainer (dev fallback)"""
        container_cmd = "apptainer" if shutil.which("apptainer") else "singularity"

        if not shutil.which(container_cmd):
            # Ultimate fallback: plain bash (only for development)
            logger.warning("No container runtime - using plain bash (DEV ONLY)")
            self._exec_plain_bash(username, project_dir)
            return

        # Check if container image exists and is accessible
        if not Path(container_path).exists():
            logger.warning(f"Container image not found: {container_path} - using plain bash")
            self._exec_plain_bash(username, project_dir)
            return

        # Try to run with fakeroot for environments without user namespace support
        # Use --compat flag for better Docker compatibility (avoids proc mount issues)
        cmd = [
            container_cmd, "shell",
            "--fakeroot",  # Enables rootless execution without user namespaces
            "--compat",    # Docker-compatible mode (minimal mounts)
            "--writable-tmpfs",
            "--hostname", "scitex-cloud",
            "--home", f"{user_data_dir}:/home/{username}",
            "--bind", f"{project_dir}:/home/{username}/proj/{self.project.slug}:rw",
            "--pwd", f"/home/{username}/proj/{self.project.slug}",
            container_path,
        ]

        env = {
            "TERM": "xterm-256color",
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "SCITEX_CLOUD": "true",
            "SCITEX_PROJECT": self.project.slug,
            "SCITEX_USER": username,
        }

        logger.info(f"Spawning direct terminal for {username}: {container_cmd} --fakeroot")
        os.execvpe(container_cmd, cmd, env)

    def _exec_plain_bash(self, username: str, project_dir: Path):
        """Fallback to plain bash when container execution fails"""
        logger.warning(f"Falling back to plain bash for {username}")
        os.chdir(str(project_dir))
        env = os.environ.copy()
        env["TERM"] = "xterm-256color"
        env["SCITEX_CLOUD"] = "true"
        env["SCITEX_PROJECT"] = self.project.slug
        os.execvpe("/bin/bash", ["bash", "--login"], env)

    async def _ensure_workspace(self, user_data_dir: Path, username: str, project_slug: str):
        """Ensure user workspace exists with proper structure"""
        def setup():
            import subprocess as sp

            # Create directory structure
            user_data_dir.mkdir(parents=True, exist_ok=True)
            (user_data_dir / "proj").mkdir(exist_ok=True)
            (user_data_dir / ".singularity").mkdir(exist_ok=True)

            project_dir = user_data_dir / "proj" / project_slug
            project_dir.mkdir(exist_ok=True)

            # Create ~/proj/dotfiles as git repo (visible in project list)
            dotfiles_dir = user_data_dir / "proj" / "dotfiles"
            if not dotfiles_dir.exists():
                dotfiles_dir.mkdir()
                self._create_dotfiles_repo(dotfiles_dir, username)
                self._create_dotfiles_symlinks(user_data_dir, dotfiles_dir)
                logger.info(f"Created ~/proj/dotfiles git repo for {username}")

            logger.info(f"Workspace ready: {user_data_dir}")

        await asyncio.to_thread(setup)

    def _create_dotfiles_repo(self, dotfiles_dir: Path, username: str):
        """Create ~/.dotfiles as a git repository with default configs"""
        import subprocess as sp

        # bashrc
        (dotfiles_dir / "bashrc").write_text(f'''# SciTeX Cloud - bashrc
# Edit this file and run ./install.sh to apply changes

# Emacs-style editing
set -o emacs

# History settings
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTCONTROL=ignoredups:erasedups

# Prompt: {username}@scitex:~/path $
PS1='\\[\\033[01;32m\\]{username}@scitex\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\] \\$ '

# Aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'

# Python
alias python=python3
alias pip=pip3

# Git
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline -10'

# Auto-activate .venv if present
if [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi
''')

        # bash_profile
        (dotfiles_dir / "bash_profile").write_text('''# SciTeX Cloud - bash_profile
# Sources bashrc for login shells

if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi
''')

        # vimrc
        (dotfiles_dir / "vimrc").write_text('''" SciTeX Cloud - vimrc
" Edit this file to customize vim

syntax on
set number
set relativenumber
set expandtab
set tabstop=4
set shiftwidth=4
set autoindent
set smartindent
set hlsearch
set incsearch
set ignorecase
set smartcase
set ruler
set showcmd
set wildmenu
set backspace=indent,eol,start

" Color scheme (if available)
silent! colorscheme desert
''')

        # gitconfig
        (dotfiles_dir / "gitconfig").write_text(f'''# SciTeX Cloud - gitconfig
[user]
    name = {username}
    email = {username}@scitex.cloud

[core]
    editor = vim
    autocrlf = input

[color]
    ui = auto

[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    lg = log --oneline --graph --decorate -10

[pull]
    rebase = false

[init]
    defaultBranch = main
''')

        # tmux.conf
        (dotfiles_dir / "tmux.conf").write_text('''# SciTeX Cloud - tmux.conf

# Use Ctrl-a as prefix (like screen)
# unbind C-b
# set -g prefix C-a
# bind C-a send-prefix

# Mouse support
set -g mouse on

# 256 colors
set -g default-terminal "xterm-256color"

# Start window numbering at 1
set -g base-index 1
setw -g pane-base-index 1

# Faster escape time
set -sg escape-time 10

# History limit
set -g history-limit 10000

# Status bar
set -g status-style bg=black,fg=white
set -g status-left '[#S] '
set -g status-right '%H:%M %d-%b'
''')

        # ipython config
        ipython_dir = dotfiles_dir / "ipython"
        ipython_dir.mkdir(exist_ok=True)
        (ipython_dir / "ipython_config.py").write_text('''# SciTeX Cloud - IPython configuration
c = get_config()

# Cleaner prompts
c.TerminalInteractiveShell.banner1 = ''
c.TerminalInteractiveShell.banner2 = ''
c.TerminalInteractiveShell.confirm_exit = False

# Auto-reload modules
c.InteractiveShellApp.extensions = ['autoreload']
c.InteractiveShellApp.exec_lines = ['%autoreload 2']
''')

        # install.sh
        (dotfiles_dir / "install.sh").write_text('''#!/bin/bash
# SciTeX Cloud - Dotfiles installer
# Run this after editing dotfiles to apply changes

DOTFILES_DIR="$HOME/proj/dotfiles"

echo "Installing dotfiles..."

# Create symlinks
ln -sf "$DOTFILES_DIR/bashrc" "$HOME/.bashrc"
ln -sf "$DOTFILES_DIR/bash_profile" "$HOME/.bash_profile"
ln -sf "$DOTFILES_DIR/vimrc" "$HOME/.vimrc"
ln -sf "$DOTFILES_DIR/gitconfig" "$HOME/.gitconfig"
ln -sf "$DOTFILES_DIR/tmux.conf" "$HOME/.tmux.conf"

# IPython
mkdir -p "$HOME/.ipython/profile_default"
ln -sf "$DOTFILES_DIR/ipython/ipython_config.py" "$HOME/.ipython/profile_default/ipython_config.py"

echo "Done! Restart your shell or run: source ~/.bashrc"
''')
        (dotfiles_dir / "install.sh").chmod(0o755)

        # README
        (dotfiles_dir / "README.md").write_text(f'''# {username}'s Dotfiles

Personal configuration files for SciTeX Cloud.

## Usage

Edit any file, then run:

```bash
./install.sh
source ~/.bashrc
```

## Files

| File | Description |
|------|-------------|
| `bashrc` | Shell configuration, aliases, prompt |
| `bash_profile` | Login shell (sources bashrc) |
| `vimrc` | Vim editor settings |
| `gitconfig` | Git configuration |
| `tmux.conf` | Tmux terminal multiplexer |
| `ipython/` | IPython configuration |

## Customization

Feel free to edit any file! Your changes are version controlled.

```bash
git add -A
git commit -m "Updated bashrc aliases"
```

## Sync to Local Machine

```bash
git clone <this-repo> ~/.dotfiles
cd ~/.dotfiles
./install.sh
```
''')

        # .gitignore
        (dotfiles_dir / ".gitignore").write_text('''# OS files
.DS_Store
Thumbs.db

# Backup files
*~
*.swp
*.bak
''')

        # Initialize git repo
        try:
            sp.run(["git", "init"], cwd=dotfiles_dir, capture_output=True)
            sp.run(["git", "add", "-A"], cwd=dotfiles_dir, capture_output=True)
            sp.run(
                ["git", "commit", "-m", "Initial dotfiles setup"],
                cwd=dotfiles_dir,
                capture_output=True,
                env={**os.environ, "GIT_AUTHOR_NAME": username,
                     "GIT_AUTHOR_EMAIL": f"{username}@scitex.cloud",
                     "GIT_COMMITTER_NAME": username,
                     "GIT_COMMITTER_EMAIL": f"{username}@scitex.cloud"}
            )
        except Exception as e:
            logger.warning(f"Git init failed (non-critical): {e}")

    def _create_dotfiles_symlinks(self, user_data_dir: Path, dotfiles_dir: Path):
        """Create symlinks from ~/ to ~/proj/dotfiles/"""
        symlinks = {
            ".bashrc": "bashrc",
            ".bash_profile": "bash_profile",
            ".vimrc": "vimrc",
            ".gitconfig": "gitconfig",
            ".tmux.conf": "tmux.conf",
        }

        for target, source in symlinks.items():
            target_path = user_data_dir / target
            source_path = dotfiles_dir / source

            # Remove existing file/symlink
            if target_path.exists() or target_path.is_symlink():
                target_path.unlink()

            # Create symlink (use relative path for portability)
            target_path.symlink_to(f"proj/dotfiles/{source}")

        # IPython config (nested)
        ipython_profile = user_data_dir / ".ipython" / "profile_default"
        ipython_profile.mkdir(parents=True, exist_ok=True)
        ipython_config = ipython_profile / "ipython_config.py"
        if ipython_config.exists() or ipython_config.is_symlink():
            ipython_config.unlink()
        ipython_config.symlink_to("../../proj/dotfiles/ipython/ipython_config.py")

    async def read_pty(self):
        """Read from PTY and send to WebSocket"""
        try:
            while True:
                r, _, _ = await asyncio.to_thread(
                    select.select, [self.fd], [], [], 0.1
                )

                if r:
                    try:
                        data = await asyncio.to_thread(os.read, self.fd, 4096)
                        if data:
                            await self.send(text_data=data.decode('utf-8', errors='replace'))
                        else:
                            break  # EOF
                    except OSError:
                        break
        except Exception as e:
            logger.error(f"PTY read error: {e}")
        finally:
            await self.close()

    async def receive(self, text_data):
        """Receive data from WebSocket and write to PTY"""
        try:
            if text_data.startswith('resize:'):
                _, rows, cols = text_data.split(':')
                await self.resize_pty(int(rows), int(cols))
            else:
                await asyncio.to_thread(os.write, self.fd, text_data.encode('utf-8'))
        except Exception as e:
            logger.error(f"PTY write error: {e}")

    async def resize_pty(self, rows: int, cols: int):
        """Resize PTY window"""
        try:
            # tcsetwinsize expects a two-item tuple (rows, cols)
            await asyncio.to_thread(termios.tcsetwinsize, self.fd, (rows, cols))
        except Exception as e:
            logger.error(f"PTY resize error: {e}")

    async def disconnect(self, close_code):
        """Clean up on disconnect"""
        if self.reader_task:
            self.reader_task.cancel()

        if self.pid and self.pid > 0:
            try:
                os.kill(self.pid, 9)
            except ProcessLookupError:
                pass

        if self.fd:
            try:
                os.close(self.fd)
            except OSError:
                pass


# EOF
