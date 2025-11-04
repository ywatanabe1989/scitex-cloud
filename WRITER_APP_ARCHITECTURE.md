# Writer App Architecture Diagrams

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SciTeX Writer System                             │
└─────────────────────────────────────────────────────────────────────────┘

                           FRONTEND (Browser)
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│  ┌─────────────────────────┐     ┌──────────────────────────────────┐   │
│  │   TypeScript Modules    │     │      Template HTML               │   │
│  ├─────────────────────────┤     ├──────────────────────────────────┤   │
│  │ • EnhancedEditor        │     │ • index.html (main page)         │   │
│  │ • SectionsManager       │────→│ • Partials (modular layout)      │   │
│  │ • PDFPreviewManager     │     │ • Base template                  │   │
│  │ • FileTreeManager       │     │ • Bootstrap grid                 │   │
│  │ • PanelResizer          │     └──────────────────────────────────┘   │
│  │ • EditorControls        │                                             │
│  │ • PDFScrollZoomHandler  │     ┌──────────────────────────────────┐   │
│  │ • CompilationManager    │     │   CSS Styling (13 files)         │   │
│  │ • WriterEditor (legacy) │────→│ • latex-editor.css               │   │
│  │ • LaTeXWrapper          │     │ • pdf-view-main.css              │   │
│  │ • StorageManager        │     │ • index-editor-panels.css        │   │
│  │ • KeyboardUtils         │     │ • collaborative-editor.css       │   │
│  │ • LaTeXUtils            │     │ • ... (theme, layout, components)│   │
│  │ • DOMUtils              │     └──────────────────────────────────┘   │
│  └─────────────────────────┘                                             │
│           ↓                                                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              Editor Interface (Split Pane)                       │   │
│  ├──────────────────┬─────────────────────────────────────────────┤   │
│  │ Left: Editor     │ Right: PDF Preview                          │   │
│  │ (Monaco/CM)      │ (iframe or embedded viewer)                 │   │
│  │ - Toolbar        │ - Zoom controls                             │   │
│  │ - Line numbers   │ - Color mode                                │   │
│  │ - Completions    │ - Auto-scroll                               │   │
│  │ - Git commit     │ - Section navigation                        │   │
│  │   dialog         │                                             │   │
│  ├──────────────────┼─────────────────────────────────────────────┤   │
│  │   Resizable Panel Divider (drag to adjust width)               │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │  Sidebar: File Tree, Section Dropdown, Active Users            │   │
│  │  Header: Project Selector, Theme Toggle, Help                  │   │
│  │  Footer: Word Count, Status, Keyboard Shortcuts                │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
                                  ↓
                         ┌─────────┴─────────┐
                         │                   │
                    HTTP Requests      WebSocket
                    (REST API)          (Collab)
                         │                   │
                         ↓                   ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                      BACKEND (Django)                                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                       REST API Views                               │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │  POST   /api/project/{id}/save-sections/                           │  │
