"""
Real PTY Terminal for Code Workspace
WebSocket-based interactive terminal with full PTY support
"""

import asyncio
import logging
import os
import pty
import select
import struct
import subprocess
import termios
from pathlib import Path

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from apps.project_app.models import Project

logger = logging.getLogger(__name__)


class TerminalConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for PTY terminal
    Provides real interactive terminal with IPython, vim, etc.
    """

    async def connect(self):
        """Accept WebSocket connection and spawn PTY"""
        self.user = self.scope['user']

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

            # Check permissions (allow authenticated users and visitors with allocated project)
            if self.user.is_authenticated:
                has_access = (
                    self.user == self.project.owner or
                    await asyncio.to_thread(
                        lambda: self.user in self.project.collaborators.all()
                    )
                )
            else:
                # For anonymous users, check if this is their allocated visitor project
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

        # Spawn PTY
        await self.spawn_pty()

    async def spawn_pty(self):
        """Spawn a pseudo-terminal"""
        username = self.project.owner.username
        project_slug = self.project.slug

        # User data directory (persisted)
        user_data_dir = Path(f"/app/data/users/{username}")

        # Home directory via symlink
        home_dir = Path(f"/home/{username}")

        # Project directory under ~/proj/
        project_dir = home_dir / "proj" / project_slug

        # Ensure user home with ~/proj/ structure
        await self._ensure_user_home(home_dir, user_data_dir, username, project_slug)

        # Create PTY
        self.pid, self.fd = pty.fork()

        if self.pid == 0:
            # Child process - shell
            os.chdir(str(project_dir))

            # Set environment
            env = os.environ.copy()
            env['HOME'] = str(home_dir)
            env['USER'] = username
            env['LOGNAME'] = username
            env['PWD'] = str(project_dir)
            env['TERM'] = 'xterm-256color'
            env['HOSTNAME'] = 'scitex-cloud'

            # SciTeX Cloud Code env vars
            env['SCITEX_CLOUD_CODE_WORKSPACE'] = 'true'
            env['SCITEX_CLOUD_CODE_BACKEND'] = 'inline'
            env['SCITEX_CLOUD_CODE_SESSION_ID'] = str(self.project.id)
            env['SCITEX_CLOUD_CODE_PROJECT_ROOT'] = str(project_dir)
            env['SCITEX_CLOUD_CODE_USERNAME'] = username

            # Start bash shell with login (sources .bashrc, etc.)
            os.execvpe('/bin/bash', ['bash', '--login'], env)

        else:
            # Parent process - read from PTY and send to WebSocket
            self.reader_task = asyncio.create_task(self.read_pty())

    async def _ensure_user_home(self, home_dir: Path, user_data_dir: Path, username: str, project_slug: str):
        """Ensure user home directory exists with ~/proj/ structure via symlink"""
        def setup_home():
            # Ensure user data directory exists
            user_data_dir.mkdir(parents=True, exist_ok=True)

            # Create symlink: /home/{username} → /app/data/users/{username}
            if not home_dir.exists():
                os.symlink(str(user_data_dir), str(home_dir))
                logger.info(f"Created home symlink: {home_dir} → {user_data_dir}")

            # Create ~/proj/ directory if it doesn't exist
            proj_dir = user_data_dir / 'proj'
            proj_dir.mkdir(exist_ok=True)

            # Symlink actual project directory into ~/proj/
            project_in_proj = proj_dir / project_slug
            actual_project = Path(f"/app/data/users/{username}/{project_slug}")

            if not project_in_proj.exists() and actual_project.exists():
                # Move project to ~/proj/ if it's at old location
                if actual_project.parent == user_data_dir:
                    actual_project.rename(project_in_proj)
                    logger.info(f"Moved project to ~/proj/: {project_slug}")
                else:
                    # Create symlink if project is elsewhere
                    os.symlink(str(actual_project), str(project_in_proj))
                    logger.info(f"Linked project to ~/proj/: {project_slug}")

            # Default .bashrc if it doesn't exist
            bashrc = home_dir / '.bashrc'
            if not bashrc.exists():
                bashrc.write_text('''# SciTeX Cloud - User .bashrc
# This file is sourced for interactive non-login shells

# Emacs-style line editing (default)
set -o emacs

# Better history
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTCONTROL=ignoredups:erasedups

# Aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'

# Python aliases
alias python=python3
alias pip=pip3

# Git aliases
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'

# Custom prompt with project info
PS1='\\[\\033[01;32m\\]\\u@\\h\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\$ '

# Welcome message
echo "[SciTeX Cloud Code] Connected to terminal"
echo "Project: $(basename $(pwd))"
echo ""
''')

            # Default .bash_profile if it doesn't exist
            bash_profile = home_dir / '.bash_profile'
            if not bash_profile.exists():
                bash_profile.write_text('''# SciTeX Cloud - User .bash_profile
# This file is sourced for login shells

# Source .bashrc if it exists
if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi
''')

            # Default .vimrc if it doesn't exist
            vimrc = home_dir / '.vimrc'
            if not vimrc.exists():
                vimrc.write_text('''" SciTeX Cloud - User .vimrc
syntax on
set number
set expandtab
set tabstop=4
set shiftwidth=4
set autoindent
set smartindent
''')

            # Default .gitconfig if it doesn't exist
            gitconfig = home_dir / '.gitconfig'
            if not gitconfig.exists():
                gitconfig.write_text(f'''[user]
    name = {username}
    email = {username}@scitex.local
[core]
    editor = vim
[color]
    ui = auto
''')

            logger.info(f"User home ready: {home_dir}")

        await asyncio.to_thread(setup_home)

    async def read_pty(self):
        """Read from PTY and send to WebSocket"""
        try:
            while True:
                # Wait for data from PTY
                r, _, _ = await asyncio.to_thread(
                    select.select, [self.fd], [], [], 0.1
                )

                if r:
                    try:
                        data = await asyncio.to_thread(os.read, self.fd, 1024)
                        if data:
                            await self.send(text_data=data.decode('utf-8', errors='ignore'))
                        else:
                            # EOF
                            break
                    except OSError:
                        break

        except Exception as e:
            logger.error(f"PTY read error: {e}", exc_info=True)
        finally:
            await self.close()

    async def receive(self, text_data):
        """Receive data from WebSocket and write to PTY"""
        try:
            if text_data.startswith('resize:'):
                # Terminal resize
                _, rows, cols = text_data.split(':')
                await self.resize_pty(int(rows), int(cols))
            else:
                # User input
                await asyncio.to_thread(os.write, self.fd, text_data.encode('utf-8'))
        except Exception as e:
            logger.error(f"PTY write error: {e}", exc_info=True)

    async def resize_pty(self, rows, cols):
        """Resize PTY"""
        try:
            winsize = struct.pack('HHHH', rows, cols, 0, 0)
            await asyncio.to_thread(
                termios.tcsetwinsize, self.fd, winsize
            )
        except Exception as e:
            logger.error(f"PTY resize error: {e}", exc_info=True)

    async def disconnect(self, close_code):
        """Clean up PTY on disconnect"""
        if hasattr(self, 'reader_task'):
            self.reader_task.cancel()

        if hasattr(self, 'pid') and self.pid > 0:
            try:
                os.kill(self.pid, 9)
            except:
                pass

        if hasattr(self, 'fd'):
            try:
                os.close(self.fd)
            except:
                pass
