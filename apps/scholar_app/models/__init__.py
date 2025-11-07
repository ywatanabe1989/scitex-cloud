#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scholar App Models Package

Organized by domain for maintainability:
    - core: Core entities (papers, authors, journals)
    - search: Search and discovery
    - library: User library and collections
    - collaboration: Annotations and groups
    - bibtex: BibTeX enrichment
"""

# Core models
from .core import (
    Author,
    AuthorPaper,
    Journal,
    Topic,
    SearchIndex,
    Citation,
)

# Search models
from .search import (
    SearchQuery,
    SearchResult,
    SearchFilter,
    SavedSearch,
)

# Library models
from .library import (
    Collection,
    UserLibrary,
    LibraryExport,
    RecommendationLog,
    UserPreference,
)

# Annotation models (collaboration feature)
from .annotation import (
    Annotation,
    AnnotationReply,
    AnnotationVote,
    AnnotationTag,
    CollaborationGroup,
    GroupMembership,
)

# BibTeX models
from .bibtex import (
    BibTeXEnrichmentJob,
)

# Repository models
from .repository import (
    Repository,
    RepositoryConnection,
    Dataset,
    DatasetFile,
    DatasetVersion,
    RepositorySync,
)

# Export all models
__all__ = [
    # Core
    'Author',
    'AuthorPaper',
    'Journal',
    'Topic',
    'SearchIndex',
    'Citation',
    # Search
    'SearchQuery',
    'SearchResult',
    'SearchFilter',
    'SavedSearch',
    # Library
    'Collection',
    'UserLibrary',
    'LibraryExport',
    'RecommendationLog',
    'UserPreference',
    # Collaboration
    'Annotation',
    'AnnotationReply',
    'AnnotationVote',
    'AnnotationTag',
    'CollaborationGroup',
    'GroupMembership',
    # BibTeX
    'BibTeXEnrichmentJob',
    # Repository
    'Repository',
    'RepositoryConnection',
    'Dataset',
    'DatasetFile',
    'DatasetVersion',
    'RepositorySync',
]

# EOF
