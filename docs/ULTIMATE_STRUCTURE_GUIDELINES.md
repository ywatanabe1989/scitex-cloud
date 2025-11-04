<!-- ---
!-- Timestamp: 2025-11-04 12:51:50
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/docs/ULTIMATE_STRUCTURE_GUIDELINES.md
!-- --- -->

# Django App Organization Guidelines

## Overview

This document defines the complete structure and rules for organizing Django apps with HTML templates, CSS, and TypeScript files in a consistent, maintainable way.

## Core Principles

1. **Complete 1:1:1 Correspondence**: Every HTML template has corresponding CSS and TS files
2. **Functional Grouping**: Organize by feature/domain, not by file type
3. **Split When Large**: Break files into partials when they exceed ~300 lines
4. **Commonize After 3**: Extract common code only after seeing it 3 times

---

## Directory Structure

### Complete Tree Example
```
project_root/
│
├── templates/                                # Global templates
│   ├── global_base.html                      # Base for all apps
│   └── global_base_partials/                 # Global shared partials
│       ├── _header.html
│       └── _footer.html
│
├── static/                                    # Global static files
│   ├── css/
│   │   └── common/                           # CSS for all apps
│   │       ├── variables.css
│   │       ├── buttons.css
│   │       └── forms.css
│   │
│   ├── js/
│   │   └── common/                           # JS for all apps
│   │       ├── api.js
│   │       └── ui.js
│   │
│   └── images/                               # Global images
│       ├── logos/
│       └── icons/
│
└── apps/
    ├── core/                                 # Django app for utilities
    │   ├── decorators.py
    │   ├── utils.py
    │   └── management/
    │       └── commands/
    │           └── check_structure.py        # Structure validation
    │
    └── project_app/                          # Example Django app
        │
        ├── templates/project_app/            # App templates
        │   │
        │   ├── base/                         # Base templates
        │   │   └── app_base.html             # App-level base
        │   │
        │   ├── shared/                       # App-wide shared partials
        │   │   ├── _sidebar.html             # Used by multiple features
        │   │   ├── _tabs.html
        │   │   └── _breadcrumb.html
        │   │
        │   ├── repository/                   # Feature group 1
        │   │   ├── browse.html               # Main page
        │   │   ├── browse/                   # browse-specific partials
        │   │   │   ├── _header.html          # ~50 lines
        │   │   │   ├── _toolbar.html         # ~80 lines
        │   │   │   └── _file_tree.html       # ~200 lines
        │   │   │
        │   │   ├── file_view.html            # Main page
        │   │   ├── file_view/                # file_view-specific partials
        │   │   │   ├── _breadcrumb.html
        │   │   │   └── _content.html
        │   │   │
        │   │   ├── file_edit.html            # Main page (no partials needed)
        │   │   └── commit_detail.html
        │   │
        │   ├── pull_requests/                # Feature group 2
        │   │   ├── list.html
        │   │   ├── detail.html
        │   │   ├── detail/                   # detail-specific partials
        │   │   │   ├── _conversation.html
        │   │   │   ├── _diff.html
        │   │   │   └── _checks.html
        │   │   └── form.html
        │   │
        │   └── issues/                       # Feature group 3
        │       ├── list.html
        │       ├── detail.html
        │       └── form.html
        │
        └── static/project_app/               # App static files
            │
            ├── css/
            │   ├── shared/                   # App-wide shared CSS
            │   │   ├── sidebar.css           # Used by multiple features
            │   │   └── tabs.css
            │   │
            │   ├── repository/               # Feature group 1 CSS
            │   │   ├── browse.css            # Main CSS (~50 lines)
            │   │   ├── browse/               # browse-specific CSS
            │   │   │   ├── header.css        # ~100 lines
            │   │   │   ├── toolbar.css       # ~150 lines
            │   │   │   └── file-tree.css     # ~200 lines
            │   │   │
            │   │   ├── file_view.css
            │   │   ├── file_view/
            │   │   │   ├── breadcrumb.css
            │   │   │   └── content.css
            │   │   │
            │   │   ├── file_edit.css
            │   │   └── commit_detail.css
            │   │
            │   ├── pull_requests/            # Feature group 2 CSS
            │   │   ├── list.css
            │   │   ├── detail.css
            │   │   ├── detail/
            │   │   │   ├── conversation.css
            │   │   │   ├── diff.css
            │   │   │   └── checks.css
            │   │   └── form.css
            │   │
            │   └── issues/                   # Feature group 3 CSS
            │       ├── list.css
            │       ├── detail.css
            │       └── form.css
            │
            ├── ts/                           # TypeScript source
            │   ├── shared/                   # App-wide shared TS
            │   │   ├── Sidebar.ts
            │   │   └── Tabs.ts
            │   │
            │   ├── repository/               # Feature group 1 TS
            │   │   ├── browse.ts             # Main TS (~50 lines)
            │   │   ├── browse/               # browse-specific TS
            │   │   │   ├── Toolbar.ts        # ~150 lines
            │   │   │   └── FileTree.ts       # ~200 lines
            │   │   │
            │   │   ├── file_view.ts
            │   │   ├── file_view/
            │   │   │   └── ContentViewer.ts
            │   │   │
            │   │   ├── file_edit.ts
            │   │   └── commit_detail.ts
            │   │
            │   ├── pull_requests/            # Feature group 2 TS
            │   │   ├── list.ts
            │   │   ├── detail.ts
            │   │   ├── detail/
            │   │   │   ├── Conversation.ts
            │   │   │   └── DiffViewer.ts
            │   │   └── form.ts
            │   │
            │   └── issues/                   # Feature group 3 TS
            │       ├── list.ts
            │       ├── detail.ts
            │       └── form.ts
            │
            ├── js/                           # Compiled JavaScript
            │   └── (mirrors ts/ structure)
            │
            ├── tsconfig.json                 # TypeScript config
            │
            └── icons/                        # App-specific icons
                ├── git-branch.svg
                └── pull-request.svg
```

