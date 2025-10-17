# Writer App Enhancement Plan

**Project**: SciTeX Cloud - Writer App
**Goal**: Integrate neurovista/paper functionality into Django writer_app
**Date**: 2025-10-16

## Overview

Enhance the writer_app to provide a comprehensive web-based LaTeX manuscript preparation system, integrating the modular structure and compilation workflow from `~/proj/neurovista/paper/`.

## Current Status

### ✅ Already Implemented (writer_app)
- Basic manuscript models (Manuscript, ManuscriptSection, Figure, Table, Citation)
- Project-linked manuscripts
- Modular structure creation (`create_modular_structure()`)
- Basic LaTeX compilation with job tracking
- Version control and branching
- Collaborative editing infrastructure
- arXiv submission integration

### 📦 Available in neurovista/paper (External)
- Unified compilation interface (`./compile`)
- Modular document structure (manuscript/supplementary/revision)
- Shared metadata (title, authors, keywords via symlinks)
- Container-based compilation system
- Watch mode for hot-recompiling
- Figure/table auto-conversion
- Mermaid diagram support
- Bibliography analysis tools
- Word count tracking per section

## Core Features to Implement

### 1. Separate TeX File Editing ⭐ HIGH PRIORITY

**Goal**: Allow users to edit individual LaTeX section files through web interface

**Implementation**:
```
Structure:
project/paper/
├── 01_manuscript/
│   └── contents/
│       ├── abstract.tex
│       ├── introduction.tex
│       ├── methods.tex
│       ├── results.tex
│       ├── discussion.tex
│       └── figures/
├── 02_supplementary/
│   └── contents/
│       └── [similar structure]
├── 03_revision/
│   └── contents/
│       └── [revision responses]
└── shared/
    ├── title.tex
    ├── authors.tex
    ├── keywords.tex
    └── bib_files/
        └── bibliography.bib
```

**Features**:
- ✅ Load individual .tex files (already implemented via `load_latex_section`)
- ✅ Save individual .tex files (already implemented via `save_latex_section`)
- 🔨 Add multi-document support (manuscript/supplementary/revision)
- 🔨 Create shared metadata editor (title, authors, keywords)
- 🔨 Add syntax highlighting for LaTeX editing
- 🔨 Real-time preview of sections

**API Endpoints**:
```python
# Already exist:
GET  /writer/project/<project_id>/load-section/?section=<name>&doc_type=<type>
POST /writer/project/<project_id>/save-section/

# To add:
GET  /writer/project/<project_id>/shared/<metadata_type>/  # title, authors, keywords
POST /writer/project/<project_id>/shared/<metadata_type>/
GET  /writer/project/<project_id>/document-types/  # list manuscript, supplementary, revision
```

---

### 2. Figure/Table Management ⭐ HIGH PRIORITY

**Goal**: Upload, organize, and manage figures/tables with captions

**Implementation**:

**Upload Interface**:
- Drag-and-drop file upload
- Support formats: `.jpg`, `.png`, `.tif`, `.pdf`, `.mmd` (Mermaid)
- Auto-organize into `figures/` or `tables/` directories
- Generate LaTeX figure/table code snippets

**Storage Structure**:
```
project/paper/01_manuscript/contents/
├── figures/
│   ├── caption_and_media/
│   │   ├── fig1_network_architecture.png
│   │   ├── fig2_results_comparison.jpg
│   │   └── fig3_workflow.mmd
│   └── generated/  # auto-converted formats
└── tables/
    ├── caption_and_media/
    │   ├── table1_demographics.xlsx
    │   └── table2_results.csv
    └── generated/  # LaTeX tables
```

**Features**:
- 🔨 File upload with preview
- 🔨 Caption editor for each figure/table
- 🔨 Order/numbering management
- 🔨 LaTeX snippet generator (`\includegraphics`, `\begin{table}`)
- 🔨 Auto-conversion (Mermaid → PNG, CSV → LaTeX table)
- 🔨 Reference tracking (which sections use which figures)

**Models** (already exist, need enhancement):
```python
class Figure(models.Model):
    manuscript = ForeignKey(Manuscript)
    file = ImageField(upload_to='manuscripts/figures/')
    caption = TextField()
    label = CharField()  # fig:network_arch
    order = IntegerField()
    document_type = CharField()  # manuscript, supplementary, revision
    # Add: mermaid_source, auto_generated_from

class Table(models.Model):
    manuscript = ForeignKey(Manuscript)
    data_file = FileField()  # CSV/Excel source
    content = TextField()  # Generated LaTeX
    caption = TextField()
    label = CharField()
    order = IntegerField()
    document_type = CharField()
```

