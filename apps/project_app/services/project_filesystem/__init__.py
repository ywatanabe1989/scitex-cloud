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

# Import base class from core
from .core import ProjectFilesystemManager as _BaseProjectFilesystemManager

# Import extended class with all operations from project_ops
from .project_ops import (
    ProjectOpsManager,
    ensure_project_directory,
)

# Export ProjectOpsManager as ProjectFilesystemManager for backward compatibility
# This ensures all code using ProjectFilesystemManager gets the full-featured class
ProjectFilesystemManager = ProjectOpsManager


def get_project_filesystem_manager(user):
    """
    Get or create a ProjectFilesystemManager for the user.

    Returns the full-featured ProjectOpsManager with all methods.

    Args:
        user: Django User instance

    Returns:
        ProjectOpsManager instance (exported as ProjectFilesystemManager)
    """
    manager = ProjectOpsManager(user)

    # Initialize workspace if it doesn't exist
    if not manager.base_path.exists():
        manager.initialize_workspace()

    return manager


# Define public API
__all__ = [
    "ProjectFilesystemManager",
    "get_project_filesystem_manager",
    "ensure_project_directory",
]
