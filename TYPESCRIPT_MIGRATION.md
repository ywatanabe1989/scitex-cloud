# TypeScript Migration Guide

This document describes the migration of the SciTeX Cloud JavaScript codebase to TypeScript modules.

## Overview

The original monolithic `writer_app.js` (2972 lines, 123KB) has been refactored into modular TypeScript files organized in the following structure:

```
static/ts/
├── types/
│   └── index.ts                 # Shared type definitions
├── utils/
│   ├── index.ts                 # Utils export index
│   ├── csrf.ts                  # CSRF token handling
│   ├── storage.ts               # localStorage management
│   ├── api.ts                   # API client with CSRF
│   └── ui.ts                    # UI utilities (toast, modal, etc.)
└── writer/
    ├── index.ts                 # Main writer app entry point
    └── modules/
        ├── index.ts             # Modules export index
        ├── editor.ts            # CodeMirror editor wrapper
        ├── sections.ts          # Section management
        └── compilation.ts       # Compilation manager
```

## Benefits of TypeScript

1. **Type Safety**: Catch errors at compile time instead of runtime
2. **Better IDE Support**: IntelliSense and refactoring tools work better with types
3. **Code Documentation**: Types serve as inline documentation
4. **Maintainability**: Easier to understand code intent and relationships
5. **Scalability**: Better structure for growing codebases
6. **Refactoring**: Safe refactoring with type checking

## Setup Instructions

### 1. Install Dependencies

```bash
cd /home/ywatanabe/proj/scitex-cloud
npm install
```

### 2. Build TypeScript

#### Development Build (with watch mode)
```bash
npm run build:watch
```

#### Production Build
```bash
npm run build
```

#### Type Checking Only
```bash
npm run type-check
```

### 3. Output Location

Compiled JavaScript files are generated in:
- `static/js/` (for shared utilities and types)
- `apps/writer_app/static/writer_app/js/` (for writer-specific code)

## Module Structure

### Shared Utilities (`static/ts/utils/`)

#### `csrf.ts`
```typescript
import { getCsrfToken } from '@/utils/csrf';

const token = getCsrfToken(); // Get CSRF token from multiple sources
```

#### `storage.ts`
```typescript
import { StorageManager, globalStorage } from '@/utils/storage';

// Using singleton instance
globalStorage.save('myKey', { data: 'value' });
const data = globalStorage.load('myKey');

// Or create new instance with custom prefix
const manager = new StorageManager('my_prefix_');
```

#### `api.ts`
```typescript
import { ApiClient, apiClient } from '@/utils/api';

// Using singleton
const response = await apiClient.post('/api/endpoint', { data: 'value' });

// Or create custom instance
const client = new ApiClient('/api/v2');
const result = await client.get('/data');
```

#### `ui.ts`
```typescript
import { showToast, debounce, throttle, Modal } from '@/utils/ui';

// Show notifications
showToast('Success!', 'success', 5000);

// Debounce/throttle functions
const debouncedSave = debounce(() => save(), 1000);

// Work with modals
const modal = new Modal('myModalId');
modal.show();
```

### Shared Types (`static/ts/types/`)

```typescript
import { WriterConfig, EditorState, CompilationJob } from '@/types';

const config: WriterConfig = {
    projectId: '123',
    username: 'john',
    projectSlug: 'my-project',
    isDemo: false,
    isAnonymous: false,
    writerInitialized: true
};
```

### Writer Modules (`static/ts/writer/`)

#### Editor Module
```typescript
import { WriterEditor } from '@/writer/modules/editor';

const editor = new WriterEditor({
    elementId: 'editor-textarea',
    mode: 'text/x-latex',
    theme: 'default'
});

editor.setContent('\\documentclass{article}...');
const content = editor.getContent();
const wordCount = editor.getWordCount();

// Undo/Redo
editor.addToHistory(content, wordCount);
if (editor.canUndo()) editor.undo();
if (editor.canRedo()) editor.redo();
```

#### Sections Manager
```typescript
import { SectionsManager } from '@/writer/modules/sections';

const sections = new SectionsManager();

// Get sections
const allSections = sections.getAll();
const visibleSections = sections.getVisible();

// Manage content
sections.setContent('abstract', 'Abstract text...');
const content = sections.getContent('abstract');

// Switch sections
sections.switchTo('introduction');

// Listen for changes
sections.onUpdate((sections) => {
    console.log('Sections updated:', sections);
});

// Export
const combined = sections.exportCombined();
const wordCount = sections.getTotalWordCount();
```

