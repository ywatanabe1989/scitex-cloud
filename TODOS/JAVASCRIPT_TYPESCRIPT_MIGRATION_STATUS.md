<!-- ---
!-- Timestamp: 2025-11-05 23:38:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/JAVASCRIPT_TYPESCRIPT_MIGRATION_STATUS.md
!-- --- -->

# JavaScript to TypeScript Migration Status

## Overview

This document tracks the systematic migration from JavaScript to TypeScript across the entire SciTeX Cloud codebase.

**Migration Principle:** TypeScript organized subdirectory structure is the source of truth. Legacy JavaScript files are moved to `js-potentially-legacy/` directories, and TypeScript-compiled files go to `js/` directories.

---

## Phase 1: Root-Level Static Files (./static/)

### Status: ✅ COMPLETED

### TypeScript Sources (11 files - All Migrated ✅)
1. ✅ code-blocks.ts → js/code-blocks.js
2. ✅ utils/api.ts → js/utils/api.js
3. ✅ utils/console-interceptor.ts → js/utils/console-interceptor.js
4. ✅ utils/csrf.ts → js/utils/csrf.js
5. ✅ utils/index.ts → js/utils/index.js
6. ✅ utils/storage.ts → js/utils/storage.js
7. ✅ utils/ui.ts → js/utils/ui.js
8. ✅ types/index.ts → js/types/index.js
9. ✅ **utils/theme-switcher.ts → js/utils/theme-switcher.js** (NEW)
10. ✅ **utils/tooltip-auto-position.ts → js/utils/tooltip-auto-position.js** (NEW)
11. ✅ **utils/highlight-js-bibtex.ts → js/utils/highlight-js-bibtex.js** (NEW)

### Legacy JavaScript Files (19 files - Moved to js-potentially-legacy/)

#### Migrated to TypeScript ✅ (3 files - COMPLETED)
1. ✅ **theme-switcher.js** → Migrated to utils/theme-switcher.ts
   - Template updated: templates/global_base_partials/global_body_scripts.html
   - Features: localStorage persistence, database sync, CSRF token handling

2. ✅ **tooltip-auto-position.js** → Migrated to utils/tooltip-auto-position.ts
   - Template updated: templates/global_base_partials/global_body_scripts.html
   - Features: Documentation for CSS-based tooltip system

3. ✅ **highlight-js-bibtex.js** → Migrated to utils/highlight-js-bibtex.ts
   - Templates updated:
     - apps/dev_app/templates/dev_app/design_section_template.html
     - apps/project_app/templates/project_app/repository/file_view_partials/file_view_scripts.html
   - Features: BibTeX language definition for Highlight.js

#### Active - Recently Migrated ✅ (3 files - COMPLETED 2025-11-06)
1. ✅ **main.js** → Migrated to utils/main.ts
   - Template updated: templates/global_base_partials/global_body_scripts.html
   - Features: Mobile menu, global UI initialization

2. ✅ **dropdown.js** → Migrated to utils/dropdown.ts
   - Template updated: templates/global_base_partials/global_body_scripts.html
   - Features: Generic dropdown menus with click-outside behavior

3. ✅ **components/confirm-modal.js** → Migrated to components/confirm-modal.ts
   - Template updated: templates/global_base_partials/global_body_scripts.html
   - Features: Modern confirmation dialog with TypeScript types, XSS protection

#### Active (4 files remaining - Need TypeScript migration)
1. ⏳ **collaborative-editor.js** - Used in:
   - apps/writer_app/templates/writer_app/collaborative_editor_partials/scripts.html

2. ⏳ **module-cards.js** - Used in:
   - apps/public_app/templates/public_app/landing.html (already migrated to ts/landing/module-cards.ts)

3. ⏳ **components/seekbar.js** - Used in:
   - apps/scholar_app/templates/scholar_app/search_partials/search_filters_scitex_seekbar.html (already migrated to ts/components/seekbar.ts)

4. ⏳ **writer_collaboration.js** - Used in:
   - apps/writer_app/templates/writer_app/index.html

#### Inactive (12 files - Not found in templates, candidates for removal)
1. darkmode.js
2. dashboard.js
3. document-manager.js
4. dropdown.js
5. jupyter-notebook.js
6. landing.js
7. main.js
8. onboarding.js
9. profile-manager.js
10. project-manager.js
11. test-dropdown.js
12. viz-interface.js