---

## Rules

### Rule 1: Directory Hierarchy (4 Layers)
```
Layer 0: Global
  templates/, static/                    # Shared across all apps

Layer 1: App
  apps/project_app/                      # Single Django app

Layer 2: Feature Group
  repository/, pull_requests/, issues/   # Related functionality

Layer 3: Page
  browse.html, list.html, detail.html    # Individual pages

Layer 4: Page-specific Partials (when large)
  browse/_header.html, browse/_toolbar.html
```

### Rule 2: Complete 1:1:1 Correspondence
```
templates/project_app/repository/browse.html
    ↕ Must correspond
static/project_app/css/repository/browse.css
    ↕ Must correspond
static/project_app/ts/repository/browse.ts
    ↕ Compiles to
static/project_app/js/repository/browse.js
```

**Every main HTML file MUST have corresponding CSS and TS files in the same relative path.**

### Rule 3: Naming Conventions

#### Main Files
```
browse.html, browse.css, browse.ts     # No prefix
```

#### Partials (Components)
```
_header.html, _toolbar.html            # Underscore prefix
```

#### Shared Directories
```
shared/, base/                         # For shared components
```

#### Feature Directories
```
repository/, pull_requests/            # No underscore
```

### Rule 4: File Splitting Guidelines

#### When to Keep Single File
```
File < 200 lines:
  → Keep as single file
  browse.html (150 lines) ✓
```

#### When to Split
```
File > 300 lines:
  → Create subdirectory and split into partials
  
  browse.html (30 lines)            # Main becomes thin
  browse/_header.html (50 lines)
  browse/_toolbar.html (80 lines)
  browse/_file_tree.html (200 lines)
```

### Rule 5: Commonization Timing
```
1st time: Write directly
  repository/browse.css

2nd time: Copy-paste
  repository/file_view.css (duplicate)

3rd time: Consider extracting to shared
  → Extract to shared/file-tree.css
  → Import from both files
```

**Do not extract common code prematurely. Duplication is better than wrong abstraction.**

### Rule 6: Import Methods

#### Django Templates
```django
{# Shared partial #}
{% include 'project_app/shared/_sidebar.html' %}

{# Page-specific partial #}
{% include 'project_app/repository/browse/_header.html' %}
```

