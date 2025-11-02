# Writer App Refactoring Analysis - Complete Structure Mapping

**Analysis Date:** 2025-11-03  
**Scope:** Very thorough analysis of writer app file organization and misplaced files  
**Status:** Current state vs. Target state for refactoring

---

## Executive Summary

The writer app has a **split structure problem**: TypeScript source files are in `./static/ts/writer/` (root level) while compiled JavaScript and related assets are in `./apps/writer_app/static/writer_app/`. This violates the project's app-centric organization principle.

**Files to migrate:** 54+ TypeScript/JavaScript files across 4 directory types  
**Complexity:** High - requires build system changes, import path updates, and template modifications  
**Risk Level:** Medium - well-contained in one app, but affects build pipeline

---

## Part 1: Current Writer App Structure

### 1.1 Properly Organized (Already in `./apps/writer_app/`)

#### Python Backend - All correctly located:
```
./apps/writer_app/
├── __init__.py
├── admin.py
├── apps.py
├── models/
│   ├── arxiv.py
│   ├── collaboration.py
│   ├── compilation.py
│   ├── core.py
│   ├── core_old.py
│   └── version_control.py
├── views/
│   ├── api_views.py
│   ├── arxiv_views.py
│   ├── editor_views.py
│   ├── main_views.py
│   ├── main_views_old.py
│   └── workspace_views.py
├── services/
│   ├── ai_service.py
│   ├── arxiv/ (subdirectory with arxiv_service.py, formatters.py)
│   ├── compiler.py
│   ├── operational_transform_service.py
│   ├── repository_service.py
│   ├── utils.py
│   ├── version_control_service.py
│   └── writer_service.py
├── configs/
│   └── sections_config.py
├── management/commands/
│   ├── cleanup_guest_users.py
│   ├── fix_compile_scripts.py
│   └── init_arxiv_categories.py
├── migrations/
│   ├── 0001_initial.py
│   └── 0002_remove_arxivaccount_user_and_more.py
├── urls.py
├── urls_.py
├── routing.py
├── consumers.py
├── tests.py
└── static/writer_app/
    ├── css/
    │   ├── arxiv.css
    │   ├── codemirror-styling.css
    │   ├── editor-enhanced.css
    │   ├── history_timeline.css
    │   ├── pdf-view-main.css
    │   ├── sidebar-improved.css
    │   ├── tex-view-main.css
    │   ├── tex-view-sidebar.css
    │   ├── writer-ui-improved.css
    │   ├── writer_app.css
    │   └── .old/ (legacy files)
    ├── js/
    │   ├── api-client.js
    │   ├── helpers.js (compiled from TS)
    │   ├── history_timeline.js
    │   ├── index.js (compiled from TS)
    │   ├── writer_app.js
    │   ├── modules/ (compiled JS from TS)
    │   ├── utils/ (compiled JS from TS)
    │   └── *.d.ts, *.js.map (TypeScript outputs)
    └── ts/ (SOURCE FILES - properly located but see note below)
        ├── services/
        │   ├── CompilationService.ts
        │   ├── EditorService.ts
        │   ├── SaveService.ts
        │   ├── SectionService.ts
        │   ├── StateService.ts
        │   └── WordCountService.ts
        ├── types/
        │   ├── api.types.ts
        │   ├── document.types.ts
        │   ├── editor.types.ts
        │   └── section.types.ts
        └── utils/
            ├── config.ts
            ├── csrf.ts
            ├── csrf.utils.ts
            ├── dom.utils.ts
            ├── keyboard.utils.ts
            ├── latex.utils.ts
            ├── storage.ts
            ├── storage.utils.ts
            └── timer.utils.ts
```

#### HTML Templates - Properly located:
```
./apps/writer_app/templates/writer_app/
├── README.md
├── writer_base.html (extends global_base.html)
├── writer_dashboard.html
├── index.html (main editor page)
├── collaborative_editor.html
├── compilation_view.html
├── default_workspace.html
├── latex_editor.html
├── version_control_dashboard.html
├── index_partials/
│   ├── demo_banner.html
│   ├── init_prompt.html
│   ├── main_editor.html
│   ├── sidebar.html
│   └── word_count.html
└── legacy/ (old templates)
    ├── account_setup.html
    ├── dashboard.html
    ├── index_landing.html
    ├── index_old.html
    ├── modular_editor.html
    ├── simple_editor.html
    ├── simple_editor_copy.html
    ├── submission_detail.html
    ├── submission_form.html
    └── submission_list.html
```

