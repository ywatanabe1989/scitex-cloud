# Project Structure Rationale

**Date:** 2025-11-15
**Status:** ✅ Approved Design

---

## The Approved Structure

```
project_root/
├── scitex/                   # Framework-managed modules
│   ├── writer/               # LaTeX manuscript (structured)
│   └── scholar/              # Bibliography (managed)
│
├── scripts/                  # User's analysis code (flexible!)
│   ├── mnist/                # Organized by experiment
│   │   ├── clf_svm.py        # Scripts with @stx.session
│   │   ├── clf_svm_out/      # Auto-generated
│   │   └── plot_*.py
│   └── template.py
│
├── config/                   # MNIST.yaml, PATH.yaml
├── data/                     # Centralized (symlink target)
├── docs/
├── externals/
├── project_management/
├── tests/
└── README.md
```

---

## Why NOT `scitex/code/`?

### ❌ Original Plan (Rejected)
```
scitex/
├── code/          # ← Force all scripts here
├── writer/
└── scholar/
```

**Problems:**
1. **Too rigid** - Forces all code into framework structure
2. **Doesn't match reality** - Scientists don't work this way
3. **Discourages exploration** - Every script needs structure
4. **Mixed mental models** - Is code "mine" or "framework's"?

### ✅ Better Design (Approved)
```
scitex/           # Framework stuff (I follow rules)
scripts/          # My stuff (I make rules)
```

**Benefits:**
1. **Clear ownership** - Framework vs user code
2. **Flexibility** - Organize scripts/ however you want
3. **Gradual adoption** - Use @stx.session when ready
4. **Mixed languages** - Python, bash, R, Julia all OK

---

## Design Philosophy

### Two Mental Models

**Framework Modules (scitex/):**
```
Purpose: Structured, reusable components
Control: Framework-managed
UI:      Specialized web interfaces
Style:   Opinionated, consistent
```

**User Code (scripts/):**
```
Purpose: Experimental, analysis code
Control: User-controlled
UI:      Code editor + terminal
Style:   Flexible, no rules
```

---

## Real Research Workflow

### Phase 1: Exploration (scripts/)

```python
# scripts/explore_data.py
# Quick and dirty - just testing ideas
import numpy as np
data = np.load('raw.npy')
print(data.shape)  # 👈 No structure needed
```

**No requirements:**
- ❌ No @stx.session needed
- ❌ No specific directory structure
- ❌ No documentation
- ✅ Just explore!

### Phase 2: Analysis (scripts/mnist/)

```python
# scripts/mnist/clf_svm.py
import scitex as stx

@stx.session.session  # 👈 Add when ready
def main(kernel='rbf', C=1.0):
    """Train SVM on MNIST."""
    # Organized, reproducible
    # Auto-creates clf_svm_out/
    # Logs everything
    ...
```

**When ready:**
- ✅ Add @stx.session decorator
- ✅ Organize into subdirectory
- ✅ Add configuration (config/MNIST.yaml)
- ✅ Write tests (tests/test_mnist.py)

### Phase 3: Publication (scitex/writer/)

```latex
% scitex/writer/01_manuscript/contents/methods.tex
We trained an SVM classifier using scikit-learn...
```

**Framework handles:**
- ✅ LaTeX compilation
- ✅ Cross-referencing
- ✅ Bibliography integration
- ✅ Version control

---

## Module Comparison

| Aspect | scitex/writer/ | scitex/scholar/ | scripts/ |
|--------|----------------|-----------------|----------|
| **Purpose** | Manuscript | Bibliography | Analysis |
| **Format** | LaTeX | BibTeX | Python/bash/R |
| **Structure** | Strict template | Managed files | Flexible |
| **Web UI** | Rich editor | Enrichment UI | Code editor |
| **Version Control** | Auto-commit | Auto-commit | Auto-commit |
| **Learning Curve** | High (LaTeX) | Low (upload) | None (Python) |
| **Flexibility** | Low (template) | Medium (upload) | **High (any)** |

---

## Code Module Workspace Features

### File Tree Navigation

```
📁 scitex/
 📁 writer/        ← Click: Opens in Writer module
 📁 scholar/       ← Click: Opens in Scholar module

📁 scripts/        ← Click: Opens in Monaco editor
 📁 mnist/
  📄 clf_svm.py    ← Click: Edits in Monaco
  📁 clf_svm_out/  ← Click: Browse read-only
  📄 plot_*.py

📁 config/         ← Click: YAML editor
📄 README.md       ← Click: Markdown editor
```

