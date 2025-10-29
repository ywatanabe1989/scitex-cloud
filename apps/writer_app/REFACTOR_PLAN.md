# Writer App Refactor Plan

## Status: PLANNING

After reviewing the new `scitex.writer.Writer` interface, the Django writer_app needs significant simplification.

## New Architecture

### What scitex.writer.Writer Already Handles
✅ Project initialization with git-based version control
✅ Document section reading/writing (manuscript, supplementary, revision)
✅ Git operations (commit, history, diff, checkout)
✅ Compilation (manuscript, supplementary, revision with timeouts)
✅ Watch mode (auto-recompile on changes)
✅ PDF extraction
✅ Project cleanup

### What Django writer_app Should Do
- REST API layer over Writer class
- Session/authentication management
- Real-time WebSocket updates for compilation progress
- Multi-user collaboration (if needed)
- Frontend integration

## Current Issues to Fix

### 1. Compilation Error: "Compile script not found"
**Root Cause:** Manuscript model tries to create compile scripts manually
**Solution:** Use `Writer.compile_manuscript()` instead
**Impact:** Remove all manual compile script creation code from models

### 2. Directory Structure Mismatch
**Current:** Models create `manuscript/src/` but readers expect `01_manuscript/contents/`
**Solution:** Use Writer which handles correct structure (`01_manuscript/contents/`)
**Impact:** Simplify create_modular_structure() or delegate to Writer entirely

### 3. Split View Syntax Highlighting Issue
**Current:** CodeMirror v5 in split view doesn't apply highlighting
**Solution:**
- Option A: Upgrade CodeMirror to v6
- Option B: Use Monaco Editor (TypeScript support)
- Option C: Just use Writer's JSON API, let frontend fetch sections

## Implementation Plan

### Phase 1: API Layer (High Priority)
```python
# apps/writer_app/api/
- sections_api.py: Read/write individual sections
- compilation_api.py: Trigger compilation, get status
- history_api.py: Get git history, diffs, checkout
```

### Phase 2: Remove Duplicated Code
- Delete: Manual compile script creation
- Delete: Manual directory structure creation
- Delete: Manual git operations
- Keep: Authentication, session management, WebSocket handling

### Phase 3: Frontend Integration
- Update JavaScript to use new API
- Improve syntax highlighting (CodeMirror v6 or Monaco)
- Add real-time compilation progress via WebSocket
- Fix dark mode support

## Key Files to Modify

### Delete/Simplify
- `models/core.py`: Remove compile script creation, directory structure creation
- `services/version_control_service.py`: Use git operations from Writer instead
- `views/main_views.py`: Simplify, use Writer API

### Create New
- `api/writer_api.py`: REST endpoints for Writer operations
- `services/writer_wrapper.py`: Django-friendly wrapper around Writer

### Update
- `urls.py`: New API endpoints
- `static/writer_app/js/writer_app.js`: Use new API

## Timeline
- Phase 1: 2-3 hours
- Phase 2: 1-2 hours
- Phase 3: 2-3 hours

**Total:** ~5-8 hours for full refactor

## Benefits
✅ Less code to maintain
✅ Fewer bugs (scitex handles the complexity)
✅ Better performance (no duplication)
✅ Cleaner API for frontend
✅ Git operations work correctly
✅ Compilation always works
