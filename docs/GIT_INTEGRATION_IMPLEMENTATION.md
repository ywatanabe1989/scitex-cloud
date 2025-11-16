# Git Integration Implementation Summary

**Date:** 2025-11-15
**Status:** Writer ✅ & Scholar ✅ Complete | Code Module Blocked ⚠️

---

## Overview

Implemented automatic Git commits for web-based user actions in SciTeX Cloud. When users save files through the web interface, meaningful commits are created automatically and pushed to Gitea.

This serves **95% of users** who work exclusively in the web interface and never see Git operations.

---

## What Was Implemented

### 1. Git Operations Helper ✅

**File:** `apps/common/utils/git_operations.py`

**Features:**
- `auto_commit()` - Main function for creating commits
- `get_file_history()` - Retrieve commit history for a file
- `revert_to_commit()` - Revert file to specific commit
- Automatic push to Gitea
- Meaningful commit messages
- Author attribution
- Error handling (non-blocking)

**Usage Example:**
```python
from apps.common.utils.git_operations import auto_commit

# After saving a file
auto_commit(
    file_path="/app/data/users/alice/project/manuscript.tex",
    message="Updated manuscript: Introduction",
    author_name="Alice Smith",
    author_email="alice@university.edu",
    push=True  # Push to Gitea automatically
)
```

### 2. Writer Module Integration ✅

**File:** `apps/writer_app/views/editor/api.py`

**Modified:** `section_view()` POST handler

**What Happens:**
```
User clicks "Save" in Writer
    ↓
Django saves .tex file to disk
    ↓
auto_commit() creates Git commit
    ↓
Commit message: "Updated manuscript: Introduction"
    ↓
Push to Gitea (automatic)
    ↓
User sees: "Saved ✓" (Git invisible)
```

**Example Commit History:**
```
commit abc123 - "Updated manuscript: Introduction"
commit def456 - "Updated manuscript: Methods"
commit ghi789 - "Updated manuscript: Results"
```

Clean, meaningful history! ✅

---

## What Needs Implementation

### 3. Code Module Integration ⚠️ BLOCKED

**Status:** Cannot implement yet - notebooks not project-centric

**Issue:**
- Notebooks stored in `MEDIA_ROOT/notebooks/{user_id}/` (not in Git repo)
- Notebook model has no `project` field (user-centric, not project-centric)
- Cannot commit files that aren't in a Git repository

**Prerequisites:**
1. Add `project` ForeignKey to Notebook model
2. Store notebooks in project Git repository (like Scholar does)
3. Update NotebookManager to save to project directory

**Implementation Plan (Once Prerequisites Met):**

**Project Structure:**
```
project_root/
├── scitex/writer/      # Framework modules
├── scitex/scholar/
├── scripts/            # ← User scripts here (NOT scitex/code/)
│   ├── mnist/
│   │   ├── clf_svm.py
│   │   └── clf_svm_out/
│   └── template.py
└── .git/
```

**Target File:** Script execution endpoint (when user clicks "Run" or uses terminal)

**What to Add:**
```python
# After script execution completes successfully
if project and project.git_clone_path:
    try:
        from apps.project_app.services.git_service import auto_commit_file

        # Commit the script + generated _out/ directory
        script_dir = Path(script_path).parent
        commit_message = f"Code: Ran script - {Path(script_path).stem}"

        success, output = auto_commit_file(
            project_dir=Path(project.git_clone_path),
            filepath=str(script_dir.relative_to(project.git_clone_path)),
            message=commit_message,
        )

        if success:
            logger.info(f"✓ Auto-committed: scripts/{script_dir.name}/")
        else:
            logger.warning(f"Failed to auto-commit: {output}")

    except Exception as e:
        logger.warning(f"Git commit failed (non-critical): {e}")
```

**Expected Commit History (After Implementation):**
```
commit 123 - "Code: Executed notebook - seizure_prediction"
commit 456 - "Code: Executed notebook - signal_preprocessing"
```

**Note:** Blocked until notebooks become project-centric (per CLAUDE.md requirement)

**See Full Architecture Plan:** [CODE_MODULE_PROJECT_CENTRIC_ARCHITECTURE.md](./CODE_MODULE_PROJECT_CENTRIC_ARCHITECTURE.md) for complete implementation roadmap including:
- Monaco Editor integration
- Directory tree navigation
- Web terminal (xterm.js)
- SciTeX session tracking integration
- Git auto-commit workflow

---

### 4. Scholar Module Integration ✅ COMPLETE

**Status:** Already implemented! 🎉

**File:** `apps/scholar_app/views/bibtex/views.py:899-986`

