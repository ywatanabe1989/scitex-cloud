# TypeScript Quick Reference Guide

## Project Structure After Consolidation

```
/static/ts/
├── types/
│   └── index.ts
│       ├── WriterConfig
│       ├── DocumentType, SectionName
│       ├── Section, SectionMetadata
│       ├── EditorState, EditorOptions
│       ├── WordCounts, DocumentStats
│       ├── CompilationJob
│       ├── HistoryEntry
│       └── ApiResponse (and all variants)
│
├── utils/
│   ├── csrf.ts ........................... getCsrfToken(), createHeadersWithCsrf()
│   ├── storage.ts ........................ StorageManager, globalStorage, writerStorage
│   ├── api.ts ........................... ApiClient, apiClient
│   ├── ui.ts ............................ showToast(), debounce(), throttle(), etc.
│   └── index.ts ......................... Re-exports all utilities
│
└── writer/
    ├── utils/
    │   ├── dom.utils.ts ................. DOM manipulation helpers
    │   ├── keyboard.utils.ts ............ Keyboard event handling
    │   ├── latex.utils.ts ............... LaTeX processing
    │   ├── timer.utils.ts ............... debounce, throttle, SimpleTimer
    │   └── index.ts ..................... Re-exports all writer utils
    │
    ├── modules/ (in static/writer/ after migration)
    │   ├── editor.ts .................... WriterEditor class
    │   ├── sections.ts .................. SectionsManager class
    │   ├── compilation.ts ............... CompilationManager class
    │   └── index.ts ..................... Module exports
    │
    └── index.ts ......................... Main writer app entry point
```

## Common Imports

### CSRF & Authentication
```typescript
import { getCsrfToken, createHeadersWithCsrf } from '@/utils/csrf';

const token = getCsrfToken();
const headers = createHeadersWithCsrf({ 'X-Custom': 'value' });
```

### Storage
```typescript
import { StorageManager, globalStorage, writerStorage } from '@/utils/storage';

// Use singleton
globalStorage.save('editorState', data);
globalStorage.load('editorState');

// Or custom instance
const storage = new StorageManager('myapp_');
storage.setItem('key', data);
```

### Types
```typescript
import {
    WriterConfig,
    DocumentType,
    SectionName,
    Section,
    EditorState,
    ApiResponse,
    CompilationJob,
} from '@/types';

const config: WriterConfig = window.WRITER_CONFIG;
const response: ApiResponse<SectionResponse> = await apiClient.get(...);
```

### DOM Utils
```typescript
import {
    querySelector,
    querySelectorAll,
    addClass,
    removeClass,
    createElement,
    setVisibility,
} from '@/writer/utils/dom.utils';

const button = querySelector<HTMLButtonElement>('#save-btn');
addClass(button, 'btn-primary');
```

### Keyboard
```typescript
import { registerShortcut, formatShortcut } from '@/writer/utils/keyboard.utils';

const unregister = registerShortcut({
    key: 's',
    ctrl: true,
    callback: (event) => console.log('Ctrl+S pressed')
});
```

### LaTeX
```typescript
import {
    extractTextFromLatex,
    convertToLatex,
    isLatexContent,
    validateLatexSyntax,
} from '@/writer/utils/latex.utils';

const cleanText = extractTextFromLatex(latexCode);
const { valid, errors } = validateLatexSyntax(code);
```

### Timing
```typescript
import { debounce, throttle, SimpleTimer, wait } from '@/writer/utils/timer.utils';

const debouncedSave = debounce(save, 1000);
const throttledScroll = throttle(handleScroll, 100);

const timer = new SimpleTimer();
timer.start((elapsed) => console.log(`${elapsed}ms passed`));
```

### API Client
```typescript
import { apiClient } from '@/utils/api';

const response = await apiClient.get<SectionResponse>('/writer/api/section/introduction/');
const saved = await apiClient.post<ApiResponse>('/writer/api/save/', { content });
```

### UI Utilities
```typescript
import { showToast, debounce, throttle, confirm } from '@/utils/ui';

showToast('Saved successfully', 'success');
const confirmed = await confirm('Are you sure?');
```

## Type Safety Examples

