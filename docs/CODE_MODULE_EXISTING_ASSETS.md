# Code Module: Existing Assets You Can Reuse

**Date:** 2025-11-15
**Good News:** You already have most components needed! 🎉

---

## ✅ Already Implemented (Ready to Reuse)

### 1. **GitHub-Style File Tree Sidebar** ⭐

**Location:** Currently used in project browse page (`/ywatanabe/default-project/`)

**Files:**
- **TypeScript:** `apps/project_app/static/project_app/ts/shared/file-tree.ts` (207 lines)
- **CSS:** `apps/project_app/static/project_app/css/shared/sidebar.css` (368 lines)
- **API Endpoint:** Already exists in `apps/project_app/views/repository/browse.py`

**Features:**
```typescript
✅ Recursive tree rendering
✅ Auto-expand current path
✅ Collapsible folders with chevron animation
✅ File/folder icons (SVG)
✅ Symlink detection and display
✅ Active file highlighting
✅ Beautiful hover effects:
   - translateX(4px) slide animation
   - Icon scale(1.1) on hover
   - Accent color transitions
   - Inset border highlights
✅ Dark theme support
✅ GitHub-style aesthetics
```

**CSS Highlights:**
```css
/* Smooth animations */
transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);

/* Hover effects */
.file-tree-item:hover {
  background: var(--color-neutral-subtle);
  transform: translateX(4px);
  box-shadow: inset 2px 0 0 var(--color-border-default);
}

/* Active state */
.file-tree-item.active {
  background: var(--color-accent-subtle);
  color: var(--color-accent-fg);
  box-shadow: inset 3px 0 0 var(--color-accent-emphasis);
}

/* Icon animations */
.file-tree-icon {
  transition: transform 0.2s, color 0.2s;
}
.file-tree-item:hover .file-tree-icon {
  transform: scale(1.1);
}

/* Chevron rotation */
.file-tree-chevron.expanded {
  transform: rotate(90deg);
}
```

**To Reuse in Code Module:**
1. Import the TypeScript module
2. Call `loadFileTree(username, slug, 'code-file-tree')`
3. Override click behavior to load in Monaco editor instead of navigating
4. Done! No CSS changes needed.

---

### 2. **Project-Centric Structure Template** ⭐

**Location:** `~/proj/examples/scitex_template_research/`

**Structure:**
```
scitex_template_research/
├── config/              # Configuration files
├── data/                # Data directory (symlink target)
├── docs/                # Documentation
├── externals/           # External dependencies
├── paper/               # ← OLD: Now use scitex/writer/
│   ├── 01_manuscript/
│   │   ├── base.tex
│   │   ├── contents/
│   │   └── manuscript.tex
│   ├── 02_supplementary/
│   └── 03_revision/
├── scripts/             # ← OLD: Now use scitex/code/
│   └── mnist/
│       ├── clf_svm.py
│       ├── clf_svm_out/
│       ├── download.py
│       └── plot_*.py
└── tests/
```

**Recommended Migration:**
```
paper/           → scitex/writer/       ✅
scripts/         → scitex/code/         ✅
(new)            → scitex/scholar/      ✅
```

---

### 3. **SciTeX Session Tracking** ⭐

**Already installed:** `scitex` package (editable mode via pip)

**Location:** `/home/ywatanabe/proj/scitex-code/src/scitex/`

**Features:**
```python
import scitex as stx

@stx.session.session
def main(n_samples=1000, verbose=True):
    """Your analysis function."""

    # Auto-creates session directory:
    # scitex/code/mnist/clf_svm_out/
    # ├── FINISHED_SUCCESS/
    # │   └── 2025Y-11M-15D-10h30m00s_abc123-main/
    # │       ├── CONFIGS/
    # │       │   ├── CONFIG.pkl
    # │       │   └── CONFIG.yaml    # All arguments
    # │       └── logs/
    # │           ├── stdout.log     # Complete stdout
    # │           └── stderr.log     # Complete stderr

    # Auto-save figures with metadata
    fig, ax = stx.plt.subplots()
    ax.plot_line(t, signal)

    stx.io.save(
        fig,
        "signal.jpg",
        metadata={"exp": "s01"},
        symlink_to="./data",  # Auto-symlink to data/
        verbose=True
    )
    # Also saves: signal.csv (auto-exported plot data)

    return 0
```

