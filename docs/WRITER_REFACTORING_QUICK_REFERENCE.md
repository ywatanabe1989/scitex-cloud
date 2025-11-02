# Writer App Refactoring - Quick Reference

## The Problem: Split Structure

```
Current (WRONG):                  Target (CORRECT):
┌─────────────────────────────┐  ┌─────────────────────────────┐
│ static/ts/writer/           │  │ apps/writer_app/            │
│  ├── index.ts ← SOURCE       │  │  ├── static/                │
│  ├── helpers.ts             │  │  │   └── writer_app/         │
│  ├── modules/ (11 files)    │  │  │       ├── ts/ ← SOURCE    │
│  └── utils/ (4 files)       │  │  │       │   ├── index.ts    │
│                             │  │  │       │   └── modules/    │
│ Compiles to:                │  │  │       ├── js/ ← COMPILED  │
│ static/js/writer/           │  │  │       │   └── index.js    │
│  ├── index.js ← COMPILED    │  │  │       └── css/            │
│  ├── modules/ (11 files)    │  │  └── templates/             │
│  └── utils/ (4 files)       │  │      └── writer_app/        │
│                             │  │          └── index.html     │
│ WRONG: split across dirs    │  │ CORRECT: app-contained      │
└─────────────────────────────┘  └─────────────────────────────┘
```

---

## Files to Move

### Phase 1: TypeScript Sources (18 files)

**FROM:** `static/ts/writer/`  
**TO:** `apps/writer_app/static/writer_app/ts/`

```
Root files:
  index.ts (1545 lines - MAIN ENTRY)
  helpers.ts (50 lines)

modules/ (11 modules):
  index.ts
  editor.ts
  monaco-editor.ts (25K - complex)
  sections.ts
  compilation.ts
  file_tree.ts (15K - complex)
  latex-wrapper.ts
  pdf-preview.ts
  pdf-scroll-zoom.ts (20K - complex)
  panel-resizer.ts
  editor-controls.ts (18K - complex)

utils/ (4 utilities):
  index.ts
  dom.utils.ts
  keyboard.utils.ts
  latex.utils.ts
  timer.utils.ts
```

### Phase 2: JavaScript File (1 file)

**FROM:** `static/js/writer_collaboration.js`  
**TO:** `apps/writer_app/static/writer_app/js/writer_collaboration.js`

**Note:** This is legacy/unused but should be moved for organization

---

## Build Configuration Changes

### tsconfig.json (Update paths)

```json
// BEFORE
"paths": {
  "@/writer/utils": ["writer/utils"],
  "@/writer/*": ["writer/*"]
}

// AFTER
"paths": {
  "@/writer/utils": ["../apps/writer_app/static/writer_app/ts/utils"],
  "@/writer/*": ["../apps/writer_app/static/writer_app/ts/*"]
}

// Also add to includes:
"include": [
  "static/ts/**/*",
  "apps/writer_app/static/writer_app/ts/**/*"  // ADD THIS
]
```

### package.json (Update build:writer script)

```json
// BEFORE
"build:writer": "tsc --rootDir static/ts/writer --outDir apps/writer_app/static/writer_app/js"

// AFTER
"build:writer": "tsc --rootDir apps/writer_app/static/writer_app/ts --outDir apps/writer_app/static/writer_app/js"
```

---

## Template Updates

### writer_base.html

```html
<!-- BEFORE -->
<link rel="stylesheet" href="{% static 'css/writer_app/writer.css' %}">

<!-- AFTER -->
<link rel="stylesheet" href="{% static 'writer_app/css/writer_app.css' %}">
```

### index.html

```html
<!-- BEFORE -->
<script type="module" src="{% static 'js/writer/index.js' %}"></script>
<script src="{% static 'js/writer_collaboration.js' %}"></script>

<!-- AFTER -->
<script type="module" src="{% static 'writer_app/js/index.js' %}"></script>
<script src="{% static 'writer_app/js/writer_collaboration.js' %}"></script>
```

---

## Migration Steps (Fast Reference)

### Step 1: Copy TypeScript Sources
```bash
mkdir -p apps/writer_app/static/writer_app/ts
cp -r static/ts/writer/* apps/writer_app/static/writer_app/ts/
```

### Step 2: Move JavaScript File
```bash
mv static/js/writer_collaboration.js apps/writer_app/static/writer_app/js/
```

### Step 3: Update Configuration Files
- Edit `tsconfig.json` (see above)
- Edit `package.json` (see above)

### Step 4: Update Templates
- Edit `apps/writer_app/templates/writer_app/writer_base.html`
- Edit `apps/writer_app/templates/writer_app/index.html`

### Step 5: Build & Test
```bash
npm run build:writer
npm run build

# Test in browser
# Open /writer/ and check:
# - No console errors
# - All scripts load from writer_app/static/
# - Editor initializes correctly
# - PDF preview works
# - File tree loads
```

### Step 6: Cleanup
```bash
rm -rf static/ts/writer/
rm -f static/js/writer_collaboration.js
```

---

## Import Paths (No Changes Needed!)

The TypeScript files use:
1. **Relative imports** (work after move):
   ```typescript
   import { WriterEditor } from './modules/editor.js';
   ```

2. **Alias imports** (handled by tsconfig):
   ```typescript
   import { getCsrfToken } from '@/utils/csrf.js';  // ← From root static
   ```

The build system automatically handles path resolution!

---

## What's Already in the Right Place

✓ CSS files (10 files) - in `apps/writer_app/static/writer_app/css/`  
✓ HTML templates (15+ files) - in `apps/writer_app/templates/writer_app/`  
✓ Python backend (30+ files) - in `apps/writer_app/`  
✓ Compiled JS output location - `apps/writer_app/static/writer_app/js/`  

Only TypeScript **sources** need to move!

---

## Risk & Complexity

| Phase | Risk | Effort | Complexity |
|-------|------|--------|------------|
| 1: Copy TypeScript | LOW | 2 min | File operations only |
| 2: Move JS | LOW | 1 min | Single file |
| 3: Config updates | MEDIUM | 10 min | tsconfig & package.json |
| 4: Template updates | LOW | 5 min | Static references |
| 5: Build & test | MEDIUM | 30 min | Verification |
| 6: Cleanup | LOW | 2 min | Removing files |

**Total Time:** ~50 minutes  
**Total Risk:** Medium (well-contained, one app only)

---

## Verification Checklist

After each phase:

- [ ] Files exist in new location
- [ ] `npm run build:writer` succeeds
- [ ] No compile errors in TypeScript
- [ ] No console errors in browser
- [ ] Scripts load from `writer_app/static/` in Network tab
- [ ] Editor initializes and works
- [ ] PDF preview renders
- [ ] File tree loads and responds
- [ ] All hotkeys work
- [ ] No 404 errors in DevTools

---

## Key Dependencies (Won't Break)

These files stay in root (shared with other apps):
- `@/utils/csrf.js` - CSRF token (shared)
- `@/utils/storage.js` - Storage wrapper (shared)
- Common DOM/keyboard utilities

The writer imports these and they remain unchanged - no refactoring impact!

---

## Questions?

Refer to `/docs/WRITER_APP_REFACTORING_ANALYSIS.md` for complete details:
- Full file listings
- Detailed dependency analysis
- Line-by-line code references
- Complete migration checklist
- Risk assessment by file
- Git/version control guidance

