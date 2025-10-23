# SciTeX Integration Guide

This document explains how Django `Project` model integrates with `scitex.project` package.

## Overview

The integration allows Django projects to have portable, self-contained metadata that works independently of the database.

```
┌─────────────────────────────────────────────────┐
│         Django Project (Database)               │
│  - id, owner, created_at, updated_at            │
│  - scitex_project_id (links to scitex)          │
│  - local_path (directory location)              │
└─────────────────────────────────────────────────┘
                   ▲ ▼
          Adapter Methods (sync, convert)
                   ▲ ▼
┌─────────────────────────────────────────────────┐
│      SciTeXProject (scitex/.metadata/)          │
│  - Pure Python, no Django dependency            │
│  - Portable across systems                      │
│  - JSON-based metadata storage                  │
└─────────────────────────────────────────────────┘
```

## New Fields Added

### `scitex_project_id`
- Type: `CharField(max_length=100, unique=True, null=True, blank=True)`
- Purpose: Links Django project to scitex/.metadata/
- Unique identifier from scitex.project package (e.g., `"proj_abc123xyz"`)

### `local_path`
- Type: `CharField(max_length=500, blank=True)`
- Purpose: Path to local project directory
- Example: `/home/ywatanabe/proj/scitex-cloud/data/users/ywatanabe/neural-decoding`

## New Methods Added

### `get_local_path() -> Path`
Get Path object for local project directory.

```python
project = Project.objects.get(slug='neural-decoding')
path = project.get_local_path()
# Returns: Path('/path/to/data/users/ywatanabe/neural-decoding')
```

### `has_scitex_metadata() -> bool`
Check if project has scitex/.metadata/ directory.

```python
if project.has_scitex_metadata():
    print("Project has scitex metadata")
```

### `to_scitex_project() -> SciTeXProject`
Convert Django model to SciTeXProject dataclass.

```python
scitex_proj = project.to_scitex_project()
print(scitex_proj.name)
print(scitex_proj.project_id)
```

### `initialize_scitex_metadata() -> SciTeXProject`
Initialize scitex/.metadata/ for existing Django project.

```python
# For existing projects without scitex metadata
scitex_proj = project.initialize_scitex_metadata()
```

### `sync_from_scitex()`
Update Django model from scitex/.metadata/.

```python
# If user edited metadata locally
project.sync_from_scitex()
```

### `sync_to_scitex()`
Update scitex/.metadata/ from Django model.

```python
# After updating Django project via web UI
project.description = "Updated description"
project.save()
project.sync_to_scitex()
```

### `update_storage_from_scitex() -> int`
Calculate storage using scitex.project.

```python
size = project.update_storage_from_scitex()
print(f"Storage: {size / 1024**2:.2f} MB")
```

### `validate_name_using_scitex(name)` (classmethod)
Validate project name using scitex.project validator.

```python
try:
    Project.validate_name_using_scitex("my-project")
except ValidationError as e:
    print(f"Invalid name: {e}")
```

## Migration Process

### Step 1: Run Database Migration

```bash
cd /home/ywatanabe/proj/scitex-cloud
python manage.py migrate project_app
```

This adds `scitex_project_id` and `local_path` fields to database.

### Step 2: Migrate Existing Projects

```bash
# Dry run (see what will happen)
python manage.py migrate_to_scitex --dry-run

# Migrate all projects
python manage.py migrate_to_scitex

# Migrate specific user's projects
python manage.py migrate_to_scitex --username ywatanabe

# Migrate specific project
python manage.py migrate_to_scitex --project-id 42

# Force migration even if directory doesn't exist
python manage.py migrate_to_scitex --force
```

### Step 3: Verify Migration

```bash
python manage.py shell
```

```python
from apps.project_app.models import Project

# Check if projects have scitex metadata
for project in Project.objects.all():
    if project.has_scitex_metadata():
        print(f"✓ {project.owner.username}/{project.slug}")
        scitex = project.to_scitex_project()
        print(f"  SciTeX ID: {scitex.project_id}")
    else:
        print(f"✗ {project.owner.username}/{project.slug} (no metadata)")
```

## Directory Structure

After migration, each project directory looks like:

```
data/users/ywatanabe/neural-decoding/
├── .git/                         # Git repository
├── scitex/                       # SciTeX directory (visible)
│   ├── .metadata/                # Metadata (hidden subdirectory)
│   │   ├── config.json           # project_id, created_at
│   │   ├── metadata.json         # name, description, tags
│   │   ├── integrations.json    # Django, Gitea integration info
│   │   └── history.jsonl         # Activity log
│   ├── scholar/                  # Created on-demand
│   ├── writer/                   # Created on-demand
│   ├── code/                     # Created on-demand
│   └── viz/                      # Created on-demand
├── data/
├── scripts/
└── docs/
```

