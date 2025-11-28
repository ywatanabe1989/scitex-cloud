"""
SciTeX Cloud - Project Filesystem Management Module

This module provides filesystem operations for managing user and project directories
in SciTeX Cloud. It handles project directory structures, file storage, execution
tracking, and template-based project initialization.

Public API:
-----------
- ProjectFilesystemManager: Core manager class for filesystem operations
- get_project_filesystem_manager: Factory function to get/create manager instance
- ensure_project_directory: Utility to ensure project has directory structure

Usage:
------
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
        ensure_project_directory
    )

    # Get manager for a user
    manager = get_project_filesystem_manager(user)

    # Ensure project has directory
    ensure_project_directory(project)

Module Structure:
-----------------
- core.py: Core ProjectFilesystemManager class and initialization
- project_ops.py: Project directory operations and template management
- files.py: File storage, listing, and project structure operations
- execution.py: Script execution tracking with RUNNING/FINISHED markers
- template.py: Template copying and customization logic
"""

# Import core class and factory function
from .core import (
    ProjectFilesystemManager,
    get_project_filesystem_manager,
)

# Import project operation utilities
from .project_ops import (
    ensure_project_directory,
)

# Define public API
__all__ = [
    "ProjectFilesystemManager",
    "get_project_filesystem_manager",
    "ensure_project_directory",
]