#### Compilation Manager
```typescript
import { CompilationManager } from '@/writer/modules/compilation';

const compiler = new CompilationManager('/writer');

// Setup callbacks
compiler.onProgress((progress, status) => {
    console.log(`${progress}% - ${status}`);
});

compiler.onComplete((jobId, pdfUrl) => {
    console.log('Compilation complete:', pdfUrl);
});

compiler.onError((error) => {
    console.log('Error:', error);
});

// Compile
const job = await compiler.compile({
    projectSlug: 'my-project',
    docType: 'manuscript',
    content: '\\documentclass{article}...'
});

// Check status
const status = await compiler.getStatus(job.id);

// Cancel
await compiler.cancel(job.id);
```

## Migration Checklist

- [x] Extract CSRF token utility
- [x] Extract storage utility with StorageManager class
- [x] Extract API client with CSRF handling
- [x] Extract UI utilities (toast, modal, debounce, throttle)
- [x] Create shared type definitions
- [x] Create WriterEditor class wrapping CodeMirror
- [x] Create SectionsManager class
- [x] Create CompilationManager class
- [x] Create main writer app entry point
- [x] Setup TypeScript configuration
- [x] Create build scripts
- [ ] Update HTML templates to use compiled modules
- [ ] Test all functionality
- [ ] Update deployment scripts
- [ ] Archive original `writer_app.js`

## Using in HTML Templates

After building TypeScript, include the compiled output in Django templates:

```html
<!-- Load shared utilities -->
<script src="{% static 'js/utils/csrf.js' %}"></script>
<script src="{% static 'js/utils/storage.js' %}"></script>
<script src="{% static 'js/utils/api.js' %}"></script>
<script src="{% static 'js/utils/ui.js' %}"></script>

<!-- Load types -->
<script src="{% static 'js/types/index.js' %}"></script>

<!-- Load writer app (includes all modules) -->
<script src="{% static 'js/writer/index.js' %}" type="module"></script>
```

Or use a bundler like Webpack/Vite for better module resolution.

## Build Configuration

The `tsconfig.json` is configured with:

- **Target**: ES2020 (modern browsers)
- **Module**: ES2020 (native ES modules)
- **Strict Mode**: All strict type checking enabled
- **Path Aliases**: 
  - `@/` → `static/ts/`
  - `@types/` → `static/ts/types/`
  - `@utils/` → `static/ts/utils/`
  - `@writer/` → `static/ts/writer/`

## Development Workflow

1. **Edit TypeScript files** in `static/ts/`
2. **Run TypeScript compiler** in watch mode: `npm run build:watch`
3. **Check for errors**: TypeScript will report type errors
4. **Test changes** in browser with compiled JS files
5. **Commit** both `.ts` source and compiled `.js` files

## Common Issues

### Issue: "CodeMirror is not defined"
**Solution**: Ensure CodeMirror is loaded before the writer app:
```html
<script src="{% static 'vendor/codemirror/codemirror.js' %}"></script>
<script src="{% static 'js/writer/index.js' %}" type="module"></script>
```

### Issue: "getCsrfToken is not a function"
**Solution**: Import from the correct module:
```typescript
import { getCsrfToken } from '@/utils/csrf';
```

### Issue: Module resolution errors
**Solution**: Check that `baseUrl` and `paths` in `tsconfig.json` match your directory structure.

## Performance Considerations

1. **Tree Shaking**: Only used modules are included in final bundle when using a bundler
2. **Code Splitting**: Large modules can be split for lazy loading
3. **Minification**: Production builds should be minified by a bundler
4. **Source Maps**: Generated for easier debugging in development

## Next Steps

1. Install dependencies: `npm install`
2. Build TypeScript: `npm run build`
3. Update Django templates to include compiled JS modules
4. Test all functionality in the browser
5. Archive the original `writer_app.js` file

## References

- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [tsconfig.json Reference](https://www.typescriptlang.org/tsconfig)
- [Modules Guide](https://www.typescriptlang.org/docs/handbook/modules.html)

## Contact & Support

For questions or issues with the TypeScript migration, refer to the project documentation or contact the development team.
