from django.db import models
from django.contrib.auth.models import User
import random
import string
from datetime import timedelta
from django.utils import timezone


# UserProfile model moved to apps.profile_app.models
# Import here for backwards compatibility
from apps.profile_app.models import UserProfile  # noqa

# Japanese Academic utilities moved to apps.profile_app.models
from apps.profile_app.models import JAPANESE_ACADEMIC_DOMAINS, is_japanese_academic_email  # noqa

# Organization and ResearchGroup models moved to apps.organizations_app.models
# Import here for backwards compatibility
from apps.organizations_app.models import (  # noqa
    Organization,
    OrganizationMembership,
    ResearchGroup,
    ResearchGroupMembership,
)

# GitFileStatus model moved to apps.gitea_app.models
# Import here for backwards compatibility
from apps.gitea_app.models import GitFileStatus  # noqa

# Project model moved to apps.project_app.models
# Import here for backwards compatibility
from apps.project_app.models import Project, ProjectMembership, ProjectPermission  # noqa

# Manuscript model moved to apps.writer_app.models
# Import here for backwards compatibility
from apps.writer_app.models import Manuscript  # noqa

# Document model moved to apps.document_app.models

# Project, ProjectMembership, ProjectPermission model definitions moved to apps.project_app.models
# Manuscript model definition moved to apps.writer_app.models
# Import statements at top of file provide backwards compatibility

# EmailVerification model moved to apps.auth_app.models