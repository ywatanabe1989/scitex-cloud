# Django Project Structure Improvement Plan

## Current Structure Analysis

The current SciTeX Web project structure has some non-standard Django elements and can be improved to better follow Django best practices as defined in our guidelines.

### Current Structure Strengths
- Separation of templates in Django app
- CSS organized in common and component directories
- Project management documentation
- Test files for TDD approach

### Current Structure Issues
- Non-standard Django project structure
- Missing key Django components (manage.py at root, etc.)
- Mixed JS/Django approach without clear separation
- Missing Django app organization (models, forms, etc.)

## Recommended Structure

Based on our Python Django Guidelines, here's the proposed structure:

```
scitex-web/
├── apps/                  # All Django applications
│   ├── about_app/         # Legal and contact pages
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── templates/
│   │   │   └── about_app/
│   │   │       ├── contact.html
│   │   │       ├── privacy_policy.html
│   │   │       └── terms_of_use.html
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── core_app/          # Core functionality
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── templates/
│   │   │   └── core_app/
│   │   │       ├── base.html
│   │   │       ├── index.html
│   │   │       └── landing.html
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── api_app/           # API functionality (future)
├── config/                # Project configuration
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py        # From django_settings.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py            # Project-level URL routing
│   └── wsgi.py            # WSGI configuration
├── static/                # Static files (CSS, JS, images)
│   ├── css/               # Move from public/css
│   │   ├── common/
│   │   └── components/
│   ├── js/                # Move from public/js
│   └── images/
├── media/                 # User-uploaded files
├── templates/             # Project-wide templates
│   └── base.html          # Move from scitex_web/templates
├── manage.py              # Django management script (new)
├── requirements/
│   ├── base.txt           # Split from requirements.txt
│   ├── development.txt
│   └── production.txt
├── project_management/    # Keep existing directory
└── .env.example           # Environment variables template
```

## Implementation Steps

### 1. Create Django Project Structure

1. Create `manage.py` at project root:
   - Standard Django management script

2. Reorganize settings:
   - Move `config/django_settings.py` to `config/settings/base.py`
   - Create `__init__.py`, `development.py`, and `production.py`

3. Create core Django files:
   - Add `config/urls.py` for root URL configuration
   - Add `config/wsgi.py` for deployment

### 2. Reorganize Apps

1. Create apps directory:
   ```bash
   mkdir -p apps/about_app apps/core_app
   ```

2. Move existing templates:
   - Move legal pages to `apps/about_app/templates/about_app/`
   - Move `base.html`, `index.html`, `landing.html` to `apps/core_app/templates/core_app/`

3. Create app structure in each app:
   - Add `__init__.py`, `admin.py`, `apps.py`, `models.py`, `urls.py`, `views.py`, `tests.py`
   - Move view logic from current `views.py` to appropriate app views

### 3. Reorganize Static Files

1. Create static directory:
   ```bash
   mkdir -p static/css static/js static/images
   ```

2. Move CSS files:
   - Move all files from `public/css/` to `static/css/`

3. Move JS files:
   - Move all files from `public/js/` to `static/js/`
   - Move JS files from `src/` to `static/js/` if they're frontend files

### 4. Update URLs and Settings

1. Update URL routing:
   - Create project-level `config/urls.py`
   - Update app-specific URL files

2. Update settings:
   - Configure static files settings
   - Configure templates settings
   - Set up environment variables

### 5. Testing and Verification

1. Run tests to ensure functionality works after restructuring
2. Verify templates render correctly
3. Check static files are properly served

## Benefits of Restructuring

1. **Maintainability**: Clear, standardized structure that follows Django conventions
2. **Scalability**: Modular apps that can grow independently
3. **Collaboration**: Easier for team members to navigate and understand
4. **Documentation**: Structure follows our guidelines document
5. **Deployment**: Proper settings separation for different environments

## Priority

This restructuring should be done **before** adding new features to ensure a solid foundation for the project.

---

*This plan follows the guidelines specified in IMPORTANT-guidelines-programming-Python-Django-Rules.md*