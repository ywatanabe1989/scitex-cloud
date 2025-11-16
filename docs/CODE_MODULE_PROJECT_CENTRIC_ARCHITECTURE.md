# Code Module: Project-Centric Architecture

**Date:** 2025-11-15
**Status:** Design Document
**Goal:** Transform Code module from isolated Jupyter notebooks to project-centric workspace with reproducible script execution

---

## Current State vs Desired State

### Current (Isolated, Not Project-Centric)

```
Code Module (apps/code_app)
├── Notebooks stored in: MEDIA_ROOT/notebooks/{user_id}/
├── No project relationship (user-centric only)
├── CodeMirror editor (basic, no IntelliSense)
├── No file navigation
├── No terminal access
└── Cannot commit to Git (files not in repository)
```

**Problems:**
- ❌ Not project-centric (violates CLAUDE.md requirement)
- ❌ No reproducibility tracking
- ❌ No file tree navigation
- ❌ No terminal for running scripts
- ❌ Cannot use Git integration
- ❌ Isolated from project workflow

### Desired (Project-Centric Workspace)

**Your Proposed Structure (Approved! ✅):**

```
Project Workspace (/data/users/{username}/{project}/)
├── scitex/                   # ← Framework-managed modules
│   ├── writer/               #    LaTeX manuscript (structured)
│   │   ├── 01_manuscript/
│   │   │   ├── base.tex
│   │   │   ├── contents/     #    introduction.tex, methods.tex, etc.
│   │   │   ├── manuscript.tex
│   │   │   └── docs/         #    LaTeX guides
│   │   ├── 02_supplementary/
│   │   └── 03_revision/
│   ├── scholar/              #    Bibliography management
│   │   ├── bib_files/        #    Individual .bib files
│   │   └── references.bib    #    Merged bibliography
│   └── (future: viz, etc.)   #    Additional framework modules
│
├── scripts/                  # ← User's analysis code (flexible!)
│   ├── mnist/                #    Organized by experiment
│   │   ├── clf_svm.py        #    Scripts with @stx.session
│   │   ├── clf_svm_out/      #    Auto-generated outputs
│   │   │   ├── FINISHED_SUCCESS/
│   │   │   └── RUNNING/
│   │   ├── download.py
│   │   ├── download_out/
│   │   │   └── data/mnist/
│   │   ├── plot_digits.py
│   │   ├── plot_digits_out/
│   │   │   └── data/mnist/figures/
│   │   ├── plot_umap_space.py
│   │   ├── plot_umap_space_out/
│   │   └── main.sh           #    Bash orchestration
│   └── template.py           #    Template for new scripts
│
├── config/                   # Project configuration
│   ├── MNIST.yaml            #    Experiment configs
│   └── PATH.yaml             #    Path configs
├── data/                     # Centralized data (symlink target)
├── docs/                     # Project documentation
├── externals/                # External dependencies
├── project_management/       # Project management files
├── tests/                    # Unit tests
├── README.md                 # Project overview
├── .git/                     # Git repository
└── .scitex/                  # SciTeX session tracking
```

**Design Philosophy:**

**Separation of Concerns:**
- `scitex/` = **Framework modules** (structured, opinionated, web UI managed)
- `scripts/` = **User code** (flexible, experimental, IDE managed)

**Why This is Better:**
1. ✅ **Flexibility** - Scientists can organize scripts/ however they want
2. ✅ **Gradual adoption** - Can use @stx.session when ready, not required
3. ✅ **Mixed workflows** - Python, bash, R, Julia all in scripts/
4. ✅ **Clear boundaries** - Framework stuff vs user stuff
5. ✅ **Matches mental model** - How researchers actually work

**From Template Research:**
- ✅ Keep `scripts/` at root (not scitex/code/)
- ✅ `paper/` → `scitex/writer/` (framework module)
- ✅ Add `scitex/scholar/` (new framework module)
- ✅ Keep `config/`, `data/`, `docs/` at root
- ✅ All `_out/` directories auto-created by @stx.session

**Benefits:**
- ✅ Project-centric (all modules integrated)
- ✅ Reproducible (scitex.session tracking)
- ✅ Git version control (auto-commit on save/run)
- ✅ File navigation (directory tree)
- ✅ Terminal access (run scripts directly)
- ✅ Professional IDE experience

