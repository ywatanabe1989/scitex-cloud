# writer_app.js Removal Plan

**Status:** Ready for removal pending migration completion
**File to Remove:** `/home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/js/writer_app.js`
**Size:** 2,937 lines

## Current State

### What's Already Migrated ✅

Services (1,501 lines migrated to TypeScript):
- ✅ `EditorService.ts` (333 lines) - CodeMirror operations
- ✅ `SectionService.ts` (327 lines) - Section management
- ✅ `CompilationService.ts` (325 lines) - Compilation handling
- ✅ `SaveService.ts` (239 lines) - Save operations
- ✅ `StateService.ts` (139 lines) - State management
- ✅ `WordCountService.ts` (138 lines) - Word counting

Utilities (consolidated):
- ✅ CSRF management (3 implementations → 1)
- ✅ Storage management (2 implementations → 1)
- ✅ DOM utilities (moved to shared location)
- ✅ Keyboard utilities (moved to shared location)
- ✅ LaTeX utilities (moved to shared location)
- ✅ Timer utilities (moved to shared location)

Type Definitions (consolidated):
- ✅ All types unified in `/static/ts/types/index.ts`
- ✅ API types, Section types, Editor types, Document types

### What Remains in writer_app.js ⏳

Based on git status and recent commits, writer_app.js contains:
1. Workspace initialization logic
2. DOM event listener setup
3. Service coordination and initialization
4. Main app entry point

This logic needs to be either:
- Migrated to TypeScript entry point, OR
- Replaced with TypeScript modules that do the same

## Removal Checklist

### Pre-Removal: Verify Migration is Complete

- [ ] All services have been updated to import from `/static/ts/`
- [ ] Services import utilities from `@/utils` and `@/writer/utils`
- [ ] Services import types from `@/types`
- [ ] Workspace initialization logic migrated to TypeScript
- [ ] All event listeners migrated to TypeScript
- [ ] Compiled TypeScript produces valid JavaScript output
- [ ] Template updated to load compiled TypeScript bundle

### Build Configuration

- [ ] `tsconfig.json` configured with proper path aliases
- [ ] Build script generates output to correct location
- [ ] `package.json` build commands working:
  - [ ] `npm run build` - Production build
  - [ ] `npm run build:watch` - Development watch
  - [ ] `npm run type-check` - Type checking

### Template Updates

Current template load:
```html
<!-- Line 97 -->
<script src="{% static 'writer_app/js/writer_app.js' %}?v=..."></script>
```

Should become:
```html
<!-- Load compiled TypeScript bundle -->
<script src="{% static 'writer_app/js/writer-app-bundle.js' %}?v=..."></script>
```

Or use TypeScript module system:
```html
<script type="module" src="{% static 'js/writer/index.js' %}"></script>
```

### Functional Verification

Before removing writer_app.js:

- [ ] Workspace initialization works
- [ ] Editor loads and is functional
- [ ] Sections can be switched
- [ ] Text can be edited and saved
- [ ] Word count updates in real-time
- [ ] Compilation works
- [ ] Theme switching works
- [ ] Auto-save functionality works
- [ ] History/undo-redo works
- [ ] CSRF token is correctly retrieved
- [ ] API calls have proper CSRF headers
- [ ] Storage persistence works

### Browser Testing

- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] Mobile browsers (if applicable)

### Fallback Plan

If issues arise after removing writer_app.js:

1. Keep a backup copy: `writer_app.js.backup`
2. Have a git branch to revert from
3. Keep compiled version alongside during transition
4. Use feature flags if partial removal needed

## Removal Steps

### Step 1: Verify Migration Complete ✅ DONE

Services and utilities consolidated:
```
✅ 1,501 lines of services migrated
✅ ~500 lines of utilities consolidated
✅ ~250 lines of types unified
```

### Step 2: Create Unified TypeScript Entry Point ⏳ IN PROGRESS

Create `/static/ts/writer/index.ts` that:
1. Imports all services from `apps/writer_app/ts/services/`
2. Imports shared utilities from `@/utils` and `@/writer/utils`
3. Imports types from `@/types`
4. Exports public API

Example structure:
```typescript
// /static/ts/writer/index.ts

// Import services
import { EditorService } from '@/writer_services/EditorService';
import { SectionService } from '@/writer_services/SectionService';
import { CompilationService } from '@/writer_services/CompilationService';
import { SaveService } from '@/writer_services/SaveService';
import { StateService } from '@/writer_services/StateService';
import { WordCountService } from '@/writer_services/WordCountService';

// Import utilities
import { getCsrfToken } from '@/utils/csrf';
import { writerStorage } from '@/utils/storage';

// Initialize app
export function initializeWriter() {
    const editorService = new EditorService();
    const sectionService = new SectionService();
    // ... initialize other services
}

// Export for external use
export {
    EditorService,
    SectionService,
    CompilationService,
    SaveService,
    StateService,
    WordCountService,
};
```

