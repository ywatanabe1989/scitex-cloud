# CSS Mirroring Structure

**Date:** 2025-11-04
**Philosophy:** CSS directory structure exactly mirrors HTML template structure

---

## One-to-One Mapping

Every HTML template has a corresponding CSS file in the same relative location:

```
templates/project_app/           css/
├── browse.html           →      ├── browse.css
├── browse_partials/      →      ├── browse_partials/
│   ├── browse_header.html →     │   ├── browse_header.css (future)
│   ├── browse_sidebar.html →    │   ├── browse_sidebar.css (future)
│   └── browse_toolbar.html →    │   └── browse_toolbar.css (future)
├── issues_list.html      →      ├── issues_list.css
├── issues_list_partials/ →      ├── issues_list_partials/
├── pr_detail.html        →      ├── pr_detail.css
└── pr_detail_partials/   →      └── pr_detail_partials/
```

---

## Naming Conventions

### Templates → CSS Mapping

| Template Pattern | CSS Pattern | Example |
|-----------------|-------------|---------|
| `xxx.html` | `xxx.css` | `browse.html` → `browse.css` |
| `xxx_yyy.html` | `xxx_yyy.css` | `issues_list.html` → `issues_list.css` |
| `xxx_partials/` | `xxx_partials/` | `browse_partials/` → `browse_partials/` |
| `xxx_partials/xxx_yyy.html` | `xxx_partials/xxx_yyy.css` | `browse_partials/browse_header.html` → `browse_partials/browse_header.css` |

**Key Rules:**
- ✅ Templates use underscores → CSS uses underscores
- ✅ Same directory structure
- ✅ Same file names (just .html → .css)

---

## Current CSS Structure

```
css/
├── common/                      # Shared/reusable styles
│   ├── variables.css           # CSS variables
│   ├── common.css              # Base styles
│   ├── buttons.css             # Button components
│   ├── forms.css               # Form components
│   ├── sidebar.css             # Sidebar component
│   ├── file-tree.css           # File tree component
│   └── ...
│
├── browse.css                   # browse.html
├── browse_partials/             # browse_partials/
│
├── issues_list.css              # issues_list.html
├── issues_list_partials/        # issues_list_partials/
│
├── pr_detail.css                # pr_detail.html
├── pr_detail_partials/          # pr_detail_partials/
│
├── file_view.css                # file_view.html
├── file_view_partials/          # file_view_partials/
│
├── security_overview.css        # security_overview.html
├── security_overview_partials/  # security_overview_partials/
│
└── ... (18 _partials directories total, mirroring templates)
```

---

## Benefits

### 1. **Predictable** ✅
If you know the template path, you automatically know the CSS path:
- Template: `browse_partials/browse_header.html`
- CSS: `css/browse_partials/browse_header.css`

### 2. **Maintainable** ✅
- Moving a template? Move its CSS to the same relative location
- Deleting a template? Delete its corresponding CSS
- Adding a partial? Create CSS in the mirrored directory

### 3. **Explicit Ownership** ✅
No ambiguity about which CSS belongs to which partial:
- `browse_partials/browse_header.css` → Only for `browse_header.html`
- No generic `header.css` that could belong to any page

### 4. **Scalable** ✅
As the template structure grows, CSS structure grows identically:
- Add nested partials? Add nested CSS directories
- Flatten templates? Flatten CSS

### 5. **Easy to Find** ✅
Developers can instantly locate styles:
```bash
# Template
apps/project_app/templates/project_app/browse_partials/browse_header.html

# CSS (same path, different base)
apps/project_app/static/project_app/css/browse_partials/browse_header.css
```

---

## Template Loading Pattern

```django
{% block extra_css %}
<!-- Main template CSS -->
<link rel="stylesheet" href="{% static 'project_app/css/browse.css' %}">

<!-- Partial CSS (when needed) -->
<link rel="stylesheet" href="{% static 'project_app/css/browse_partials/browse_header.css' %}">

<!-- Common/shared CSS -->
<link rel="stylesheet" href="{% static 'project_app/css/common/sidebar.css' %}">
{% endblock %}
```