---

## Architecture: Monaco Editor vs VS Code

### Option 1: Monaco Editor (Recommended ⭐)

**What is Monaco?**
- The **editor component** from VS Code
- MIT licensed, standalone library
- Used by: GitHub, StackBlitz, CodeSandbox

**Pros:**
- ✅ Lightweight (~2-3 MB gzipped)
- ✅ Full IntelliSense, autocomplete, syntax highlighting
- ✅ Python language server support
- ✅ Easy Django integration (just serve static files)
- ✅ Customizable (can hide/show features)
- ✅ No external dependencies (self-hosted)
- ✅ Works with your existing backend

**Cons:**
- ⚠️ Requires custom file tree implementation
- ⚠️ Requires custom terminal integration
- ⚠️ More frontend development needed

**Implementation:**
```html
<!-- Monaco Editor Setup -->
<script src="{% static 'monaco-editor/min/vs/loader.js' %}"></script>
<script>
  require.config({ paths: { vs: '{% static "monaco-editor/min/vs" %}' } });
  require(['vs/editor/editor.main'], function() {
    const editor = monaco.editor.create(document.getElementById('editor'), {
      value: '# Python script\\nimport scitex as stx\\n',
      language: 'python',
      theme: 'vs-dark',
      automaticLayout: true,
      minimap: { enabled: true },
    });
  });
</script>
```

### Option 2: VS Code Server (code-server)