#### CSS Files - Properly located:
```
./apps/writer_app/static/writer_app/css/ (10 files)
- arxiv.css
- codemirror-styling.css
- editor-enhanced.css
- history_timeline.css
- pdf-view-main.css
- sidebar-improved.css
- tex-view-main.css
- tex-view-sidebar.css
- writer-ui-improved.css
- writer_app.css
```

### 1.2 Misplaced Files (PRIMARY REFACTORING TARGETS)

#### Problem 1: TypeScript Sources in Root Static Directory

**Current Location:** `/home/ywatanabe/proj/scitex-cloud/static/ts/writer/`
**Target Location:** `/home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/`

**Files to move (18 TypeScript source files):**

```
./static/ts/writer/ (ENTIRE DIRECTORY - 18 files)
├── index.ts (1545 lines - main entry point)
├── helpers.ts (50 lines - helper functions)
├── modules/ (11 modules)
│   ├── editor.ts
│   ├── monaco-editor.ts (25K)
│   ├── sections.ts
│   ├── compilation.ts
│   ├── file_tree.ts (15K)
│   ├── latex-wrapper.ts
│   ├── pdf-preview.ts
│   ├── pdf-scroll-zoom.ts (20K - important!)
│   ├── panel-resizer.ts
│   ├── editor-controls.ts (18K)
│   └── index.ts
└── utils/ (4 utilities)
    ├── dom.utils.ts
    ├── keyboard.utils.ts
    ├── latex.utils.ts
    ├── timer.utils.ts
    └── index.ts
```

**Statistics:**
- 18 total TypeScript files (36 with compiled output)
- ~170KB of TypeScript source code
- All compile to JS in `apps/writer_app/static/writer_app/js/`

**Dependencies & Imports:**
```typescript
// From ./static/ts/writer/index.ts (main entry)
import { WriterEditor, EnhancedEditor, SectionsManager, ... } 
  from './modules/index.js';
import { getCsrfToken } from '@/utils/csrf.js';
import { writerStorage } from '@/utils/storage.js';
import { getWriterConfig, createDefaultEditorState } from './helpers.js';

// Path aliases in tsconfig.json:
"@/writer/utils/*": ["writer/utils/*"]  // Points to ./static/ts/writer/utils/
"@/writer/*": ["writer/*"]              // Points to ./static/ts/writer/
"@/utils/*": ["utils/*"]                // Points to ./static/ts/utils/
```

**Cross-app dependencies:**
- Imports from `@/utils/` (root level): `csrf.js`, `storage.js`, etc.
- These utilities are shared with other apps (scholar, etc.)
- Need to remain in root for reusability

---

#### Problem 2: Misplaced JavaScript File in Root Static

**Current Location:** `/home/ywatanabe/proj/scitex-cloud/static/js/writer_collaboration.js`
**Target Location:** `/home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/js/writer_collaboration.js`

**File Details:**
- 180 lines (uncompiled JS, not from TypeScript)
- WebSocket client for collaborative editing
- Class: `WriterCollaboration`
- Not referenced in current templates (appears to be legacy/unused)

**Check Status:** 
```bash
grep -r "writer_collaboration" /home/ywatanabe/proj/scitex-cloud/apps/writer_app/
# Result: appears in static references but NOT actively used in current flow
```

---

## Part 2: Build System Configuration

### 2.1 Current Build Configuration

**TypeScript Compiler Setup (`./tsconfig.json`):**
```json
{
  "compilerOptions": {
    "rootDir": "./static/ts",           // SOURCE: root level
    "outDir": "./static/js",            // OUTPUT: root level
    "baseUrl": "./static/ts",
    "paths": {
      "@/writer/utils": ["writer/utils"],
      "@/writer/*": ["writer/*"],
      "@/utils": ["utils"],
      "@/utils/*": ["utils/*"],
      "@/*": ["*"]
    }
  },
  "include": ["static/ts/**/*"]
}
```

**NPM Scripts (`./package.json`):**
```json
{
  "scripts": {
    "build": "tsc",                     // Compiles all TS from ./static/ts
    "build:watch": "tsc --watch",
    "build:writer": "tsc --rootDir static/ts/writer --outDir apps/writer_app/static/writer_app/js",
    "build:scholar": "tsc --rootDir static/ts/scholar --outDir apps/scholar_app/static/scholar_app/js"
  }
}
```

