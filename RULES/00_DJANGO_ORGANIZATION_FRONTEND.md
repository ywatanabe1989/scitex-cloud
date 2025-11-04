<!-- ---
!-- Timestamp: 2025-11-04 11:30:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/RULES/00_DJANGO_ORGANIZATION_FRONTEND.md
!-- --- -->

# Django Frontend Organization Rules

**Core Principle:** Explicit is better than implicit. File structure mirrors HTML hierarchy.

---

## The Four Laws

1. **App-Centric** - App files in their app directory
2. **No Inline Styles** - All CSS/JS in separate files
3. **Explicit Naming** - Partials prefixed with parent template name
4. **Flat Structure** - No nested feature directories

---

## Quick Reference

### ✅ Correct Locations

| Type          | Location                                           |
|---------------|----------------------------------------------------|
| App CSS       | `apps/xxx_app/static/xxx_app/css/`                 |
| App TS        | `apps/xxx_app/static/xxx_app/ts/`                  |
| App JS        | `apps/xxx_app/static/xxx_app/js/` (compiled)       |
| App templates | `apps/xxx_app/templates/xxx_app/`                  |
| App partials  | `apps/xxx_app/templates/xxx_app/xxx_partials/`     |
| Global CSS    | `static/css/common/` or `static/css/components/`   |
| Global utils  | `static/ts/utils/` → `static/js/utils/` (compiled) |

---

## Template Organization

### Flat Structure (All Pages at Top Level)

```
templates/xxx_app/
├── browse.html                    # User-facing page
├── browse_partials/               # Partials for browse.html
├── settings.html                  # User-facing page
├── settings_partials/             # Partials for settings.html
├── issues_list.html               # Flattened (NOT issues/list.html)
├── issues_list_partials/          # Partials for issues_list.html
├── issues_detail.html             # Flattened
├── issues_detail_partials/        # Partials for issues_detail.html
└── admin_maintenance.html         # Admin page (prefixed with admin_)
```

**Why flat?**
- ✅ All pages visible with `ls *.html`
- ✅ Easy to search: `grep "issues_list"`
- ✅ Clear in editor tabs
- ✅ No ambiguity about location

### Naming Pattern: Explicit Prefixing

**Rule:** Partials are prefixed with their parent template name

```
xxx.html
xxx_partials/
  xxx_yyy.html              ← Prefixed with "xxx_"
  xxx_yyy_partials/
    xxx_yyy_zzz.html        ← Prefixed with "xxx_yyy_"
```

**Example:**
```
browse.html
browse_partials/
  browse_header.html                    {% include "xxx_app/browse_partials/browse_header.html" %}
  browse_header_partials/
    browse_header_toolbar.html          {% include "xxx_app/browse_partials/browse_header_partials/browse_header_toolbar.html" %}
    browse_header_breadcrumb.html
  browse_file_browser.html
  browse_sidebar.html
```

**Why prefixed?**
- ✅ Unique filenames (no "header.html" confusion)
- ✅ Search "browse_header" → exact match
- ✅ Editor tabs show clear names
- ✅ Explicit ownership of partials

### Admin/Service Pages

Prefix admin pages with `admin_`:

```
templates/xxx_app/
├── browse.html                        # Regular user page
├── settings.html                      # Regular user page
├── admin_repository_maintenance.html  # Admin-only page
└── admin_repository_maintenance_partials/
```

**Why prefix instead of directory?**
- ✅ Consistent with flat structure
- ✅ Easy to identify: `ls admin_*`
- ✅ No special directory needed

---

## Real-World Example

### ❌ Wrong (Old Pattern)

```
templates/project_app/
├── browse/                    # Nested directory
│   ├── project_root.html
│   └── partials/              # Generic "partials"
│       ├── header.html        # Which page's header?
│       └── toolbar.html       # Which toolbar?
├── issues/                    # Nested directory
│   ├── list.html
│   └── partials/              # Generic "partials"
└── partials/                  # Shared? Generic? Unclear!
    ├── breadcrumb.html
    └── header.html            # Which header?
```

**Problems:**
- ❌ Hard to find files (which directory?)
- ❌ Ambiguous names ("header.html" - which one?)
- ❌ Confusing editor tabs
- ❌ Duplicated partials

### ✅ Correct (New Pattern)

```
templates/project_app/
├── browse.html
├── browse_partials/
│   ├── browse_header.html
│   ├── browse_header_partials/
│   │   ├── browse_header_toolbar.html
│   │   └── browse_header_breadcrumb.html
│   ├── browse_file_browser.html
│   └── browse_sidebar.html
│
├── settings.html
├── settings_partials/
│   ├── settings_general.html
│   ├── settings_collaborators.html
│   └── settings_danger_zone.html
│
├── issues_list.html
├── issues_list_partials/
│   ├── issues_list_filters.html
│   ├── issues_list_item.html
│   └── issues_list_pagination.html
│
├── issues_detail.html
├── issues_detail_partials/
│   ├── issues_detail_header.html
│   ├── issues_detail_comments.html
│   └── issues_detail_sidebar.html
│
└── admin_repository_maintenance.html
    └── admin_repository_maintenance_partials/
```

