# Project App Frontend Refactoring Proposal

**Goal:** Follow writer_app pattern + separate services from user-facing pages

**Inspired by:** `./apps/writer_app/` structure

---

## Current Problems

1. ❌ Mixed naming: `browse/partials/` instead of `browse_partials/`
2. ❌ Duplicate partials in two locations
3. ❌ No separation between user pages and service/admin pages
4. ❌ Inconsistent file naming (underscores vs hyphens)
5. ❌ Backup files scattered everywhere

---

## Proposed Structure

### Templates

```
templates/project_app/
├── # ━━━ Core User Pages (Top Level) ━━━
├── list.html                           # Project list
├── list_partials/
│   ├── project_card.html
│   ├── create_form.html
│   └── pagination.html
│
├── browse.html                         # Main file browser
├── browse_partials/
│   ├── header.html
│   ├── header_partials/
│   │   ├── toolbar.html
│   │   └── breadcrumb.html
│   ├── file_browser.html
│   ├── file_browser_partials/
│   │   ├── file_list.html
│   │   └── sidebar.html
│   ├── readme.html
│   └── empty_state.html
│
├── create.html                         # Create project
├── create_partials/
│   ├── name_field.html
│   ├── description_field.html
│   ├── init_options.html
│   └── scripts.html
│
├── edit.html                           # Edit project
├── edit_partials/
│   ├── name_field.html
│   ├── description_field.html
│   └── source_url_field.html
│
├── delete.html                         # Delete project
├── delete_partials/
│   ├── warning_box.html
│   ├── consequences_list.html
│   ├── confirmation_form.html
│   └── confirmation_script.html
│
├── settings.html                       # Project settings
├── settings_partials/
│   ├── navigation.html
│   ├── general.html
│   ├── visibility.html
│   ├── collaborators.html
│   ├── danger_zone.html
│   └── delete_modal.html
│
├── # ━━━ File Viewer ━━━
├── file_view.html                      # View/edit file
├── file_view_partials/
│   ├── header.html
│   ├── breadcrumb.html
│   ├── tabs.html
│   ├── commit_info.html
│   ├── content_code.html
│   ├── content_text.html
│   ├── content_markdown.html
│   ├── content_pdf.html
│   ├── content_image.html
│   ├── content_binary.html
│   ├── scripts.html
│   └── pdf_scripts.html
│
├── file_history.html                   # File commit history
├── file_history_partials/
│   ├── header.html
│   ├── filter_bar.html
│   └── pagination.html
│
├── # ━━━ Features (Subdirectories for Complex Features) ━━━
├── issues/
│   ├── list.html
│   ├── list_partials/
│   ├── detail.html
│   ├── detail_partials/
│   ├── form.html
│   └── form_partials/
│
├── pull_requests/
│   ├── list.html
│   ├── list_partials/
│   ├── detail.html
│   ├── detail_partials/
│   ├── form.html
│   └── form_partials/
│
├── actions/
│   ├── list.html
│   ├── list_partials/
│   ├── workflow_detail.html
│   ├── workflow_detail_partials/
│   ├── workflow_editor.html
│   ├── workflow_editor_partials/
│   └── run_detail.html
│
├── security/
│   ├── overview.html
│   ├── overview_partials/
│   ├── alerts.html
│   ├── alerts_partials/
│   └── alert_detail.html
│
├── commits/
│   ├── detail.html
│   └── detail_partials/
│
├── users/
│   ├── profile.html
│   ├── profile_partials/
│   ├── projects.html
│   ├── bio.html
│   ├── board.html
│   └── stars.html
│
├── # ━━━ Services/Admin (Separate Directory) ━━━
├── services/
│   ├── repository_maintenance.html
│   └── repository_maintenance_partials/
│
└── # ━━━ Shared Components ━━━
    └── shared_partials/                 # Only truly shared components
        ├── breadcrumb.html
        └── commit_list_item.html
```

### Static Files