│  │  GET    /api/project/{id}/section/{name}/                          │  │
│  │  POST   /api/project/{id}/section/{name}/                          │  │
│  │  POST   /api/project/{id}/section/{name}/commit/                   │  │
│  │  GET    /api/project/{id}/section/{name}/history/                  │  │
│  │  GET    /api/project/{id}/section/{name}/diff/                     │  │
│  │  POST   /api/project/{id}/section/{name}/checkout/                 │  │
│  │  POST   /api/project/{id}/compile-preview/                         │  │
│  │  POST   /api/project/{id}/compile-full/                            │  │
│  │  GET    /api/project/{id}/pdf/                                     │  │
│  │  GET    /api/project/{id}/preview-pdf/                             │  │
│  │  GET    /api/project/{id}/file-tree/                               │  │
│  │  GET    /api/project/{id}/read-tex-file/                           │  │
│  │  POST   /api/project/{id}/presence/update/                         │  │
│  │  GET    /api/project/{id}/presence/list/                           │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                  ↓                                        │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                        Services Layer                              │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │  WriterService (wrapper for scitex.writer)                         │  │
│  │  ├─ read_section(name, doc_type)                                   │  │
│  │  ├─ write_section(name, content, doc_type)                         │  │
│  │  ├─ commit_section(name, message, doc_type)                        │  │
│  │  ├─ compile_preview(content, timeout)                              │  │
│  │  ├─ compile_manuscript/supplementary/revision(timeout)             │  │
│  │  ├─ get_section_history/diff/checkout(name)                        │  │
│  │  └─ read_tex_file(path)                                            │  │
│  │                                                                      │  │
│  │  CompilationService                                                 │  │
│  │  ├─ compile_manuscript()                                            │  │
│  │  ├─ watch_manuscript()                                              │  │
│  │  └─ get_pdf()                                                       │  │
│  │                                                                      │  │
│  │  (NOT INTEGRATED) OTCoordinator                                      │  │
│  │  ├─ submit_operation()                                              │  │
│  │  ├─ acknowledge_operation()                                         │  │
│  │  └─ get_queue_status()                                              │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                  ↓                                        │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                      Django Models                                 │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │  Manuscript                                                         │  │
│  │  ├─ project: OneToOneField(Project)                                │  │
│  │  ├─ owner: ForeignKey(User)                                        │  │
│  │  ├─ title, description: str                                        │  │
│  │  └─ @property writer_initialized: bool                             │  │
│  │                                                                      │  │
│  │  WriterPresence (polling-based collaboration)                       │  │
│  │  ├─ user, project: FK                                              │  │
│  │  ├─ current_section: str                                           │  │
│  │  ├─ last_seen: DateTime                                            │  │
│  │  └─ is_active: bool                                                │  │
│  │                                                                      │  │
│  │  CollaborativeSession (WebSocket sessions)                          │  │
│  │  ├─ manuscript, user: FK                                           │  │
│  │  ├─ session_id: str                                                │  │
│  │  ├─ locked_sections: JSON (list)                                   │  │
│  │  ├─ cursor_position: JSON (dict)                                   │  │
│  │  └─ characters_typed, operations_count: int                        │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    WebSocket Consumer                              │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │  WriterConsumer (async, Django 5.2)                                │  │
│  │  ├─ connect() → authenticate, create session                       │  │
│  │  ├─ receive() → dispatch message to handler                        │  │
│  │  ├─ handle_text_change() → submit to OTCoordinator               │  │
│  │  ├─ handle_cursor_position() → broadcast                           │  │
│  │  ├─ handle_section_lock/unlock() → update session                  │  │
│  │  ├─ handle_undo/redo() → apply to document                         │  │
│  │  └─ disconnect() → end session                                     │  │
│  │                                                                      │  │
│  │  (NOT INTEGRATED) Messages:                                         │  │
│  │  ├─ text_change → OT operations                                    │  │
│  │  ├─ cursor_position → user cursors                                 │  │
│  │  ├─ section_lock/unlock → prevent conflicts                        │  │
│  │  ├─ undo/redo → collaborative history                              │  │
│  │  └─ operation_ack → confirm delivery                               │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                    scitex.writer Package (pip)                           │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Writer Class (main API)                                                 │
│  ├─ __init__(path, name=None, git_strategy='parent')                   │
│  ├─ manuscript: Document                                                 │
│  ├─ supplementary: Document                                              │
│  ├─ revision: Document                                                   │
│  ├─ compile_manuscript/supplementary/revision(timeout)                   │
│  ├─ get_pdf(doc_type) → Path                                            │
│  └─ watch(on_compile=callback)                                           │
│                                                                           │
│  Document Class (represents one doc type)                                │
│  └─ contents: SectionGroup                                               │
│      ├─ abstract, introduction, methods, results, ...                    │
│      └─ each section has:                                                │
│          ├─ read() → str                                                 │
│          ├─ write(content) → bool                                        │
│          ├─ commit(message) → bool                                       │
│          ├─ history() → list                                             │
│          ├─ diff(ref) → str                                              │
│          └─ checkout(ref) → bool                                         │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                      Filesystem (Project Root)                           │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  data/users/{username}/{project-slug}/                                   │
│  ├─ scitex/writer/                                                       │
│  │  ├─ .git/                          # Shared repo                      │
│  │  ├─ 01_manuscript/                                                    │
│  │  │  ├─ manuscript.tex             # Compiled (merged)                 │
│  │  │  ├─ manuscript.pdf             # Output PDF                        │
│  │  │  └─ contents/                                                      │
│  │  │     ├─ abstract.tex                                                │
│  │  │     ├─ introduction.tex                                            │
│  │  │     ├─ methods.tex                                                 │
│  │  │     ├─ results.tex                                                 │
│  │  │     ├─ discussion.tex                                              │
│  │  │     ├─ conclusion.tex                                              │
│  │  │     └─ highlights.tex                                              │
│  │  ├─ 02_supplementary/             # Same structure                   │
│  │  │  ├─ supplementary.tex                                              │
│  │  │  ├─ supplementary.pdf                                              │
│  │  │  └─ contents/                                                      │
│  │  ├─ 03_revision/                  # Peer review                       │
│  │  │  ├─ revision.tex                                                   │
│  │  │  ├─ revision.pdf                                                   │
│  │  │  └─ contents/                                                      │
│  │  ├─ shared/                        # Shared across all doc types      │
│  │  │  ├─ title.tex                                                      │
│  │  │  ├─ authors.tex                                                    │
│  │  │  ├─ keywords.tex                                                   │
│  │  │  └─ bibliography.bib                                               │
│  │  └─ preview_output/                # Auto-compiled previews           │
│  │     ├─ preview-abstract.pdf                                           │
│  │     ├─ preview-introduction.pdf                                       │
│  │     └─ ...                                                            │
│  │                                                                        │
│  └─ .git/                             # Project git repo                 │
│     └─ All changes tracked here                                          │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Section Editing

