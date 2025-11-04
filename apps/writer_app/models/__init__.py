"""Writer app models - Feature-based organization."""

# Editor models
from .editor.document import Manuscript
from .editor.section import ManuscriptSection

# Compilation models
from .compilation.compilation import CompilationJob, AIAssistanceLog

# Version control models
from .version_control.version import (
    ManuscriptVersion,
    ManuscriptBranch,
    DiffResult,
    MergeRequest,
)

# arXiv integration models
from .arxiv.submission import (
    ArxivAccount,
    ArxivCategory,
    ArxivSubmission,
    ArxivSubmissionHistory,
    ArxivValidationResult,
    ArxivApiResponse,
)

# Collaboration models
from .collaboration.session import WriterPresence, CollaborativeSession

# Legacy models (TODO: move to proper feature dirs)
from .core_old import Citation, Figure, Table

__all__ = [
    # Editor
    'Manuscript',
    'ManuscriptSection',
    # Compilation
    'CompilationJob',
    'AIAssistanceLog',
    # Version Control
    'ManuscriptVersion',
    'ManuscriptBranch',
    'DiffResult',
    'MergeRequest',
    # arXiv
    'ArxivAccount',
    'ArxivCategory',
    'ArxivSubmission',
    'ArxivSubmissionHistory',
    'ArxivValidationResult',
    'ArxivApiResponse',
    # Collaboration
    'WriterPresence',
    'CollaborativeSession',
    # Legacy (TODO: refactor)
    'Citation',
    'Figure',
    'Table',
]
