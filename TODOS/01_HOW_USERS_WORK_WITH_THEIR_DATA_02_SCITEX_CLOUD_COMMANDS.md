<!-- ---
!-- Timestamp: 2025-10-20 18:45:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/10_SCITEX_CLOUD_COMMAND.md
!-- Priority: P1 - Strategic Infrastructure
!-- --- -->

# SciTeX CLI Command Strategy

**Status:** Architecture Defined
**Priority:** P1 (Strategic)
**Timeline:** 2-3 weeks

---

## Overview

Create `scitex` CLI tool that combines:
1. **Standard Git operations** (like `gh`/`tea`) → Gitea backend
2. **Unique scientific workflows** (Scholar/Code/Viz/Writer) → Django API

---

## Architecture Decision

### ✅ Chosen: Extend existing `scitex-code` package

**Package:**
```bash
pip install scitex           # One package for everything
```

**Structure:**
```
scitex CLI
├── cloud.*        → Gitea API (git.scitex.ai)     [Standard Git]
├── scholar.*      → Django API (scitex.ai/api/)   [UNIQUE VALUE]
├── code.*         → Django API (scitex.ai/api/)   [UNIQUE VALUE]
├── viz.*          → Django API (scitex.ai/api/)   [UNIQUE VALUE]
├── writer.*       → Django API (scitex.ai/api/)   [UNIQUE VALUE]
└── project.*      → Both APIs                     [UNIQUE VALUE]
```

---

## Command Categories

### 1. Cloud Commands (= gh/tea equivalent)

**Purpose:** Standard Git/repository operations
**Backend:** Gitea API (git.scitex.ai)

```bash
# Authentication
scitex cloud login                    # Auth to scitex.ai
scitex cloud logout

# Repository operations
scitex cloud clone user/repo          # Clone from git.scitex.ai
scitex cloud push                     # Push to git.scitex.ai
scitex cloud pull
scitex cloud repo create my-project   # Create repository
scitex cloud repo list                # List repositories
scitex cloud repo delete repo-name

# Collaboration
scitex cloud fork user/repo           # Fork repository
scitex cloud pr create                # Create pull request
scitex cloud pr list
scitex cloud pr merge

# Issues
scitex cloud issue create
scitex cloud issue list
```

**Implementation:** Wraps Gitea REST API (similar to tea)

---

### 2. Scholar Commands (UNIQUE VALUE)

**Purpose:** Literature review and reference management
**Backend:** Django API (scitex.ai/api/scholar/)

```bash
# Literature search
scitex scholar search "neural networks"
scitex scholar search --doi 10.1234/example
scitex scholar search --pmid 12345678

# Reference management
scitex scholar add-ref paper.bib
scitex scholar add-ref --doi 10.1234/example
scitex scholar export refs.bib
scitex scholar import zotero-library.bib

# PDF management
scitex scholar download --doi 10.1234/example
scitex scholar extract-text paper.pdf
scitex scholar extract-figures paper.pdf
```

---

### 3. Code Commands (UNIQUE VALUE)

**Purpose:** Execute analysis, manage compute
**Backend:** Django API (scitex.ai/api/code/)

```bash
# Local execution (uses local scitex-code)
scitex code run analysis.py
scitex code test

# Cloud execution (NEW - via Django)
scitex code run analysis.py --cloud
scitex code submit-job script.py --gpu --mem 16G
scitex code job status
scitex code job list
scitex code job cancel job-123

# Environment management
scitex code install requirements.txt
scitex code env create my-env
scitex code env list
```

---

### 4. Viz Commands (UNIQUE VALUE)

**Purpose:** Create publication-quality figures
**Backend:** Django API (scitex.ai/api/viz/)

```bash
# Local visualization (uses local scitex-viz)
scitex viz create plot.png from data.csv
scitex viz template list

# Cloud rendering (NEW - via Django)
scitex viz render figure.py --cloud
scitex viz export figure.pdf --format pdf
scitex viz export figure.svg --format svg

# Gallery management
scitex viz upload figure.png
scitex viz list
```

---

### 5. Writer Commands (UNIQUE VALUE)

**Purpose:** Manuscript writing and compilation
**Backend:** Django API (scitex.ai/api/writer/)

```bash
# Local compilation (uses local scitex-writer)
scitex writer compile manuscript/
scitex writer check-citations
scitex writer word-count

# Cloud compilation (NEW - via Django)
scitex writer compile --cloud
scitex writer preview                 # Generate preview PDF
scitex writer diff v1.tex v2.tex     # Show changes

# Submission helpers
scitex writer format --journal nature
scitex writer check-style --journal science
scitex writer export --format docx   # For Word-only journals
```