### Step 3: Update Service Imports ⏳ PENDING

Update each service to import from consolidated locations:

Before:
```typescript
import { EditorState } from '../types/editor.types';
import { querySelector } from '../utils/dom.utils';
import { storage } from '../utils/storage.utils';
```

After:
```typescript
import { EditorState } from '@/types';
import { querySelector } from '@/writer/utils/dom.utils';
import { writerStorage } from '@/utils/storage';
```

### Step 4: Update Template ⏳ PENDING

File: `/home/ywatanabe/proj/scitex-cloud/apps/writer_app/templates/writer_app/index.html`

Replace line 97:
```html
<!-- OLD -->
<script src="{% static 'writer_app/js/writer_app.js' %}?v=..."></script>

<!-- NEW - Option 1: Module -->
<script type="module" src="{% static 'js/writer/index.js' %}"></script>

<!-- NEW - Option 2: Bundle -->
<script src="{% static 'js/writer-bundle.js' %}"></script>
```

### Step 5: Build and Test ⏳ PENDING

```bash
# Build TypeScript
npm run build

# Test in development
npm run dev

# Verify in browser
# - Check all writer functionality
# - Check console for errors
# - Verify network tab shows proper CSRF headers
```

### Step 6: Remove writer_app.js ⏳ PENDING

```bash
# Create backup
cp apps/writer_app/static/writer_app/js/writer_app.js apps/writer_app/static/writer_app/js/writer_app.js.backup

# Remove original
rm apps/writer_app/static/writer_app/js/writer_app.js

# Commit
git add apps/writer_app/static/writer_app/js/
git commit -m "refactor: Remove writer_app.js after complete TypeScript migration"
```

## Files to Keep (Duplicates in writer_app/ts/)

These can also be removed once verified:

```
/apps/writer_app/static/writer_app/ts/
├── types/                # ✂️ Can remove (moved to /static/ts/types)
├── utils/                # ✂️ Can remove (moved to /static/ts/utils and /static/ts/writer/utils)
├── api/                  # ✂️ Empty - can remove
├── compilation/          # ✂️ Empty - can remove
├── editor/               # ✂️ Empty - can remove
├── sections/             # ✂️ Empty - can remove
├── ui/                   # ✂️ Empty - can remove
└── viewer/               # ✂️ Empty - can remove
└── services/             # ✅ KEEP (active services)
```

### Cleanup Command (After Full Migration)

```bash
# Remove empty and duplicate directories
rm -rf apps/writer_app/static/writer_app/ts/types
rm -rf apps/writer_app/static/writer_app/ts/utils
rm -rf apps/writer_app/static/writer_app/ts/api
rm -rf apps/writer_app/static/writer_app/ts/compilation
rm -rf apps/writer_app/static/writer_app/ts/editor
rm -rf apps/writer_app/static/writer_app/ts/sections
rm -rf apps/writer_app/static/writer_app/ts/ui
rm -rf apps/writer_app/static/writer_app/ts/viewer

# Keep only
# apps/writer_app/static/writer_app/ts/services/

git add apps/writer_app/static/writer_app/ts/
git commit -m "refactor: Remove duplicate TypeScript directories after consolidation"
```

## Rollback Plan

If removal causes issues:

```bash
# Restore from backup
cp apps/writer_app/static/writer_app/js/writer_app.js.backup apps/writer_app/static/writer_app/js/writer_app.js

# Revert to previous compiled version
npm run build

# Update template to use old version
git checkout apps/writer_app/templates/writer_app/index.html

# Restart server
```

## Migration Timeline

| Phase | Task | Status | ETA |
|-------|------|--------|-----|
| 1 | Consolidate utilities | ✅ | Done |
| 2 | Create unified entry | ⏳ | In Progress |
| 3 | Update service imports | ⏳ | Pending |
| 4 | Update template | ⏳ | Pending |
| 5 | Build & test | ⏳ | Pending |
| 6 | Remove writer_app.js | ⏳ | Pending |

## Success Criteria

✅ Removal is successful when:
1. Template loads TypeScript bundle instead of writer_app.js
2. All writer functionality works identically
3. No console errors
4. Network tab shows proper CSRF headers in API calls
5. Tests pass
6. Browser compatibility verified
7. No regression in any features

---

**Last Updated:** October 29, 2025
**Ready to Remove:** ⏳ Pending Phase 2 & 3 completion
**Current Progress:** Phase 1 Complete (Consolidation done)
