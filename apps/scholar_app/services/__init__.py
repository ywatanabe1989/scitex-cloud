#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scholar App Services Layer

This package contains business logic and domain services for the Scholar application.

Services are organized by domain/feature:
    - repository: Data repository integration and DOI management
    - search: Paper search and discovery services
    - bibtex: BibTeX enrichment and processing services
    - utils: Common utilities for citation formatting and parsing
"""

# Import repository services (DOI & dataset management)
from .repository import (
    auto_assign_doi_on_publish,
    validate_and_format_doi,
    get_doi_metadata,
    sync_dataset_with_repository,
    upload_dataset_to_repository,
)

__all__ = [
    # DOI Services
    'auto_assign_doi_on_publish',
    'validate_and_format_doi',
    'get_doi_metadata',
    # Repository Services
    'sync_dataset_with_repository',
    'upload_dataset_to_repository',
]

# EOF
