<!-- ---
!-- Timestamp: 2025-10-17 20:01:09
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/PERMISSIONS_SYSTEM.md
!-- --- -->

# GitLab-Style Permissions System for SciTeX

## Vision
Fine-grained access control across all modules (Scholar, Code, Viz, Writer) with organization support.

---

## Current Situation
- ✅ Projects have owner + collaborators (basic)
- ❌ No role differentiation
- ❌ No module-specific permissions
- ❌ No organization/group support

---

## GitLab Permission Levels

### Repository/Project Roles
| Role           | Can Read | Can Write | Can Delete | Can Manage | Can Admin |
|----------------|----------|-----------|------------|------------|-----------|
| **Guest**      | ✓        | ✗         | ✗          | ✗          | ✗         |
| **Reporter**   | ✓        | ✗         | ✗          | ✗          | ✗         |
| **Developer**  | ✓        | ✓         | ✗          | ✗          | ✗         |
| **Maintainer** | ✓        | ✓         | ✓          | ✓          | ✗         |
| **Owner**      | ✓        | ✓         | ✓          | ✓          | ✓         |

---

## SciTeX Adapted Roles

### Project-Level Roles

**Owner** (Creator)
- Full control over project
- Manage collaborators
- Delete project
- Transfer ownership
- Configure integrations

**Maintainer** (Senior Collaborator)
- Edit all modules (Scholar, Code, Viz, Writer)
- Compile and publish
- Invite collaborators
- Manage settings
- Cannot delete project

**Developer** (Active Collaborator)
- Edit assigned modules
- Run analyses
- Compile drafts
- View all content
- Cannot invite others

**Reporter** (Reviewer/Observer)
- Read-only access
- Add comments
- Download PDFs
- View history
- Cannot edit

**Guest** (Email invite)
- Time-limited access (7-30 days)
- Read manuscript only
- Add review comments
- Download PDF
- No module access

---

## Module-Specific Permissions

### Scholar Module
| Role | Search Papers | Import | Annotate | Organize Library | Export .bib |
|------|---------------|--------|----------|------------------|-------------|
| Guest | ✗ | ✗ | ✗ | ✗ | ✗ |
| Reporter | ✓ | ✗ | ✗ | ✗ | ✓ |
| Developer | ✓ | ✓ | ✓ | ✓ | ✓ |
| Maintainer | ✓ | ✓ | ✓ | ✓ | ✓ |
| Owner | ✓ | ✓ | ✓ | ✓ | ✓ |

### Code Module
| Role | View Code | Run | Edit | Commit | Deploy |
|------|-----------|-----|------|--------|--------|
| Guest | ✗ | ✗ | ✗ | ✗ | ✗ |
| Reporter | ✓ | ✗ | ✗ | ✗ | ✗ |
| Developer | ✓ | ✓ | ✓ | ✓ | ✗ |
| Maintainer | ✓ | ✓ | ✓ | ✓ | ✓ |
| Owner | ✓ | ✓ | ✓ | ✓ | ✓ |

### Viz Module
| Role | View Figs | Create | Edit | Delete | Export |
|------|-----------|--------|------|--------|--------|
| Guest | ✗ | ✗ | ✗ | ✗ | ✗ |
| Reporter | ✓ | ✗ | ✗ | ✗ | ✓ |
| Developer | ✓ | ✓ | ✓ | ✗ | ✓ |
| Maintainer | ✓ | ✓ | ✓ | ✓ | ✓ |
| Owner | ✓ | ✓ | ✓ | ✓ | ✓ |

### Writer Module
| Role | View | Comment | Edit | Compile | Submit to arXiv |
|------|------|---------|------|---------|-----------------|
| Guest | ✓ | ✓ | ✗ | ✗ | ✗ |
| Reporter | ✓ | ✓ | ✗ | ✓ | ✗ |
| Developer | ✓ | ✓ | ✓ | ✓ | ✗ |
| Maintainer | ✓ | ✓ | ✓ | ✓ | ✓ |
| Owner | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## Organization/Group Support

### Use Cases
1. **Research Lab** - Professor + PhD students + postdocs
2. **Collaboration** - Multi-institution project
3. **Course** - Professor + students (read-only for students)

### Organization Hierarchy
```
Organization (e.g., "Smith Lab")
├── Owners (Professor)
├── Members (PhD students, postdocs)
│   ├── Project A (role: Developer)
│   ├── Project B (role: Maintainer)
│   └── Project C (role: Reporter)
└── Settings
    ├── Default member role
    ├── Visibility (private/internal/public)
    └── Module access policies
```

### Organization Models