**What is VS Code Server?**
- Full VS Code running in browser
- Runs as separate server process
- Maintained by Coder (https://github.com/coder/code-server)

**Pros:**
- ✅ Complete VS Code experience
- ✅ All extensions work (Pylance, Jupyter, GitLens)
- ✅ Built-in terminal
- ✅ Built-in file tree
- ✅ Git integration built-in
- ✅ Debugging support

**Cons:**
- ❌ Heavy (~200 MB download, ~500 MB RAM)
- ❌ Separate server process (complexity)
- ❌ Authentication challenges (iframe security)
- ❌ Harder to integrate with Django
- ❌ Overkill for most users

**Implementation:**
```yaml
# docker-compose.yml
code-server:
  image: codercom/code-server:latest
  volumes:
    - ./data/users:/home/coder/projects
  ports:
    - "8443:8080"
  environment:
    - PASSWORD=your_password
```

### Option 3: Keep CodeMirror (Not Recommended)

**Current Setup:**
- Basic syntax highlighting
- No IntelliSense
- No autocomplete
- Limited features

**Why Upgrade?**
- Users expect modern IDE features
- Python development needs autocomplete
- Scientific computing benefits from IntelliSense

---

## Recommendation: Monaco + Custom Components

**Why Monaco?**
1. **Best balance** of features vs complexity
2. **Full IDE experience** without heavyweight VS Code server
3. **Easy integration** with existing Django architecture
4. **Self-hosted** - no external dependencies
5. **Customizable** - can add exactly what users need

**Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│  Project-Centric Code Workspace                         │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌───────────────────┐  ┌──────────┐ │
│  │ File Tree    │  │  Monaco Editor    │  │ Terminal │ │
│  │              │  │                   │  │          │ │
│  │ 📁 scitex/   │  │ #!/usr/bin/python3│  │ $ cd scr │ │
│  │  📁 writer/  │  │ import scitex as  │  │ ipts/mni │ │
│  │  📁 scholar/ │  │ stx               │  │ st       │ │
│  │ 📁 scripts/  │  │                   │  │ $ python │ │
│  │  📁 mnist/   │  │ @stx.session      │  │  clf_svm │ │
│  │   📄 *.py ✓  │  │ def main():       │  │ .py      │ │
│  │  📄 template │  │   ...             │  │ Running. │ │
│  │ 📁 config/   │  │                   │  │ ..       │ │
│  └──────────────┘  └───────────────────┘  └──────────┘ │
│                                                           │
│  [Save] [Run] [Git Status] [Terminal Toggle]             │
└─────────────────────────────────────────────────────────┘
```

---

## Component Implementation

### 1. Monaco Editor Integration

**Installation:**
```bash
# Download Monaco Editor
npm install monaco-editor
# OR use CDN
```

**Django Template:**
```html
{% extends "code_app/code_base.html" %}
{% load static %}

<div class="workspace-container">
  <!-- File Tree (left sidebar) -->
  <div id="file-tree" class="file-tree">
    <!-- Custom file tree implementation -->
  </div>

  <!-- Monaco Editor (center) -->
  <div id="editor-container" class="editor-container"></div>

  <!-- Terminal (bottom panel, toggleable) -->
  <div id="terminal" class="terminal-panel">
    <!-- xterm.js terminal -->
  </div>
</div>

<script src="{% static 'monaco-editor/min/vs/loader.js' %}"></script>
<script>
  require.config({ paths: { vs: '{% static "monaco-editor/min/vs" %}' } });
  require(['vs/editor/editor.main'], function() {
    window.editor = monaco.editor.create(
      document.getElementById('editor-container'),
      {
        value: '',
        language: 'python',
        theme: 'vs-dark',
        automaticLayout: true,
        fontSize: 14,
        minimap: { enabled: true },
        scrollBeyondLastLine: false,
      }
    );
  });
</script>
```

### 2. Directory Tree (✅ Already Implemented!)

**Good news:** Your project already has a beautiful GitHub-style file tree!

**Location:**
- **TypeScript:** `apps/project_app/static/project_app/ts/shared/file-tree.ts`
- **CSS:** `apps/project_app/static/project_app/css/shared/sidebar.css`
- **API:** `apps/project_app/views/repository/browse.py` (file tree endpoint)

**Features:**
- ✅ Recursive tree rendering
- ✅ Expand/collapse folders (auto-expands current path)
- ✅ Beautiful GitHub-style hover effects
- ✅ Icon animations (scale on hover, rotate chevron)
- ✅ Dark theme support
- ✅ Symlink detection and display
- ✅ Active file highlighting

**Reusable TypeScript Module:**
```typescript
// apps/project_app/static/project_app/ts/shared/file-tree.ts
export interface TreeItem {
  name: string;
  path: string;
  type: "file" | "directory";
  children?: TreeItem[];
  is_symlink?: boolean;
  symlink_target?: string;
}

export function buildTreeHTML(
  items: TreeItem[],
  username: string,
  slug: string,
  level: number = 0
): string {
  // Recursively builds HTML with GitHub-style tree
  // Auto-expands folders in current path
  // Supports symlinks, icons, hover effects
}

export async function loadFileTree(
  username: string,
  slug: string,
  containerId: string = "file-tree"
): Promise<void> {
  // Fetches tree from API and renders it
}
```

**Integration Plan:**

1. **Reuse existing file-tree module** in Code workspace
2. **Modify click behavior** to load files in Monaco editor instead of navigating
3. **Keep all existing CSS** (hover effects, animations, dark theme)

**Updated Code Module Implementation:**
```typescript
// apps/code_app/static/code_app/ts/workspace.ts
import { loadFileTree, TreeItem } from '../../project_app/ts/shared/file-tree.js';

// Initialize file tree in Code workspace
await loadFileTree(username, projectSlug, 'code-file-tree');

// Override file click behavior to load in Monaco editor
document.addEventListener('click', (e) => {
  const fileLink = e.target.closest('.file-tree-file');
  if (fileLink && fileLink.dataset.path) {
    e.preventDefault();
    loadFileInMonaco(fileLink.dataset.path);
  }
});

async function loadFileInMonaco(filePath: string) {
  const response = await fetch(`/${username}/${slug}/raw/${filePath}`);
  const content = await response.text();

  editor.setValue(content);
  editor.setSelection({ startLineNumber: 1, startColumn: 1 });
}
```

**No need to rebuild!** Just reuse your existing, polished implementation.

### 3. Web Terminal (xterm.js + Django Channels)

**Why xterm.js?**
- Same terminal as VS Code uses
- Full ANSI color support
- Clipboard, scrollback, etc.

**Installation:**
```bash
pip install channels channels-redis
npm install xterm xterm-addon-fit
```

**Django Channels Consumer:**
```python
# apps/code_app/consumers.py
import asyncio
import pty
import subprocess
from channels.generic.websocket import AsyncWebsocketConsumer

class TerminalConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        project = await get_project(self.project_id, self.scope['user'])

        # Start bash in project directory
        self.master, self.slave = pty.openpty()
        self.process = subprocess.Popen(
            ['/bin/bash'],
            stdin=self.slave,
            stdout=self.slave,
            stderr=self.slave,
            cwd=project.git_clone_path,
        )

        await self.accept()
        asyncio.create_task(self.read_output())

    async def read_output(self):
        """Read terminal output and send to WebSocket."""
        while True:
            try:
                output = os.read(self.master, 1024)
                if output:
                    await self.send(text_data=output.decode())
            except:
                break

    async def receive(self, text_data):
        """Receive input from WebSocket and write to terminal."""
        os.write(self.master, text_data.encode())

    async def disconnect(self, close_code):
        self.process.terminate()
        os.close(self.master)
        os.close(self.slave)
```

**Frontend (xterm.js):**
```html
<div id="terminal"></div>

<script src="{% static 'xterm/xterm.js' %}"></script>
<script>
  const term = new Terminal({
    cursorBlink: true,
    fontSize: 14,
    theme: { background: '#1e1e1e' }
  });

  term.open(document.getElementById('terminal'));

  // WebSocket connection
  const ws = new WebSocket(`ws://localhost:8000/ws/terminal/{{ project.id }}/`);

  ws.onmessage = (event) => {
    term.write(event.data);
  };

  term.onData((data) => {
    ws.send(data);
  });
</script>
```

---

## Integration with SciTeX Package

### Scripts with @stx.session Decorator

**Workflow:**
1. User writes script in Monaco editor
2. Script uses `@stx.session.session` decorator
3. User clicks "Run" or uses terminal
4. SciTeX creates session directory with timestamp
5. Auto-commits script + results to Git

**Example Script:**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scitex/code/scripts/seizure_prediction.py

import scitex as stx
import numpy as np

@stx.session.session
def main(n_samples=1000, verbose=True):
    """Seizure prediction analysis."""

    # Generate data
    data = np.random.randn(n_samples, 10)

    # Create figure
    fig, ax = stx.plt.subplots()
    ax.plot_line(range(n_samples), data[:, 0])
    ax.set_xyt("Time", "Signal", "EEG Signal")

    # Auto-save with metadata
    stx.io.save(
        fig,
        "seizure_signal.jpg",
        metadata={"subject": "S001", "session": "pre"},
        symlink_to="./data",
        verbose=verbose,
    )

    return 0

if __name__ == "__main__":
    main()
```

**What SciTeX Does Automatically:**
```
scitex/code/scripts/seizure_prediction_out/
├── seizure_signal.jpg             # Figure
├── seizure_signal.csv             # Auto-exported data
├── FINISHED_SUCCESS/
│   └── 2025Y-11M-15D-10h30m00s_abc123-main/
│       ├── CONFIGS/
│       │   ├── CONFIG.pkl
│       │   └── CONFIG.yaml       # All arguments logged
│       └── logs/
│           ├── stdout.log        # Complete stdout
│           └── stderr.log        # Complete stderr
└── data/                          # Symlinked outputs
```

### Git Auto-Commit After Execution

**Django Integration:**
```python
# apps/code_app/views/api_views.py
@api_view(['POST'])
def run_script(request, project_id):
    """Run Python script with scitex session tracking."""
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    script_path = request.data.get('script_path')

    # Run script
    result = subprocess.run(
        ['python', script_path],
        cwd=project.git_clone_path,
        capture_output=True,
        text=True,
    )

    # Auto-commit to Git
    if project.git_clone_path and result.returncode == 0:
        try:
            from apps.project_app.services.git_service import auto_commit_file

            # Commit script + generated files
            auto_commit_file(
                project_dir=Path(project.git_clone_path),
                filepath="scitex/code/",
                message=f"Code: Ran script - {Path(script_path).stem}",
            )
            logger.info(f"✓ Auto-committed script execution")
        except Exception as e:
            logger.warning(f"Git commit failed (non-critical): {e}")

    return Response({
        'success': result.returncode == 0,
        'stdout': result.stdout,
        'stderr': result.stderr,
    })
```

---

## Database Schema Changes

### Add Project Relationship to Code Models

**Migration:**
```python
# apps/code_app/migrations/XXXX_add_project_to_code_models.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('code_app', 'XXXX_previous_migration'),
        ('project_app', 'XXXX_latest_migration'),
    ]

    operations = [
        # Add project field to Notebook
        migrations.AddField(
            model_name='notebook',
            name='project',
            field=models.ForeignKey(
                null=True,  # Allow NULL for backward compatibility
                blank=True,
                on_delete=models.CASCADE,
                to='project_app.project',
                related_name='notebooks',
            ),
        ),

        # Add project field to CodeExecutionJob
        migrations.AddField(
            model_name='codeexecutionjob',
            name='project',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.CASCADE,
                to='project_app.project',
                related_name='code_jobs',
            ),
        ),
    ]
```

### Update Models

```python
# apps/code_app/models.py
class Notebook(models.Model):
    """Jupyter notebook - NOW PROJECT-CENTRIC."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(
        'project_app.Project',
        on_delete=models.CASCADE,
        related_name='notebooks',
        null=True,  # Backward compatibility
        blank=True,
    )

    # Store in project directory instead of MEDIA_ROOT
    @property
    def file_path_in_project(self):
        if self.project and self.project.git_clone_path:
            return Path(self.project.git_clone_path) / 'scitex' / 'code' / 'notebooks' / f'{self.notebook_id}.ipynb'
        return None

class CodeExecutionJob(models.Model):
    """Code execution job - NOW PROJECT-CENTRIC."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(
        'project_app.Project',
        on_delete=models.CASCADE,
        related_name='code_jobs',
        null=True,
        blank=True,
    )
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Add `project` field to Notebook and CodeExecutionJob models
- [ ] Create migration script
- [ ] Update NotebookManager to save in project directory
- [ ] Test basic project-centric notebook storage

### Phase 2: Monaco Editor (Week 2)
- [ ] Install Monaco Editor (npm or CDN)
- [ ] Create new template: `code_workspace.html`
- [ ] Replace CodeMirror with Monaco
- [ ] Add Python language server support
- [ ] Test IntelliSense and autocomplete

### Phase 3: File Tree (Week 3)
- [ ] Implement backend API: `/code/api/project/{id}/files/`
- [ ] Create frontend file tree component
- [ ] Add file operations: create, delete, rename
- [ ] Add file loading in Monaco editor
- [ ] Test navigation

### Phase 4: Terminal (Week 4)
- [ ] Install Django Channels + xterm.js
- [ ] Create TerminalConsumer (WebSocket)
- [ ] Integrate xterm.js in frontend
- [ ] Test running scripts in terminal
- [ ] Add terminal toggle button

### Phase 5: Git Integration (Week 5)
- [ ] Add auto-commit on file save
- [ ] Add auto-commit after script execution
- [ ] Add Git status indicator
- [ ] Test full workflow
- [ ] Update documentation

### Phase 6: SciTeX Integration (Week 6)
- [ ] Test scripts with `@stx.session` decorator
- [ ] Verify session directory creation
- [ ] Verify auto-save and symlink features
- [ ] Test reproducibility workflow
- [ ] Document best practices

---

## Success Criteria

- ✅ All notebooks and scripts stored in project Git repository
- ✅ Monaco editor with IntelliSense works
- ✅ File tree allows navigation
- ✅ Terminal allows script execution
- ✅ Git auto-commits on save/run
- ✅ SciTeX session tracking works
- ✅ Complete reproducibility achieved

---

## Benefits Summary

### For Users
- 🎨 **Professional IDE** - Monaco editor like VS Code
- 📁 **File navigation** - Directory tree, easy to find files
- 💻 **Terminal access** - Run scripts directly
- 🔄 **Reproducibility** - SciTeX session tracking
- 📊 **Auto-export** - Figures + CSV data together
- 🌲 **Git history** - Version control automatic

### For Research
- 📝 **Traceable** - Every run logged with timestamps
- 🔁 **Reproducible** - Exact arguments and environment saved
- 📦 **Portable** - Project directory contains everything
- 🤝 **Collaborative** - Git-based workflow
- 📈 **Professional** - Publication-ready outputs

### For Platform
- ✅ **Project-centric** - Follows CLAUDE.md requirements
- 🔧 **Maintainable** - Clean architecture
- 🚀 **Scalable** - Per-project isolation
- 🎯 **Integrated** - Works with Writer, Scholar, Viz

---

**Last Updated:** 2025-11-15
**Next Steps:** Review with user, prioritize phases, start implementation
