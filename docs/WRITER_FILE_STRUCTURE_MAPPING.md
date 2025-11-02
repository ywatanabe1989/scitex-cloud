# Writer App - Complete File Structure Mapping

## Current State vs. Target State

### Current Structure (SPLIT - WRONG)

```
Project Root
├── static/
│   ├── ts/
│   │   └── writer/ ← MOVE TO: apps/writer_app/static/writer_app/ts/
│   │       ├── index.ts (1545 lines)
│   │       ├── helpers.ts (50 lines)
│   │       ├── modules/
│   │       │   ├── index.ts
│   │       │   ├── editor.ts (6.7K)
│   │       │   ├── monaco-editor.ts (25K) ★ LARGE & COMPLEX
│   │       │   ├── sections.ts (9.9K)
│   │       │   ├── compilation.ts (9.2K)
│   │       │   ├── file_tree.ts (15K) ★ COMPLEX
│   │       │   ├── latex-wrapper.ts (5.3K)
│   │       │   ├── pdf-preview.ts (9.7K)
│   │       │   ├── pdf-scroll-zoom.ts (20K) ★ LARGE & COMPLEX
│   │       │   ├── panel-resizer.ts (6.9K)
│   │       │   └── editor-controls.ts (18K) ★ COMPLEX
│   │       └── utils/
│   │           ├── index.ts
│   │           ├── dom.utils.ts
│   │           ├── keyboard.utils.ts
│   │           ├── latex.utils.ts
│   │           └── timer.utils.ts
│   │
│   ├── js/
│   │   ├── writer/ ← AUTO-COMPILED OUTPUT (will be in apps/writer_app after migration)
│   │   │   ├── index.js (compiled)
│   │   │   ├── helpers.js (compiled)
│   │   │   ├── modules/ (compiled)
│   │   │   ├── utils/ (compiled)
│   │   │   ├── *.d.ts (type declarations)
│   │   │   └── *.js.map (source maps)
│   │   │
│   │   └── writer_collaboration.js ← MOVE TO: apps/writer_app/static/writer_app/js/
│   │
│   └── ts/utils/ ← KEEP HERE (shared with other apps)
│       ├── csrf.ts
│       ├── storage.ts
│       └── [other shared utilities]
│
└── apps/
    └── writer_app/
        ├── static/
        │   └── writer_app/
        │       ├── css/ ✓ CORRECT (10 files)
        │       │   ├── arxiv.css
        │       │   ├── codemirror-styling.css
        │       │   ├── editor-enhanced.css
        │       │   ├── history_timeline.css
        │       │   ├── pdf-view-main.css
        │       │   ├── sidebar-improved.css
        │       │   ├── tex-view-main.css
        │       │   ├── tex-view-sidebar.css
        │       │   ├── writer-ui-improved.css
        │       │   └── writer_app.css
        │       │
        │       ├── js/ ✓ CORRECT LOCATION (for compiled output)
        │       │   ├── api-client.js
        │       │   ├── history_timeline.js
        │       │   └── writer_app.js
        │       │   (Note: Compiled TypeScript .js files will go here after build)
        │       │
        │       └── ts/ ← NEEDS TO BE CREATED & POPULATED
        │
        ├── templates/
        │   └── writer_app/ ✓ CORRECT (15+ files)
        │       ├── index.html (main editor)
        │       ├── writer_base.html (master template)
        │       ├── collaborative_editor.html
        │       ├── compilation_view.html
        │       ├── index_partials/
        │       │   ├── demo_banner.html
        │       │   ├── init_prompt.html
        │       │   ├── main_editor.html
        │       │   ├── sidebar.html
        │       │   └── word_count.html
        │       └── legacy/ (old templates)
        │
        ├── views/
        ├── models/
        ├── services/
        └── [Python files - all correct]
```

---

### Target Structure (UNIFIED - CORRECT)

