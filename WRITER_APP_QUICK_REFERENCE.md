# Writer App Quick Reference

## What Currently Works (Fully Functional)

### Editor
- **Monaco Editor** with LaTeX support (primary) + CodeMirror fallback
- Syntax highlighting, code completion, themes, keybindings
- Undo/redo, word count, line numbers, auto-save (5s debounce)

### Document Management
- 7 sections per manuscript: Abstract, Introduction, Methods, Results, Discussion, Conclusion, Highlights
- 3 document types: Manuscript, Supplementary, Revision (peer review)
- Section switching with auto-save

### Compilation & Preview
- **Live preview**: Auto-compile on typing (2s delay) → PDF in right pane
- **Full compile**: Click button → compile all sections → output PDF
- **Preview timeout**: 60 seconds per section
- **Color modes**: Light, Dark, Sepia, Paper (injected into LaTeX)
- **PDF controls**: Zoom In/Out, Fit Width, Reset Zoom

### Version Control
- **Auto-save**: Changes saved to disk automatically (no git yet)
- **Manual commits**: Click "Commit" → enter message → git commit created
- **History**: View commits, restore from history
- **Per-section commits**: Each section has its own git history

### User Experience
- Split-pane layout (editor left, PDF right) with resizable divider
- Dark/light theme toggle (synced with site theme)
- Project selector (for users with multiple projects)
- Active users list (shows who's editing and their section)

---

## What Needs Work (Top Issues)

### Critical (Blocking Functionality)
1. **Real-time collaboration**: WebSocket connected but not sending OT messages
   - Currently uses HTTP polling for presence only
   - Framework ready, just needs frontend integration
   
2. **Bibliography**: No UI for searching or inserting citations
   - Manual editing only
   - TODO in `writer-commands.js` lines 219-230
   
3. **Peer review interface**: Revision document structure exists but UI incomplete
   - Can't create comment/response/revision triplets yet
   - Just editable text sections

### Medium (Quality/Polish)
4. **Error handling**: Compilation errors shown as alerts, not logged to central log
5. **Performance**: pdflatex can be slow for large sections (60s timeout limit)
6. **Search/replace**: Hidden in toolbar, not easily discoverable

---

## File Locations (What to Edit)

### Frontend Code

**TypeScript Modules** (compile to JS):
- Main entry: `/apps/writer_app/static/writer_app/ts/index.ts` (huge file, coordinates everything)
- Editor: `/apps/writer_app/static/writer_app/ts/modules/monaco-editor.ts`
- PDF preview: `/apps/writer_app/static/writer_app/ts/modules/pdf-preview.ts`
- Sections: `/apps/writer_app/static/writer_app/ts/modules/sections.ts`
- File tree: `/apps/writer_app/static/writer_app/ts/modules/file_tree.ts`

**Compiled JavaScript** (auto-generated, don't edit):
- `/apps/writer_app/static/writer_app/js/index.js` (compiled from index.ts)
- `/apps/writer_app/static/writer_app/js/modules/*.js` (compiled modules)

**Styles**:
- Main editor: `/apps/writer_app/static/writer_app/css/latex-editor.css`
- PDF view: `/apps/writer_app/static/writer_app/css/pdf-view-main.css`
- Layout: `/apps/writer_app/static/writer_app/css/index-editor-panels.css`
- (13+ CSS files total)

**Templates**:
- Main page: `/apps/writer_app/templates/writer_app/index.html`
- Partials in: `/apps/writer_app/templates/writer_app/index_partials/`

### Backend Code

**Django Models**:
- `/apps/writer_app/models/core.py` - Manuscript (minimal)
- `/apps/writer_app/models/collaboration.py` - WriterPresence, CollaborativeSession

**Views**:
- `/apps/writer_app/views/main_views.py` - Page views, workspace initialization
- `/apps/writer_app/views/api_views.py` - REST API endpoints (150+ lines each)

**Services**:
- `/apps/writer_app/services/writer_service.py` - Django wrapper for scitex.writer
- `/apps/writer_app/services/compiler.py` - Compilation management
- `/apps/writer_app/services/operational_transform_service.py` - OT framework (not integrated)

**WebSocket**:
- `/apps/writer_app/consumers.py` - WriterConsumer (async, ready to use)
- `/apps/writer_app/routing.py` - WebSocket URL routing

**Configuration**:
- `/apps/writer_app/configs/sections_config.py` - Section hierarchy

---

## API Endpoints (REST)

All under: `/writer/api/project/{project_id}/`

### Sections
```
GET  /section/{name}/?doc_type=manuscript     # Read section
POST /section/{name}/                          # Write section
POST /section/{name}/commit/                   # Git commit
GET  /section/{name}/history/                  # Git log
GET  /section/{name}/diff/                     # Uncommitted changes
POST /section/{name}/checkout/                 # Restore from history
```

### Compilation
```
POST /compile-preview/                         # Quick preview (section)
POST /compile-full/                            # Full manuscript (workspace)
GET  /pdf/?doc_type=manuscript                 # Get compiled PDF
GET  /preview-pdf/?section=abstract            # Get preview PDF
```

### File Management
```
GET  /file-tree/                               # Directory structure
GET  /read-tex-file/?path=main.tex             # Read .tex file
GET  /available-sections/                      # Section list by doc type
POST /save-sections/                           # Batch save sections
```

### Presence (Collaboration)
```
POST /presence/update/                         # Update current section
GET  /presence/list/                           # Active users
```

---

## Database Models

### Manuscript
- Links user & project to scitex.writer.Writer
- Stores manuscript title & description (display only)
- `@property writer_initialized`: Checks if workspace exists on filesystem

### WriterPresence (Polling-based)
- `user`, `project`, `current_section`, `last_seen`, `is_active`
- `@classmethod get_active_users(project_id, minutes=2)`: Returns users active in last N minutes

### CollaborativeSession (WebSocket)
- `manuscript`, `user`, `session_id`, `locked_sections`, `cursor_position`
- Tracks editing sessions (when created, last activity, who locked what)
- **Note**: Section locks detected but not enforced in UI

---

## Code Flow Examples

### User Edits Section
```
User types in editor
  → EnhancedEditor.onChange() fires
  → SectionsManager.setContent() (in-memory)
  → scheduleSave() debounces (5 seconds)
  → fetch /writer/api/project/{id}/save-sections/ POST
  → WriterService.write_section()
  → Writer.manuscript.contents.section.write()
  → File written to: scitex/writer/manuscript/contents/abstract.tex
  → Auto-save complete (no git commit yet)
```

### User Compiles to View PDF
```
User stops typing
  → scheduleAutoCompile() waits 2 seconds
  → fetch /writer/api/project/{id}/compile-preview/ POST (section content)
  → WriterService.compile_preview() → subprocess.run(pdflatex)
  → PDF written to: scitex/writer/preview_output/preview-abstract.pdf
  → <iframe src> updated to show PDF
  → PDF visible in right pane (live preview)
```

### User Commits Changes to Git
```
User clicks "Commit" button
  → showCommitModal() opens dialog
  → User types commit message
  → fetch /writer/api/project/{id}/section/abstract/commit/ POST
  → WriterService.commit_section(message)
  → Writer.manuscript.contents.abstract.commit(message)
  → git add scitex/writer/manuscript/contents/abstract.tex
  → git commit -m "user message"
  → Commit appears in git history
```

---

## Key Numbers

| What | Value | Notes |
|------|-------|-------|
| Auto-save debounce | 5 seconds | User types, changes saved after 5s inactivity |
| Live preview delay | 2 seconds | User stops typing, PDF compiles 2s later |
| Preview timeout | 60 seconds | pdflatex max time for section preview |
| Full compile timeout | 300 seconds | pdflatex max time for full manuscript |
| Presence timeout | 2 minutes | User considered "active" if seen in last 2 min |
| Session timeout | 5 minutes | Collaborative session ends if no activity |
| Editor font size | 14-20px | Adjustable via toolbar slider |
| Max history size | 50 entries | Editor undo/redo history limit |
| LaTeX completions | 50+ commands | Snippets for document structure |

---

## Common Tasks

### Add a New Section
1. Add to `SECTION_HIERARCHY` in `/apps/writer_app/configs/sections_config.py`
2. Frontend automatically loads it in dropdown
3. API creates file on first write

### Change Default Font Size
- Edit `/apps/writer_app/static/writer_app/ts/modules/monaco-editor.ts` line ~150
- Change `fontSize: 14,` to desired size

### Change Auto-save Delay
- Edit `/apps/writer_app/static/writer_app/ts/index.ts` function `scheduleSave()`
- Change `5000` (milliseconds) to desired delay

### Change Preview Compile Timeout
- Edit `/apps/writer_app/services/writer_service.py` function `compile_preview()`
- Change `timeout: int = 60` to desired seconds

### Add LaTeX Command to Autocomplete
- Edit `/apps/writer_app/static/writer_app/ts/modules/monaco-editor.ts`
- Find array `suggestions` in `provideCompletionItems()` function
- Add new object: `{ label: '\\command', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\command{$0}', ... }`

### Enable Monaco Minimap
- Edit `/apps/writer_app/static/writer_app/ts/modules/monaco-editor.ts` line ~153
- Change `minimap: { enabled: false },` to `minimap: { enabled: true },`

---

## Debugging Tips

### Check if Writer is Initialized
```python
from apps.writer_app.models import Manuscript
m = Manuscript.objects.get(project_id=1)
print(m.writer_initialized)  # True if scitex/writer/ exists
```

### Check Section Content
```python
from apps.writer_app.services.writer_service import WriterService
service = WriterService(project_id=1, user_id=1)
content = service.read_section('abstract', 'manuscript')
print(content)
```

### Check Git History
```bash
cd data/users/{username}/{project-slug}/scitex/writer/
git log --oneline
git log -- 01_manuscript/contents/abstract.tex
```

### Monitor Live Preview
```bash
ls -la data/users/{username}/{project-slug}/scitex/writer/preview_output/
# Check if PDFs are being created
```

### Check for Compilation Errors
```
Open browser DevTools → Network tab
Filter by "compile" requests
Check response body for error details
```

---

## Performance Notes

### Slow Compilation?
- pdflatex is slow for large documents (10+ pages takes 30-60s)
- Live preview 60s timeout is hardcoded
- Consider breaking into smaller sections

### Slow Section Switching?
- Large sections (10k+ lines) take time to render
- Monaco handles this better than CodeMirror
- Enable virtualScrolling if needed

### High Memory Usage?
- Sections loaded into memory (SectionsManager)
- Large projects with many sections will use more RAM
- Consider lazy-loading for future improvement

---

## When Something Breaks

1. **Check browser console** (F12 → Console tab) for JavaScript errors
2. **Check server logs** (terminal running `./start_dev.sh`) for Python errors
3. **Check API responses** (F12 → Network tab → filter by XHR) for backend errors
4. **Check filesystem** (`ls -la scitex/writer/`) for missing directories
5. **Check git status** (`git status` in project dir) for unstaged changes

Common errors:
- **"Writer not initialized"**: Run workspace initialization from UI
- **"Project not found"**: Check project ID in URL
- **"Access denied"**: User doesn't own project
- **"Compilation timeout"**: Section too large for 60s, try smaller content