```
static/project_app/
├── css/
│   ├── # Core Pages
│   ├── list.css
│   ├── browse.css
│   ├── create.css
│   ├── edit.css
│   ├── delete.css
│   ├── settings.css
│   ├── file-view.css                   # Hyphens ✓
│   ├── file-history.css                # Hyphens ✓
│   │
│   ├── # Features
│   ├── issues/
│   │   ├── list.css
│   │   └── detail.css
│   ├── pull-requests/                  # Hyphens ✓
│   │   ├── list.css
│   │   └── detail.css
│   ├── actions/
│   │   ├── list.css
│   │   └── workflow-detail.css         # Hyphens ✓
│   ├── security/
│   │   └── overview.css
│   ├── commits/
│   │   └── detail.css
│   ├── users/
│   │   ├── profile.css
│   │   └── bio.css
│   │
│   ├── # Shared/Common
│   ├── common.css
│   ├── variables.css
│   └── components/
│       ├── badges.css
│       ├── buttons.css
│       ├── cards.css
│       ├── file-tree.css
│       ├── forms.css
│       ├── icons.css
│       ├── sidebar.css
│       └── tables.css
│
├── js/
│   ├── # Core Pages
│   ├── browse.js
│   ├── file-view.js                    # Hyphens ✓
│   ├── file-history.js                 # Hyphens ✓
│   ├── project-create.js               # Hyphens ✓
│   ├── project-detail.js               # Hyphens ✓
│   ├── settings.js
│   ├── profile.js
│   │
│   ├── # Features
│   ├── issue-detail.js                 # Hyphens ✓
│   ├── pr-detail.js                    # Hyphens ✓
│   ├── pr-conversation.js              # Hyphens ✓
│   ├── pr-form.js                      # Hyphens ✓
│   ├── workflow-detail.js              # Hyphens ✓
│   ├── workflow-editor.js              # Hyphens ✓
│   ├── security-alert-detail.js        # Hyphens ✓
│   ├── security-scan.js                # Hyphens ✓
│   │
│   └── # Shared/Common
│       ├── icons.js
│       └── pdf-viewer.js
│
└── ts/
    └── utils/
```

---

## Key Principles

### 1. Flat Structure for Core Pages ✓
Like writer_app, main user pages are at top level:
- `list.html`
- `browse.html`
- `create.html`
- `edit.html`
- `delete.html`
- `settings.html`

### 2. xxx.html → xxx_partials/ ✓
Every template has its own partials directory:
- `browse.html` → `browse_partials/`
- `file_view.html` → `file_view_partials/`
- NOT generic `partials/`

### 3. Nested Hierarchy ✓
Show component relationships:
```
browse_partials/
  ├── header.html
  └── header_partials/
      ├── toolbar.html
      └── breadcrumb.html
```

### 4. Feature Subdirectories for Complex Features ✓
Keep related features together:
- `issues/` - Issue tracking
- `pull_requests/` - PR management
- `actions/` - CI/CD workflows
- `security/` - Security scanning

### 5. Services Separation ✓
Admin/service pages in separate directory:
- `services/repository_maintenance.html`

### 6. Consistent Naming ✓
- Templates: underscores (`file_view.html`)
- Directories: underscores (`file_view_partials/`)
- CSS: hyphens (`file-view.css`)
- JS: hyphens (`file-view.js`)

### 7. No Duplication ✓
- Each partial in ONE location
- Truly shared components in `shared_partials/`

---

## Migration Plan

### Phase 1: Templates
1. Flatten core pages to top level
2. Rename `partials/` → `xxx_partials/`
3. Move service pages to `services/`
4. Remove duplicates
5. Clean up backups

### Phase 2: Static Files
1. Rename JS files to use hyphens
2. Organize CSS by page
3. Update template references

### Phase 3: Cleanup
1. Remove backup files
2. Move legacy to `.old/`
3. Update documentation

---

## Benefits

✅ **Clear Ownership** - Each page owns its partials
✅ **No Duplication** - Single source of truth
✅ **Follows Rules** - Matches `/RULES/00_DJANGO_ORGANIZATION_FRONTEND.md`
✅ **Like Writer** - Follows successful writer_app pattern
✅ **Separation** - User pages vs service pages
✅ **Consistent** - Uniform naming conventions
✅ **Maintainable** - Easy to find and modify

---

## Questions

1. Should we keep feature subdirectories (issues/, pull_requests/, etc.) or flatten everything?
2. Do we want `services/` or another name for admin pages?
3. Any exceptions to the hyphen rule for JS/CSS?

<!-- EOF -->