---

### 6. Project Commands (UNIQUE VALUE - Integrates Everything)

**Purpose:** Unified project management
**Backend:** Both Gitea + Django APIs

```bash
# Project initialization
scitex project init my-research
scitex project init my-research --template neuroscience

# Sync operations
scitex project sync                  # Sync: code + papers + data + refs
scitex project push                  # Push all changes
scitex project pull                  # Pull all updates

# Project status
scitex project status                # Git status + cloud sync status
scitex project info                  # Project metadata

# Complete workflows
scitex project publish               # Compile paper + push + deploy
scitex project backup                # Full project backup
scitex project share user@email      # Share with collaborator
```

---

## Implementation Plan

### Week 1: Core Infrastructure
- [ ] Create `src/scitex/cli/` module in scitex-code package
- [ ] Implement `scitex cloud` commands (Gitea API wrapper)
- [ ] Authentication system (token storage at ~/.scitex/credentials)
- [ ] Basic error handling and logging

**Deliverables:**
```bash
scitex cloud login
scitex cloud clone user/repo
scitex cloud repo create my-project
```

### Week 2: Scientific Workflows
- [ ] Implement `scitex scholar` commands (Django API)
- [ ] Implement `scitex code` commands (Django API)
- [ ] Implement `scitex viz` commands (Django API)
- [ ] Implement `scitex writer` commands (Django API)

**Deliverables:**
```bash
scitex scholar search "topic"
scitex code run --cloud script.py
scitex viz render figure.py
scitex writer compile manuscript/
```

### Week 3: Integration & Publishing
- [ ] Implement `scitex project` commands (combines all)
- [ ] Write comprehensive tests
- [ ] Documentation and usage examples
- [ ] Update README with CLI examples
- [ ] Publish updated package to PyPI

**Deliverables:**
```bash
scitex project init my-research
scitex project sync
scitex project publish
```

---

## User Workflows

### Example 1: Start New Research Project
```bash
scitex project init neuroscience-study
cd neuroscience-study/

scitex scholar search "spike sorting algorithms"
scitex scholar add-ref --doi 10.1038/example

scitex code run analysis.py
scitex viz create results.png

scitex writer compile manuscript/
scitex project push    # Push everything to cloud
```

### Example 2: Collaborate on Existing Project
```bash
scitex cloud clone lab-pi/shared-project
cd shared-project/

scitex project pull    # Pull code + papers + data
scitex code run --cloud preprocessing.py
scitex project push    # Push results back
```

### Example 3: Publish Paper
```bash
cd my-research/
scitex writer compile manuscript/
scitex writer check-citations
scitex writer format --journal nature
scitex project publish    # Final push + archive
```

---

## Key Insight

> **"scitex cloud = gh/tea" BUT "scitex scholar/code/viz/writer = UNIQUE VALUE"**

### Strategy:
- ✅ Match `gh`/`tea` for familiarity (cloud operations)
- ✅ Exceed `gh`/`tea` with scientific workflows (unique innovation)
- ✅ One unified CLI tool instead of separate tools

### Positioning:
**"gh/tea for researchers, with integrated scientific workflows"**

### Competitive Advantage:
- `gh` → GitHub operations only
- `tea` → Gitea operations only
- **`scitex`** → Git operations + Scholar + Code + Viz + Writer

---

## Distribution

### Phase 1: PyPI (Immediate)
```bash
pip install scitex
# Includes everything: local tools + cloud commands
```

### Phase 2: Homebrew (Later)
```bash
brew install scitex
```

### Phase 3: System packages (Much later)
```bash
sudo apt install scitex     # Ubuntu/Debian
sudo dnf install scitex     # Fedora/RHEL
```

---

## Related Files

**Implementation:**
- `/home/ywatanabe/proj/scitex-code/src/scitex/cli/` - CLI module (to be created)
- `/home/ywatanabe/proj/scitex-cloud/apps/*/api/` - Django REST API endpoints

**Documentation:**
- `TODOS/01_USER_DATA_ACCESS_INFRASTRUCTURE.md` - Infrastructure plan
- `TODOS/10_GITEA_GIT_HOSTING.md` - Gitea backend
- `deployment/gitea/` - Gitea deployment scripts

**Reference:**
- `tea` CLI source - For Git operations patterns
- `gh` CLI - For GitHub-style workflows

<!-- EOF -->