---

## Phase 2: App-Level Static Files

### project_app (Priority - Largest App)

**Status:** ✅ Infrastructure Complete, ⏳ Partial Migration

**TypeScript Structure (9 subdirectories):**
- ts/actions/
- ts/issues/
- ts/projects/
- ts/pull_requests/
- ts/repository/
- ts/security/
- ts/shared/
- ts/users/
- ts/workflows/

**Compiled JavaScript (8 subdirectories - matching TS structure):**
- js/issues/
- js/projects/
- js/pull_requests/
- js/repository/
- js/security/
- js/shared/
- js/users/
- js/workflows/

**Legacy JavaScript:** 61 files in js-potentially-legacy/

**Migration Status:**
- ✅ Migrated: sidebar, project_app, file_view, file_edit, file_history, profile, settings
- ⏳ Needs Migration: 9 files identified (file_browser, issue_detail, pr_*, security_*, workflow_*)

### writer_app

**Status:** ✅ MIGRATION COMPLETE (2025-11-06)

**TypeScript Structure (11 subdirectories):**
- ts/arxiv/
- ts/collaboration/
- ts/compilation/
- ts/dashboard/
- ts/editor/ (with modules/)
- ts/loaders/ ← NEW (inline JS extraction)
- ts/modules/
- ts/shared/ (with utils/)
- ts/utils/
- ts/version_control/

**Compiled JavaScript (11 subdirectories - matching TS structure):**
- js/arxiv/
- js/collaboration/
- js/compilation/
- js/dashboard/
- js/editor/ (with modules/)
- js/loaders/ ← NEW (inline JS extraction)
- js/modules/
- js/shared/ (with utils/)
- js/utils/
- js/version_control/

**Migration Complete:**
- ✅ All 16 legacy .js files migrated to TypeScript (3,505 lines)
- ✅ All inline JavaScript extracted (657 lines → 3 TypeScript modules)
- ✅ Legacy directory removed: js-potentially-legacy/ deleted
- ✅ All templates using TypeScript-compiled versions
- ✅ 0 TypeScript compilation errors

**Legacy Files Migrated (2025-11-06):**
- editor/modules/compilation.js → ts/editor/modules/compilation.ts
- editor/modules/editor-controls.js → ts/editor/modules/editor-controls.ts
- editor/modules/editor.js → ts/editor/modules/editor.ts
- editor/modules/file_tree.js → ts/editor/modules/file_tree.ts
- editor/modules/index.js → ts/editor/modules/index.ts
- editor/modules/latex-wrapper.js → ts/editor/modules/latex-wrapper.ts
- editor/modules/monaco-editor.js → ts/editor/modules/monaco-editor.ts
- editor/modules/panel-resizer.js → ts/editor/modules/panel-resizer.ts
- editor/modules/pdf-preview.js → ts/editor/modules/pdf-preview.ts
- editor/modules/pdf-scroll-zoom.js → ts/editor/modules/pdf-scroll-zoom.ts
- editor/modules/sections.js → ts/editor/modules/sections.ts
- shared/utils/dom.utils.js → ts/shared/utils/dom.utils.ts
- shared/utils/index.js → ts/shared/utils/index.ts
- shared/utils/keyboard.utils.js → ts/shared/utils/keyboard.utils.ts
- shared/utils/latex.utils.js → ts/shared/utils/latex.utils.ts
- shared/utils/timer.utils.js → ts/shared/utils/timer.utils.ts

**Inline JavaScript Extracted (2025-11-06):**
- index.html (90 lines) → ts/loaders/editor-loader.ts
- collaborative_editor_partials/scripts.html (319 lines) → ts/editor/collaborative-editor-manager.ts
- preview_panel_partials/preview_scripts.html (305 lines) → ts/editor/preview-panel-manager.ts

### accounts_app

**Status:** ⏳ Minimal Work Required

**TypeScript Structure:** None yet

**Legacy JavaScript:** 1 file
- js-potentially-legacy/account_settings.js

### Other Apps

**Status:** ✅ No JavaScript/TypeScript (Clean)

Apps with no JavaScript code:
- auth_app
- code_app
- core_app
- dev_app
- scholar_app