---

## File Organization Examples

### Browse Page
```
templates/project_app/
├── browse.html
└── browse_partials/
    ├── browse_header.html
    ├── browse_sidebar.html
    ├── browse_toolbar.html
    ├── browse_empty_state.html
    ├── browse_file_browser.html
    ├── browse_readme.html
    ├── browse_tabs.html
    └── browse_scripts.html

css/
├── browse.css                  ← Main page styles
└── browse_partials/            ← Partial-specific styles (when needed)
    ├── browse_header.css
    ├── browse_sidebar.css
    └── browse_toolbar.css
```

### Issues List
```
templates/project_app/
├── issues_list.html
└── issues_list_partials/
    (no partials yet)

css/
├── issues_list.css             ← Main page styles
└── issues_list_partials/       ← Ready for partials
```

### PR Detail
```
templates/project_app/
├── pr_detail.html
└── pr_detail_partials/
    ├── pr_detail_header.html
    ├── pr_detail_tabs.html
    ├── pr_detail_conversation.html
    ├── pr_detail_commits.html
    └── ...

css/
├── pr_detail.css               ← Main page styles
└── pr_detail_partials/         ← Partial-specific styles (when needed)
    ├── pr_detail_header.css
    ├── pr_detail_tabs.css
    └── pr_detail_conversation.css
```

---

## Common vs. Page-Specific CSS

### Common CSS (`css/common/`)
Use for **truly reusable** components:
- Variables (`variables.css`)
- Base styles (`common.css`)
- Buttons (`buttons.css`)
- Forms (`forms.css`)
- Sidebar (`sidebar.css`)
- File tree (`file-tree.css`)

### Page-Specific CSS (`css/xxx.css`, `css/xxx_partials/`)
Use for **page-unique** styles:
- Layout specific to that page
- Styles that won't be reused elsewhere
- Overrides for that specific context

---

## Migration Guide

### Adding a New Page

1. Create template: `templates/project_app/my_page.html`
2. Create CSS: `css/my_page.css`
3. Create partials dir: `templates/project_app/my_page_partials/`
4. Create CSS partials dir: `css/my_page_partials/`
5. Load CSS in template:
   ```django
   {% block extra_css %}
   <link rel="stylesheet" href="{% static 'project_app/css/my_page.css' %}">
   {% endblock %}
   ```

### Adding a Partial

1. Create template: `templates/project_app/my_page_partials/my_page_section.html`
2. Create CSS (if needed): `css/my_page_partials/my_page_section.css`
3. Include in parent template CSS:
   ```django
   <link rel="stylesheet" href="{% static 'project_app/css/my_page_partials/my_page_section.css' %}">
   ```

### Moving a Template

1. Move template: `old_dir/page.html` → `new_dir/page.html`
2. Move CSS: `css/old_dir/page.css` → `css/new_dir/page.css`
3. Update references

---

## Current Status

### Completed ✅
- [x] CSS files renamed to match template naming (underscores)
- [x] 18 `xxx_partials/` CSS directories created
- [x] Common/component CSS moved to `common/`
- [x] Old nested CSS directories removed
- [x] Template CSS references updated

### Future Enhancements
- [ ] Extract partial-specific CSS from main CSS files
- [ ] Create CSS files for individual partials (as needed)
- [ ] Document CSS naming conventions
- [ ] Add CSS build/bundle process

---

## Verification

### Check Structure Mirroring
```bash
# List template directories
ls -d apps/project_app/templates/project_app/*_partials/

# List CSS directories (should match)
ls -d apps/project_app/static/project_app/css/*_partials/
```

### Verify CSS Loading
```bash
# Check which templates load CSS
grep -l "extra_css" apps/project_app/templates/project_app/*.html
```

---

**Perfect symmetry achieved! HTML ↔ CSS structure now mirrors exactly.** 🎉

<!-- EOF -->
