# Feature Request: Local HTML Development Server

## Description
Create a local HTML development server for the SciTeX Web project, inspired by the successful implementations in ~/proj/ai_ielts and ~/proj/airight projects. This server should provide rapid development workflow with hot reload, static file serving, and easy setup for local development.

## Justification
- **Faster Development**: Immediate feedback during development without complex setup
- **Consistency**: Match development patterns used successfully in ai_ielts and airight projects
- **Testing**: Easy local testing of HTML, CSS, and JavaScript changes
- **Collaboration**: Simplified onboarding for new developers
- **Standards**: Follow Django best practices established in existing projects

## Reference Implementation Analysis

### AI IELTS Project Approach
- **Framework**: Pure Django with `python manage.py runserver`
- **Static Files**: App-specific static directories with automatic serving
- **Hot Reload**: Built-in Django development server auto-reload
- **Environment**: Python virtual environment with comprehensive requirements.txt

### AIRight Project Approach  
- **Framework**: Django with enhanced development tools
- **Hot Reload**: `django-browser-reload` for automatic browser refresh
- **Scripts**: Custom start/stop scripts (`./scripts/start`)
- **Static Organization**: Structured CSS/JS with component-based architecture
- **Dependencies**: Minimal Node.js + comprehensive Python stack

## Acceptance Criteria

### 1. Development Server Setup
- [ ] Create Django development server configuration
- [ ] Implement hot reload functionality for templates and static files
- [ ] Set up automatic browser refresh on file changes
- [ ] Configure proper static file serving for development

### 2. Project Structure
- [ ] Organize static files following Django best practices:
  ```
  static/
  ├── css/
  │   ├── common/      # Base styles, variables, reset
  │   ├── components/  # Reusable UI components
  │   └── pages/       # Page-specific styles
  ├── js/
  │   ├── common/      # Shared JavaScript utilities
  │   ├── components/  # Component-specific JS
  │   └── pages/       # Page-specific JavaScript
  └── images/          # Static images and assets
  ```

### 3. Development Scripts
- [ ] Create `start_dev.sh` script for easy server startup
- [ ] Create `start_prod.sh` script for production-like testing
- [ ] Implement automatic virtual environment activation
- [ ] Add database migration checks

### 4. Configuration Files
- [ ] Split Django settings into development/production
- [ ] Create environment variables template (`.env.example`)
- [ ] Configure proper DEBUG and ALLOWED_HOSTS settings
- [ ] Set up logging configuration for development

### 5. Static File Management
- [ ] Move existing CSS/JS from `public/` to Django `static/` directory
- [ ] Update template references to use Django static file tags
- [ ] Implement static file compression for production
- [ ] Configure browser caching headers for development

### 6. Hot Reload Implementation
- [ ] Install and configure `django-browser-reload`
- [ ] Set up file watching for templates, CSS, and JavaScript
- [ ] Configure automatic page refresh on file changes
- [ ] Implement WebSocket-based reload for faster updates

## Implementation Approach

Based on the analysis of ai_ielts and airight projects, implement the following:

### Phase 1: Basic Django Server (Day 1)
```bash
# 1. Create manage.py at project root
# 2. Set up Django settings in config/settings/
# 3. Configure basic URL routing
# 4. Test basic server startup
```

### Phase 2: Static File Organization (Day 1-2)
```bash
# 1. Create static/ directory structure
# 2. Move CSS/JS files from public/ to static/
# 3. Update template {% load static %} tags
# 4. Test static file serving
```

### Phase 3: Hot Reload Setup (Day 2)
```bash
# 1. Install django-browser-reload
# 2. Configure middleware and URLs
# 3. Set up file watching
# 4. Test automatic refresh functionality
```

### Phase 4: Development Scripts (Day 2-3)
```bash
# 1. Create start_dev.sh script
# 2. Add virtual environment management
# 3. Implement database setup automation
# 4. Add production testing script
```

### Phase 5: Advanced Features (Day 3)
```bash
# 1. Configure environment variables
# 2. Set up logging
# 3. Add development debugging tools
# 4. Create comprehensive documentation
```

## Technical Requirements

### Dependencies
**Python Requirements** (requirements/development.txt):
```
Django>=4.2
django-browser-reload>=1.12.1
django-extensions>=3.2.3
django-debug-toolbar>=4.2.0
python-decouple>=3.8
whitenoise>=6.5.0
```

**Node.js Requirements** (package.json) - Optional:
```json
{
  "scripts": {
    "watch-css": "sass --watch static/scss:static/css",
    "build-css": "sass static/scss:static/css --style compressed"
  },
  "devDependencies": {
    "sass": "^1.60.0",
    "autoprefixer": "^10.4.14"
  }
}
```

### Development Scripts

**start_dev.sh**:
```bash
#!/bin/bash
# Check if virtual environment exists
if [ ! -d "env" ]; then
    python -m venv env
    source env/bin/activate
    pip install -r requirements/development.txt
else
    source env/bin/activate
fi

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start development server
python manage.py runserver 0.0.0.0:8000
```

### Settings Configuration

**config/settings/development.py**:
```python
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

INSTALLED_APPS += [
    'django_browser_reload',
    'django_extensions',
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]

# Hot reload settings
INTERNAL_IPS = ['127.0.0.1']

# Development static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

## Expected Benefits

1. **Rapid Development**: Instant feedback on changes with hot reload
2. **Simplified Setup**: One-command server startup for new developers
3. **Professional Workflow**: Match industry standards used in ai_ielts/airight
4. **Better Testing**: Easy local testing environment before deployment
5. **Consistent Standards**: Follow Django best practices established in reference projects

## Success Metrics

- [ ] Server starts successfully with single command
- [ ] Hot reload works for all file types (HTML, CSS, JS)
- [ ] Page loads in <2 seconds on local development
- [ ] All existing functionality works in development server
- [ ] Easy onboarding for new developers (documented setup time <5 minutes)

## Future Enhancements

1. **Docker Integration**: Add containerized development environment
2. **SASS/SCSS Support**: Compile modern CSS preprocessing
3. **JavaScript Bundling**: Add webpack or similar for JS optimization
4. **Testing Integration**: Automated testing on file changes
5. **API Development**: RESTful API endpoints for dynamic features

---

*This feature request follows the guidelines specified in guidelines-programming-Feature-Request-Rules.md and incorporates successful patterns from ai_ielts and airight reference projects.*