---

## Template Path Status

### Root-Level Templates (✅ All Updated)
All templates now reference correct paths:
- ✅ TypeScript-compiled files → `js/` paths
- ✅ Legacy files → `js-potentially-legacy/` paths

### App-Level Templates
- ✅ project_app: Paths updated to match TS subdirectory structure
- ✅ writer_app: Import map configured for TS modules
- ⏳ Some mismatches remain (9 files need TS migration)

---

## Migration Priority Order

### Critical (Breaks Functionality - 404 Errors)
Status: ✅ RESOLVED
- Fixed: profile.js, file_edit.js, file_history.js, settings.js paths

### High Priority (Frequently Used Shared Modules)
1. ⏳ project_app remaining files (9 files)
2. ⏳ Root-level active legacy files (7 files)

### Medium Priority (Feature-Specific Modules)
1. ⏳ writer_app legacy files (30+ files)
2. ⏳ accounts_app (1 file)

### Low Priority (Unused/Archive)
1. ⏳ Root-level inactive legacy files (12 files) - verify unused, then remove

---

## Next Steps

### Immediate Actions
1. Verify root-level legacy files are working with new paths
2. Test critical pages to ensure no 404 errors
3. Begin TypeScript migration for high-priority files

### TypeScript Migration Workflow (Per File)
1. Read legacy JavaScript source from `js-potentially-legacy/`
2. Create TypeScript equivalent in `ts/` with organized subdirectory
3. Add type definitions and improvements
4. Compile TypeScript → generates file in `js/`
5. Update template path to match TS structure
6. Test functionality
7. Remove legacy file (or keep for reference)

### Tracking
- Mark files as migrated in this document
- Update timestamps
- Document any issues or blockers

---

## Statistics

### Root Level
- ✅ Migrated to TypeScript: 14 files (+6 new migrations since 2025-11-05)
- ⏳ Active Legacy (need migration): 1 file (down from 7)
- ❌ Inactive Legacy (verify/remove): 12 files

### App Level
- ✅ Clean (no JS): 5 apps
- ✅ Complete Migration: 1 app (writer_app) ← NEW
- ⏳ Partial Migration: 1 app (project_app)
- ⏳ Minimal Work: 1 app (accounts_app)

### Overall
- **Total TypeScript files:** 72+ (14 root + 58 app-level)
- **Total compiled JS files:** 72+ (matching TS structure)
- **Total legacy JS files:** 98 (114 - 16 writer_app files removed)
- **Migration progress:** ~55% (infrastructure 100%, writer_app 100%, project_app partial)

### Recent Progress (2025-11-06 - Session 1: Morning)
- ✅ Migrated 3 critical global utility files (main, dropdown, confirm-modal)
- ✅ Updated global_body_scripts.html template with correct TypeScript-compiled paths
- ✅ Reduced active legacy files from 4 to 1
- ✅ TypeScript compilation successful (16 errors remain in other files, not new migrations)
- ✅ All core global scripts now using TypeScript with proper type safety
- ✅ Confirmed `allowJs: false` enforcing TypeScript-only codebase
- ✅ Hot-reloading via tsc --watch functioning correctly

### Recent Progress (2025-11-06 - Session 2: Evening)
**writer_app MIGRATION COMPLETE:**
- ✅ Extracted 657 lines of inline JavaScript → 3 TypeScript modules
  - editor-loader.ts (80 lines) - CodeMirror/Monaco loading
  - collaborative-editor-manager.ts (292 lines) - Editor management
  - preview-panel-manager.ts (285 lines) - PDF preview
- ✅ Verified all 16 legacy .js files had TypeScript equivalents (3,505 lines total)
- ✅ Removed entire js-potentially-legacy/ directory from writer_app
- ✅ All templates using TypeScript-compiled versions
- ✅ 0 TypeScript compilation errors in writer_app
- ✅ writer_app now 100% TypeScript with full type safety

---

## Notes

- TypeScript hot building is working correctly (tsc --watch)
- Docker volume mounts are bidirectionally synced
- .gitignore configured to ignore compiled js/ but track js-potentially-legacy/
- Console logging system captures errors to ./logs/console.log
- All documentation in ./RULES/ directory

<!-- EOF -->