**Benefits:**
- ✅ All pages at top level
- ✅ Unique, searchable filenames
- ✅ Clear ownership
- ✅ No duplication

---

## CSS Rules

### Naming: Use Hyphens

```
css/
├── browse.css              ← Matches browse.html
├── issues-list.css         ← Matches issues_list.html (underscore → hyphen)
├── issues-detail.css       ← Matches issues_detail.html
└── admin-maintenance.css   ← Matches admin_repository_maintenance.html
```

**Pattern:** Template `xxx_yyy.html` → CSS `xxx-yyy.css`

### ❌ Never

```html
<div style="color: red;">           <!-- Inline style -->
<style>body { margin: 0; }</style>  <!-- Inline block -->
```

### ✅ Always

```html
<link rel="stylesheet" href="{% static 'xxx_app/css/browse.css' %}">
<div class="text-red">
```

---

## JavaScript/TypeScript Rules

### Naming: Use Hyphens

```
js/
├── browse.js               ← Matches browse.html
├── issues-list.js          ← Matches issues_list.html (underscore → hyphen)
├── issues-detail.js        ← Matches issues_detail.html
└── admin-maintenance.js    ← Matches admin_repository_maintenance.html
```

**Pattern:** Template `xxx_yyy.html` → JS `xxx-yyy.js`

### Source vs Compiled

```
ts/ ← Only .ts files (source)
js/ ← Only .js, .d.ts, .map (compiled output)
```

### Build

```bash
cd frontend && npm run build:writer
```

### Template References

```django
<script src="{% static 'writer_app/js/browse.js' %}"></script>
```

---

## Common Mistakes

| ❌ Don't                           | ✅ Do                                        |
|------------------------------------|----------------------------------------------|
| `templates/xxx_app/issues/list.html` | `templates/xxx_app/issues_list.html`     |
| `issues/partials/header.html`      | `issues_list_partials/issues_list_header.html` |
| `partials/header.html`             | `browse_partials/browse_header.html`      |
| App files in `/static/` root       | App files in `/apps/xxx_app/static/xxx_app/` |
| Inline `style=""`                  | CSS classes                                  |
| `file_name.css`                    | `file-name.css`                              |
| `issue_detail.js`                  | `issue-detail.js`                            |
| Edit `.js` files                   | Edit `.ts` source, rebuild                   |

---

## File Naming Convention Summary

| File Type | Naming Rule | Example |
|-----------|-------------|---------|
| **Templates** | `xxx_yyy.html` (underscores) | `issues_list.html` |
| **Partial dirs** | `xxx_yyy_partials/` (underscores) | `issues_list_partials/` |
| **Partial files** | `parent_child.html` (underscores) | `issues_list_header.html` |
| **CSS files** | `xxx-yyy.css` (hyphens) | `issues-list.css` |
| **JS files** | `xxx-yyy.js` (hyphens) | `issues-list.js` |
| **TS files** | `xxx-yyy.ts` (hyphens) | `issues-list.ts` |

**Why different conventions?**
- Templates: Python/Django convention (underscores)
- CSS/JS: Web convention (hyphens, URL-friendly)

---

## New Feature Checklist

When creating a new page:

- [ ] Create `xxx.html` at top level (< 50 lines)
- [ ] Create `xxx_partials/` directory
- [ ] Name partials with prefix: `xxx_yyy.html`
- [ ] Create `css/xxx.css` (hyphens)
- [ ] Create `ts/xxx.ts` if needed (hyphens)
- [ ] Build: `cd frontend && npm run build:xxx`
- [ ] Test: Check browser console for 404s

---

## Migration from Old Structure

### Step 1: Flatten Directories

```bash
# Before
templates/xxx_app/issues/list.html

# After
templates/xxx_app/issues_list.html
```

### Step 2: Rename Partials Directories

```bash
# Before
templates/xxx_app/issues/partials/

# After
templates/xxx_app/issues_list_partials/
```

### Step 3: Add Prefixes to Partials

```bash
# Before
issues_list_partials/header.html

# After
issues_list_partials/issues_list_header.html
```

### Step 4: Update Template Includes

```django
<!-- Before -->
{% include "xxx_app/issues/partials/header.html" %}

<!-- After -->
{% include "xxx_app/issues_list_partials/issues_list_header.html" %}
```

### Step 5: Rename CSS/JS (Add Hyphens)

```bash
# Before
css/issue_detail.css
js/issue_detail.js

# After
css/issue-detail.css
js/issue-detail.js
```

---

## Examples from Existing Apps

### writer_app (Reference Implementation) ✓

```
templates/writer_app/
├── index.html
├── index_partials/
│   ├── editor.html
│   └── editor_partials/
│       └── toolbar.html
├── latex_editor.html
├── latex_editor_partials/
└── collaborative_editor.html
```

**What to learn:**
- ✅ Flat structure
- ✅ `xxx.html` → `xxx_partials/` pattern
- ✅ Consistent naming

### project_app (To be refactored)

Currently needs refactoring to match these rules.

---

**That's it.** Explicit naming, flat structure, clear hierarchy. Searchable, maintainable, scalable.

<!-- EOF -->