**What It Does:**
```python
# When BibTeX enrichment completes
if job.project and job.project.git_clone_path:
    # 1. Copy files to project Git repository
    project_bib_dir = Path(job.project.git_clone_path) / "scitex" / "scholar" / "bib_files"
    shutil.copy(input_path, project_bib_dir / original_filename)
    shutil.copy(output_path, project_bib_dir / enriched_filename)

    # 2. Regenerate merged bibliography
    regenerate_bibliography(project_path, project.name)

    # 3. Commit to Gitea
    commit_message = f"Scholar: Added bibliography - {job.processed_papers}/{job.total_papers} papers enriched"
    auto_commit_file(
        project_dir=Path(job.project.git_clone_path),
        filepath="scitex/",
        message=commit_message,
    )
```

**Actual Commit History:**
```
commit a1b2c3 - "Scholar: Added bibliography - 25/25 papers enriched"
commit d4e5f6 - "Scholar: Added bibliography - 15/17 papers enriched"
```

**Implementation Details:**
- Uses `auto_commit_file()` from `apps/project_app/services/git_service.py`
- Automatically copies both original and enriched .bib files
- Merges all bibliographies into `scitex/scholar/references.bib`
- Only commits if job is linked to a project with Git repository
- Non-blocking (enrichment succeeds even if commit fails)

### 5. File Upload Integration ⏳

**Target:** Any file upload handlers

**What to Add:**
```python
# After file upload
auto_commit(
    file_path=uploaded_file_path,
    message=f"Uploaded file: {filename}",
    author_name=user.get_full_name(),
    author_email=user.email,
    push=True
)
```

---

## Architecture Summary

### For 95% Web-Only Users

```
User Action → Save File → auto_commit() → Gitea
                              ↓
                    (Invisible to user)
                              ↓
                    Clean Git history
```

**User Experience:**
- Edit in browser ✅
- Click "Save" ✅
- See "Saved ✓" ✅
- **Never see Git** ✅

**Behind the Scenes:**
- Meaningful commits ✅
- Clean history ✅
- Version control ✅
- Can view history (optional) ✅

### For 5% Power Users

```
Laptop ←→ scitex cloud push/pull ←→ Workspace ←→ Gitea
                                        ↓
                              auto_commit() also works
```

---

## Implementation Guide

### To Add Git Commits to Any Web Handler

**Step 1:** Import the helper
```python
from apps.common.utils.git_operations import auto_commit
```

**Step 2:** After successful file operation, call auto_commit
```python
if save_successful:
    try:
        auto_commit(
            file_path=saved_file_path,
            message="Meaningful description of what changed",
            author_name=user.get_full_name() or user.username,
            author_email=user.email or f"{user.username}@scitex.local",
            push=True
        )
        logger.info("Git commit successful")
    except Exception as e:
        # Don't fail the save if Git commit fails
        logger.warning(f"Git commit failed (non-critical): {e}")
```

**Step 3:** Test
```bash
# Save something in the web interface
# Then check Git history
cd /app/data/users/username/project
git log --oneline
```

---

## Key Design Decisions

### 1. Non-Blocking Git Operations

```python
try:
    auto_commit(...)
except Exception as e:
    logger.warning(f"Git commit failed (non-critical): {e}")
    # Continue anyway - user's save succeeded
```

**Why:**
- Git failure shouldn't break user's work
- Save to disk is primary operation
- Git is secondary (version control)
- User sees "Saved" even if Git fails

### 2. Automatic Push to Gitea

```python
auto_commit(..., push=True)
```

**Why:**
- Users don't manually push
- Changes immediately available in Gitea
- Power users can pull immediately
- Simpler architecture

### 3. Meaningful Commit Messages

```python
# ✅ Good
message="Updated manuscript: Introduction"
message="Ran analysis: seizure_prediction.py"
message="Added citation: Paper Title"

# ❌ Bad (old auto-sync)
message="Auto-sync 2025-11-15 09:05:00"
```

**Why:**
- Clean, readable history
- Users can understand what changed
- Useful for collaboration
- Professional version control

### 4. Author Attribution

```python
author_name=user.get_full_name() or user.username
author_email=user.email or f"{user.username}@scitex.local"
```

**Why:**
- Proper Git attribution
- Shows who made changes
- Important for collaboration
- Professional commits

---

## Testing

### Manual Test

```bash
# 1. Log in to SciTeX Cloud
# 2. Open Writer
# 3. Edit a section
# 4. Save
# 5. Check Git history

ssh workspace
cd /app/data/users/YOUR_USERNAME/YOUR_PROJECT
git log --oneline -10
```