#### CSS
```css
/* Global common */
@import url('/static/css/common/variables.css');

/* App-wide shared */
@import url('../../shared/sidebar.css');

/* Page-specific */
@import url('./browse/header.css');
```

#### TypeScript
```typescript
// Global common
import { api } from '/static/js/common/api.js';

// App-wide shared
import { Sidebar } from '../../shared/Sidebar.js';

// Page-specific
import { FileTree } from './browse/FileTree.js';
```

### Rule 7: TypeScript Compilation
```
Development:
  static/project_app/ts/repository/browse.ts  # Edit this

Build:
  static/project_app/js/repository/browse.js  # Auto-generated

HTML loads:
  <script src="{% static 'project_app/js/repository/browse.js' %}">
  (Load .js, not .ts)
```

#### tsconfig.json Location
```
apps/project_app/static/project_app/tsconfig.json  # Per-app config
```

#### Basic tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ES2020",
    "outDir": "./js",
    "rootDir": "./ts",
    "strict": true
  },
  "include": ["ts/**/*"],
  "exclude": ["node_modules", "js"]
}
```

#### Build Command
```bash
cd apps/project_app/static/project_app/
tsc --watch
```

### Rule 8: Global vs App-scoped

#### Use Global (`static/`) When:
```
All apps use it:
  static/css/common/buttons.css      # Common buttons
  static/js/common/api.js             # API wrapper
  static/images/icons/file.svg        # Common icons
```

#### Use App-scoped (`static/project_app/`) When:
```
Only this app uses it:
  static/project_app/css/shared/      # App-wide shared CSS
  static/project_app/ts/shared/       # App-wide shared TS
  static/project_app/icons/           # App-specific icons
```

---

## Terminology

### Standardized Terms

| Term | Usage | Location |
|------|-------|----------|
| `common/` | Used by all apps | `static/css/common/`, `static/js/common/` |
| `shared/` | Used by multiple features within one app | `templates/xxx_app/shared/`, `static/xxx_app/css/shared/` |
| `base/` | Base templates only | `templates/xxx_app/base/app_base.html` |
| `core/` | Django app name for utilities | `apps/core/` |

### Examples
```python
# Global common
/static/css/common/buttons.css
/static/js/common/api.js

# App-wide shared
templates/project_app/shared/_sidebar.html
static/project_app/css/shared/sidebar.css
static/project_app/ts/shared/Sidebar.ts

# Base templates
templates/global_base.html                      # Global
templates/project_app/base/app_base.html       # App-level

# Core utilities
apps/core/decorators.py
apps/core/utils.py
```

---

## Correspondence Table

| HTML                                                      | CSS                                                      | TypeScript                                            | JavaScript                                            |
|-----------------------------------------------------------|----------------------------------------------------------|-------------------------------------------------------|-------------------------------------------------------|
| `templates/project_app/repository/browse.html`            | `static/project_app/css/repository/browse.css`           | `static/project_app/ts/repository/browse.ts`          | `static/project_app/js/repository/browse.js`          |
| `templates/project_app/repository/browse/_header.html`    | `static/project_app/css/repository/browse/header.css`    | (no JS)                                               | -                                                     |
| `templates/project_app/repository/browse/_file_tree.html` | `static/project_app/css/repository/browse/file-tree.css` | `static/project_app/ts/repository/browse/FileTree.ts` | `static/project_app/js/repository/browse/FileTree.js` |
| `templates/project_app/shared/_sidebar.html`              | `static/project_app/css/shared/sidebar.css`              | `static/project_app/ts/shared/Sidebar.ts`             | `static/project_app/js/shared/Sidebar.js`             |

---

## Automated Structure Validation

### Management Command

Create: `apps/core/management/commands/check_structure.py`
```python
from django.core.management.base import BaseCommand
from django.apps import apps
from pathlib import Path