```python
class Organization(models.Model):
    """Research group, lab, or institution."""
    name = CharField(max_length=200)
    slug = SlugField(unique=True)
    description = TextField()
    
    # Ownership
    owner = ForeignKey(User, related_name='owned_organizations')
    
    # Members
    members = ManyToManyField(User, through='OrganizationMembership')
    
    # Settings
    visibility = CharField(choices=[
        ('private', 'Private - Members only'),
        ('internal', 'Internal - All SciTeX users'),
        ('public', 'Public - Anyone')
    ])
    default_member_role = CharField(default='developer')
    
    # Billing (future)
    plan = CharField(default='free')
    max_members = IntegerField(default=10)


class OrganizationMembership(models.Model):
    """User's membership in an organization."""
    organization = ForeignKey(Organization)
    user = ForeignKey(User)
    role = CharField(choices=[
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('member', 'Member')
    ])
    
    # Status
    is_active = BooleanField(default=True)
    joined_at = DateTimeField(auto_now_add=True)


class ProjectMember(models.Model):
    """User's role in a specific project."""
    project = ForeignKey(Project)
    user = ForeignKey(User)
    role = CharField(choices=[
        ('owner', 'Owner'),
        ('maintainer', 'Maintainer'),
        ('developer', 'Developer'),
        ('reporter', 'Reporter')
    ])
    
    # Module-specific permissions (override defaults)
    can_edit_scholar = BooleanField(default=True)
    can_edit_code = BooleanField(default=True)
    can_edit_viz = BooleanField(default=True)
    can_edit_writer = BooleanField(default=True)
    
    # Special permissions
    can_compile = BooleanField(default=True)
    can_publish = BooleanField(default=False)
    can_invite = BooleanField(default=False)
    
    invited_by = ForeignKey(User, related_name='invited_members')
    joined_at = DateTimeField(auto_now_add=True)
```

---

## Permission Checking

### Simple Decorator Pattern
```python
from functools import wraps
from django.http import HttpResponseForbidden

def require_role(min_role='developer', module=None):
    """Check if user has required role in project."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            project_id = kwargs.get('project_id')
            project = Project.objects.get(id=project_id)
            
            # Check role
            if not has_permission(request.user, project, min_role, module):
                return HttpResponseForbidden("Insufficient permissions")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage
@require_role('developer', module='writer')
def edit_manuscript(request, project_id):
    # User must be Developer+ to edit Writer
    pass

@require_role('reporter')
def view_manuscript(request, project_id):
    # Anyone Reporter+ can view
    pass
```

### Template Permission Checks
```django
{% if user|can_edit_module:project:'writer' %}
    <button>Edit</button>
{% else %}
    <span class="text-muted">Read-only</span>
{% endif %}
```

---

## Implementation Complexity

### Easy (1-2 weeks)
- ✅ Project roles (Owner, Maintainer, Developer, Reporter)
- ✅ Basic permission decorators
- ✅ Template permission checks
- ✅ Guest token system

### Medium (2-3 weeks)
- ⚠️ Module-specific permissions
- ⚠️ Organization/group support
- ⚠️ Invitation system
- ⚠️ Role management UI

### Complex (1 month)
- ⚠️ Nested organizations (Lab → Sub-group)
- ⚠️ Custom permission sets
- ⚠️ Audit logging
- ⚠️ SAML/OAuth for organizations

---

## Recommended Phased Approach

### Phase 1: Basic Roles (Week 1-2) ⭐ START HERE
```
1. Add ProjectMember model with 4 roles
2. Create permission decorators
3. Add role selection when inviting
4. Simple UI: "Invite as Developer/Reporter"
```

**Impact:** HIGH
**Effort:** LOW
**Value:** Immediate practical benefit

### Phase 2: Guest Access (Week 3) ⭐ HIGH VALUE
```
1. GuestCollaborator model
2. Token generation + email
3. Guest view (read-only)
4. Comment system
```

**Impact:** HIGH (enables professor reviews!)
**Effort:** MEDIUM
**Value:** Removes friction for reviewers

### Phase 3: Organizations (Month 2)
```
1. Organization model
2. Group-based project access
3. Organization settings
4. Billing tiers
```

**Impact:** MEDIUM (nice to have)
**Effort:** HIGH
**Value:** Unlocks team/lab workflows

---

## Database Schema

```sql
-- Add to existing Project model
ALTER TABLE project_app_project ADD COLUMN visibility VARCHAR(20) DEFAULT 'private';

-- New tables
CREATE TABLE project_members (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects,
    user_id INTEGER REFERENCES auth_user,
    role VARCHAR(20),
    can_edit_scholar BOOLEAN DEFAULT TRUE,
    can_edit_code BOOLEAN DEFAULT TRUE,
    can_edit_viz BOOLEAN DEFAULT TRUE,
    can_edit_writer BOOLEAN DEFAULT TRUE,
    invited_by_id INTEGER REFERENCES auth_user,
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(project_id, user_id)
);

CREATE TABLE guest_collaborators (
    id SERIAL PRIMARY KEY,
    manuscript_id INTEGER REFERENCES writer_app_manuscript,
    email VARCHAR(254),
    access_token VARCHAR(64) UNIQUE,
    can_comment BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## GitLab Feature Comparison

| Feature | GitLab | SciTeX (Planned) | Priority |
|---------|--------|------------------|----------|
| Project roles | ✓ | ✓ | P0 |
| Guest access | ✓ | ✓ | P0 |
| Groups/Organizations | ✓ | ✓ | P1 |
| Protected branches | ✓ | ✓ (versions) | P1 |
| Merge approval | ✓ | ✓ (review) | P2 |
| SAML/OAuth | ✓ | Future | P3 |

---

## Quick Win: Start with Project Roles

**This Week:**
1. Add `role` field to Manuscript.collaborators (through table)
2. Create 4 roles: Owner, Maintainer, Developer, Reporter
3. Add `@require_role` decorator
4. Update Writer to check permissions

**Next Week:**
1. Guest token system
2. Email invitations
3. Guest view UI

This gives you GitLab-level access control with reasonable effort!

Want me to implement Phase 1 (Basic Roles)?

<!-- EOF -->