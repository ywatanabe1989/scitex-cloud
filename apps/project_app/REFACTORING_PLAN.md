<!-- ---
!-- Timestamp: 2025-11-03 23:15:00
!-- Author: Claude Code
!-- File: /home/ywatanabe/proj/scitex-cloud/apps/project_app/REFACTORING_PLAN.md
!-- --- -->

# Project App Refactoring Plan

## Current Issues

1. **base_views.py is 2795 lines** - violates 1000-2000 line rule
2. **Monolithic views** - collaboration, settings, members all mixed
3. **No TypeScript** - hard to debug, no type safety
4. **Forms not working reliably** - collaboration form submission unclear
5. **No central logging** - hard to troubleshoot

## Target Structure (Following RULES/)

### Backend Organization

```
project_app/
├── models/
│   ├── __init__.py              # Export all models
│   ├── core.py                  # Project, Organization, ResearchGroup
│   ├── collaboration.py         # ProjectMembership, ProjectInvitation
│   ├── repository.py            # VisitorAllocation, filesystem models
│   └── issues_prs.py            # Issues, PRs (imported from separate files)
│
├── views/
│   ├── __init__.py              # Export common views
│   ├── project_views.py         # Project CRUD (list, create, detail, edit, delete)
│   ├── collaboration_views.py   # Invitations, members, permissions
│   ├── settings_views.py        # Settings page + POST handlers
│   ├── directory_views.py       # File browser, commits
│   └── api_views.py             # REST API endpoints
│
├── services/
│   ├── __init__.py
│   ├── collaboration_service.py # Invitation logic, email sending
│   ├── project_utils.py         # get_current_project, etc.
│   └── email_service.py         # Already exists
│
└── static/project_app/
    ├── ts/                       # TypeScript source
    │   ├── settings.ts
    │   ├── collaboration.ts
    │   └── utils/
    │       └── api.ts
    └── js/                       # Compiled output
        └── (generated from ts/)
```

### Frontend Organization (TypeScript)

```
apps/project_app/static/project_app/
├── ts/                          # NEW - TypeScript source
│   ├── settings.ts              # Settings page logic
│   ├── collaboration.ts         # Collaboration autocomplete, invitations
│   ├── project.ts               # Project list/detail
│   └── utils/
│       ├── api.ts               # Centralized API calls
│       └── logger.ts            # Central logging system
│
├── js/                          # Compiled JavaScript
│   ├── settings.js              # Compiled from settings.ts
│   ├── collaboration.js
│   ├── project.js
│   ├── *.d.ts                   # Type definitions
│   └── *.js.map                 # Source maps for debugging
│
└── css/
    └── project_app.css
```

## Migration Strategy

### Phase 1: Split Views (Immediate)
**Priority: Fix current broken features**

1. **Create `views/collaboration_views.py`**
   - Move: `project_collaborate`, `project_members`, invitation handlers
   - Add: Proper POST handling for invitations
   - Add: Email notification logic

2. **Create `views/settings_views.py`**
   - Move: `project_settings` + all action handlers
   - Split by action type (general, visibility, collaborators, danger zone)

3. **Keep in `base_views.py`** (rename to `views/project_views.py`)
   - Project CRUD: list, create, detail, edit, delete
   - Basic directory browsing

### Phase 2: TypeScript Migration (Next)
**Priority: Debugging and maintainability**

1. **Setup TypeScript**
   ```bash
   cd apps/project_app/static/project_app
   npm init -y
   npm install -D typescript @types/node
   npx tsc --init
   ```

2. **Migrate settings.js → settings.ts**
   - Add types for form elements
   - Add centralized error logging
   - Add API response types

3. **Create collaboration.ts**
   - User search autocomplete
   - Invitation management
   - Proper error handling

4. **Create utils/logger.ts**
   ```typescript
   export const logger = {
     info: (msg: string, data?: any) => console.log('[INFO]', msg, data),
     error: (msg: string, error?: any) => console.error('[ERROR]', msg, error),
     debug: (msg: string, data?: any) => console.debug('[DEBUG]', msg, data)
   };
   ```

### Phase 3: Service Layer (Best Practice)
**Priority: Clean architecture**

1. **Create `services/collaboration_service.py`**
   - `send_invitation(project, user, role)` - Handles invitation + email
   - `accept_invitation(token, user)` - Validates and accepts
   - `list_pending_invitations(user)` - User's pending invitations

2. **Views call services**
   ```python
   # views/collaboration_views.py
   from ..services.collaboration_service import CollaborationService

   def add_collaborator(request, username, slug):
       service = CollaborationService()
       result = service.send_invitation(
           project=project,
           invited_user=collaborator,
           invited_by=request.user,
           role=role
       )
       if result.success:
           messages.success(request, result.message)
       else:
           messages.error(request, result.error)
   ```

## Immediate Action Items

### Fix Current Broken Feature (Today)
- [ ] Debug why collaboration form isn't creating invitations
- [ ] Add console logging to track form submission
- [ ] Verify POST is reaching backend
- [ ] Add error messages display

### Refactoring (This Week)
- [ ] Split base_views.py into feature modules
- [ ] Setup TypeScript build system
- [ ] Migrate settings.js → settings.ts
- [ ] Create central logging system

## Benefits After Refactoring

1. **Easier debugging** - TypeScript catches errors at compile time
2. **Better IDE support** - Autocomplete, go-to-definition
3. **Maintainable** - Each file < 2000 lines
4. **Testable** - Services can be unit tested
5. **Clear ownership** - Each feature in its own file
6. **Central logging** - All errors go to one place

## Example: Well-Organized App (writer_app)

Writer app already follows good practices:
- Models split: `models/core.py`, `models/collaboration.py`
- Views split: `views/main_views.py`, `views/api_views.py`
- TypeScript: `static/writer_app/ts/` → `js/` (compiled)
- Modular: Each module ~200-500 lines

Let's make project_app match this quality!

<!-- EOF -->