## Usage Examples

### Example 1: Create New Project with SciTeX

```python
# In Django view
from apps.project_app.models import Project
from scitex.project import validate_name

# Validate name
name = request.POST.get('name')
try:
    Project.validate_name_using_scitex(name)
except ValidationError as e:
    return JsonResponse({'error': str(e)})

# Create Django project
project = Project.objects.create(
    name=name,
    owner=request.user,
    description=request.POST.get('description', ''),
    visibility='private'
)

# Initialize scitex metadata
scitex_proj = project.initialize_scitex_metadata()

# Now project has both Django and scitex metadata
```

### Example 2: Sync After Web UI Changes

```python
# User updated project via web form
project = Project.objects.get(slug='neural-decoding')
project.description = "Updated via web UI"
project.save()

# Sync changes to scitex/.metadata/
project.sync_to_scitex()
```

### Example 3: Sync After Local Edits

```python
# User edited scitex/.metadata/metadata.json locally
project = Project.objects.get(slug='neural-decoding')

# Sync changes to Django
project.sync_from_scitex()

# Now Django model has updated values
print(project.description)  # Updated description from local file
```

### Example 4: Calculate Storage

```python
# Use scitex.project for accurate storage calculation
project = Project.objects.get(slug='neural-decoding')
size = project.update_storage_from_scitex()

print(f"Total storage: {size / 1024**2:.2f} MB")

# Get detailed breakdown
scitex_proj = project.to_scitex_project()
breakdown = scitex_proj.get_storage_breakdown()
print(f"Git repo: {breakdown['git'] / 1024**2:.2f} MB")
print(f"User files: {breakdown['user_files'] / 1024**2:.2f} MB")
```

### Example 5: Access SciTeX Features

```python
project = Project.objects.get(slug='neural-decoding')
scitex_proj = project.to_scitex_project()

# Get feature directories
scholar_dir = scitex_proj.get_scitex_directory('scholar')
writer_dir = scitex_proj.get_scitex_directory('writer')

# Save bibliography to scholar directory
bib_file = scholar_dir / 'bibliography.bib'
bib_file.write_text('@article{...}')

# Log activity
scitex_proj.log_activity('bibliography_saved', user=request.user.username)
```

## Benefits

### 1. Portability
Projects work independently of Django:
- Move directories between systems
- Use in containers
- Work offline
- No database required for metadata

### 2. Transparency
Metadata in readable JSON files:
- Version-controlled
- Human-readable
- Easy to backup
- Can be edited manually

### 3. Separation of Concerns
- Django = web layer (auth, collaboration, UI)
- scitex.project = business logic (validation, storage, metadata)
- Clear boundaries between layers

### 4. Reusability
Same logic works in:
- CLI tools (`scitex project ...`)
- Web interface (Django)
- Python scripts (`import scitex.project`)
- Jupyter notebooks

## Troubleshooting

### "scitex package is not installed"

```bash
# In your Django virtual environment
pip install scitex
```

Or install from source:
```bash
pip install -e /home/ywatanabe/proj/scitex-code
```

### "Project has no scitex/.metadata/ directory"

Run migration:
```bash
python manage.py migrate_to_scitex --username <username>
```

Or initialize manually:
```python
project = Project.objects.get(slug='my-project')
project.initialize_scitex_metadata()
```

### "Directory not found"

Check `local_path`:
```python
project = Project.objects.get(slug='my-project')
print(project.get_local_path())
```

Create directory:
```python
project.get_local_path().mkdir(parents=True, exist_ok=True)
```

### Sync Issues

If Django and scitex get out of sync:
```python
# Option 1: Trust Django, update scitex
project.sync_to_scitex()

# Option 2: Trust scitex, update Django
project.sync_from_scitex()
```

## Next Steps

1. ✅ Database migration (`python manage.py migrate`)
2. ✅ Migrate existing projects (`python manage.py migrate_to_scitex`)
3. Update views to use `validate_name_using_scitex()`
4. Update storage calculations to use `update_storage_from_scitex()`
5. Add sync buttons in web UI (optional)

## See Also

- [scitex.project README](../../../../../../../proj/scitex-code/src/scitex/project/README.md)
- [scitex.project DESIGN](../../../../../../../proj/scitex-code/src/scitex/project/DESIGN.md)
- [scitex.project DJANGO_INTEGRATION](../../../../../../../proj/scitex-code/src/scitex/project/DJANGO_INTEGRATION.md)