**API Endpoints**:
```python
POST /writer/project/<project_id>/upload-figure/
POST /writer/project/<project_id>/upload-table/
GET  /writer/project/<project_id>/figures/
GET  /writer/project/<project_id>/tables/
PUT  /writer/project/<project_id>/figure/<id>/caption/
PUT  /writer/project/<project_id>/figure/<id>/order/
DELETE /writer/project/<project_id>/figure/<id>/
```

---

### 3. Unified Compilation System ⭐ HIGH PRIORITY

**Goal**: Integrate neurovista/paper compilation workflow

**Current Implementation**:
- ✅ Basic compilation job tracking (CompilationJob model)
- ✅ PDF generation
- ⚠️ Limited: Only single-document compilation

**Enhancement Required**:

**Compilation Options**:
```python
# Delegate to neurovista/paper compile script
./compile -m  # manuscript
./compile -s  # supplementary
./compile -r  # revision
```

**Implementation Strategy**:
```python
def compile_manuscript(manuscript, doc_type='manuscript'):
    """
    Use neurovista/paper compile script.

    Args:
        manuscript: Manuscript instance
        doc_type: 'manuscript', 'supplementary', or 'revision'
    """
    paper_path = manuscript.get_project_paper_path()
    compile_script = paper_path / 'compile'

    # Run compilation
    result = subprocess.run(
        ['bash', 'compile', f'-{doc_type[0]}'],  # -m, -s, -r
        cwd=paper_path,
        capture_output=True,
        timeout=300
    )

    # Track output PDFs
    pdf_paths = {
        'manuscript': paper_path / '01_manuscript/manuscript.pdf',
        'supplementary': paper_path / '02_supplementary/supplementary.pdf',
        'revision': paper_path / '03_revision/revision.pdf'
    }

    return {
        'success': result.returncode == 0,
        'pdf_path': pdf_paths[doc_type],
        'log': result.stdout
    }
```

**Features**:
- 🔨 Multi-document compilation (manuscript, supplementary, revision)
- 🔨 Compilation queue management
- 🔨 Progress tracking with WebSocket updates
- 🔨 Error reporting with LaTeX log parsing
- 🔨 PDF preview in browser
- 🔨 Download compiled PDFs
- 🔨 Compilation history

**API Endpoints**:
```python
POST /writer/project/<project_id>/compile/  # body: {doc_type: 'manuscript'}
GET  /writer/project/<project_id>/compile/<job_id>/status/
GET  /writer/project/<project_id>/compile/<job_id>/pdf/
GET  /writer/project/<project_id>/compilation-history/
```

---

### 4. Watch Mode (Hot-Recompiling) 🔄 MEDIUM PRIORITY

**Goal**: Auto-recompile on file changes (optional feature)

**Implementation**:
- Use WebSocket for file change notifications
- Run `./compile -m -w` in background process
- Stream compilation output to frontend
- Update PDF preview automatically

**Technical Approach**:
```python
# Using Django Channels
class CompilationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.manuscript_id = self.scope['url_route']['kwargs']['manuscript_id']
        await self.accept()

        # Start watch compilation
        await self.start_watch_compilation()

    async def start_watch_compilation(self):
        # Run compile -m -w in background
        # Stream stdout to WebSocket
        pass
```

**Features**:
- 🔨 Enable/disable watch mode
- 🔨 Real-time compilation status
- 🔨 Auto-refresh PDF preview
- 🔨 Error notifications

---

### 5. LaTeX ↔ Plain Text Conversion 🔄 MEDIUM PRIORITY

**Goal**: Allow users to edit in plain text or LaTeX mode

**Use Cases**:
- Beginners: Write in plain text, system generates LaTeX
- Advanced users: Write LaTeX directly
- Collaborative: Mixed editing modes

**Implementation**:

**Text → LaTeX Conversion**:
```python
def text_to_latex(plain_text: str) -> str:
    """
    Convert plain text to LaTeX.

    - Detect sections (headings)
    - Wrap paragraphs
    - Escape special characters
    - Detect equations (lines with math symbols)
    """
    # Basic conversion
    latex = plain_text

    # Escape LaTeX special characters
    for char in ['&', '%', '$', '#', '_', '{', '}', '~', '^', '\\']:
        latex = latex.replace(char, f'\\{char}')

    # Detect equations (heuristic: lines with =, +, -, *, /)
    # Wrap in $ ... $ or \[ ... \]

    # Add paragraph breaks
    latex = re.sub(r'\n\n+', r'\n\n', latex)

    return latex
```

