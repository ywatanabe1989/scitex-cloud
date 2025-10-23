# Project-Gitea-Local Directory Architecture

## One-to-One Relationship Enforcement

This document describes the architecture for maintaining strict one-to-one relationships between:
1. **Django Project** (database)
2. **Gitea Repository** (version control)
3. **Local Directory** (filesystem)

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Creates Project                     │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. Django Project Created                                       │
│     - Unique slug generated                                      │
│     - Name unique per user (owner, name)                         │
│     - Database record created                                    │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Gitea Repository Created (if init_type="gitea")              │
│     - Checks if repo already exists                              │
│     - Checks if project already has repo                         │
│     - Creates repo in Gitea                                      │
│     - Links via gitea_repo_id + gitea_repo_name                  │
│     - ROLLBACK on failure: delete Gitea repo                     │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Local Directory Created                                      │
│     - Clones Gitea repo to: data/{username}/{slug}/              │
│     - Sets directory_created=True                                │
│     - Updates data_location field                                │
│     - Signal updates storage_used                                │
└─────────────────────────────────────────────────────────────────┘
```

## Database Constraints

### UniqueConstraint on Gitea Integration
```python
models.UniqueConstraint(
    fields=['owner', 'gitea_repo_name'],
    condition=models.Q(gitea_enabled=True),
    name='unique_gitea_repo_per_user'
)
```
**Purpose**: Ensures each user can only have ONE Django project per Gitea repository name

### UniqueConstraint on Gitea ID
```python
models.UniqueConstraint(
    fields=['gitea_repo_id'],
    condition=models.Q(gitea_repo_id__isnull=False),
    name='unique_gitea_repo_id'
)
```
**Purpose**: Ensures each Gitea repository (by ID) maps to exactly ONE Django project

### Unique Together on Project Name
```python
unique_together = ('name', 'owner')
```
**Purpose**: Ensures each user can only have ONE project with a given name

## Validation Flow in `create_gitea_repository()`

### Step 1: Check if Project Already Has Gitea Repo
```python
if self.gitea_enabled and self.gitea_repo_id:
    raise Exception("Project already has a Gitea repository")
```

### Step 2: Check if Another Django Project Claims This Repo
```python
existing_project = Project.objects.filter(
    owner=self.owner,
    gitea_repo_name=self.slug,
    gitea_enabled=True
).exclude(id=self.id).first()

if existing_project:
    raise Exception(f"Project '{existing_project.name}' already uses this Gitea repository")
```

### Step 3: Check if Repo Exists in Gitea
```python
try:
    existing_repo = client.get_repository(self.owner.username, self.slug)
    if existing_repo:
        raise Exception("Repository already exists in Gitea")
except Exception as e:
    if "404" not in str(e):
        raise
```

### Step 4: Create Repo and Update Django (Atomic)
```python
repo = client.create_repository(...)
self.gitea_repo_id = repo['id']
self.gitea_repo_name = repo['name']
self.gitea_enabled = True
self.save()
```

### Step 5: Rollback on Failure
```python
except Exception as e:
    client.delete_repository(self.owner.username, self.slug)
    raise
