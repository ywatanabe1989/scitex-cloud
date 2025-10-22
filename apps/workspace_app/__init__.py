"""
Core app for SciTeX
Central functionality for projects, authentication, and file management
"""

# Lazy import for backward compatibility
def __getattr__(name):
    if name == 'EmailService':
        from .services import EmailService
        return EmailService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = []
