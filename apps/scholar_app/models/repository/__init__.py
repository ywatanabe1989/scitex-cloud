"""
Repository module - Research data repository models.

Refactored from monolithic models.py into focused model files:
- repository.py: Repository model (Zenodo, Figshare, etc.)
- connection.py: RepositoryConnection model (user credentials)
- dataset.py: Dataset model (research datasets)
- dataset_file.py: DatasetFile model (individual files)
- dataset_version.py: DatasetVersion model (version tracking)
- sync.py: RepositorySync model (sync operations)
"""

from .repository import Repository
from .connection import RepositoryConnection
from .dataset import Dataset
from .dataset_file import DatasetFile
from .dataset_version import DatasetVersion
from .sync import RepositorySync

__all__ = [
    "Repository",
    "RepositoryConnection",
    "Dataset",
    "DatasetFile",
    "DatasetVersion",
    "RepositorySync",
]