**Key Observation:**
- `build:writer` script EXISTS but compiles from wrong source directory
- Should compile from `apps/writer_app/static/writer_app/ts/` (after migration)

### 2.2 Build Configuration Changes Required

**After refactoring, tsconfig.json paths need:**
```json
{
  "paths": {
    "@/writer/utils": ["writer_app/static/writer_app/ts/utils"],
    "@/writer/*": ["writer_app/static/writer_app/ts/*"],
    "@/utils": ["utils"],              // Keep for shared utilities
    "@/utils/*": ["utils/*"],
    "@/*": ["*"]
  }
}
```

---

## Part 3: Template References

### 3.1 Current Template References

**`writer_base.html` (Master template):**
```html
<!-- Currently references root-level CSS that doesn't exist -->
<link rel="stylesheet" href="{% static 'css/writer_app/writer.css' %}">
<!-- Should reference: -->
<link rel="stylesheet" href="{% static 'writer_app/css/writer_app.css' %}">
```

**`index.html` (Main editor page):**
```html
<!-- Existing CSS references (correct app-level location) -->
<link rel="stylesheet" href="{% static 'writer_app/css/tex-view-main.css' %}">
<link rel="stylesheet" href="{% static 'writer_app/css/editor-enhanced.css' %}">
<link rel="stylesheet" href="{% static 'writer_app/css/pdf-view-main.css' %}">
<link rel="stylesheet" href="{% static 'writer_app/css/history_timeline.css' %}">
<link rel="stylesheet" href="{% static 'writer_app/css/writer-ui-improved.css' %}">

<!-- Main entry point - problematic reference -->
<script type="module" src="{% static 'js/writer/index.js' %}?v={{ build_id|default:'dev' }}"></script>

<!-- API client - correct location -->
<script src="{% static 'writer_app/js/api-client.js' %}?v={{ build_id|default:'dev' }}"></script>

<!-- Collaboration - problematic reference -->
<script src="{% static 'js/writer_collaboration.js' %}?v={{ build_id|default:'dev' }}"></script>
```

### 3.2 Template Updates Required

After moving files to `apps/writer_app/static/writer_app/`:

```html
<!-- BEFORE -->
<script type="module" src="{% static 'js/writer/index.js' %}"></script>
<script src="{% static 'js/writer_collaboration.js' %}"></script>

<!-- AFTER -->
<script type="module" src="{% static 'writer_app/js/index.js' %}"></script>
<script src="{% static 'writer_app/js/writer_collaboration.js' %}"></script>
```

---

## Part 4: File Migration Plan

### 4.1 Phase 1: Move TypeScript Source Files

**Action:** Copy entire `./static/ts/writer/` to `./apps/writer_app/static/writer_app/ts/`

**Command:**
```bash
# Create target directory
mkdir -p apps/writer_app/static/writer_app/ts

# Copy TypeScript sources
cp -r static/ts/writer/* apps/writer_app/static/writer_app/ts/

# Verify copy
ls -la apps/writer_app/static/writer_app/ts/
# Expected: index.ts, helpers.ts, modules/, utils/
```

**Files Moved (18 source files):**
1. `index.ts` (main entry, 1545 lines)
2. `helpers.ts` (helpers)
3. `modules/index.ts`
4. `modules/editor.ts`
5. `modules/monaco-editor.ts`
6. `modules/sections.ts`
7. `modules/compilation.ts`
8. `modules/file_tree.ts`
9. `modules/latex-wrapper.ts`
10. `modules/pdf-preview.ts`
11. `modules/pdf-scroll-zoom.ts`
12. `modules/panel-resizer.ts`
13. `modules/editor-controls.ts`
14. `utils/index.ts`
15. `utils/dom.utils.ts`
16. `utils/keyboard.utils.ts`
17. `utils/latex.utils.ts`
18. `utils/timer.utils.ts`

### 4.2 Phase 2: Move Misplaced JavaScript File

**Action:** Move `writer_collaboration.js` to app static directory

**Command:**
```bash
# Move file
mv static/js/writer_collaboration.js apps/writer_app/static/writer_app/js/

# Update template references (see Part 3.2)
```

