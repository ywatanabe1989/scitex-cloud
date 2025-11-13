#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scholar App API Layer

This package contains REST API components for the Scholar application.
"""

from .serializers import (
    PaperSerializer,
    CollectionSerializer,
    SavedSearchSerializer,
    AnnotationSerializer,
    RepositoryConnectionSerializer,
    DatasetMetadataSerializer,
)

from .viewsets import (
    PaperViewSet,
    CollectionViewSet,
    SavedSearchViewSet,
    AnnotationViewSet,
)

from .permissions import (
    IsOwner,
    IsOwnerOrReadOnly,
    CanAccessPaper,
    CanAccessCollection,
    CanAccessAnnotation,
)

__all__ = [
    # Serializers
    "PaperSerializer",
    "CollectionSerializer",
    "SavedSearchSerializer",
    "AnnotationSerializer",
    "RepositoryConnectionSerializer",
    "DatasetMetadataSerializer",
    # ViewSets
    "PaperViewSet",
    "CollectionViewSet",
    "SavedSearchViewSet",
    "AnnotationViewSet",
    # Permissions
    "IsOwner",
    "IsOwnerOrReadOnly",
    "CanAccessPaper",
    "CanAccessCollection",
    "CanAccessAnnotation",
]

# EOF
