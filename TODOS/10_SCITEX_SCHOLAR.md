<!-- ---
!-- Timestamp: 2025-10-22 14:40:52
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

### Refactoring ✅ (Completed)
- [x] **Heavy HTML refactored**: index.html reduced from 2,694 lines to 638 lines (76% reduction)
  - **CSS Extraction**: 388 lines extracted to `static/styles/scholar-index.css`
  - **JavaScript Extraction**: 2,059 lines extracted to modular files:
    - `static/scripts/panel-toggle.js` (48 lines) - Split-screen panel functionality
    - `static/scripts/scholar-index-main.js` (2,011 lines) - Main functionality (BibTeX upload, search, diff, URLs, resource monitor)
  - **Files Modified**:
    - `/home/ywatanabe/proj/scitex-cloud/apps/scholar_app/templates/scholar_app/index.html`
    - Removed all inline `<style>` tags (lines 11-342)
    - Removed all inline `<script>` tags (lines 639-2644)
    - Added external CSS/JS imports via Django static template tags
  - **Result**: Clean, maintainable HTML template with proper separation of concerns

### Next Steps (Future Enhancements)

/home/ywatanabe/proj/scitex-cloud/apps/scholar_app/templates/scholar_app/index.html
this is too large
Split into
  /home/ywatanabe/proj/scitex-cloud/apps/scholar_app/templates/scholar_app/index_partials:
  drwxr-xr-x 2 ywatanabe ywatanabe 4.0K Oct 22 14:39 .
  drwxr-xr-x 5 ywatanabe ywatanabe 4.0K Oct 22 14:39 ..
  -rw-r--r-- 1 ywatanabe ywatanabe    0 Oct 22 14:39 asta_tooltip.html
  -rw-r--r-- 1 ywatanabe ywatanabe    0 Oct 22 14:39 enrich.html
  -rw-r--r-- 1 ywatanabe ywatanabe    0 Oct 22 14:39 search.html

  /home/ywatanabe/proj/scitex-cloud/apps/scholar_app/static/scholar_app:
  drwxr-xr-x 5 ywatanabe ywatanabe 4.0K Oct 22 14:40 .
  drwxr-xr-x 3 ywatanabe ywatanabe 4.0K Oct 22 14:40 ..
  drwxr-xr-x 2 ywatanabe ywatanabe 4.0K Oct 22 13:30 data
  drwxr-xr-x 2 ywatanabe ywatanabe 4.0K Oct 22 14:35 scripts
  drwxr-xr-x 2 ywatanabe ywatanabe 4.0K Oct 22 14:32 styles

<!-- EOF -->