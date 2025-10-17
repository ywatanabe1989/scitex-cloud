# Permissions App - GitLab-Style Access Control for SciTeX

## Overview

The `permissions_app` provides fine-grained, role-based access control across all SciTeX modules (Scholar, Code, Viz, Writer). Inspired by GitLab's permission system, it enables:

- **Project-level roles** (Owner, Maintainer, Developer, Reporter, Guest)
- **Module-specific permissions** (can edit Writer but not Code)
- **Guest access** (email-based tokens for reviewers)
- **Clean, centralized permission logic**

## Quick Start

### Check Permission in View

```python
from apps.permissions_app.decorators import require_permission, require_role

# Require specific permission
@require_permission('write', 'writer')
def edit_manuscript(request, project_id):
    # User has write permission for Writer module
    pass

# Require minimum role
@require_role('developer')
def run_analysis(request, project_id):
    # User is Developer, Maintainer, or Owner
    pass
```

### Check Permission in Template

```django
{% load permission_tags %}

{# Check if user can edit Writer module #}
{% if user|can:"write:writer:project" %}
    <button class="btn btn-primary">Edit Manuscript</button>
{% else %}
    <span class="text-muted">Read-only access</span>
{% endif %}

{# Get user's role #}
{% user_role user project as role %}
<span>Your role: {{ role }}</span>
```

### Add Member to Project

```python
from apps.permissions_app.models import ProjectMember, Role

# Add as Developer
ProjectMember.objects.create(
    project=project,
    user=user,
    role=Role.DEVELOPER,
    invited_by=request.user
)

# Add as Reporter (read-only)
ProjectMember.objects.create(
    project=project,
    user=reviewer,
    role=Role.REPORTER,
    invited_by=request.user
)
```

### Invite Guest (Email-based, no account)

```python
from apps.permissions_app.models import GuestCollaborator
from django.utils import timezone
from datetime import timedelta
import secrets

# Generate secure token
token = secrets.token_urlsafe(48)

# Create guest invitation
guest = GuestCollaborator.objects.create(
    manuscript=manuscript,
    email='professor@university.edu',
    access_token=token,
    invited_by=request.user,
    expires_at=timezone.now() + timedelta(days=7)
)

# Send email with link
send_mail(
    subject=f'Review invitation: {manuscript.title}',
    message=f'Access: https://scitex.ai/writer/guest/{token}/',
    recipient_list=[guest.email]
)
```

---

## Roles

### Role Hierarchy (High to Low)

| Role | Level | Read | Write | Delete | Manage | Admin |
|------|-------|------|-------|--------|--------|-------|
| **Owner** | 4 | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Maintainer** | 3 | ✓ | ✓ | ✓ | ✓ | ✗ |
| **Developer** | 2 | ✓ | ✓ | ✗ | ✗ | ✗ |
| **Reporter** | 1 | ✓ | ✗ | ✗ | ✗ | ✗ |
| **Guest** | 0 | ✓* | ✗ | ✗ | ✗ | ✗ |

*Guest: Limited read access via token

### Role Descriptions

**Owner (Project Creator)**
- Full control over project
- Can delete project
- Can transfer ownership
- Can manage all settings
- Default: Project creator

**Maintainer (Senior Collaborator)**
- Can edit all modules
- Can delete resources
- Can invite collaborators
- Can manage project settings
- Cannot delete project
- Use for: Lab managers, co-PIs

**Developer (Active Collaborator)**
- Can edit assigned modules
- Can run analyses & compile
- Cannot delete resources
- Cannot invite others
- Use for: PhD students, postdocs, collaborators

**Reporter (Observer/Reviewer)**
- Read-only access
- Can comment
- Can download exports
- Can compile (view results)
- Cannot edit anything
- Use for: Committee members, reviewers, auditors

**Guest (External Reviewer)**
- Time-limited access (default: 7 days)
- Email-based (no account needed)
- Can view manuscript
- Can add comments
- Cannot access other modules
- Use for: External professors, journal reviewers

---

## Module-Specific Permissions

Each member can have different permissions per module:

```python
member = ProjectMember.objects.create(
    project=project,
    user=student,
    role=Role.DEVELOPER,
    can_edit_scholar=True,   # Can search/import papers
    can_edit_code=True,      # Can write code
    can_edit_viz=False,      # Cannot edit visualizations
    can_edit_writer=False    # Cannot edit manuscript
)
```

