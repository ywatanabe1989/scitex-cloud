# TypeScript Mirroring Structure

**Date:** 2025-11-04
**Philosophy:** TypeScript source structure exactly mirrors HTML templates and CSS

---

## Perfect Mirroring Achieved

All three layers now use **identical structure and naming**:

```
templates/project_app/          css/                          ts/
├── browse.html          →      ├── browse.css         →     ├── browse.ts
├── browse_partials/     →      ├── browse_partials/   →     ├── browse_partials/
├── issues_list.html     →      ├── issues_list.css    →     ├── issues_list.ts
├── issues_list_partials/→      ├── issues_list_partials/→   ├── issues_list_partials/
├── pr_detail.html       →      ├── pr_detail.css      →     ├── pr_detail.ts
├── pr_detail_partials/  →      ├── pr_detail_partials/→     ├── pr_detail_partials/
└── file_view.html       →      └── file_view.css      →     └── file_view.ts
```

---

## Directory Structure

### TypeScript Sources (`ts/`)

```
ts/
├── browse.ts                    # Source for browse.html
├── browse_partials/             # Future modular scripts
├── file_view.ts                 # Source for file_view.html
├── file_view_partials/          # Future modular scripts
├── issues_detail.ts             # Source for issues_detail.html
├── issues_detail_partials/      # Future modular scripts
├── pr_detail.ts                 # Source for pr_detail.html
├── pr_detail_partials/          # Future modular scripts
├── file_browser.ts              # Source for file_browser.html
├── file_edit.ts                 # Source for file_edit.html
├── file_history.ts              # Source for file_history.html
├── icons.ts                     # Icon utilities
├── pdf_viewer.ts                # PDF viewing functionality
├── pr_conversation.ts           # PR conversation handling
├── pr_form.ts                   # PR form handling
├── profile.ts                   # User profile scripts
├── project_app.ts               # Main app script
├── project_create.ts            # Project creation
├── project_detail.ts            # Project detail view
├── settings.ts                  # Settings page
├── security_alert_detail.ts     # Security alert detail
├── security_scan.ts             # Security scanning
├── sidebar_improvements.ts      # Sidebar enhancements
├── workflow_detail.ts           # Workflow detail view
├── workflow_editor.ts           # Workflow editor
├── workflow_run_detail.ts       # Workflow run details
└── utils/                       # Shared utilities
    ├── api.ts                   # API helpers
    ├── csrf.ts                  # CSRF token handling
    ├── storage.ts               # Local storage
    └── ui.ts                    # UI helpers
```

### Compiled JavaScript (`js/`)

**This directory is AUTO-GENERATED** - DO NOT EDIT!

```
js/
├── browse.js                    # Compiled from ts/browse.ts
├── browse.d.ts                  # Type definitions
├── browse.js.map                # Source map
├── file_view.js                 # Compiled from ts/file_view.ts
├── file_view.d.ts
├── file_view.js.map
└── ... (all compiled outputs)
```

---

## Naming Conventions

### Consistent Across All Layers

| Layer | Pattern | Example |
|-------|---------|---------|
| **Template** | `xxx_yyy.html` | `issues_detail.html` |
| **CSS** | `xxx_yyy.css` | `issues_detail.css` |
| **TypeScript** | `xxx_yyy.ts` | `issues_detail.ts` |
| **JavaScript** | `xxx_yyy.js` (compiled) | `issues_detail.js` |

**Key Point:** All use **underscores**, not hyphens!

---

## File Mapping

| Template | CSS | TypeScript Source | Compiled JS |
|----------|-----|-------------------|-------------|
| `browse.html` | `browse.css` | `ts/browse.ts` | `js/browse.js` |
| `file_view.html` | `file_view.css` | `ts/file_view.ts` | `js/file_view.js` |
| `issues_detail.html` | `issues_detail.css` | `ts/issues_detail.ts` | `js/issues_detail.js` |
| `pr_detail.html` | `pr_detail.css` | `ts/pr_detail.ts` | `js/pr_detail.js` |

---

## Build Process

### Compilation

```bash
# Compile TypeScript
cd apps/project_app/static/project_app
npx tsc

# Watch mode (auto-recompile on changes)
npx tsc --watch
```

### What Gets Generated

For each `ts/xxx.ts` file, TypeScript creates:
- `js/xxx.js` - Compiled JavaScript
- `js/xxx.d.ts` - Type definitions
- `js/xxx.js.map` - Source map for debugging