```
USER ACTION: Types in editor
│
├─→ MonacoEditor.onChange() fires
│
├─→ SectionsManager.setContent(section_id, new_content)
│   └─ In-memory storage updated
│
├─→ state.unsavedSections.add(section_id)
│   └─ Marks section for auto-save
│
├─→ scheduleSave() debounces (5 seconds of inactivity)
│
├─→ saveSections() called
│
├─→ fetch /writer/api/project/{id}/save-sections/ POST
│   {
│     "sections": { "abstract": "...", "introduction": "..." },
│     "doc_type": "manuscript"
│   }
│
├─→ Django view: save_sections_view()
│
├─→ WriterService.write_section(name, content, doc_type)
│   └─ Gets Document from Writer
│   └─ Gets Section from Document.contents
│   └─ Calls section.write(content)
│
├─→ scitex.writer.Writer writes file
│   └─ File: scitex/writer/{doctype}/contents/{section}.tex
│
├─→ File saved to disk (NOT YET COMMITTED)
│
└─→ Auto-save complete. Changes are:
    ✓ In editor
    ✓ In memory (SectionsManager)
    ✓ On disk (file system)
    ✗ NOT in git (uncommitted)
```

---

## Data Flow: Live PDF Preview

```
USER ACTION: Stops typing
│
├─→ scheduleAutoCompile() debounces (2 seconds)
│
├─→ PDFPreviewManager.compileQuick(content, section_id)
│
├─→ fetch /writer/api/project/{id}/compile-preview/ POST
│   {
│     "content": "LaTeX source...",
│     "section_name": "abstract",
│     "color_mode": "light"
│   }
│
├─→ Django view: compile_preview_view()
│
├─→ WriterService.compile_preview(content, timeout=60, color_mode='light')
│
├─→ Apply color mode (inject LaTeX color commands)
│
├─→ Write temp file: scitex/writer/preview-abstract-temp.tex
│
├─→ subprocess.run(['pdflatex', '-interaction=nonstopmode', ...])
│   └─ Timeout: 60 seconds
│   └─ Output dir: scitex/writer/preview_output/
│
├─→ Check return code
│   ├─ If success (0):
│   │   └─ Move preview-abstract-temp.pdf → preview-abstract.pdf
│   └─ If error:
│       └─ Return error log to client
│
├─→ Return to frontend:
│   {
│     "success": true/false,
│     "output_pdf": "/path/to/preview-abstract.pdf",
│     "log": "pdflatex output...",
│     "error": "error message or null"
│   }
│
├─→ PDFPreviewManager receives response
│
├─→ If success:
│   ├─→ Update <iframe src> to new PDF URL
│   └─→ PDF renders in right panel
│
└─→ If error:
    └─→ Display error message in preview area
```

