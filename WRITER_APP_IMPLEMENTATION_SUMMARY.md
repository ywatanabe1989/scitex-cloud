# SciTeX Writer App - Implementation Summary

**Date**: 2025-11-04  
**Status**: Refactored, Modular Architecture Implemented  
**Branch**: `refactor/project-app-typescript`

---

## Executive Summary

The Writer App is a **modular manuscript editing system** with LaTeX support, real-time PDF preview, git-based version control, and collaboration features. It delegates core logic to the `scitex.writer.Writer` package while Django handles cloud infrastructure, authentication, and UI.

**Architecture Pattern**: Minimal Django models + REST API + TypeScript frontend + WebSocket collaboration

---

## Current Feature Status

### What Works ✅

#### Core Editor
- [x] **Monaco Editor** (primary) with fallback to CodeMirror
- [x] LaTeX syntax highlighting with custom Monarch tokenizer
- [x] LaTeX code completion (50+ commands with snippets)
- [x] Theme system (Monaco themes + CodeMirror fallback)
- [x] Keybinding support (Vim, Emacs, Default)
- [x] Undo/redo with history tracking
- [x] Word count display
- [x] Font size control (14px-20px)
- [x] Line numbers and word wrapping

#### Document Structure
- [x] **Modular section editing**: Abstract, Introduction, Methods, Results, Discussion, Conclusion, Highlights
- [x] **Multiple document types**: Manuscript, Supplementary, Revision (peer review)
- [x] **Shared sections**: Title, Authors, Keywords (common to all doc types)
- [x] **Section hierarchy** from `/apps/writer_app/configs/sections_config.py`
- [x] **Section switching** with content persistence
- [x] **Live section content loading** from REST API