### 4.3 Phase 3: Update Build Configuration

**Update `./tsconfig.json`:**
```json
{
  "compilerOptions": {
    "rootDir": "./static/ts",           // Keep for shared code
    "outDir": "./static/js",            // Keep for shared code
    "baseUrl": "./static/ts",
    "paths": {
      "@/writer/utils": ["../apps/writer_app/static/writer_app/ts/utils"],
      "@/writer/*": ["../apps/writer_app/static/writer_app/ts/*"],
      "@/utils": ["utils"],
      "@/utils/*": ["utils/*"],
      "@/*": ["*"]
    }
  },
  "include": [
    "static/ts/**/*",
    "apps/writer_app/static/writer_app/ts/**/*"
  ]
}
```

**Update `./package.json`:**
```json
{
  "scripts": {
    "build": "tsc",
    "build:watch": "tsc --watch",
    "build:writer": "tsc --rootDir apps/writer_app/static/writer_app/ts --outDir apps/writer_app/static/writer_app/js",
    "build:scholar": "tsc --rootDir static/ts/scholar --outDir apps/scholar_app/static/scholar_app/js"
  }
}
```

### 4.4 Phase 4: Update Import Paths

**In moved TypeScript files, NO changes needed** because:
- Internal imports use relative paths: `./modules/index.js`
- External imports use aliases: `@/utils/csrf.js`, `@/utils/storage.js`
- Build system (tsconfig) handles path resolution

**Verification:**
```bash
# After running: npm run build:writer
# Should see output in:
ls -la apps/writer_app/static/writer_app/js/
# Expected: index.js, helpers.js, modules/, utils/, and .d.ts, .js.map files
```

### 4.5 Phase 5: Update Templates

Update all references in templates from root static to app static:

**Files to Update:**
1. `apps/writer_app/templates/writer_app/writer_base.html`
2. `apps/writer_app/templates/writer_app/index.html`
3. Any other writer templates that reference scripts

**Changes:**
```html
<!-- Change: -->
<script type="module" src="{% static 'js/writer/index.js' %}"></script>
<script src="{% static 'js/writer_collaboration.js' %}"></script>

<!-- To: -->
<script type="module" src="{% static 'writer_app/js/index.js' %}"></script>
<script src="{% static 'writer_app/js/writer_collaboration.js' %}"></script>
```

### 4.6 Phase 6: Clean Up Root Static

After migration and verification:

**Command:**
```bash
# Remove TypeScript source from root
rm -rf static/ts/writer/

# Remove moved JS file
# (already moved in Phase 2, if it exists in static/js/)
rm -f static/js/writer_collaboration.js
```

**Verify cleanup:**
```bash
# Should not find writer files in root static/ts/ or static/js/
find static/ts/ -name "*writer*" -type f  # Should return nothing
find static/js/ -name "*writer*" -type f  # Should return nothing
```

---

## Part 5: Dependency & Import Analysis

### 5.1 Internal Writer Dependencies

**Module Structure (Dependency Graph):**
```
index.ts (main entry)
├── modules/index.ts
│   ├── editor.ts
│   ├── monaco-editor.ts
│   ├── sections.ts
│   ├── compilation.ts
│   ├── file_tree.ts
│   ├── latex-wrapper.ts
│   ├── pdf-preview.ts
│   ├── pdf-scroll-zoom.ts
│   ├── panel-resizer.ts
│   └── editor-controls.ts
├── helpers.ts
└── utils/
    ├── dom.utils.ts
    ├── keyboard.utils.ts
    ├── latex.utils.ts
    └── timer.utils.ts
```

**Import Patterns (No Changes Needed):**
```typescript
// Relative imports (will work after move)
import { WriterEditor } from './modules/editor.js';
import { getPDFScrollZoomHandler } from './modules/pdf-scroll-zoom.js';

// Alias imports (resolved by tsconfig paths)
import { getCsrfToken } from '@/utils/csrf.js';
import { writerStorage } from '@/utils/storage.js';
```

### 5.2 External Dependencies (Shared with Other Apps)

**Utilities used from root `./static/ts/utils/`:**
- `csrf.js` - CSRF token management
- `storage.js` - Local storage wrapper
- Common DOM utilities, keyboard utilities

**Status:** No change needed - these remain in root static (shared)

### 5.3 Cross-App References