### Intelligent Routing

**Framework modules (scitex/):**
- `scitex/writer/*.tex` → Writer module (rich LaTeX editor)
- `scitex/scholar/*.bib` → Scholar module (enrichment UI)

**User code (scripts/):**
- `scripts/**/*.py` → Monaco editor + terminal
- `scripts/**/*.sh` → Monaco editor + terminal
- `scripts/**/_out/` → Read-only file browser

**Configuration:**
- `config/*.yaml` → Monaco YAML editor
- `*.md` → Monaco Markdown editor (with preview?)

---

## Git Integration

### Auto-Commit Triggers

**Writer:**
```
User saves section → Auto-commit to Git
Message: "Updated manuscript: Introduction"
```

**Scholar:**
```
BibTeX enrichment completes → Auto-commit
Message: "Scholar: Added bibliography - 25/25 papers enriched"
```

**Code (scripts/):**
```
User runs script successfully → Auto-commit
Message: "Code: Ran script - clf_svm"

Commits:
- scripts/mnist/clf_svm.py (modified)
- scripts/mnist/clf_svm_out/ (new outputs)
```

### Clean Git History

```bash
$ git log --oneline

abc123 Code: Ran script - plot_umap_space
def456 Updated manuscript: Results
ghi789 Scholar: Added bibliography - 15/17 papers enriched
jkl012 Code: Ran script - clf_svm
mno345 Updated manuscript: Methods
pqr678 Code: Ran script - download
```

**Meaningful, chronological, traceable!** ✅

---

## Migration from scitex_template_research

### Old Structure → New Structure

```
OLD                          NEW
───────────────────────────  ────────────────────────────
paper/                    →  scitex/writer/
scripts/                  →  scripts/ (KEEP AT ROOT!)
(none)                    →  scitex/scholar/
config/                   →  config/ (keep)
data/                     →  data/ (keep)
docs/                     →  docs/ (keep)
externals/                →  externals/ (keep)
project_management/       →  project_management/ (keep)
tests/                    →  tests/ (keep)
```

**Key changes:**
- ✅ Move `paper/` → `scitex/writer/`
- ✅ Add `scitex/scholar/`
- ✅ Keep `scripts/` at root (don't move to scitex/)
- ✅ Everything else stays the same

---

## Why This Works

### 1. **Matches Mental Model**

Researchers think:
- "My code" (scripts/) vs "Framework tools" (scitex/)
- Not: "Everything is a framework module"

### 2. **Encourages Adoption**

**Low barrier:**
```python
# scripts/test.py
print("Hello")  # ← Just works!
```

**Add features gradually:**
```python
# scripts/test.py
import scitex as stx

@stx.session.session  # ← Add when ready
def main():
    print("Hello")  # ← Same code!
```

### 3. **Supports Mixed Workflows**

```bash
scripts/
├── mnist/
│   ├── download.py        # Python
│   ├── preprocess.R       # R script
│   ├── main.sh            # Bash orchestration
│   └── visualize.ipynb    # Jupyter notebook
```

All work together! No artificial boundaries.

### 4. **Framework Expands Naturally**

```
Today:
scitex/writer/
scitex/scholar/

Future:
scitex/viz/        # Data visualization module
scitex/collab/     # Collaboration features
scitex/publish/    # Publishing pipeline
```

`scripts/` remains stable - user code doesn't change!

---

## Success Criteria

**Code Module Goals:**
- ✅ Scientists can write Python freely in scripts/
- ✅ Monaco editor provides IDE experience
- ✅ Terminal allows script execution
- ✅ @stx.session provides reproducibility (optional)
- ✅ Git auto-commits track all changes
- ✅ File tree allows easy navigation
- ✅ Integration with Writer/Scholar modules

**Overall Platform:**
- ✅ Project-centric (all modules share one repo)
- ✅ Reproducible (SciTeX session tracking)
- ✅ Collaborative (Git-based workflow)
- ✅ Flexible (scripts/ for freedom)
- ✅ Structured (scitex/ for consistency)

---

## Conclusion

**Separation of concerns wins:**

```
scitex/    = Framework territory (consistency, integration)
scripts/   = User territory (freedom, exploration)
```

This design:
- ✅ **Respects** how scientists actually work
- ✅ **Encourages** best practices without forcing them
- ✅ **Scales** from quick experiments to production
- ✅ **Integrates** with framework when beneficial

**The right abstraction at the right level.**

---

**Last Updated:** 2025-11-15
**Status:** Approved and ready for implementation