```
Project Root
├── static/
│   ├── ts/
│   │   ├── utils/ ← KEEP (shared with other apps)
│   │   │   ├── csrf.ts
│   │   │   ├── storage.ts
│   │   │   └── [other shared utilities]
│   │   │
│   │   └── [other app-specific TS if any]
│   │
│   └── js/
│       ├── [other compiled JS if any]
│       └── [NO writer files here]
│
└── apps/
    └── writer_app/
        ├── static/
        │   └── writer_app/
        │       ├── ts/ ← TYPESCRIPT SOURCES (18 files)
        │       │   ├── index.ts (1545 lines) ★ MAIN ENTRY
        │       │   ├── helpers.ts (50 lines)
        │       │   ├── modules/
        │       │   │   ├── index.ts
        │       │   │   ├── editor.ts (6.7K)
        │       │   │   ├── monaco-editor.ts (25K) ★
        │       │   │   ├── sections.ts (9.9K)
        │       │   │   ├── compilation.ts (9.2K)
        │       │   │   ├── file_tree.ts (15K) ★
        │       │   │   ├── latex-wrapper.ts (5.3K)
        │       │   │   ├── pdf-preview.ts (9.7K)
        │       │   │   ├── pdf-scroll-zoom.ts (20K) ★
        │       │   │   ├── panel-resizer.ts (6.9K)
        │       │   │   └── editor-controls.ts (18K) ★
        │       │   └── utils/
        │       │       ├── index.ts
        │       │       ├── dom.utils.ts
        │       │       ├── keyboard.utils.ts
        │       │       ├── latex.utils.ts
        │       │       └── timer.utils.ts
        │       │
        │       ├── js/ ← COMPILED OUTPUT (auto-generated)
        │       │   ├── index.js ← FROM: index.ts
        │       │   ├── helpers.js ← FROM: helpers.ts
        │       │   ├── modules/
        │       │   │   ├── index.js (compiled)
        │       │   │   ├── editor.js (compiled)
        │       │   │   ├── monaco-editor.js (compiled)
        │       │   │   ├── sections.js (compiled)
        │       │   │   ├── compilation.js (compiled)
        │       │   │   ├── file_tree.js (compiled)
        │       │   │   ├── latex-wrapper.js (compiled)
        │       │   │   ├── pdf-preview.js (compiled)
        │       │   │   ├── pdf-scroll-zoom.js (compiled)
        │       │   │   ├── panel-resizer.js (compiled)
        │       │   │   └── editor-controls.js (compiled)
        │       │   ├── utils/
        │       │   │   ├── index.js (compiled)
        │       │   │   ├── dom.utils.js (compiled)
        │       │   │   ├── keyboard.utils.js (compiled)
        │       │   │   ├── latex.utils.js (compiled)
        │       │   │   └── timer.utils.js (compiled)
        │       │   ├── *.d.ts (type declarations, auto-generated)
        │       │   ├── *.js.map (source maps, auto-generated)
        │       │   ├── api-client.js (existing)
        │       │   ├── history_timeline.js (existing)
        │       │   ├── writer_app.js (existing)
        │       │   └── writer_collaboration.js ← MOVED HERE
        │       │
        │       ├── css/ ← CSS (10 files, unchanged)
        │       │   ├── arxiv.css
        │       │   ├── codemirror-styling.css
        │       │   ├── editor-enhanced.css
        │       │   ├── history_timeline.css
        │       │   ├── pdf-view-main.css
        │       │   ├── sidebar-improved.css
        │       │   ├── tex-view-main.css
        │       │   ├── tex-view-sidebar.css
        │       │   ├── writer-ui-improved.css
        │       │   └── writer_app.css
        │       │
        │       └── .old/ (old CSS, unchanged)
        │
        ├── templates/
        │   └── writer_app/ ← TEMPLATES (15+ files, unchanged)
        │       ├── index.html ← NEEDS SCRIPT TAG UPDATE
        │       ├── writer_base.html ← NEEDS CSS PATH UPDATE
        │       ├── collaborative_editor.html
        │       ├── compilation_view.html
        │       └── [other templates]
        │
        ├── views/ ← PYTHON (unchanged)
        ├── models/ ← PYTHON (unchanged)
        ├── services/ ← PYTHON (unchanged)
        └── [All Python files in correct location]
```

---

## File Movement Details

### Group 1: TypeScript Modules (11 files)