**Benefits:**
- ✅ Perfect reproducibility
- ✅ All arguments logged
- ✅ All outputs logged
- ✅ Timestamps on everything
- ✅ Figures + CSV data together
- ✅ Symlinks to centralized `data/`

---

### 4. **Git Integration Helper** ⭐

**Already implemented:**
- `apps/common/utils/git_operations.py` → Generic `auto_commit()`
- `apps/project_app/services/git_service.py` → Project-specific `auto_commit_file()`

**Usage:**
```python
from apps.project_app.services.git_service import auto_commit_file

# After script execution
auto_commit_file(
    project_dir=Path(project.git_clone_path),
    filepath="scitex/code/mnist/",
    message=f"Code: Ran analysis - {script_name}",
)
```

**Already works for:**
- ✅ Writer module (manuscript saves)
- ✅ Scholar module (bibliography enrichment)

---

## 🔨 What Needs Implementation

### 1. **Monaco Editor Integration**

**Status:** CodeMirror currently used, needs upgrade to Monaco

**Required:**
```bash
npm install monaco-editor
# OR use CDN
```

**Effort:** ~4-6 hours (straightforward replacement)

---

### 2. **Web Terminal (xterm.js)**

**Status:** Not implemented

**Required:**
```bash
pip install channels channels-redis
npm install xterm xterm-addon-fit
```

**Effort:** ~8-12 hours (WebSocket consumer + frontend)

---

### 3. **Database Migration**

**Status:** Notebook model needs `project` field

**Required:**
```python
# Migration to add
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='notebook',
            name='project',
            field=models.ForeignKey('project_app.Project', ...),
        ),
    ]
```

**Effort:** ~2-4 hours (migration + update NotebookManager)

---

## 📊 Implementation Effort Summary

| Component | Status | Reuse? | Effort |
|-----------|--------|--------|--------|
| File Tree Sidebar | ✅ Ready | **100%** | 0 hours (just import!) |
| CSS/Styling | ✅ Ready | **100%** | 0 hours (already perfect) |
| Project Structure | ✅ Template exists | **90%** | 1-2 hours (migration guide) |
| SciTeX Integration | ✅ Installed | **100%** | 0 hours (already works) |
| Git Helpers | ✅ Implemented | **100%** | 0 hours (already works) |
| Monaco Editor | ⏳ Pending | 0% | 4-6 hours |
| Web Terminal | ⏳ Pending | 0% | 8-12 hours |
| Database Migration | ⏳ Pending | 0% | 2-4 hours |

**Total new work:** ~14-22 hours

**Reusable assets:** ~90% of the UI/UX is already done! 🎉

---

## 🎯 Quick Win Strategy

**Phase 1: Reuse Everything (2-3 hours)**
1. Create new Code workspace template
2. Import existing file tree module
3. Test file navigation with current CodeMirror editor
4. Verify it works end-to-end

**Phase 2: Upgrade Editor (4-6 hours)**
5. Replace CodeMirror with Monaco
6. Add Python language server
7. Test IntelliSense

**Phase 3: Add Terminal (8-12 hours)**
8. Implement WebSocket consumer
9. Integrate xterm.js
10. Test script execution

**Phase 4: Make Project-Centric (2-4 hours)**
11. Database migration
12. Update NotebookManager
13. Test Git integration

**Total:** 16-25 hours → **Professional IDE in ~1 week!**

---

## 💡 Key Insight

**You already built 90% of this!**

Your existing file tree sidebar is:
- ✨ Beautiful (GitHub-style animations)
- 🎨 Polished (dark theme, hover effects)
- 🔧 Robust (TypeScript, error handling)
- 📱 Responsive (works on all screen sizes)

**Don't rebuild.** Just import and modify click behavior:

```typescript
// Instead of navigating to /blob/path
// Load file content in Monaco editor
document.querySelector('.file-tree-file').addEventListener('click', (e) => {
  e.preventDefault();
  loadInMonaco(e.target.dataset.path);
});
```

That's it! 🚀

---

**Last Updated:** 2025-11-15
**Recommendation:** Start with Phase 1 (reuse existing sidebar) to validate the approach, then proceed with Monaco + Terminal.
