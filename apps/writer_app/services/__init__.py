"""
Writer App Services - Minimal Interface

All heavy lifting delegated to scitex.writer.Writer.
WriterService provides Django convenience wrapper.
"""

from .writer_service import WriterService

__all__ = [
    'WriterService',
]
