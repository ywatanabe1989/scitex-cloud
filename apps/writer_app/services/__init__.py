"""
Writer App Services - Minimal Interface

All heavy lifting delegated to scitex.writer.Writer.
WriterService provides Django convenience wrapper.
"""

from .writer_service import WriterService
from .editor import DocumentService
from .compilation import CompilationService

__all__ = [
    'WriterService',
    'DocumentService',
    'CompilationService',
]