**Use cases:**
- Student can run code but not write paper
- Collaborator can edit methods section but not results
- RA can collect data but not analyze

---

## API Reference

### PermissionService

**Location:** `apps/permissions_app/services.py`

```python
from apps.permissions_app.services import PermissionService

# Get user's role
role = PermissionService.get_user_role(user, project)
# Returns: 'owner', 'maintainer', 'developer', 'reporter', 'guest', or None

# Check specific permission
can_write = PermissionService.can_write(user, project, module='writer')
# Returns: True/False

# Universal check
has_perm = PermissionService.check_permission(
    user=user,
    project=project,
    action='write',  # or 'read', 'delete', 'manage', 'admin', 'invite', 'compile'
    module='writer'  # optional: 'scholar', 'code', 'viz', 'writer'
)
```

### Available Methods

```python
PermissionService.can_read(user, project) -> bool
PermissionService.can_write(user, project, module=None) -> bool
PermissionService.can_delete(user, project) -> bool
PermissionService.can_manage(user, project) -> bool
PermissionService.can_admin(user, project) -> bool
PermissionService.can_invite(user, project) -> bool
PermissionService.can_compile(user, project) -> bool
PermissionService.check_permission(user, project, action, module=None) -> bool
```

---

## Decorators

### @require_permission

**Check specific action:**

```python
from apps.permissions_app.decorators import require_permission

@require_permission('write', 'writer')
def edit_manuscript(request, project_id):
    # project available as request.project
    pass

@require_permission('delete')
def delete_analysis(request, project_id):
    # Requires Maintainer or Owner
    pass

@require_permission('manage')
def update_settings(request, project_id):
    # Requires Maintainer or Owner
    pass
```

### @require_role

**Check minimum role:**

```python
from apps.permissions_app.decorators import require_role

@require_role('developer')
def advanced_feature(request, project_id):
    # User is Developer, Maintainer, or Owner
    # request.user_role contains actual role
    pass

@require_role('reporter')
def view_results(request, project_id):
    # Anyone (Reporter+) can view
    pass
```

---

## Template Tags

**Load tags:**
```django
{% load permission_tags %}
```

### Filter: `can`

```django
{# Check permission with project context #}
{% if user|can:"write:writer:project" %}
    <button>Edit</button>
{% endif %}

{# Different actions #}
{% if user|can:"delete::project" %}
    <button class="btn-danger">Delete</button>
{% endif %}

{% if user|can:"invite::project" %}
    <button>Invite Collaborator</button>
{% endif %}
```

### Tag: `user_role`

```django
{% user_role user project as role %}

{% if role == 'owner' %}
    <span class="badge badge-danger">Owner</span>
{% elif role == 'maintainer' %}
    <span class="badge badge-warning">Maintainer</span>
{% elif role == 'developer' %}
    <span class="badge badge-primary">Developer</span>
{% elif role == 'reporter' %}
    <span class="badge badge-info">Reporter</span>
{% endif %}
```

---

## Testing

### Run Migrations
```bash
python manage.py makemigrations permissions_app
python manage.py migrate
```

### Test Permission Checks
```python
from apps.permissions_app.services import PermissionService
from apps.permissions_app.models import ProjectMember, Role

# Create member
member = ProjectMember.objects.create(
    project=project,
    user=user,
    role=Role.DEVELOPER
)

# Check permissions
assert PermissionService.can_read(user, project) == True
assert PermissionService.can_write(user, project, 'writer') == True
assert PermissionService.can_delete(user, project) == False
assert PermissionService.can_admin(user, project) == False
```

---

## Architecture

**Why It Stays Clean:**

✅ **Single source of truth** - All logic in `services.py`
✅ **Simple decorators** - Easy to read and use
✅ **No scattered checks** - Enforced via decorators
✅ **Template integration** - Clean Django template syntax
✅ **Only ~300 lines** - Not a massive framework

**Maintainability:**
- Add new role? Update Role enum
- Change permission logic? Edit PermissionService
- Add new action? Add one method

---

## Related Documentation

- `/TODOS/PERMISSIONS_SYSTEM.md` - Full design document
- `/TODOS/GUEST_COLLABORATORS.md` - Guest access design
- `/TODOS/WRITER.md` - Writer module roadmap

---

**Principle:** Keep it simple, keep it centralized, keep it clean. 🎯