**Writer imports from:**
- `@/utils/csrf.ts` ✓ (shared, stays in root)
- `@/utils/storage.ts` ✓ (shared, stays in root)
- `@/types` (if any - need to verify)

**Who imports from Writer?**
- `index.html` template in writer_app ✓
- No other apps import from writer modules (isolated)

---

## Part 6: Risk Assessment by File

### High Risk Files (Complex, Large)

| File | Lines | Risk | Reason |
|------|-------|------|--------|
| `index.ts` | 1545 | HIGH | Main entry point, extensive logic |
| `monaco-editor.ts` | 25K | HIGH | Complex editor integration |
| `editor-controls.ts` | 18K | HIGH | Many event handlers |
| `file_tree.ts` | 15K | HIGH | File system interaction |
| `pdf-scroll-zoom.ts` | 20K | HIGH | Complex scroll/zoom logic |

**Mitigation:**
- Test after each file move
- Use `npm run build:writer` to verify compilation
- Check browser console for runtime errors
- Test PDF preview, editor controls, file tree

### Medium Risk Files (Moderate Complexity)

| File | Lines | Risk | Reason |
|------|-------|------|--------|
| `compilation.ts` | 9.2K | MEDIUM | Compilation service |
| `pdf-preview.ts` | 9.7K | MEDIUM | PDF rendering |
| `panel-resizer.ts` | 6.9K | MEDIUM | UI layout |
| `sections.ts` | 9.9K | MEDIUM | Section management |

### Low Risk Files (Simple, Small)

| File | Lines | Risk | Reason |
|------|-------|------|--------|
| `editor.ts` | 6.7K | LOW | Basic editor wrapper |
| `latex-wrapper.ts` | 5.3K | LOW | Utility wrapper |
| `helpers.ts` | 50 | LOW | Helper functions |
| `dom.utils.ts` | < 1K | LOW | DOM utilities |
| `keyboard.utils.ts` | < 1K | LOW | Keyboard utilities |
| `latex.utils.ts` | < 1K | LOW | LaTeX utilities |
| `timer.utils.ts` | < 1K | LOW | Timer utilities |
| `writer_collaboration.js` | 180 | LOW | Unused/legacy |

---

## Part 7: File Checklist for Refactoring

### Directories to Create
- [ ] `apps/writer_app/static/writer_app/ts/`
- [ ] `apps/writer_app/static/writer_app/ts/modules/`
- [ ] `apps/writer_app/static/writer_app/ts/utils/`

### Files to Copy (Phase 1)
- [ ] `static/ts/writer/index.ts` → `apps/writer_app/static/writer_app/ts/index.ts`
- [ ] `static/ts/writer/helpers.ts` → `apps/writer_app/static/writer_app/ts/helpers.ts`
- [ ] `static/ts/writer/modules/*` → `apps/writer_app/static/writer_app/ts/modules/`
- [ ] `static/ts/writer/utils/*` → `apps/writer_app/static/writer_app/ts/utils/`

### Files to Move (Phase 2)
- [ ] `static/js/writer_collaboration.js` → `apps/writer_app/static/writer_app/js/writer_collaboration.js`

### Configuration to Update (Phase 3)
- [ ] `tsconfig.json` - Update paths and include
- [ ] `package.json` - Update build:writer script

### Templates to Update (Phase 5)
- [ ] `apps/writer_app/templates/writer_app/writer_base.html`
- [ ] `apps/writer_app/templates/writer_app/index.html`
- [ ] Any other writer templates with script references

### Cleanup to Perform (Phase 6)
- [ ] Remove `static/ts/writer/` directory
- [ ] Remove remaining `static/js/writer_collaboration.js` (if any)

---

## Part 8: Compilation & Testing Checklist

### Pre-Migration Baseline
```bash
# 1. Record current build output size
ls -lh static/js/writer/
du -sh static/js/writer/

# 2. Record current template references
grep -r "writer" apps/writer_app/templates/

# 3. Test current build
npm run build
npm run build:writer
```

### Post-Migration Verification

**Build System:**
```bash
# [ ] All TypeScript files compile without errors
npm run build

# [ ] Writer-specific build works
npm run build:writer

# [ ] Output files exist in correct location
ls -la apps/writer_app/static/writer_app/js/
# Should see: index.js, helpers.js, modules/, utils/, *.d.ts, *.js.map

# [ ] No duplicate compiled files in root
ls static/js/writer* 2>/dev/null
# Should return nothing or error
```