**LaTeX → Text Conversion**:
```python
def latex_to_text(latex_content: str) -> str:
    """
    Convert LaTeX to readable plain text.

    - Remove LaTeX commands
    - Keep text content
    - Preserve structure
    """
    # Remove comments
    text = re.sub(r'%.*', '', latex_content)

    # Remove commands but keep arguments
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)

    # Remove environment wrappers
    text = re.sub(r'\\begin\{[^}]*\}', '', text)
    text = re.sub(r'\\end\{[^}]*\}', '', text)

    return text.strip()
```

**Features**:
- 🔨 Toggle editing mode (LaTeX / Plain Text)
- 🔨 Bidirectional conversion
- 🔨 Preserve special formatting where possible
- 🔨 Equation detection and protection
- 🔨 AI-assisted conversion (optional, using LLM)

**UI Toggle**:
```html
<div class="editor-mode-toggle">
    <button id="mode-latex">LaTeX Mode</button>
    <button id="mode-text">Text Mode</button>
</div>
<textarea id="section-editor"></textarea>
```

---

### 6. Simultaneous Editing 🔄 MEDIUM PRIORITY

**Goal**: Real-time collaborative editing

**Current Status**:
- ✅ CollaborativeSession model exists
- ✅ Section locking mechanism
- ⚠️ WebSocket infrastructure needed

**Implementation**:
```python
# Django Channels for WebSocket
# apps/writer_app/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/writer/manuscript/<manuscript_id>/',
         consumers.ManuscriptEditConsumer.as_asgi()),
]
```

**Operational Transform (OT)**:
```python
class OperationalTransform:
    """Simple OT for text editing."""

    def transform_insert(op1, op2):
        """Transform insert operations."""
        if op1.position <= op2.position:
            return op1
        else:
            op1.position += len(op2.text)
            return op1

    def transform_delete(op1, op2):
        """Transform delete operations."""
        # Handle conflict resolution
        pass
```

**Features**:
- 🔨 WebSocket-based real-time sync
- 🔨 Operational Transform for conflict resolution
- 🔨 User presence indicators
- 🔨 Section-level locking
- 🔨 Change history per session
- 🔨 Cursor position tracking

---

## Implementation Priority

### Phase 1: Core Editing (2-3 weeks)
1. ✅ Separate TeX file editing (mostly done)
2. 🔨 Shared metadata editor (title, authors, keywords)
3. 🔨 Multi-document support (manuscript/supplementary/revision)

### Phase 2: Asset Management (2 weeks)
4. 🔨 Figure upload and management
5. 🔨 Table upload and management
6. 🔨 LaTeX snippet generation

### Phase 3: Compilation (1-2 weeks)
7. 🔨 Unified compilation system
8. 🔨 PDF preview and download
9. 🔨 Error reporting

### Phase 4: Advanced Features (3-4 weeks)
10. 🔨 Watch mode (hot-recompiling)
11. 🔨 LaTeX ↔ Text conversion
12. 🔨 Real-time collaborative editing

---

## Technical Architecture

### Directory Structure
```
scitex-cloud/
├── apps/
│   └── writer_app/
│       ├── models.py              # ✅ Already comprehensive
│       ├── views.py               # ✅ Basic CRUD done
│       ├── compilation_views.py   # 🔨 New: Compilation endpoints
│       ├── figure_views.py        # 🔨 New: Figure/table management
│       ├── shared_views.py        # 🔨 New: Shared metadata
│       ├── consumers.py           # 🔨 New: WebSocket consumers
│       ├── latex_utils.py         # 🔨 New: LaTeX conversion
│       ├── templates/writer_app/
│       │   ├── project_writer.html          # ✅ Exists
│       │   ├── section_editor.html          # 🔨 New
│       │   ├── figure_manager.html          # 🔨 New
│       │   └── compilation_dashboard.html   # 🔨 New
│       └── static/writer_app/
│           ├── js/
│           │   ├── section_editor.js        # 🔨 New
│           │   ├── figure_upload.js         # 🔨 New
│           │   └── collaborative_edit.js    # 🔨 New
│           └── css/
│               └── writer.css
├── externals/
│   └── paper/                     # Symlink to ~/proj/neurovista/paper
│       ├── compile                # ✅ Use as-is
│       ├── 01_manuscript/         # ✅ Template structure
│       ├── 02_supplementary/
│       └── scripts/
└── data/
    └── user_data/
        └── <user_id>/
            └── projects/
                └── <project_id>/
                    └── paper/     # Created per project
                        ├── 01_manuscript/
                        ├── 02_supplementary/
                        ├── 03_revision/
                        └── shared/
```

### Database Schema Additions

