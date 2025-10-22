#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scholar App Services Layer

This package contains business logic and domain services for the Scholar application.

Services are organized by domain:
    - doi_services: DOI validation and metadata retrieval
    - repository_services: Data repository integration
    - utils: Common utilities for citation formatting and parsing
"""

# Import DOI services
from .doi_services import (
    auto_assign_doi_on_publish,
    validate_and_format_doi,
    get_doi_metadata,
)

# Import repository services
from .repository_services import (
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
