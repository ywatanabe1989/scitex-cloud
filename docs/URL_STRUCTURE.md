# SciTeX Cloud URL Structure

**Updated**: 2025-10-16
**Pattern**: GitHub-style workspace URLs

## URL Organization

### Landing Pages (Marketing/Public)
```
/                          → Cloud landing page
/writer/                   → Writer module landing page (what is Writer?)
/scholar/                  → Scholar module landing page (what is Scholar?)
/code/                     → Code module landing page (what is Code?)
/viz/                      → Viz module landing page (what is Viz?)
```

### User & Project URLs (Workspace)
```
/<username>/                              → User's projects list
/<username>/<project>/                    → Project dashboard
/<username>/<project>/writer/             → Writer workspace
/<username>/<project>/scholar/            → Scholar workspace
/<username>/<project>/code/               → Code workspace
/<username>/<project>/viz/                → Viz workspace
```

### Project Directories (Scientific Workflow)
```
/<username>/<project>/scripts/            → Scripts directory
/<username>/<project>/data/               → Data directory
/<username>/<project>/docs/               → Documentation directory
/<username>/<project>/results/            → Results directory
/<username>/<project>/config/             → Configuration directory
/<username>/<project>/temp/               → Temporary files directory
```

### Project Management
```
/<username>/<project>/edit/               → Edit project settings
/<username>/<project>/delete/             → Delete project
/<username>/<project>/files/              → File manager
/<username>/<project>/collaborate/        → Collaboration settings
/<username>/<project>/members/            → Member management
/<username>/<project>/github/             → GitHub integration
/<username>/<project>/sync/               → External sync
```

## Examples

### User: `ywatanabe1989`, Project: `neurovista-analysis`

```
/ywatanabe1989/                                    → All projects by ywatanabe1989
/ywatanabe1989/neurovista-analysis/                → Project dashboard
/ywatanabe1989/neurovista-analysis/writer/         → Write manuscript
/ywatanabe1989/neurovista-analysis/scholar/        → Search papers, manage bibliography
/ywatanabe1989/neurovista-analysis/code/           → Code analysis and execution
/ywatanabe1989/neurovista-analysis/viz/            → Visualizations and figures
/ywatanabe1989/neurovista-analysis/scripts/        → Browse scripts directory
/ywatanabe1989/neurovista-analysis/data/raw/       → Browse data/raw subdirectory
```

## Implementation Details

### Main URL Configuration (`config/urls.py`)

```python
urlpatterns = [
    path("admin/", admin.site.urls),
] + discover_app_urls()  # Auto-discover app URLs

urlpatterns += [
    # Reserved paths (must come before username pattern)
    path("projects/", project_list, name="projects"),

    # Root landing page
    path("", include("apps.cloud_app.urls", namespace="cloud_app")),
]

# GitHub-style pattern (MUST be last)
urlpatterns += [
    path("<str:username>/", include("apps.project_app.user_urls")),
]
```

### User URLs (`project_app/user_urls.py`)

```python
urlpatterns = [
    path('', user_project_list_wrapper),                    # /<username>/
    path('<slug:slug>/', project_detail_wrapper),           # /<username>/<project>/
    path('<slug:slug>/writer/', project_writer_wrapper),    # /<username>/<project>/writer/
    path('<slug:slug>/scholar/', project_scholar_wrapper),  # /<username>/<project>/scholar/
    path('<slug:slug>/code/', project_code_wrapper),        # /<username>/<project>/code/
    path('<slug:slug>/viz/', project_viz_wrapper),          # /<username>/<project>/viz/
    # ... more patterns
]
```

### Module Integration (`project_app/views.py`)

Each module integration view:
1. Validates username and project slug
2. Checks user permissions
3. Calls the module's view directly with `project_id`

```python
def project_writer(request, username, slug):
    """Writer interface for this project"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check permissions...

    # Call writer view directly
    from apps.writer_app import views as writer_views
    return writer_views.project_writer(request, project.id)
```

### Module URLs

Each module (`writer_app`, `scholar_app`, etc.) has two types of URLs:

**1. Public/Marketing URLs** (`/writer/`, `/scholar/`)
```python
# writer_app/urls.py
urlpatterns = [
    path('', simple_views.index, name='index'),          # Landing page
    path('features/', simple_views.features),            # Feature showcase
    path('pricing/', simple_views.pricing),              # Pricing info
]
```

**2. Project-specific URLs** (accessed via `/<username>/<project>/<module>/`)
```python
# These use project_id for internal routing
path('project/<int:project_id>/', views.project_writer, name='project-writer'),
path('project/<int:project_id>/save-section/', views.save_section),
path('project/<int:project_id>/compile/', views.compile_modular_manuscript),
```

## Access Control

### Permission Levels
1. **Owner**: Full access (read, write, delete)
2. **Collaborator**: Read/write access
3. **Public**: Read-only (if project visibility = 'public')
4. **Anonymous**: No access (redirect to login)

### Implementation
```python
has_access = (
    project.owner == request.user or
    project.collaborators.filter(id=request.user.id).exists() or
    request.user.is_staff
)
```

## Reserved Usernames

These cannot be used as usernames (conflict with app URLs):
- `admin`
- `writer`
- `scholar`
- `code`
- `viz`
- `projects`
- `api`
- `auth`
- `core`
- `billing`
- `docs`
- `dev`
- `cloud`
- `static`
- `media`

Enforced in `User` model validation.

## Migration Path

### Old URLs → New URLs

| Old URL | New URL |
|---------|---------|
| `/project/123/` | `/<username>/<project>/` |
| `/writer/project/123/` | `/<username>/<project>/writer/` |
| `/scholar/project/123/` | `/<username>/<project>/scholar/` |
| `/projects/` | `/<username>/` (if logged in) |

**Backward Compatibility**: Old URLs redirect to new URLs via `project_detail_redirect` view.

## Benefits

✅ **Clear workspace identification**: Every URL shows whose workspace you're in
✅ **GitHub-familiar**: Users already know this pattern
✅ **Shareable**: URLs can be shared easily
✅ **SEO-friendly**: Better indexing with meaningful URLs
✅ **Permission-clear**: Ownership is explicit in the URL

---

**Last Updated**: 2025-10-16
**Status**: Implemented