| File | Lines | From | To | Type |
|------|-------|------|-----|------|
| `modules/editor.ts` | 6.7K | `static/ts/writer/modules/` | `apps/writer_app/static/writer_app/ts/modules/` | MOVE |
| `modules/monaco-editor.ts` | 25K | `static/ts/writer/modules/` | `apps/writer_app/static/writer_app/ts/modules/` | MOVE ★ LARGE |
| `modules/sections.ts` | 9.9K | `static/ts/writer/modules/` | `apps/writer_app/static/writer_app/ts/modules/` | MOVE |
| `modules/compilation.ts` | 9.2K | `static/ts/writer/modules/` | `apps/writer_app/static/writer_app/ts/modules/` | MOVE |
| `modules/file_tree.ts` | 15K | `static/ts/writer/modules/` | `apps/writer_app/static/writer_app/ts/modules/` | MOVE ★ COMPLEX |
| `modules/latex-wrapper.ts` | 5.3K | `static/ts/writer/modules/` | `apps/writer_app/static/writer_app/ts/modules/` | MOVE |
| `modules/pdf-preview.ts` | 9.7K | `static/ts/writer/modules/` | `apps/writer_app/static/writer_app/ts/modules/` | MOVE |
| `modules/pdf-scroll-zoom.ts` | 20K | `static/ts/writer/modules/` | `apps/writer_app/static/writer_app/ts/modules/` | MOVE ★ LARGE |
| `modules/panel-resizer.ts` | 6.9K | `static/ts/writer/modules/` | `apps/writer_app/static/writer_app/ts/modules/` | MOVE |
| `modules/editor-controls.ts` | 18K | `static/ts/writer/modules/` | `apps/writer_app/static/writer_app/ts/modules/` | MOVE ★ COMPLEX |
| `modules/index.ts` | ~1K | `static/ts/writer/modules/` | `apps/writer_app/static/writer_app/ts/modules/` | MOVE |

### Group 2: TypeScript Utilities (4 files)

| File | From | To | Type |
|------|------|-----|------|
| `utils/dom.utils.ts` | `static/ts/writer/utils/` | `apps/writer_app/static/writer_app/ts/utils/` | MOVE |
| `utils/keyboard.utils.ts` | `static/ts/writer/utils/` | `apps/writer_app/static/writer_app/ts/utils/` | MOVE |
| `utils/latex.utils.ts` | `static/ts/writer/utils/` | `apps/writer_app/static/writer_app/ts/utils/` | MOVE |
| `utils/timer.utils.ts` | `static/ts/writer/utils/` | `apps/writer_app/static/writer_app/ts/utils/` | MOVE |

### Group 3: Root TypeScript Files (2 files)

| File | Lines | From | To | Type |
|------|-------|------|-----|------|
| `index.ts` | **1545** | `static/ts/writer/` | `apps/writer_app/static/writer_app/ts/` | MOVE ★ MAIN ENTRY |
| `helpers.ts` | 50 | `static/ts/writer/` | `apps/writer_app/static/writer_app/ts/` | MOVE |

### Group 4: JavaScript Files (1 file)

| File | From | To | Type |
|------|------|-----|------|
| `writer_collaboration.js` | `static/js/` | `apps/writer_app/static/writer_app/js/` | MOVE |

---

## Compiled Output (Auto-Generated by Build)

After running `npm run build:writer`, these files will be automatically created:

### In `apps/writer_app/static/writer_app/js/`

**From TypeScript modules (36+ files generated):**
- `index.js` + `index.d.ts` + `index.js.map`
- `helpers.js` + `helpers.d.ts` + `helpers.js.map`
- `modules/index.js`, `modules/editor.js`, etc. (11 files + declarations + maps)
- `utils/index.js`, `utils/dom.utils.js`, etc. (4 files + declarations + maps)

**Total auto-generated:** ~36+ files

---

## Import Path Resolution (No Changes Needed!)

The TypeScript files use these import patterns:

### Relative Imports (Work After Move)
```typescript
// In ./modules/index.ts
export { WriterEditor, type EditorConfig } from './editor.js';
export { EnhancedEditor, type MonacoEditorConfig } from './monaco-editor.js';
// These work because we're moving the entire tree intact
```

### Alias Imports (Resolved by tsconfig)
```typescript
// In ./index.ts
import { getCsrfToken } from '@/utils/csrf.js';      // → static/ts/utils/
import { writerStorage } from '@/utils/storage.js';  // → static/ts/utils/
import { getWriterConfig } from './helpers.js';       // → ./helpers.ts (relative)

// tsconfig.json maps:
// "@/utils/*": ["utils/*"]                          // → static/ts/utils/
// "@/writer/utils/*": ["writer/utils/*"]            // → apps/writer_app/.../ts/utils/
// "@/writer/*": ["writer/*"]                        // → apps/writer_app/.../ts/
```

**Key Point:** No code changes needed in TypeScript files! The build system handles path resolution.

---

## Configuration File Changes

### tsconfig.json Changes

**BEFORE:**
```json
{
  "compilerOptions": {
    "rootDir": "./static/ts",
    "outDir": "./static/js",
    "baseUrl": "./static/ts",
    "paths": {
      "@/writer/utils": ["writer/utils"],
      "@/writer/*": ["writer/*"],
      "@/utils/*": ["utils/*"]
    }
  },
  "include": ["static/ts/**/*"]
}
```

