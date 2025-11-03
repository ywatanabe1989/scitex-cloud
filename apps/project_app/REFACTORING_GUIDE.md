<!-- ---
!-- Timestamp: 2025-11-03 23:16:00
!-- Author: Claude Code
!-- File: /home/ywatanabe/proj/scitex-cloud/apps/project_app/REFACTORING_GUIDE.md
!-- --- -->

# Project App Refactoring Guide

## Learning from writer_app (Well-Organized Example)

### Writer App Structure (Follow This Pattern)

```
writer_app/
├── models/                    # Split by domain
│   ├── collaboration.py      # 41 lines - WriterPresence
│   ├── core.py               # 78 lines - Manuscript
│   ├── arxiv.py              # ArXiv submission models
│   └── __init__.py           # Exports all models
│
├── views/                     # Split by feature (~500-1000 lines each)
│   ├── main_views.py         # 561 lines - Core writer views
│   ├── api_views.py          # 1069 lines - REST API
│   ├── arxiv_views.py        # 578 lines - ArXiv submission
│   ├── editor_views.py       # 571 lines - Editor features
│   ├── workspace_views.py    # 43 lines - Workspace init
│   ├── main_views_old.py     # 3393 lines - ARCHIVED (kept for reference)
│   └── __init__.py           # 157 lines - Exports common views
│
├── services/                  # Business logic
│   ├── writer_service.py     # Delegates to scitex.writer
│   ├── compiler.py           # LaTeX compilation
│   ├── arxiv/                # ArXiv integration
│   └── utils.py              # Shared utilities
│
└── static/writer_app/
    ├── ts/                   # TypeScript SOURCE
    │   ├── index.ts
    │   ├── helpers.ts
    │   ├── modules/          # Feature modules
    │   │   ├── editor.ts
    │   │   ├── compilation.ts
    │   │   └── file_tree.ts
    │   └── utils/            # Utilities
    │       ├── dom.utils.ts
    │       └── logger.ts (PLANNED)
    │
    └── js/                   # Compiled OUTPUT (never edit!)
        ├── index.js
        ├── index.d.ts
        ├── index.js.map
        └── (all compiled from ts/)
```

**Key Observations:**
- ✅ Each view file < 1100 lines
- ✅ Old code archived (main_views_old.py) not deleted
- ✅ TypeScript organized in modules
- ✅ Clear separation: source (ts/) vs compiled (js/)

---

## Refactoring Plan for project_app

### Current Problems

| File | Lines | Problem |
|------|-------|---------|
| `base_views.py` | 2864 | Too large, multiple concerns mixed |
| `models.py` | 1230 | Should be split into collaboration.py, core.py |
| `static/project_app/js/settings.js` | Plain JS | No types, hard to debug |
| Forms | - | Submission unclear, no error handling |

### Phase 1: Split Backend (1-2 hours)

#### Step 1: Create views/ directory

```bash
mkdir -p apps/project_app/views
```

#### Step 2: Split base_views.py

**Create `views/collaboration_views.py`** (~400 lines)
```python
# Move from base_views.py:
- project_collaborate
- project_members
- accept_invitation
- decline_invitation
- add_collaborator (POST handler)
- remove_collaborator (POST handler)
```

**Create `views/settings_views.py`** (~600 lines)
```python
# Move from base_views.py:
- project_settings (main settings view)
- All POST action handlers (update_general, update_visibility, delete_repository)
```

**Keep in `views/project_views.py`** (rename base_views.py)
```python
- project_list
- project_detail
- project_create
- project_edit
- project_delete
- project_directory (file browsing)
```

**Create `views/__init__.py`**
```python
# Export commonly used views
from .project_views import project_detail, project_create
from .collaboration_views import accept_invitation
from .settings_views import project_settings

__all__ = [...]
```

### Phase 2: TypeScript Migration (2-3 hours)

#### Step 1: Setup TypeScript for project_app

```bash
cd apps/project_app/static/project_app
mkdir -p ts/modules ts/utils
```

#### Step 2: Create tsconfig for project_app

**`apps/project_app/static/project_app/tsconfig.json`:**
```json
{
  "extends": "../../../../frontend/tsconfig.json",
  "compilerOptions": {
    "rootDir": "./ts",
    "outDir": "./js",
    "baseUrl": "./ts"
  },
  "include": ["ts/**/*"],
  "exclude": ["js/**/*", "node_modules"]
}
```

#### Step 3: Migrate settings.js → settings.ts