```python
# Add to existing models
class Manuscript(models.Model):
    # Add:
    document_types_enabled = JSONField(default=list)  # ['manuscript', 'supplementary', 'revision']
    active_document_type = CharField(default='manuscript')

class Figure(models.Model):
    # Add:
    document_type = CharField()  # manuscript, supplementary, revision
    mermaid_source = TextField(blank=True)  # For .mmd files
    auto_generated = BooleanField(default=False)

class SharedMetadata(models.Model):
    """New model for shared metadata."""
    manuscript = OneToOneField(Manuscript)
    title = TextField()
    authors = TextField()
    keywords = TextField()
    journal_name = CharField()
    updated_at = DateTimeField(auto_now=True)
```

---

## API Specification

### Section Editing
```
GET    /api/writer/project/<id>/sections/               # List all sections
GET    /api/writer/project/<id>/section/<name>/         # Load section content
PUT    /api/writer/project/<id>/section/<name>/         # Save section content
POST   /api/writer/project/<id>/section/<name>/convert/ # LaTeX ↔ Text
```

### Figure/Table Management
```
POST   /api/writer/project/<id>/figures/                # Upload figure
GET    /api/writer/project/<id>/figures/                # List figures
PUT    /api/writer/project/<id>/figures/<fig_id>/       # Update caption/order
DELETE /api/writer/project/<id>/figures/<fig_id>/       # Delete figure
POST   /api/writer/project/<id>/tables/                 # Upload table
```

### Compilation
```
POST   /api/writer/project/<id>/compile/                # Start compilation
GET    /api/writer/project/<id>/compile/<job_id>/       # Get status
GET    /api/writer/project/<id>/compile/<job_id>/pdf/   # Download PDF
```

### Shared Metadata
```
GET    /api/writer/project/<id>/metadata/               # Get all metadata
PUT    /api/writer/project/<id>/metadata/title/         # Update title
PUT    /api/writer/project/<id>/metadata/authors/       # Update authors
```

### WebSocket
```
WS     /ws/writer/manuscript/<id>/                      # Real-time editing
```

---

## Dependencies

### Python Packages (to add)
```
# requirements.txt additions
channels==4.0.0                  # WebSocket support
channels-redis==4.1.0            # Redis backend for Channels
redis==5.0.0                     # Redis client
Pillow==10.0.0                   # Image processing
PyPDF2==3.0.0                    # PDF manipulation
```

### Frontend Libraries
```html
<!-- Already using -->
<script src="bootstrap.js"></script>
<script src="jquery.js"></script>

<!-- To add -->
<script src="codemirror.js"></script>        <!-- LaTeX syntax highlighting -->
<script src="pdfjs"></script>                 <!-- PDF preview -->
<script src="socket.io.js"></script>          <!-- WebSocket client -->
```

---

## Testing Strategy

### Unit Tests
- LaTeX conversion functions
- Citation extraction
- File operations

### Integration Tests
- Compilation workflow
- WebSocket communication
- File upload/download

### End-to-End Tests
- Complete manuscript editing flow
- Multi-user collaborative editing
- Compilation and PDF generation

---

## Deployment Considerations

### Docker
```dockerfile
# Add to Dockerfile
RUN apt-get update && apt-get install -y \
    texlive-full \
    imagemagick \
    chromium-browser

# For Mermaid diagrams
RUN npm install -g @mermaid-js/mermaid-cli
```

### Redis for Channels
```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Environment Variables
```bash
# .env
REDIS_URL=redis://localhost:6379/0
LATEX_TIMEOUT=300
ENABLE_WATCH_MODE=True
```

---

## Success Metrics

- ✅ Users can edit all manuscript sections separately
- ✅ Users can upload and manage figures/tables
- ✅ Compilation succeeds for manuscript, supplementary, revision
- ✅ PDF preview works in browser
- ✅ Real-time editing works for 2+ concurrent users
- ✅ LaTeX ↔ Text conversion maintains content integrity

---

## Future Enhancements (Beyond Initial Scope)

- AI-powered writing assistance (grammar, style, citations)
- Template gallery (journal-specific templates)
- Export to Word (.docx)
- Integration with reference managers (Zotero, Mendeley)
- Automated figure generation from code
- Version comparison with visual diff
- Comments and annotations on sections
- Publishing workflow integration

---

## Timeline

**Total Estimated Time**: 8-10 weeks

- **Week 1-2**: Core editing features
- **Week 3-4**: Asset management (figures/tables)
- **Week 5-6**: Compilation system
- **Week 7-8**: LaTeX conversion
- **Week 9-10**: Collaborative editing, polish, testing

---

## Notes

- Prioritize stability over features
- Keep UI simple and intuitive
- Leverage existing neurovista/paper scripts
- Ensure backward compatibility with existing manuscripts
- Document all API endpoints thoroughly

---

**Last Updated**: 2025-10-16
**Status**: Planning Phase