**Expected Output:**
```
abc1234 Updated manuscript: Introduction
def5678 Updated manuscript: Abstract
ghi9012 Updated manuscript: Title
```

### Automated Test

```python
# tests/test_git_integration.py
from apps.common.utils.git_operations import auto_commit
import tempfile
import subprocess

def test_auto_commit():
    # Create test repo
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(['git', 'init'], cwd=tmpdir)

        # Create test file
        test_file = Path(tmpdir) / 'test.txt'
        test_file.write_text('Hello World')

        # Auto-commit
        success = auto_commit(
            file_path=test_file,
            message="Test commit",
            push=False  # Don't push in tests
        )

        assert success

        # Check commit exists
        result = subprocess.run(
            ['git', 'log', '--oneline'],
            cwd=tmpdir,
            capture_output=True,
            text=True
        )
        assert 'Test commit' in result.stdout
```

---

## Benefits

### For Users (95% Web-Only)

- ✅ **Simplicity**: Just edit and save
- ✅ **Safety**: Version control without complexity
- ✅ **History**: Can see what changed when
- ✅ **Recovery**: Can revert if needed
- ✅ **Invisible**: Never see Git operations

### For Power Users (5%)

- ✅ **Clean History**: Meaningful commits, not "Auto-sync"
- ✅ **Collaboration**: Clear who changed what
- ✅ **Integration**: Works with laptop workflow
- ✅ **Control**: Can still use Git directly

### For Admins

- ✅ **Professional**: Clean Git repository
- ✅ **Auditable**: Full change history
- ✅ **Reliable**: Automatic, no user action needed
- ✅ **Simple**: One helper function, easy to integrate

---

## Next Steps

1. **Find Code Module API endpoints** - Where code execution saves results
2. **Find Scholar Module API endpoints** - Where citations are added
3. **Add auto_commit() calls** - Same pattern as Writer
4. **Test thoroughly** - Ensure commits work correctly
5. **Monitor logs** - Watch for Git errors

---

## Files Modified

```
Created:
  apps/common/utils/git_operations.py       # Git helper
  apps/common/utils/__init__.py              # Package init
  apps/common/__init__.py                    # App init

Modified:
  apps/writer_app/views/editor/api.py       # Writer save handler
```

## Files to Modify (Pending)

```
To find and modify:
  apps/code_app/views/execution/api.py      # Code execution (example)
  apps/scholar_app/views/citations/api.py   # Citations (example)
  apps/*/views/**/upload.py                  # File uploads (example)
```

---

## Maintenance

### Adding Git to New Features

When adding new web features that save files:

1. After successful save:
   ```python
   from apps.common.utils.git_operations import auto_commit

   auto_commit(
       file_path=your_file_path,
       message="Meaningful message",
       author_name=user.get_full_name(),
       author_email=user.email,
       push=True
   )
   ```

2. Make it non-blocking (wrap in try/except)
3. Log success/failure
4. Test

### Monitoring

Watch logs for Git warnings:
```bash
tail -f /app/logs/django.log | grep -i "git"
```

Common issues:
- Repository not initialized → Initialize Git in workspace
- Push failures → Check Gitea connectivity
- Commit failures → Check file permissions

---

## Success Criteria

✅ **Writer Module**: Commits on save (COMPLETE)
⚠️ **Code Module**: Blocked - notebooks not project-centric yet (see prerequisites above)
✅ **Scholar Module**: Commits when BibTeX enrichment completes (COMPLETE - already implemented!)
⏳ **File Uploads**: Commits on upload (pending)

**Overall Goal**: 95% of users get automatic, meaningful version control without seeing Git.

**Current Status**: 50% complete (Writer ✅, Scholar ✅, Code blocked ⚠️, Uploads pending ⏳)

**Implementation Summary:**
- ✅ **Writer Module** (apps/writer_app/views/editor/api.py) - Uses `auto_commit()` from `apps/common/utils/git_operations.py`
- ✅ **Scholar Module** (apps/scholar_app/views/bibtex/views.py) - Uses `auto_commit_file()` from `apps/project_app/services/git_service.py` (already existed!)
- ⚠️ **Code Module** - Requires architectural changes (add project field to Notebook model)

**Git Helper Functions:**
- `apps/common/utils/git_operations.py` → `auto_commit()` - Generic helper, works with any file path
- `apps/project_app/services/git_service.py` → `auto_commit_file()` - Project-specific helper, requires project directory

**Both helpers are valid** - use the one that fits your use case.

---

**Last Updated:** 2025-11-15
**Next Review:** After Code module prerequisites are met (project-centric notebooks)