**AFTER:**
```json
{
  "compilerOptions": {
    "rootDir": "./static/ts",  // Keep for shared code
    "outDir": "./static/js",   // Keep for shared code
    "baseUrl": "./static/ts",
    "paths": {
      "@/writer/utils": ["../apps/writer_app/static/writer_app/ts/utils"],
      "@/writer/*": ["../apps/writer_app/static/writer_app/ts/*"],
      "@/utils/*": ["utils/*"]  // Still shared, stays in root
    }
  },
  "include": [
    "static/ts/**/*",
    "apps/writer_app/static/writer_app/ts/**/*"  // ADD THIS LINE
  ]
}
```

### package.json Changes

**BEFORE:**
```json
{
  "scripts": {
    "build": "tsc",
    "build:writer": "tsc --rootDir static/ts/writer --outDir apps/writer_app/static/writer_app/js"
  }
}
```

**AFTER:**
```json
{
  "scripts": {
    "build": "tsc",
    "build:writer": "tsc --rootDir apps/writer_app/static/writer_app/ts --outDir apps/writer_app/static/writer_app/js"
  }
}
```

---

## Template Script References (Need Updating)

### writer_base.html

**Line with issue:**
```html
<link rel="stylesheet" href="{% static 'css/writer_app/writer.css' %}">
```

**Problem:** File doesn't exist at that path (CSS files are in `writer_app/css/`, not `css/writer_app/`)

**Fix options:**
1. Change to correct CSS file: `{% static 'writer_app/css/writer_app.css' %}`
2. Or remove entirely if not needed (check if this CSS is duplicated elsewhere)

---

### index.html

**Script tags that need updating:**

**BEFORE:**
```html
<!-- Line ~280-290 -->
<script type="module" src="{% static 'js/writer/index.js' %}?v={{ build_id|default:'dev' }}"></script>
<script src="{% static 'writer_app/js/api-client.js' %}?v={{ build_id|default:'dev' }}"></script>
<script src="{% static 'js/writer_collaboration.js' %}?v={{ build_id|default:'dev' }}"></script>
```

**AFTER:**
```html
<!-- Line ~280-290 -->
<script type="module" src="{% static 'writer_app/js/index.js' %}?v={{ build_id|default:'dev' }}"></script>
<script src="{% static 'writer_app/js/api-client.js' %}?v={{ build_id|default:'dev' }}"></script>
<script src="{% static 'writer_app/js/writer_collaboration.js' %}?v={{ build_id|default:'dev' }}"></script>
```

**Changes:**
- `'js/writer/index.js'` → `'writer_app/js/index.js'`
- `'js/writer_collaboration.js'` → `'writer_app/js/writer_collaboration.js'`
- `'writer_app/js/api-client.js'` stays the same (already correct)

---

## Summary: Files Affected

### Total Files to Move: 20

**TypeScript sources:** 18 files  
**JavaScript files:** 1 file  
**Configuration files:** 2 files  
**Template files:** 2 files  

### Total Directory Changes: 4

1. Create `apps/writer_app/static/writer_app/ts/`
2. Create `apps/writer_app/static/writer_app/ts/modules/`
3. Create `apps/writer_app/static/writer_app/ts/utils/`
4. Update `apps/writer_app/static/writer_app/ts/utils/index.ts` if needed

### Files That DON'T Change: 30+

- Python files (views, models, services, etc.) - all stay in place
- CSS files (10 files) - all stay in place
- HTML templates (except script tags) - all stay in place
- Existing JS files in `apps/writer_app/static/writer_app/js/` - stay in place
- Shared utilities in `static/ts/utils/` - stay in place

---

## Validation Checklist

After migration, verify:

```
Directory Structure:
  [ ] apps/writer_app/static/writer_app/ts/ exists
  [ ] apps/writer_app/static/writer_app/ts/modules/ has 11 files
  [ ] apps/writer_app/static/writer_app/ts/utils/ has 4 files
  [ ] static/ts/writer/ is empty or deleted
  [ ] static/js/writer_collaboration.js is deleted or moved

Build System:
  [ ] npm run build succeeds
  [ ] npm run build:writer succeeds
  [ ] apps/writer_app/static/writer_app/js/index.js exists
  [ ] apps/writer_app/static/writer_app/js/modules/ contains compiled .js files
  [ ] No errors in TypeScript compilation

Templates:
  [ ] writer_base.html CSS reference is fixed
  [ ] index.html script tags use new paths
  [ ] No other templates reference old paths

Runtime:
  [ ] Browser loads /writer/ without 404 errors
  [ ] Network tab shows scripts from writer_app/static/
  [ ] No console.log errors
  [ ] Editor initializes
  [ ] PDF preview renders
  [ ] File tree loads
```