```

## Directory Structure

```
/home/ywatanabe/proj/scitex-cloud/data/
├── users/{username}/                # User workspace directory
│   ├── {project-slug}/              # Project directory (1:1 with Django + Gitea)
│   │   ├── .git/                    # Cloned from Gitea
│   │   ├── README.md
│   │   ├── scitex/                  # (Optional) SciTeX-specific metadata
│   │   │   ├── scholar/             # Bibliography, enriched .bib files
│   │   │   ├── writer/              # LaTeX compilation artifacts
│   │   │   ├── code/                # Analysis tracking
│   │   │   └── viz/                 # Visualization outputs
│   │   └── ...                      # User's project files
│   └── workspace_info.json          # User workspace metadata
├── backups/                         # System-level backups
├── db/                              # Database files
└── ssh_keys/                        # SSH key storage
```

### Design Philosophy

**Absolutely Minimal Structure:**
- Each project is a self-contained Git repository
- Direct path: `data/users/{username}/{project-slug}/`
- No shared/, temp/, or legacy directories
- Projects are completely independent

**SciTeX Feature Integration:**
- SciTeX features use `{project-slug}/scitex/` subdirectory
- Created on-demand only when needed
- Avoids namespace conflicts with user's project structure
- Examples:
  - `project/scitex/scholar/bibliography.bib` - Enriched citations
  - `project/scitex/writer/build/` - LaTeX compilation output
  - `project/scitex/code/analysis-2025-01-15.json` - Analysis metadata

**Future Expansion:**
All new SciTeX features add subdirectories under `scitex/` to maintain clean separation.

## Key Files and Methods

### Model: `apps/project_app/models.py`
- `Project.create_gitea_repository()` - Create with validation
- `Project.delete_gitea_repository()` - Delete and unlink
- `Project.cleanup_orphaned_gitea_repos()` - Find orphans
- `Project.update_storage_usage()` - Calculate directory size

### Signal: `apps/workspace_app/signals.py`
- `handle_project_directory()` - Create directory on project creation
- `cleanup_project_directory()` - Delete directory on project deletion

### Management Command: `apps/project_app/management/commands/cleanup_all_projects.py`
```bash
python manage.py cleanup_all_projects --username ywatanabe
python manage.py cleanup_all_projects --all
python manage.py cleanup_all_projects --dry-run
```

## Error Scenarios and Handling

### Scenario 1: User Tries to Create Duplicate Project Name
**Detection**: Django `unique_together` constraint
**Result**: ValidationError before any resources are created
**User Message**: "You already have a project named 'X'"

### Scenario 2: Gitea Repo Already Exists
**Detection**: `get_repository()` check in `create_gitea_repository()`
**Result**: Exception raised, Django project deleted
**User Message**: "Repository 'X' already exists in Gitea. Choose a different name."

### Scenario 3: Gitea Creation Succeeds, Clone Fails
**Detection**: `clone_gitea_to_local()` returns (False, error)
**Result**: Delete both Gitea repo and Django project
**User Message**: "Gitea repository created but clone failed: {error}"

### Scenario 4: Django Save Fails After Gitea Creation
**Detection**: Exception in `save()` after Gitea repo created
**Result**: Automatic rollback deletes Gitea repo
**User Message**: "Failed to link Gitea repository to project"

## Cleanup and Maintenance

### Finding Orphaned Resources

#### Orphaned Gitea Repositories
```python
from apps.project_app.models import Project
from django.contrib.auth.models import User

user = User.objects.get(username='ywatanabe')
result = Project.cleanup_orphaned_gitea_repos(user)
print(f"Orphaned repos: {result['orphaned']}")
```

#### Orphaned Local Directories
```bash
# Run from workspace_app signals
python manage.py shell
>>> from apps.workspace_app.signals import cleanup_orphaned_files
>>> cleanup_orphaned_files()
```

### Complete Cleanup
```bash
# Delete all projects for a user (Django + Gitea + Local)
python manage.py cleanup_all_projects --username ywatanabe

# Delete all projects for all users
python manage.py cleanup_all_projects --all

# Preview without deleting
python manage.py cleanup_all_projects --all --dry-run
```

## Future Enhancements

1. **Background Sync**: Periodic job to verify Django ↔ Gitea ↔ Local consistency
2. **Repair Command**: `python manage.py repair_project_relationships` to fix inconsistencies
3. **Audit Log**: Track all create/delete operations for debugging
4. **Soft Delete**: Add `deleted_at` field instead of hard delete for recovery
5. **Lock Mechanism**: Prevent concurrent operations on same project

## Testing Checklist

- [ ] Create project with Gitea → Check all 3 layers created
- [ ] Try duplicate name → Should fail at Django level
- [ ] Try duplicate Gitea repo → Should fail with clear message
- [ ] Delete project → All 3 layers cleaned up
- [ ] Interrupt during creation → Rollback properly
- [ ] Check constraints in DB → Verify uniqueness enforced
- [ ] Run cleanup command → Orphans removed
- [ ] Multiple users → No conflicts between users

## Migration History

- `0011_add_gitea_uniqueness_constraints.py` - Added database-level uniqueness constraints
