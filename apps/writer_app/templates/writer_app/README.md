# SciTeX Writer Templates

This directory contains templates for the SciTeX Writer application, organized following the same structure as scholar_app.

## Directory Structure

```
writer_app/templates/writer_app/
├── index.html                      # Main page - project-linked writer (most sophisticated)
├── writer_base.html                # Base template for all writer pages
├── legacy/                         # Old/obsolete templates moved here
│   ├── index_landing.html         # Old landing page (removed 2025-10-24)
│   ├── index_partials/            # Old partials (removed 2025-10-24)
│   ├── modular_editor.html        # Modular text-based editor
│   └── simple_editor.html         # Simple LaTeX editor
├── collaborative_editor.html      # Real-time collaborative editing
├── compilation_view.html          # Compilation status and logs
├── default_workspace.html         # Default workspace for users without projects
├── mvp_dashboard.html            # MVP simplified dashboard
├── mvp_editor.html               # MVP simplified editor
└── version_control_dashboard.html # Version control interface
```

## Main Templates

### index.html
- **Purpose**: Main page - project-linked writer interface (most sophisticated)
- **Requirements**: Accessible to all users (guest or logged-in)
- **Features**: Full manuscript editing with sections, word counts, LaTeX editing, workspace initialization
- **URL**: `/writer/`
- **Note**: Previously named `project_writer.html`, renamed to follow scholar_app convention (2025-10-24)

### mvp_editor.html
- **Purpose**: Simplified Overleaf-style editor
- **Features**: CodeMirror editor, PDF preview, compilation
- **URL**: `/writer/advanced/`

### mvp_dashboard.html
- **Purpose**: Simplified dashboard for authenticated users
- **Features**: Manuscript list, compilation history, metrics
- **URL**: `/writer/advanced/dashboard/`

## Organization Principles

Following scholar_app structure:
1. **Main page**: `index.html` - THE main entry point at `/writer/`
2. **Base**: `writer_base.html` - consistent styling across all pages
3. **Legacy**: `legacy/` - old templates kept for reference

## Template Accessibility

- **Public** (no login required): `index.html` (with guest mode)
- **Authenticated** (login required): `mvp_dashboard.html`, `mvp_editor.html`
- **Collaborative**: `collaborative_editor.html`

## Recent Changes (2025-10-24)

- Renamed `project_writer.html` → `index.html` to match scholar_app convention
- Moved old `index.html` → `legacy/index_landing.html`
- Moved `index_partials/` → `legacy/index_partials/`
- Simplified structure: ONE main page (`index.html`) for `/writer/`

Last updated: 2025-10-24
