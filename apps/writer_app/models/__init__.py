"""
Writer app models package.

Minimal model set:
- core: Manuscript (links user/project to scitex.writer.Writer)

All other functionality (sections, compilation, collaboration, version control, arxiv)
delegated to scitex.writer.Writer and exposed via REST API.
"""

# Core models
from .core import Manuscript

# Collaboration models
from .collaboration import WriterPresence

__all__ = [
    'Manuscript',
    'WriterPresence',
]