class Command(BaseCommand):
    help = 'Check HTML/CSS/TS correspondence for all apps'
    
    def handle(self, *args, **options):
        errors = []
        
        for app_config in apps.get_app_configs():
            app_path = Path(app_config.path)
            templates_dir = app_path / 'templates' / app_config.name
            
            if not templates_dir.exists():
                continue
            
            css_dir = app_path / 'static' / app_config.name / 'css'
            ts_dir = app_path / 'static' / app_config.name / 'ts'
            
            for html in templates_dir.rglob('*.html'):
                # Skip partials (files starting with _)
                if html.stem.startswith('_'):
                    continue
                
                # Skip base templates
                if 'base' in html.parts:
                    continue
                
                rel = html.relative_to(templates_dir)
                css = css_dir / rel.with_suffix('.css')
                ts = ts_dir / rel.with_suffix('.ts')
                
                if not css.exists():
                    errors.append(f'❌ {app_config.name}: Missing {css}')
                
                if not ts.exists():
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  {app_config.name}: No TS for {html.name}')
                    )
        
        if errors:
            self.stdout.write(self.style.ERROR('\n'.join(errors)))
            raise SystemExit(1)
        else:
            self.stdout.write(self.style.SUCCESS('✅ All apps structure OK'))
```

### System Check Integration

Create: `apps/core/checks.py`
```python
from django.core.checks import Error, register
from django.apps import apps
from pathlib import Path

@register()
def check_all_apps_correspondence(app_configs, **kwargs):
    errors = []
    
    for app_config in apps.get_app_configs():
        app_path = Path(app_config.path)
        templates_dir = app_path / 'templates' / app_config.name
        
        if not templates_dir.exists():
            continue
        
        css_dir = app_path / 'static' / app_config.name / 'css'
        
        for html in templates_dir.rglob('*.html'):
            if html.stem.startswith('_') or 'base' in html.parts:
                continue
            
            rel = html.relative_to(templates_dir)
            css = css_dir / rel.with_suffix('.css')
            
            if not css.exists():
                errors.append(Error(
                    f'{app_config.name}: Missing CSS for {html.name}',
                    hint=f'Create {css}',
                    id=f'{app_config.name}.E001',
                ))
    
    return errors
```

Update: `apps/core/apps.py`
```python
from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = 'apps.core'
    
    def ready(self):
        from . import checks
```

### Usage
```bash
# Manual check
python manage.py check_structure

# Automatic on runserver
python manage.py runserver
# → Runs check on startup

# Automatic on migrate
python manage.py migrate
# → Runs check before migration
```

---

## Migration from Existing Structure

### Step 1: Create Feature Directories
```bash
cd apps/project_app/templates/project_app/
mkdir -p repository pull_requests issues security workflows users
```

### Step 2: Move Files by Feature
```bash
# Repository-related
mv browse.html repository/
mv file_view.html repository/
mv file_edit.html repository/

# Pull requests
mv pr_*.html pull_requests/
cd pull_requests
mv pr_list.html list.html
mv pr_detail.html detail.html

# Issues
mv issues_*.html issues/
cd issues
mv issues_list.html list.html
```

### Step 3: Apply Same Structure to CSS/TS
```bash
cd apps/project_app/static/project_app/css/
mkdir -p repository pull_requests issues

mv browse.css repository/
mv file_view.css repository/
mv pr_*.css pull_requests/
```

### Step 4: Update View References
```python
# Before
return render(request, 'project_app/browse.html', context)

# After
return render(request, 'project_app/repository/browse.html', context)
```

---

## Best Practices

### DO ✓

- Maintain 1:1:1 correspondence between HTML/CSS/TS
- Group by feature/domain
- Use underscore prefix for partials
- Split files when they exceed 300 lines
- Run `check_structure` before committing
- Place `tsconfig.json` per app

### DON'T ✗

- Mix different features in same directory
- Create premature abstractions
- Skip corresponding CSS/TS files
- Use different naming patterns
- Ignore structure validation errors

---

## Summary

This structure provides:

1. **Clarity**: File location immediately reveals its purpose
2. **Maintainability**: Easy to find and modify related files
3. **Scalability**: Clean growth path as features expand
4. **Consistency**: Enforced through automated validation
5. **Team-friendly**: New developers quickly understand organization

Follow these rules strictly for all Django apps in the project.

<!-- EOF -->