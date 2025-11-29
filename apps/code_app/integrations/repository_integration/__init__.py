"""
Repository integration for Code execution results.

Automatically sync code outputs, datasets, and analysis results
to research data repositories.

Module Structure:
    - integrator.py: Main CodeRepositoryIntegrator class
    - dataset_creators.py: Dataset creation mixin
    - file_handlers.py: File handling mixin
    - utils.py: Utility functions for auto-sync
"""

from .integrator import CodeRepositoryIntegrator
from .utils import auto_sync_code_completion, sync_project_data_to_repository

__all__ = [
    "CodeRepositoryIntegrator",
    "auto_sync_code_completion",
    "sync_project_data_to_repository",
]