### Configuration

See `tsconfig.json`:
- **Input**: `ts/` directory (TypeScript sources)
- **Output**: `js/` directory (compiled)
- **Target**: ES2020
- **Module**: ES2020 modules
- **Source Maps**: Enabled for debugging

---

## Template Loading

Templates load the **compiled** JavaScript:

```django
{% block extra_js %}
<script src="{% static 'project_app/js/file_view.js' %}"></script>
{% endblock %}
```

**Note:** Always reference `js/xxx.js`, not `ts/xxx.ts`!

---

## Development Workflow

### 1. Edit TypeScript Sources
```bash
# Edit the TypeScript source
vim ts/file_view.ts
```

### 2. Compile
```bash
# Compile TypeScript
npx tsc

# Or use watch mode
npx tsc --watch
```

### 3. Test
```bash
# Refresh browser - Django serves compiled JS
```

### 4. Commit Both
```bash
# Commit both source and compiled
git add ts/file_view.ts js/file_view.js js/file_view.d.ts js/file_view.js.map
git commit -m "feat: Update file view functionality"
```

---

## Benefits

### 1. **Perfect Symmetry** ✅
```
templates/xxx.html ↔ css/xxx.css ↔ ts/xxx.ts → js/xxx.js
```

### 2. **Type Safety** ✅
- TypeScript catches errors at compile time
- Better IDE autocomplete
- Refactoring is safer

### 3. **Predictable Paths** ✅
Know the template? Know everything:
- Template: `file_view.html`
- CSS: `css/file_view.css`
- TypeScript: `ts/file_view.ts`
- JavaScript: `js/file_view.js`

### 4. **Maintainable** ✅
- Move template → move CSS & TS to same location
- Delete template → delete CSS & TS
- Structure scales identically

### 5. **Consistent Naming** ✅
All use underscores - no more mental switching between:
- ❌ `file-view.js` vs `file_view.html`
- ✅ `file_view.ts` = `file_view.html` = `file_view.css`

---

## Migration Status

### ✅ Completed
- [x] Created `ts/` directory structure
- [x] Copied all 21 JS files to TS
- [x] Renamed to use underscores (hyphens → underscores)
- [x] Created `tsconfig.json`
- [x] Created _partials directories in ts/
- [x] Preserved utils/ for shared code

### 📋 Next Steps (Optional)
- [ ] Add TypeScript type annotations
- [ ] Set up npm scripts for build
- [ ] Add to CI/CD pipeline
- [ ] Extract partial-specific scripts to _partials/

---

## File Count

- **Templates**: 42 files + 100 partials
- **CSS**: 25 files + 18 _partials dirs
- **TypeScript**: 21 source files + 4 _partials dirs
- **JavaScript**: 21 compiled files (auto-generated)
- **Utilities**: 4 shared TS modules

---

## Example: Complete Symmetry

### File View Page

```
templates/project_app/
└── file_view.html                    # Main template

templates/project_app/file_view_partials/
├── file_view_header.html             # Header partial
├── file_view_tabs.html               # Tabs partial
└── file_view_breadcrumb.html         # Breadcrumb partial

css/
└── file_view.css                     # Main styles

css/file_view_partials/
├── file_view_header.css              # Header styles (future)
├── file_view_tabs.css                # Tabs styles (future)
└── file_view_breadcrumb.css          # Breadcrumb styles (future)

ts/
└── file_view.ts                      # Main script source

ts/file_view_partials/
├── file_view_header.ts               # Header logic (future)
├── file_view_tabs.ts                 # Tabs logic (future)
└── file_view_breadcrumb.ts           # Breadcrumb logic (future)

js/ (compiled)
└── file_view.js                      # Compiled output
    file_view.d.ts                    # Type definitions
    file_view.js.map                  # Source map
```

---

## Git Workflow

### What to Track
- ✅ **Track**: `ts/` directory (TypeScript sources)
- ✅ **Track**: `js/` directory (compiled JavaScript for deployment)
- ✅ **Track**: `tsconfig.json`

### Why Track Compiled JS?
1. **Django serves it directly** - No build step in production
2. **Easy deployment** - Just pull and run
3. **Debugging** - Source maps link to TS sources

---

**Perfect mirroring achieved: Templates ↔ CSS ↔ TypeScript!** 🎉

<!-- EOF -->