---

## Data Flow: Git Commit

```
USER ACTION: Clicks "Commit" button
│
├─→ showCommitModal() opens dialog
│
└─→ User enters commit message
    │
    ├─→ handleGitCommit() called
    │
    ├─→ Extract from state.currentSection (e.g., "manuscript/abstract")
    │
    ├─→ fetch /writer/api/project/{id}/section/abstract/commit/ POST
    │   {
    │     "doc_type": "manuscript",
    │     "message": "User entered message"
    │   }
    │
    ├─→ Django view: section_commit_view()
    │
    ├─→ WriterService.commit_section(section_name, message, doc_type)
    │
    ├─→ Get Document from Writer
    │
    ├─→ Get Section from Document.contents
    │
    ├─→ Call section.commit(message)
    │   └─ scitex.writer handles git internally
    │
    ├─→ scitex.writer performs:
    │   ├─ git add scitex/writer/manuscript/contents/abstract.tex
    │   ├─ git commit -m "User entered message"
    │   └─ Updates .git/ in project root
    │
    ├─→ Return to frontend:
    │   { "success": true, "message": "Section committed..." }
    │
    ├─→ Close modal
    │
    └─→ Commit appears in git history
        └─ Viewable via: git log --oneline -- scitex/writer/manuscript/contents/abstract.tex
```

---

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     INDEX.TS (Main Orchestrator)                     │
└─────────────────────────────────────────────────────────────────────┘
     │
     ├─→ EnhancedEditor                     (editor keyboard input)
     │   ├─ onChange() → SectionsManager.setContent()
     │   └─ undo/redo buttons
     │
     ├─→ SectionsManager                    (in-memory state)
     │   ├─ getContent(section_id)
     │   ├─ setContent(section_id, content)
     │   └─ getAll() for batch save
     │
     ├─→ FileTreeManager                    (sidebar file list)
     │   ├─ load() → fetch /file-tree/
     │   └─ onFileSelect() → loadTexFile() or switchSection()
     │
     ├─→ PDFPreviewManager                  (right panel PDF)
     │   ├─ compileQuick(content) → fetch /compile-preview/
     │   ├─ compile(sections) → fetch /compile-preview/ batch
     │   └─ displayPlaceholder() initially
     │
     ├─→ PDFScrollZoomHandler               (PDF zoom controls)
     │   ├─ zoomIn/zoomOut/fitToWidth/resetZoom()
     │   └─ toggleColorMode() → recompile with color
     │
     ├─→ PanelResizer                       (draggable divider)
     │   └─ onDrag() → adjust left/right pane widths
     │
     ├─→ EditorControls                     (toolbar buttons)
     │   ├─ Font size slider
     │   ├─ Auto-preview checkbox
     │   ├─ Preview button
     │   └─ Compile button
     │
     └─→ CompilationManager                 (job tracking)
         ├─ compileFull() → fetch /compile-full/
         └─ getIsCompiling() state
