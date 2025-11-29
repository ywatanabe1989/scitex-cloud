"""
Remote Project Manager

Manages remote filesystem projects with TRAMP-like on-demand access via SSHFS.

Key Features:
- SSHFS mounting on-demand (lazy loading)
- Auto-unmount after timeout (privacy)
- No local data storage
- No Git support (prevents confusion)

This module has been refactored into smaller components for maintainability:
- manager.py: Main RemoteProjectManager class (coordination)
- mount_manager.py: SSHFS mount/unmount operations
- file_operations.py: File CRUD operations
- connection_manager.py: SSH connection testing
"""

# Main manager class
from .manager import RemoteProjectManager

# Component managers (for advanced usage)
from .mount_manager import MountManager
from .file_operations import FileOperations
from .connection_manager import ConnectionManager

__all__ = [
    # Main interface (backward compatible)
    "RemoteProjectManager",
    # Component managers
    "MountManager",
    "FileOperations",
    "ConnectionManager",
]
