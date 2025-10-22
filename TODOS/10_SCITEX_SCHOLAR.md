<!-- ---
!-- Timestamp: 2025-10-22 13:42:51
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/10_SCITEX_SCHOLAR.md
!-- --- -->

DON'T TELL A LIE
YOU **MUST** confirm your statement with visual check or user confirmation
Django server is running with hot reloading
User is checking the webpage with Ctrl + Shift + R to clear cache


### Scholar System TODOs

Fill checkboxes of this file when implemented and confirmed their functionality correctly

## scitex.scholar module is available in ~/proj/scitex_repo/src/scitex/scholar

### **PDF Download Mode** (Future Feature)
- [ ] First only open papers
- [ ] Paywalled papers can be obtained by correctly setting authentication
  - [ ] Currently, we have confirmed `OpenAthens + OpenURL` locally
  - [ ] About 70% of papers downloaded (~/.scitex/scholar/library/neurovista)
- [ ] We need to plan how to serve this functionality
- [ ] Yes, but your instinct is right; the index html should be index.html instead of index.html
  - [ ] So, after index.html implemented, please 

### BibTeX Diff/Comparison Feature ✅ (Implemented)
- [x] Compare before/after enrichment statistics
  - [x] "Show what enhanced" button to show diff in colored format
  - [x] Diff between original bib file and enhanced bibfile
  - [x] API endpoint: `/scholar/api/bibtex/job/<id>/diff/`
  - [x] Shows statistics: total entries, entries enhanced, fields added, enhancement rate
  - [x] GitHub-style diff display:
    - Shows ALL entries (not just changed ones)
    - Green background with + prefix for added fields
    - Black on white for original fields
    - Red for removed fields (if any)
    - Monospace font for code-like appearance
    - Statistics dashboard at top
  - [x] Handle empty diff (all entries already complete)

### Bug Fixes ✅
- [x] **CRITICAL FIX**: "Please enter a search query" error on BibTeX buttons
  - **Root Cause**: `document.querySelector('form')` was selecting the first form (BibTeX) instead of search form
  - **Solution**:
    1. Added `id="literatureSearchForm"` to search form (line 608)
    2. Changed `document.querySelector('form')` to `document.getElementById('literatureSearchForm')` (lines 1636, 1922)
  - **Impact**: BibTeX upload, Show What Enhanced, Open URLs buttons now work correctly
  - **Files Modified**: `apps/scholar_app/templates/scholar_app/index.html`

### Next Steps (Future Enhancements)

### Refactoring
we cannot accept heavy html pages
/home/ywatanabe/proj/scitex-cloud/apps/scholar_app/templates/scholar_app/index.html
should be refactored using
/home/ywatanabe/proj/scitex-cloud/apps/scholar_app/static/scholar_app/styles/*.css
/home/ywatanabe/proj/scitex-cloud/apps/scholar_app/static/scholar_app/scripts/*.js

### Open All URLS functionality ✅
- [x] When bibtex updated or after enrichment try to open new URLs from doi and URL fields
- [x] when doi is available we should prioritize doi, adding https://doi.org/ as prefix
- [x] By opening all by new tabs, users can effectively download PDF files
- **Implemented:** Added "Open All URLs" button with dynamic count display
- **Features:** Confirmation dialog, staggered tab opening (100ms delay), error handling
- **API:** `/scholar/api/bibtex/job/<id>/urls/` endpoint extracts and returns URLs/DOIs

### UI Improvements ✅
- [x] Simplified System Resources panel
  - Removed detailed CPU/Memory usage (saved for future reuse)
  - Now shows only "Job Queue Status" with Active Jobs and Queued counts
  - Cleaner, less technical interface for users
- [x] Added 10-minute timeout for enrichment jobs
  - Prevents jobs from hanging indefinitely
  - Clear error message if timeout occurs
  - Implemented in `bibtex_views.py` using `asyncio.wait_for()`

<!-- EOF -->