### Accessing Writer Config
```typescript
import { WriterConfig } from '@/types';

const config: WriterConfig = {
    projectId: '123',
    username: 'john',
    projectSlug: 'my-project',
    isDemo: false,
    isAnonymous: false,
    writerInitialized: true,
    csrfToken: 'abc123'
};
```

### Working with Sections
```typescript
import { Section, SectionName, DocumentType } from '@/types';

const section: Section = {
    name: 'introduction' as SectionName,
    title: 'Introduction',
    content: 'This is the introduction...',
    wordCount: 250,
    docType: 'manuscript' as DocumentType,
    isDirty: false,
    isSaving: false,
};
```

### API Responses
```typescript
import { ApiResponse, SectionResponse } from '@/types';

const response: SectionResponse = await apiClient.get('/api/section/');
if (response.success) {
    console.log(response.data?.content);
} else {
    console.error(response.error);
}
```

## Migration Checklist for Existing Code

### When Adding New Code
- [ ] Import types from `@/types`
- [ ] Import shared utils from `@/utils`
- [ ] Import writer utils from `@/writer/utils`
- [ ] Use `StorageManager` instead of direct localStorage access
- [ ] Use `getCsrfToken()` instead of custom implementations

### When Updating Old Code
- [ ] Replace old import paths with new ones
- [ ] Use centralized types instead of local definitions
- [ ] Remove duplicate utility functions
- [ ] Use singleton storage instances
- [ ] Add proper TypeScript types

### Before → After

**Before:**
```typescript
import { getCsrfToken } from '@/writer_app/ts/utils/csrf';
import { StorageManager } from '@/writer_app/ts/utils/storage.utils';
import { WriterConfig } from '@/writer_app/ts/types/api.types';

const token = getCsrfToken();
const storage = new StorageManager('myapp_');
storage.setItem('key', data);
```

**After:**
```typescript
import { getCsrfToken } from '@/utils/csrf';
import { StorageManager } from '@/utils/storage';
import { WriterConfig } from '@/types';

const token = getCsrfToken();
const storage = new StorageManager('myapp_');
storage.setItem('key', data);
```

## FAQ

### Q: Where should I put new utilities?
A:
- If generic/shared → `/static/ts/utils/`
- If writer-specific → `/static/ts/writer/utils/`
- If app-specific → `apps/[appname]/static/[appname]/ts/utils/`

### Q: How do I access CSRF token?
A:
```typescript
import { getCsrfToken } from '@/utils/csrf';
const token = getCsrfToken(); // Checks multiple sources automatically
```

### Q: Can I use localStorage directly?
A:
It's better to use `StorageManager` for consistency:
```typescript
import { StorageManager } from '@/utils/storage';
const storage = new StorageManager('myprefix_');
storage.save('key', data);
```

### Q: Where are the type definitions?
A: All in `/static/ts/types/index.ts`. Import from `@/types`.

### Q: How do I use debounce/throttle?
A:
```typescript
import { debounce, throttle } from '@/writer/utils/timer.utils';
// or
import { debounce, throttle } from '@/utils/ui'; // Also available here
```

### Q: Can I create a custom StorageManager instance?
A: Yes, with a custom prefix:
```typescript
const myStorage = new StorageManager('myapp_');
myStorage.save('key', data);
```

## Path Aliases Configuration

In `tsconfig.json`, these aliases are available:
```json
{
    "compilerOptions": {
        "baseUrl": ".",
        "paths": {
            "@/*": ["static/ts/*"],
            "@/utils/*": ["static/ts/utils/*"],
            "@/types": ["static/ts/types/index.ts"],
            "@/writer/utils/*": ["static/ts/writer/utils/*"]
        }
    }
}
```

## Build Commands

```bash
# Development (watch mode)
npm run build:watch

# Production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint

# Formatting
npm run format
```

## Resources

- **TYPESCRIPT_CONSOLIDATION_SUMMARY.md** - Detailed consolidation work
- **TYPESCRIPT_MIGRATION_PROGRESS.md** - Phase progress and metrics
- **/static/ts/README.md** - Module documentation
- **TYPESCRIPT_SETUP.md** - Installation and setup
- **TYPESCRIPT_MIGRATION.md** - Complete reference

---

**Last Updated:** October 29, 2025
**Version:** 1.0
**Status:** Ready for Phase 2 Integration
