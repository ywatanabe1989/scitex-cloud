"""
Admin configuration for scholar_app.

This module imports all admin classes from their respective modules
for backward compatibility and to register them with Django admin.
"""
from .author_journal_topic import AuthorAdmin, JournalAdmin, TopicAdmin
from .search_collection import SearchIndexAdmin, CollectionAdmin, UserLibraryAdmin
from .repository import RepositoryAdmin, RepositoryConnectionAdmin
from .dataset import DatasetAdmin, DatasetFileAdmin, DatasetVersionAdmin
from .repository_sync import RepositorySyncAdmin
from .actions import sync_datasets_with_repository, test_repository_connections

# Add actions to admin classes
DatasetAdmin.actions = [sync_datasets_with_repository]
RepositoryConnectionAdmin.actions = [test_repository_connections]

__all__ = [
    "AuthorAdmin",
    "JournalAdmin",
    "TopicAdmin",
    "SearchIndexAdmin",
    "CollectionAdmin",
    "UserLibraryAdmin",
    "RepositoryAdmin",
    "RepositoryConnectionAdmin",
    "DatasetAdmin",
    "DatasetFileAdmin",
    "DatasetVersionAdmin",
    "RepositorySyncAdmin",
    "sync_datasets_with_repository",
    "test_repository_connections",
]