```

---

## WebSocket Message Flow (NOT CURRENTLY INTEGRATED)

```
┌──────────────────────────────────────────────────────────────────────┐
│                        WebSocket (ws://)                              │
│                  WriterConsumer ↔ Frontend                            │
└──────────────────────────────────────────────────────────────────────┘

CLIENT → SERVER (from browser)
│
├─→ { "type": "text_change",
│      "section_id": "manuscript/abstract",
│      "operation": { "type": "insert", "pos": 100, "text": "new" },
│      "version": 42 }
│
├─→ { "type": "cursor_position",
│      "section": "manuscript/abstract",
│      "position": { "line": 10, "ch": 25 } }
│
├─→ { "type": "section_lock",
│      "section": "manuscript/abstract" }
│
├─→ { "type": "section_unlock",
│      "section": "manuscript/abstract" }
│
├─→ { "type": "undo",
│      "section_id": "manuscript/abstract",
│      "version": 42 }
│
├─→ { "type": "redo",
│      "section_id": "manuscript/abstract",
│      "version": 42 }
│
└─→ { "type": "operation_ack",
      "operation_id": "op-123",
      "section_id": "manuscript/abstract" }

SERVER → CLIENT (to browser)
│
├─→ { "type": "collaborators_list",
│      "collaborators": [
│        { "user_id": 1, "username": "alice", "locked_sections": ["abstract"] },
│        { "user_id": 2, "username": "bob", "locked_sections": [] }
│      ] }
│
├─→ { "type": "user_joined",
│      "user_id": 3,
│      "username": "charlie",
│      "timestamp": "2025-11-04T10:00:00Z" }
│
├─→ { "type": "user_left",
│      "user_id": 2,
│      "username": "bob",
│      "timestamp": "2025-11-04T10:05:00Z" }
│
├─→ { "type": "text_change",
│      "section": "manuscript/abstract",
│      "operation": { ... },
│      "user_id": 1,
│      "username": "alice",
│      "timestamp": "2025-11-04T10:01:00Z" }
│
├─→ { "type": "cursor_update",
│      "section": "manuscript/abstract",
│      "position": { "line": 5, "ch": 10 },
│      "user_id": 1,
│      "username": "alice" }
│
├─→ { "type": "section_locked",
│      "section": "manuscript/abstract",
│      "user_id": 1,
│      "username": "alice",
│      "timestamp": "2025-11-04T10:00:30Z" }
│
├─→ { "type": "section_unlocked",
│      "section": "manuscript/abstract",
│      "user_id": 1,
│      "username": "alice",
│      "timestamp": "2025-11-04T10:02:00Z" }
│
├─→ { "type": "operation_submitted",
│      "operation_id": "op-123",
│      "status": "queued",
│      "queue_length": 3 }
│
└─→ { "type": "error",
      "message": "Something went wrong" }

NOTE: Currently NOT INTEGRATED
- Frontend doesn't send text_change messages
- Only presence updates via HTTP polling
- WebSocket connection ready but dormant
- Framework in place for future integration
```

---

## HTTP Request/Response Examples

### Read Section
```
GET /writer/api/project/1/section/abstract/?doc_type=manuscript

RESPONSE 200:
{
  "success": true,
  "section": "abstract",
  "doc_type": "manuscript",
  "content": "\\section{Abstract}\n\nThis is the abstract..."
}
```

### Write Sections
```
POST /writer/api/project/1/save-sections/
Content-Type: application/json

{
  "sections": {
    "abstract": "New abstract content",
    "introduction": "New introduction content"
  },
  "doc_type": "manuscript"
}

RESPONSE 200:
{
  "success": true,
  "message": "Processed 2 sections (2 saved)",
  "sections_saved": 2,
  "sections_skipped": 0
}
```

### Compile Preview
```
POST /writer/api/project/1/compile-preview/
Content-Type: application/json

{
  "content": "\\documentclass{article}\n\\begin{document}\n...",
  "section_name": "abstract",
  "color_mode": "light",
  "timeout": 60
}

RESPONSE 200:
{
  "success": true,
  "output_pdf": "/path/to/preview-abstract.pdf",
  "pdf_path": "/path/to/preview-abstract.pdf",
  "log": "This is pdflatex output...",
  "error": null
}

OR (on error):

RESPONSE 500:
{
  "success": false,
  "output_pdf": null,
  "pdf_path": null,
  "log": "pdflatex error output...",
  "error": "pdflatex returned 1"
}
```

### Commit Section
```
POST /writer/api/project/1/section/abstract/commit/
Content-Type: application/json

{
  "doc_type": "manuscript",
  "message": "Updated abstract with new findings"
}

RESPONSE 200:
{
  "success": true,
  "message": "Section committed: Updated abstract with new findings",
  "data": {
    "section": "abstract",
    "doc_type": "manuscript",
    "commit_message": "Updated abstract with new findings"
  }
}

OR (if nothing to commit):

RESPONSE 400:
{
  "success": false,
  "error": "No changes to commit. The section has not been modified...",
  "stderr": "nothing to commit, working tree clean"
}
```

---

## State Management

### Frontend State (in-memory)
```javascript
// Global variables from window.WRITER_CONFIG
window.WRITER_CONFIG = {
  projectId: 1,
  projectName: "My Project",
  projectSlug: "my-project",
  userId: 42,
  username: "alice",
  isAuthenticated: true,
  isDemo: false,
  writerInitialized: true,
  csrfToken: "..."
}

// In-memory section cache
const state = {
  currentSection: "manuscript/abstract",
  currentDocType: "manuscript",
  unsavedSections: Set(), // Tracks which sections need saving
  // ... other state
}

// SectionsManager (in-memory storage)
sectionsManager.getContent(section_id)  // Returns content string
sectionsManager.setContent(section_id, content)
sectionsManager.getAll()  // Returns { section_id: content, ... }
```

### Backend State (database)
```python
# WriterPresence (updated every request)
WriterPresence.objects.get_or_create(
  user=request.user,
  project=project,
  defaults={
    'current_section': 'manuscript/abstract',
    'is_active': True
  }
)

# CollaborativeSession (created on WebSocket connect)
CollaborativeSession.objects.update_or_create(
  manuscript=manuscript,
  user=request.user,
  session_id=channel_name,
  defaults={
    'is_active': True,
    'locked_sections': []
  }
)
```

### Filesystem State (on disk)
```
scitex/writer/
├─ .git/                    # Git repository state
├─ 01_manuscript/
│  ├─ manuscript.tex        # Compiled merged document
│  ├─ manuscript.pdf        # Compiled PDF
│  └─ contents/
│     ├─ abstract.tex       # Individual section (auto-saved)
│     └─ ...
└─ preview_output/
   └─ preview-abstract.pdf  # Live preview
```

---

## State Consistency Guarantees

```
┌────────────────────────────────────────────────────────────────┐
│              State Consistency Model                            │
└────────────────────────────────────────────────────────────────┘

EDITOR                      SECTIONS MANAGER              FILESYSTEM
(Monaco/CM)                 (In-Memory Cache)             (Disk)
     ↓                             ↓                          ↓
   [text]                      [content] ←────→ auto-save    [.tex]
     ↑                             ↑                 POST      ↑
     │                             │                           │
User types ──→ onChange() ──→ setContent() ──→ fetch API ──→ write()
                                  ↓                           ↓
                            unsavedSections.add()       [file on disk]
                                  ↓
                            scheduleSave()
                                  ↓
                          fetch /save-sections/
                                  ↓
                          WriterService.write_section()
                                  ↓
                        Writer.section.write()

CONSISTENCY RULES:
1. Editor always matches SectionsManager (onChange updates both)
2. SectionsManager always matches Filesystem (auto-save polls every 5s)
3. Filesystem always matches Git (manual commit breaks this chain)
   - After commit: Filesystem synced with Git
   - Between commits: Filesystem ahead of Git

SPECIAL CASES:
- If user navigates away: unsavedSections stay in memory
- On browser refresh: SectionsManager wiped, reloaded from API
- If network fails: Changes stay in editor until save succeeds
- Multiple users: No conflict detection (OT not integrated)
```

This comprehensive architecture documentation should give you a clear understanding of how the Writer App is organized, how data flows through the system, and where the critical pieces fit together.