#### Compilation & Preview
- [x] **Live PDF preview** (auto-compile with 2-second debounce)
- [x] **Section-specific previews** (quick compile for individual sections)
- [x] **Full manuscript compilation** (from workspace with all sections)
- [x] **Supplementary compilation** (separate PDF)
- [x] **Color mode support** (Light/Dark/Sepia/Paper - injected into LaTeX)
- [x] **PDF zoom controls** (Zoom In/Out, Fit Width, Reset)
- [x] **PDF scroll priority** (PDF scrolling doesn't scroll page)
- [x] **Preview output directory** (`scitex/writer/preview_output/`)

#### Version Control (Git)
- [x] **Auto-save** to filesystem (5-second debounce)
- [x] **Git commits** with user-provided messages (per-section)
- [x] **Commit history** display (per-section)
- [x] **Diff viewing** (against HEAD or specific refs)
- [x] **Checkout from history** (restore to specific commit)
- [x] **Nested repository support** (`git_strategy="parent"`)

#### File Management
- [x] **File tree view** of workspace `.tex` files
- [x] **Direct .tex file loading** (for non-section files)
- [x] **Read-only compiled sections** (compiled_pdf, compiled_tex)
- [x] **Dynamic file tree refresh** button

#### User Experience
- [x] **Dark/Light theme toggle** (synced with global site theme)
- [x] **Split-pane layout** (editor left, PDF preview right)
- [x] **Panel resizer** for adjustable layout
- [x] **Responsive design** (works on desktop and tablet)
- [x] **Keyboard shortcuts**:
  - `Ctrl+S`: Save sections
  - `Ctrl+Shift+X`: Compile full manuscript
  - `Ctrl+/`: Toggle comment (Monaco)
  - Monaco/CodeMirror defaults (Undo, Redo, etc.)

#### Collaboration (Partial ✏️ WIP)
- [x] **Polling-based presence tracking** (WriterPresence model)
- [x] **Active users list** (with section info)
- [x] **WebSocket consumer** (WriterConsumer - async ORM ready)
- [x] **Session tracking** (CollaborativeSession model)
- [x] **Section locking** (per-user, prevents conflicts)
- [ ] **Operational Transform (OT)** - Framework ready, not fully integrated
- [ ] **Real-time cursor position** broadcasting
- [ ] **Collaborative undo/redo** - Framework exists, needs integration

#### Workspace Initialization
- [x] **One-click workspace setup** (creates scitex/writer structure)
- [x] **Project selector** (for multi-project users)
- [x] **Auto-initialization** on first access (demo users)
- [x] **Error handling** with user-friendly messages

### What's Incomplete or Missing ❌

#### Critical TODO Items
- [ ] **OT Integration**: Operational Transform coordinator (`OTCoordinator`) exists but not integrated with frontend
- [ ] **Real-time collaborative editing**: WebSocket connected but OT messages not flowing
- [ ] **Bibliography Management**: No BibTeX entry UI or citation searching
  - Comment in `writer-commands.js` lines 219-230 marked as TODO
  - Needs UI modal for searching and inserting citations
- [ ] **Revision Management**: Structure exists but UI not complete
  - Needs CRUD for comment/response/revision triplets
  - Need UI to track reviewer vs editor feedback

#### Quality/Polish TODO Items
- [ ] **Mouse wheel scroll** in editor (CodeMirror default, need Monaco config)
- [ ] **Syntax highlighting colors** not fully distinct (all commands look similar)
- [ ] **Error cascading**: Errors shown as JS alerts, not central logging
- [ ] **Status bar**: No line/column position display
- [ ] **Search/replace**: Not visible in toolbar (hidden feature)
- [ ] **Minimap**: Monaco minimap disabled (can be re-enabled)
- [ ] **Breakpoints/Bookmarks**: Not implemented

#### Infrastructure TODO Items
- [ ] **Compilation status polling** (long-running compilations)
- [ ] **Job queue** for parallel compilations
- [ ] **Preview caching** (avoid recompiling unchanged sections)
- [ ] **Background auto-compile** (for non-interactive users)
- [ ] **Compilation logging** (per-job persistent logs)

---

## Architecture Overview

### Directory Structure

```
apps/writer_app/
├── models/
│   ├── core.py              # Manuscript (minimal, delegates to scitex.writer.Writer)
│   ├── collaboration.py     # WriterPresence, CollaborativeSession
│   ├── arxiv.py            # (deprecated, marked for removal)
│   └── ...
├── views/
│   ├── main_views.py       # Main page, workspace init, stubs
│   ├── api_views.py        # REST API endpoints (sections, compilation, git, presence)
│   ├── editor_views.py     # Legacy editor views
│   └── ...
├── services/
│   ├── writer_service.py   # Django wrapper for scitex.writer.Writer
│   ├── compiler.py         # Compilation service
│   ├── operational_transform_service.py  # (framework ready, not integrated)
│   └── arxiv/             # (deprecated)
├── static/writer_app/
│   ├── js/                # JavaScript - old code, mostly deprecated
│   │   ├── writer-*.js    # Feature-specific files (initialization, compilation, etc.)
│   │   └── modules/       # TypeScript-compiled modules (editor, sections, PDF, etc.)
│   ├── ts/                # TypeScript source
│   │   ├── index.ts       # Main entry point (large, coordinates all modules)
│   │   ├── helpers.ts     # Utility functions
│   │   ├── modules/       # Individual modules
│   │   │   ├── monaco-editor.ts      # Monaco+CodeMirror wrapper
│   │   │   ├── editor.ts             # WriterEditor (basic editor)
│   │   │   ├── file_tree.ts          # File tree UI
│   │   │   ├── sections.ts           # Section manager
│   │   │   ├── compilation.ts        # Compilation manager
│   │   │   ├── pdf-preview.ts        # PDF preview
│   │   │   ├── pdf-scroll-zoom.ts    # PDF controls
│   │   │   ├── panel-resizer.ts      # Draggable split view
│   │   │   ├── editor-controls.ts    # Toolbar buttons
│   │   │   └── latex-wrapper.ts      # LaTeX utilities
│   │   └── utils/         # Shared utilities (DOM, keyboard, storage, etc.)
│   └── css/               # Styling
│       ├── latex-editor.css
│       ├── collaborative-editor.css
│       ├── pdf-view-main.css
│       ├── index-editor-panels.css
│       └── ... (13+ CSS files)
├── templates/writer_app/
│   ├── index.html         # Main editor page
│   ├── collaborative_editor.html  # WebSocket collaboration interface
│   ├── writer_base.html   # Base template
│   ├── *_partials/        # Template includes (modular)
│   └── .old/              # Legacy templates
├── configs/
│   └── sections_config.py # Section hierarchy definition
├── routing.py             # WebSocket URL routing
├── consumers.py           # WebSocket consumer (WriterConsumer)
└── urls.py, urls_.py      # URL routing
```

### Key Classes & Models

#### Django Models
```python
# Manuscript - minimal, links user/project to scitex.writer.Writer
class Manuscript(models.Model):
    project: OneToOneField → Project
    owner: ForeignKey → User
    title, description: str
    @property writer_initialized: bool  # Checks filesystem

# WriterPresence - polling-based presence tracking
class WriterPresence(models.Model):
    user, project: FK
    current_section: str
    last_seen: DateTime
    is_active: bool
    
    @classmethod.get_active_users(project_id, minutes=2): List

# CollaborativeSession - tracks editing sessions
class CollaborativeSession(models.Model):
    manuscript, user: FK
    session_id, locked_sections: str/JSON
    cursor_position: JSON
    characters_typed, operations_count: int
    is_session_active(): bool
```

#### REST API Endpoints
```
/writer/api/project/{project_id}/
├── section/{section_name}/           # GET: read, POST: write
│   └── commit/                        # POST: git commit
├── save-sections/                     # POST: batch save
├── compile-preview/                   # POST: quick compile (no workspace)
├── compile-full/                      # POST: full manuscript (from workspace)
├── compile/                           # POST: deprecated endpoint
├── pdf/                               # GET: compiled PDF file
├── preview-pdf/                       # GET: section preview PDF
├── section/{name}/history/            # GET: git history
├── section/{name}/diff/               # GET: uncommitted changes
├── section/{name}/checkout/           # POST: restore from history
├── read-tex-file/                     # GET: read arbitrary .tex file
├── file-tree/                         # GET: workspace structure
├── available-sections/                # GET: section list by doc type
└── presence/
    ├── update/                        # POST: update current section
    └── list/                          # GET: active users
```

#### TypeScript Modules
```typescript
// Core editors
EnhancedEditor          # Monaco + CodeMirror fallback
WriterEditor            # Basic CodeMirror editor (legacy)

// Document management
SectionsManager         # In-memory section storage
FileTreeManager         # File tree UI + click handling

// Compilation & Preview
CompilationManager      # Compilation job tracking
PDFPreviewManager       # Live PDF preview with auto-compile
PDFScrollZoomHandler    # PDF zoom + scroll controls

// UI Components
PanelResizer            # Draggable split-pane divider
EditorControls          # Toolbar (font size, compile, preview)

// Utilities
StorageManager          # localStorage wrapper
KeyboardUtils           # Keyboard shortcut helpers
LaTeXUtils              # LaTeX command snippets
```

### Data Flow

#### Section Editing Flow
```
User types in editor
  ↓
EnhancedEditor.onChange fires
  ↓
SectionsManager.setContent() (in-memory update)
  ↓
scheduleSave() debounces (5s)
  ↓
fetch /writer/api/project/{id}/save-sections/ POST
  ↓
WriterService.write_section() → Writer.manuscript.contents.section.write()
  ↓
File written to scitex/writer/{doctype}/contents/{section}.tex
  ↓
Auto-save complete (no commit yet)
```

#### Compilation Flow (Live Preview)
```
User stops typing
  ↓
scheduleAutoCompile() debounces (2s)
  ↓
PDFPreviewManager.compileQuick(content, section_id)
  ↓
fetch /writer/api/project/{id}/compile-preview/ POST
  ↓
WriterService.compile_preview(content) → subprocess.run(pdflatex)
  ↓
Output written to scitex/writer/preview_output/preview-{section}.pdf
  ↓
<iframe> src updated to preview PDF URL
  ↓
PDF displayed in right panel
```

#### Compilation Flow (Full Manuscript)
```
User clicks "Compile Manuscript" button
  ↓
handleCompileFull()
  ↓
fetch /writer/api/project/{id}/compile-full/ POST
  ↓
WriterService.compile_manuscript() → Writer.compile_manuscript()
  ↓
Merges all sections into single .tex file
  ↓
Runs pdflatex (full timeout: 300s)
  ↓
Output written to scitex/writer/{doctype}/{doctype}.pdf
  ↓
Returns PDF URL
  ↓
Switch to compiled_pdf section (read-only view)
```

#### Git Commit Flow
```
User clicks "Commit" button
  ↓
showCommitModal() opens dialog
  ↓
User enters commit message
  ↓
handleGitCommit()
  ↓
fetch /writer/api/project/{id}/section/{name}/commit/ POST
  ↓
WriterService.commit_section(message)
  ↓
Writer.manuscript.contents.section.commit(message)
  ↓
Changes staged and committed in git
  ↓
Git history updated
```

### Collaboration Architecture (WIP)

#### WebSocket Flow (Not Fully Integrated)
```
Client connects to /ws/writer/{manuscript_id}/
  ↓
WriterConsumer.connect() authenticates user
  ↓
Creates CollaborativeSession
  ↓
Broadcasts "user_joined" to group
  ↓
Sends "collaborators_list" to new user

Client sends text_change message
  ↓
WriterConsumer.handle_text_change()
  ↓
OTCoordinator.submit_operation() (NOT INTEGRATED)
  ↓
Operation queued and transformed
  ↓
Processed operations broadcast to group
  ↓
Clients apply transformations locally

Client disconnects
  ↓
WriterConsumer.disconnect()
  ↓
Updates CollaborativeSession (is_active=False)
  ↓
Broadcasts "user_left"
```

**Current Status**: Framework is ready but frontend doesn't send OT messages through WebSocket. Currently uses polling for presence only.

---

## Implementation Details

### Monaco Editor Integration

**File**: `/apps/writer_app/static/writer_app/ts/modules/monaco-editor.ts`

**Features**:
- Dynamic LaTeX language registration (custom Monarch tokenizer)
- 50+ LaTeX command completions with snippets
- Auto-closing brackets and pairs
- Surroundings pairs support
- Comment toggle (Ctrl+/)
- Custom SciTeX dark theme
- Theme auto-switching with global dark mode
- Word wrap, line numbers, minimap (disabled)

**Fallback**: CodeMirror (LaTeX STex mode) if Monaco fails to load

**Known Issues**:
- Monaco Vim/Emacs keybindings need separate packages (not included)
- Minimap disabled for cleaner UI
- Line height fixed at 21px (matching 14px font with 1.5x spacing)

### Section Hierarchy

**File**: `/apps/writer_app/configs/sections_config.py`

```python
SECTION_HIERARCHY = {
    "shared": {
        "label": "Shared",
        "sections": [
            {"id": "shared/title", "label": "Title", ...},
            {"id": "shared/authors", "label": "Authors", ...},
            ...
        ]
    },
    "manuscript": {
        "label": "Manuscript",
        "sections": [
            {"id": "manuscript/abstract", ...},
            {"id": "manuscript/introduction", ...},
            ...
        ]
    },
    "supplementary": {...},
    "revision": {...}
}
```

### PDF Preview System

**Auto-compile** with 2-second debounce:
1. User stops typing
2. Current section content sent to preview API
3. pdflatex compiles in isolation (temp file)
4. Output saved to `preview_output/preview-{section}.pdf`
5. PDF displayed in split-pane preview

**Benefits**:
- Non-blocking (doesn't lock editor)
- Per-section (users see only what they're editing)
- Timeout: 60 seconds
- Color mode support (light/dark/sepia/paper)

### Auto-Save Strategy

**Hybrid Approach**:
- **Auto-save** (automatic, no user interaction): 5-second debounce
  - Triggered on every keystroke
  - Saves to filesystem
  - No git commit (uncommitted changes)
- **Manual commit** (user-initiated): One commit per section
  - User clicks "Commit" button
  - Provides commit message
  - Creates git commit with message
  - `git log` shows history

**Why This Approach**:
- Users never lose work (auto-saved continuously)
- Git history stays clean (meaningful commits only)
- Peer review possible (exact changes tracked)

---

## Collaboration Features Status

### Fully Implemented
- [x] **WriterPresence model**: Tracks who's editing and current section
- [x] **CollaborativeSession model**: Tracks session metadata
- [x] **WebSocket consumer**: Async, Django 5.2 ORM ready
- [x] **Presence API endpoints**: Update and list active users

### Partially Implemented
- [ ] **Operational Transform**: Framework exists (`OTCoordinator`) but not integrated with frontend
- [ ] **Real-time cursor broadcasting**: Message handler exists but frontend doesn't send
- [ ] **Section locking**: Detected on connect but not enforced

### TODO
- [ ] **OT Client**: Frontend needs to send `text_change` messages through WebSocket
- [ ] **Conflict resolution**: When two users edit same section
- [ ] **Undo/redo sync**: Collaborative undo/redo coordinator exists but needs frontend hooks
- [ ] **Activity indicators**: Show real-time cursors and selections

### Integration Notes
- WebSocket connected but messages not flowing from frontend
- Add `writer-websocket.js` to send operations through WebSocket instead of HTTP
- Keep HTTP auto-save as fallback for reliability

---

## Critical Issues & Warnings

### 1. Compilation Timeout Strategy
**Issue**: Long manuscripts can exceed 60s preview timeout
**Current**: Separate timeouts for preview (60s) and full (300s)
**Solution**: Use full timeout only for "Compile" button, keep preview short

### 2. OT Integration Incomplete
**Issue**: WebSocket consumer ready but frontend doesn't use it
**Status**: Non-blocking - system works with polling
**Next Step**: Implement `text_change` messages in frontend when OT ready

### 3. Bibliography Management Missing
**Issue**: No UI for citations or bibliography entries
**TODO**: Add BibTeX modal (search, insert citations)
**Blocked**: Requires understanding scitex.writer bibliography API

### 4. Error Handling
**Issue**: Compilation errors shown as browser alerts, not logged centrally
**Current**: Errors displayed in PDF preview area on failure
**Todo**: Implement central error logging to `/logs/console.log`

### 5. Performance
**Issue**: Live preview with pdflatex can be slow for large sections
**Current**: 2-second debounce helps but doesn't solve fundamental latency
**Solution**: Consider pre-compiled snippets or simpler preview renderer

---

## File Summary

### Models (400 lines)
- `core.py`: Manuscript model (minimal)
- `collaboration.py`: WriterPresence, CollaborativeSession (polling-based)

### Views (800 lines)
- `main_views.py`: Main page, stubs, initialization
- `api_views.py`: REST API (sections, compilation, git, presence)

### Services (1200+ lines)
- `writer_service.py`: Django wrapper for scitex.writer.Writer
- `compiler.py`: Compilation management
- `operational_transform_service.py`: OT framework (not integrated)
- `arxiv/*`: Deprecated (marked for removal)

### Frontend TypeScript (3000+ lines compiled)
- `index.ts`: Main entry point (coordinates all modules)
- `modules/*`: Individual feature modules (editor, sections, PDF, etc.)
- `utils/*`: Shared utilities
- **Generated from TypeScript**: Compiled to `/js/modules/*.js` with source maps

### Templates (500 lines)
- `index.html`: Main editor page
- `*_partials/`: Modular template includes
- Legacy templates in `.old/`

### CSS (1500+ lines across 13 files)
- Layout: `tex-view-main.css`, `index-editor-panels.css`
- Components: `latex-editor.css`, `collaborative-editor.css`
- PDF: `pdf-view-main.css`, `pdf-scroll-zoom.css`

---

## Development Workflow

### Running Writer App

1. **Start dev server**:
   ```bash
   ./start_dev.sh  # Includes auto-hot-reload
   ```

2. **Access page**:
   ```
   http://127.0.0.1:8000/writer/
   ```

3. **Create test workspace** (if needed):
   - Select/create project
   - Click "Create Workspace"
   - Editor initializes

### Testing Collaboration (Manual)

1. Open two browser windows to same project
2. Watch "Active Users" update with presence
3. Edit in one window, see presence update in the other
4. Section locks prevent conflicts (not enforced yet)

### Making Changes

- **Frontend**: Edit `.ts` files, TypeScript compiler auto-builds to `.js`
- **Models**: Edit `models/*.py`, run migrations
- **Views**: Edit `views/*.py`, auto-reloaded
- **CSS**: Edit `.css` files, auto-reloaded
- **Templates**: Edit `.html` files, auto-reloaded

### Debugging

- **Browser console**: `console.log` messages from TypeScript
- **Django logs**: Server output and `logging.getLogger(__name__)`
- **Network tab**: API requests/responses
- **Application tab**: LocalStorage (WRITER_CONFIG, sections)

---

## Known Limitations

1. **No concurrent editing**: Two users editing same section will have conflicts (OT not integrated)
2. **No offline mode**: Requires active connection for saves
3. **No version diff UI**: Can view diffs but no visual comparison
4. **Bibliography**: Manual editing only (no search/insert UI)
5. **LaTeX errors**: Shown as text, not parsed and highlighted
6. **Preview timeout**: 60 seconds max for single section preview

---

## Next Steps (Priority Order)

### High Priority
1. **Integrate OT** into frontend (enable real-time collaboration)
2. **Fix bibliography UI** (search & citation insertion)
3. **Add revision management UI** (comment triplets)
4. **Centralized error logging** (to `/logs/console.log`)

### Medium Priority
5. **Status bar** (line/column position)
6. **Search/replace** (visible in toolbar)
7. **Compilation caching** (avoid recompiling unchanged sections)
8. **Background auto-compile** for non-interactive users

### Low Priority (Polish)
9. **Minimap** (re-enable in Monaco)
10. **Syntax highlighting colors** (more distinct)
11. **Mouse wheel scroll** in Monaco
12. **Breakpoints/bookmarks** for navigation

---

## Configuration Files

### Writer Configuration
- **Sections**: `/apps/writer_app/configs/sections_config.py`
- **Models**: `/apps/writer_app/models/`
- **Views**: `/apps/writer_app/views/`
- **URLs**: `/apps/writer_app/urls.py`

### Django Settings
- **App installed**: In `settings.INSTALLED_APPS` as `writer_app`
- **URLs included**: In `config/urls.py`
- **Static files**: Served via `django.contrib.staticfiles`

### scitex.writer Package
- **Installed**: From `~/proj/scitex-code` (editable mode)
- **API docs**: In package `README.md` and `Writer` class docstrings
- **Version**: Latest from git

---

## Summary Table

| Feature | Status | Notes |
|---------|--------|-------|
| **Editor** | ✅ Full | Monaco primary, CodeMirror fallback |
| **Syntax Highlighting** | ✅ Full | LaTeX Monarch tokenizer |
| **Code Completion** | ✅ Full | 50+ commands with snippets |
| **Live PDF Preview** | ✅ Full | 2s debounce, section-specific |
| **Full Compilation** | ✅ Full | From workspace, 300s timeout |
| **Auto-save** | ✅ Full | 5s debounce, to filesystem |
| **Git Integration** | ✅ Full | Per-section commits, history, checkout |
| **File Tree** | ✅ Full | Browse workspace .tex files |
| **Presence Tracking** | ✅ Polling | HTTP polling, not WebSocket |
| **Real-time Collab** | 🔴 WIP | WebSocket ready, OT not integrated |
| **Bibliography** | ❌ Missing | Manual editing only |
| **Peer Review** | 🟡 Partial | Revision doc structure ready, UI incomplete |
| **Vim/Emacs Keys** | 🟡 Partial | CodeMirror supported, Monaco needs packages |
| **Dark Mode** | ✅ Full | Monaco + CodeMirror support |

---

## References

- **Django Model Docs**: `/apps/writer_app/models/`
- **REST API**: `/apps/writer_app/views/api_views.py`
- **TypeScript Modules**: `/apps/writer_app/static/writer_app/ts/`
- **scitex.writer Docs**: `~/proj/scitex-code/README.md`
- **TODO List**: `/apps/writer_app/TODO.md`
