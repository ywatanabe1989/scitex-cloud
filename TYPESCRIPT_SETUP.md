# TypeScript Setup Quick Start

## What Was Done

The monolithic `writer_app.js` (2972 lines, 123KB) has been **refactored into modular TypeScript**:

### Directory Structure
```
static/ts/
├── types/index.ts              # Shared type definitions
├── utils/
│   ├── csrf.ts                 # CSRF token utility
│   ├── storage.ts              # StorageManager class
│   ├── api.ts                  # ApiClient class with CSRF
│   ├── ui.ts                   # UI helpers (toast, modal, debounce, throttle)
│   └── index.ts                # Utils export index
└── writer/
    ├── index.ts                # Main writer app entry point
    └── modules/
        ├── editor.ts           # WriterEditor class (CodeMirror wrapper)
        ├── sections.ts         # SectionsManager class
        ├── compilation.ts      # CompilationManager class
        └── index.ts            # Modules export index

tsconfig.json                    # TypeScript compiler configuration
package.json                     # Build scripts and dependencies
```

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
cd /home/ywatanabe/proj/scitex-cloud
npm install
```

### 2. Build TypeScript
```bash
# Watch mode (development)
npm run build:watch

# One-time build (production)
npm run build

# Type checking only
npm run type-check
```

### 3. Output
Compiled JavaScript is generated in:
- `static/js/` (shared utilities and types)
- `apps/writer_app/static/writer_app/js/` (writer app)

## Key Benefits

✅ **Type Safety** - Errors caught at compile time  
✅ **Better IDE Support** - Full IntelliSense and refactoring  
✅ **Code Documentation** - Types as inline docs  
✅ **Modular** - Small, focused modules instead of monolith  
✅ **Maintainable** - Clear separation of concerns  
✅ **Scalable** - Easy to extend with new features  

## Module Usage Examples

### CSRF Token
```typescript
import { getCsrfToken } from '@/utils/csrf';
const token = getCsrfToken();
```

### Storage
```typescript
import { globalStorage } from '@/utils/storage';
globalStorage.save('key', { data: 'value' });
const data = globalStorage.load('key');
```

### API Client
```typescript
import { apiClient } from '@/utils/api';
const response = await apiClient.post('/api/endpoint', { data: 'value' });
```

### UI Utilities
```typescript
import { showToast, debounce } from '@/utils/ui';
showToast('Success!', 'success');
const debouncedFn = debounce(() => console.log('done'), 1000);
```

### Editor
```typescript
import { WriterEditor } from '@/writer/modules/editor';
const editor = new WriterEditor({ elementId: 'editor-textarea' });
editor.setContent('\\documentclass{article}...');
```

### Sections Manager
```typescript
import { SectionsManager } from '@/writer/modules/sections';
const sections = new SectionsManager();
sections.setContent('abstract', 'Abstract text...');
```

### Compilation
```typescript
import { CompilationManager } from '@/writer/modules/compilation';
const compiler = new CompilationManager('/writer');
const job = await compiler.compile({
    projectSlug: 'my-project',
    docType: 'manuscript',
    content: 'LaTeX content...'
});
```

## Build Scripts

```bash
npm run build              # Compile all TypeScript
npm run build:watch       # Watch mode for development
npm run build:writer      # Build writer-specific modules
npm run build:scholar     # Build scholar-specific modules
npm run type-check        # Type checking only (no output)
npm run dev              # Development with pretty output
npm run lint             # Run ESLint
npm run format           # Format with Prettier
```

## Configuration Files

### `tsconfig.json`
- Target: ES2020 (modern browsers)
- Module: ES2020 (native ES modules)
- Strict: All strict type checking enabled
- Path Aliases: `@/`, `@types/`, `@utils/`, `@writer/`

### `package.json`
- Dependencies: None (uses vanilla TypeScript)
- DevDependencies: TypeScript 5.2, ESLint, Prettier

## Next Steps

1. **Install**: `npm install`
2. **Build**: `npm run build:watch`
3. **Test**: Check compiled output in `static/js/`
4. **Update Templates**: Include compiled JS in Django templates
5. **Deploy**: Include compiled JS in production builds

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "CodeMirror is not defined" | Load CodeMirror before the writer app script |
| "Module not found" | Check `baseUrl` and `paths` in `tsconfig.json` |
| "Type errors" | Run `npm run type-check` to see all issues |
| Build fails | Run `npm install` to ensure dependencies are installed |

## File Sizes Comparison

| Component | Before | After |
|-----------|--------|-------|
| writer_app.js | 123 KB | Split into smaller modules |
| Total size | 123 KB | ~60-80 KB (after minification) |

## Configuration Path Aliases

Use these aliases in TypeScript imports:

```typescript
// Instead of:
import { getCsrfToken } from '../../../utils/csrf';

// Use:
import { getCsrfToken } from '@/utils/csrf';
```

## Git Workflow

```bash
# 1. Edit TypeScript files
nano static/ts/utils/csrf.ts

# 2. Build (watch mode)
npm run build:watch

# 3. Test in browser
# Open browser console to verify

# 4. Commit both source and compiled output
git add static/ts/ static/js/ apps/*/static/*/js/
git commit -m "feat: update TypeScript modules"
```

## Further Reading

See `TYPESCRIPT_MIGRATION.md` for detailed documentation on:
- Module structure and organization
- API reference for each module
- Migration checklist
- Advanced configuration
- Performance considerations

---

**Ready to start?** Run `npm install && npm run build:watch` and start developing with TypeScript!
