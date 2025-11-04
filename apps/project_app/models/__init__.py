"""
Project App Models
Central export point for all project-related models

Following Django organization best practices:
- Models are split into domain-specific modules
- All models are exported from this __init__.py for backward compatibility
- Existing imports like `from apps.project_app.models import Project` continue to work
"""

# Core models (Project, ProjectMembership, ProjectPermission, VisitorAllocation)
from .core import (
    Project,
    ProjectMembership,
    ProjectPermission,
    VisitorAllocation,
)

# Collaboration models (Watch, Star, Fork, Invitation)
from .collaboration import (
    ProjectWatch,
    ProjectStar,
    ProjectFork,
    ProjectInvitation,
)

# Issue models
from .issues import (
    Issue,
    IssueComment,
    IssueLabel,
    IssueMilestone,
    IssueAssignment,
    IssueEvent,
)

# Pull Request models
from .pull_requests import (
    PullRequest,
    PullRequestReview,
    PullRequestComment,
    PullRequestCommit,
    PullRequestLabel,
    PullRequestEvent,
)

# Actions models (CI/CD workflows)
from .actions import (
    Workflow,
    WorkflowRun,
    WorkflowJob,
    WorkflowStep,
)

# Explicit exports for clarity
__all__ = [
    # Core models
    'Project',
    'ProjectMembership',
    'ProjectPermission',
    'VisitorAllocation',
    # Collaboration models
    'ProjectWatch',
    'ProjectStar',
    'ProjectFork',
    'ProjectInvitation',
    # Issue models
    'Issue',
    'IssueComment',
    'IssueLabel',
    'IssueMilestone',
    'IssueAssignment',
    'IssueEvent',
    # Pull Request models
    'PullRequest',
    'PullRequestReview',
    'PullRequestComment',
    'PullRequestCommit',
    'PullRequestLabel',
    'PullRequestEvent',
    # Actions models
    'Workflow',
    'WorkflowRun',
    'WorkflowJob',
    'WorkflowStep',
]
