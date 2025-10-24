"""
Writer app models package.

Organized by domain:
- core: DocumentTemplate, Manuscript, ManuscriptSection, Figure, Table, Citation
- compilation: CompilationJob, AIAssistanceLog
- collaboration: CollaborativeSession, DocumentChange
- version_control: ManuscriptVersion, ManuscriptBranch, DiffResult, MergeRequest
- arxiv: ArxivAccount, ArxivCategory, ArxivSubmission, ArxivSubmissionHistory, ArxivValidationResult, ArxivApiResponse
"""

# Core models
from .core import (
    DocumentTemplate,
    Manuscript,
    ManuscriptSection,
    Figure,
    Table,
    Citation,
)

# Compilation models
from .compilation import (
    CompilationJob,
    AIAssistanceLog,
)

# Collaboration models
from .collaboration import (
    CollaborativeSession,
    DocumentChange,
)

# Version control models
from .version_control import (
    ManuscriptVersion,
    ManuscriptBranch,
    DiffResult,
    MergeRequest,
)

# arXiv integration models
from .arxiv import (
    ArxivAccount,
    ArxivCategory,
    ArxivSubmission,
    ArxivSubmissionHistory,
    ArxivValidationResult,
    ArxivApiResponse,
)

__all__ = [
    # Core
    'DocumentTemplate',
    'Manuscript',
    'ManuscriptSection',
    'Figure',
    'Table',
    'Citation',
    # Compilation
    'CompilationJob',
    'AIAssistanceLog',
    # Collaboration
    'CollaborativeSession',
    'DocumentChange',
    # Version control
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
]