**Functionality Testing:**
```bash
# [ ] Load /writer/ in browser - no console errors
# [ ] Check Network tab - all scripts load from writer_app/static/
# [ ] Test editor initialization
# [ ] Test PDF preview
# [ ] Test file tree
# [ ] Test section switching
# [ ] Test compilation
# [ ] Check browser DevTools console - no 404 errors
```

**Static File Collection:**
```bash
# After refactoring, run collectstatic
python manage.py collectstatic --no-input

# Verify output in staticfiles/
ls -la staticfiles/writer_app/js/
ls -la staticfiles/writer_app/css/
```

---

## Part 9: Summary Table - File Locations

### Current vs. Target State

| Category | File Type | Current Location | Target Location | Count | Status |
|----------|-----------|------------------|-----------------|-------|--------|
| TypeScript Sources | `.ts` | `static/ts/writer/` | `apps/writer_app/static/writer_app/ts/` | 18 | MOVE |
| TypeScript Compiled | `.js` | `static/js/writer/` | `apps/writer_app/static/writer_app/js/` | 36+ | AUTO (via build) |
| Type Declarations | `.d.ts` | `static/js/writer/` | `apps/writer_app/static/writer_app/js/` | 36+ | AUTO (via build) |
| Source Maps | `.js.map` | `static/js/writer/` | `apps/writer_app/static/writer_app/js/` | 36+ | AUTO (via build) |
| JavaScript (misc) | `writer_collaboration.js` | `static/js/` | `apps/writer_app/static/writer_app/js/` | 1 | MOVE |
| CSS | `.css` | `apps/writer_app/static/writer_app/css/` | `(already here)` | 10 | NO CHANGE |
| HTML Templates | `.html` | `apps/writer_app/templates/writer_app/` | `(already here)` | 15+ | UPDATE REFS |
| Python Backend | `.py` | `apps/writer_app/` | `(already here)` | 30+ | NO CHANGE |

---

## Part 10: References & Impact Analysis

### Files that Reference Writer Statics

**Template Files:**
1. `apps/writer_app/templates/writer_app/writer_base.html`
   - Line: `<link rel="stylesheet" href="{% static 'css/writer_app/writer.css' %}">`
   - Issue: CSS file doesn't exist - should be `writer_app/css/writer_app.css`

2. `apps/writer_app/templates/writer_app/index.html`
   - Line: `<script type="module" src="{% static 'js/writer/index.js' %}">`
   - Fix: Change to `writer_app/js/index.js`
   - Line: `<script src="{% static 'js/writer_collaboration.js' %}">`
   - Fix: Change to `writer_app/js/writer_collaboration.js`

**Python View Files:**
- No Python files import or reference static file paths (templates handle this)

**Build/Config Files:**
1. `tsconfig.json` - Define path aliases
2. `package.json` - Define build scripts

---

## Part 11: Git Considerations

### What to Commit

After refactoring, ensure these are version-controlled:
- [ ] New TypeScript files in `apps/writer_app/static/writer_app/ts/`
- [ ] Updated `tsconfig.json`
- [ ] Updated `package.json`
- [ ] Updated template files with new script references
- [ ] Updated `.gitignore` (if needed) to ignore compiled `js/` directory

### What to .gitignore (Already Should Be)

```
# Compiled JavaScript output
apps/writer_app/static/writer_app/js/
static/js/writer/
staticfiles/
```

### Cleanup Commits

Consider separate commits for:
1. "chore: Move writer TypeScript sources to apps/writer_app/"
2. "chore: Move writer_collaboration.js to app static directory"
3. "chore: Update build configuration for app-centric structure"
4. "fix: Update template script references after refactoring"
5. "chore: Remove old writer files from root static directory"

---

## Conclusion

This refactoring brings the writer app into full compliance with the project's app-centric organization principle. The migration is **well-scoped and low-risk** because:

1. **No cross-app dependencies** - Writer is isolated
2. **Build system support** - npm scripts and tsconfig already have placeholders
3. **Clear file locations** - No ambiguity about where things belong
4. **Minimal code changes** - Only template references and build config need updates
5. **Well-documented** - This analysis provides complete reference

The refactoring should take **2-4 hours** including testing and verification.