**Create `ts/settings.ts`:**
```typescript
// Type definitions
interface CollaboratorSearchResult {
    id: number;
    username: string;
    email: string | null;
    full_name: string;
}

interface APIResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
}

// Central logger (like writer_app)
const logger = {
    info: (msg: string, data?: any) => console.log(`[Settings] ${msg}`, data || ''),
    error: (msg: string, err?: any) => console.error(`[Settings ERROR] ${msg}`, err || ''),
    warn: (msg: string, data?: any) => console.warn(`[Settings WARN] ${msg}`, data || '')
};

// API utilities
class CollaborationAPI {
    static async searchUsers(query: string): Promise<CollaboratorSearchResult[]> {
        try {
            const response = await fetch(`/api/users/search/?q=${encodeURIComponent(query)}`);
            const data: APIResponse<{ users: CollaboratorSearchResult[] }> = await response.json();

            if (!response.ok) {
                logger.error('User search failed', { status: response.status, data });
                return [];
            }

            logger.info('User search success', { count: data.data?.users.length });
            return data.data?.users || [];
        } catch (error) {
            logger.error('User search exception', error);
            return [];
        }
    }

    static async addCollaborator(username: string, role: string): Promise<boolean> {
        logger.info('Adding collaborator', { username, role });
        // Form will submit naturally - this is just for logging
        return true;
    }
}

// Initialize autocomplete
document.addEventListener('DOMContentLoaded', () => {
    logger.info('Collaboration module initialized');

    const input = document.getElementById('collaboratorUsername') as HTMLInputElement | null;
    if (input) {
        setupCollaboratorAutocomplete(input);
    }
});

function setupCollaboratorAutocomplete(input: HTMLInputElement): void {
    // ... autocomplete logic with proper types
}
```

#### Step 4: Build

```bash
cd frontend
npm run build   # Compiles all TypeScript
# Or specifically:
# tsc -p ../apps/project_app/static/project_app/tsconfig.json
```

### Phase 3: Central Logging (30 minutes)

**Create `static/ts/utils/logger.ts`:**
```typescript
export enum LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3
}

export class Logger {
    constructor(private module: string, private minLevel: LogLevel = LogLevel.INFO) {}

    debug(msg: string, data?: any) {
        if (this.minLevel <= LogLevel.DEBUG) {
            console.debug(`[${this.module}] ${msg}`, data || '');
        }
    }

    info(msg: string, data?: any) {
        if (this.minLevel <= LogLevel.INFO) {
            console.log(`[${this.module}] ${msg}`, data || '');
        }
    }

    warn(msg: string, data?: any) {
        if (this.minLevel <= LogLevel.WARN) {
            console.warn(`[${this.module} WARN] ${msg}`, data || '');
        }
    }

    error(msg: string, error?: any) {
        if (this.minLevel <= LogLevel.ERROR) {
            console.error(`[${this.module} ERROR] ${msg}`, error || '');

            // Also send to backend for central logging
            this.sendToBackend(msg, error);
        }
    }

    private sendToBackend(msg: string, error?: any) {
        // Send to Django logging endpoint
        fetch('/api/frontend-errors/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                module: this.module,
                message: msg,
                error: error?.toString(),
                stack: error?.stack,
                url: window.location.href,
                timestamp: new Date().toISOString()
            })
        }).catch(() => {
            // Silent fail - don't break app if logging fails
        });
    }
}

// Usage:
// const logger = new Logger('Settings');
// logger.info('Form submitted', { username: 'test-user' });
// logger.error('API call failed', error);
```

### Phase 4: Immediate Debug Fix (15 minutes)

For NOW, before full refactoring, let's add simple debugging:

**Add to settings.js (temporary):**
```javascript
// At the top
const DEBUG = true;
const log = (msg, data) => DEBUG && console.log(`[Settings] ${msg}`, data || '');
const logError = (msg, err) => console.error(`[Settings ERROR] ${msg}`, err || '');

// Before form submit:
log('Form submitting', {
    action: document.querySelector('[name="action"]:checked')?.value,
    username: document.getElementById('collaboratorUsername')?.value
});

// After API calls:
fetch('/api/users/search/?q=' + query)
    .then(r => {
        log('User search response', { status: r.status, ok: r.ok });
        return r.json();
    })
    .then(data => {
        log('User search data', data);
    })
    .catch(err => logError('User search failed', err));
```

---

## Recommended Order

1. **Today: Quick Debug** (30 min)
   - Add console logging to track form submission
   - Verify POST reaches backend
   - Check database for invitations

2. **Tomorrow: Split Views** (2 hours)
   - Create views/ directory
   - Split base_views.py into 3-4 files
   - Test each feature still works

3. **This Week: TypeScript Migration** (4 hours)
   - Setup tsconfig for project_app
   - Migrate settings.js → settings.ts
   - Create collaboration.ts with autocomplete
   - Add central logger

4. **Next Week: Service Layer** (2 hours)
   - Create services/collaboration_service.py
   - Move business logic out of views
   - Add unit tests

---

## Success Criteria

✅ **After refactoring:**
- Each Python file < 1500 lines
- All JS migrated to TypeScript
- Central logging shows all errors
- Forms work reliably with clear error messages
- Can debug issues in < 5 minutes
- New features take < 30 minutes to add

---

## Commands

```bash
# Build TypeScript
cd frontend
npm run build              # Build all
npm run build:watch        # Auto-rebuild on changes

# Check for errors
npm run type-check         # TypeScript type checking
npm run lint               # ESLint

# Run server
./start_dev.sh             # Auto-reloads on Python changes
```

<!-- EOF -->
