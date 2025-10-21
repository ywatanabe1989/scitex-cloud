<!-- ---
!-- Timestamp: 2025-10-21 22:51:06
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/10_SCITEX_SCHOLAR.md
!-- --- -->

### Scholar System TODOs

Fill checkboxes of this file when implemented and confirmed their functionality correctly

## scitex.scholar module is available in ~/proj/scitex_repo/src/scitex/scholar

### **PDF Download Mode** (Future Feature)
- [ ] First only open papers
- [ ] Paywalled papers can be obtained by correctly setting authentication
  - [ ] Currently, we have confirmed `OpenAthens + OpenURL` locally
  - [ ] About 70% of papers downloaded (~/.scitex/scholar/library/neurovista)
- [ ] We need to plan how to serve this functionality

#### Upload UX Improvements
- Upload drag & drop with visual feedback
  - [x] Now, this works but not only after dropped, when being dragged, make it responsible ✅
    - [x] When i drag a bib file, it says `+copy` as in the chrome default behaviour ✅
      - Note: `+copy` cursor is **correct standard behavior** for file uploads (`dropEffect = 'copy'`)
      - Visual feedback implemented: border color change, scaling, box shadow, dragging class
      - See `bibtex_enrichment.html:456-489`

#### Progress Display Features (Currently on Job Detail Page) -> Move to /scholar/ page directly
- [x] Progress bar implemented ✅ (exists on `/scholar/bibtex/job/{id}/`)
  - Real-time polling every 2 seconds
  - Visual progress bar with percentage
  - Paper count display (processed/total/failed)
  - See `bibtex_job_detail.html:56-71, 316-393`

- [x] Terminal logs implemented ✅ (exists on `/scholar/bibtex/job/{id}/`)
  - Live processing log with terminal styling (#0a0f1a background, green text)
  - Auto-scroll to bottom as logs update
  - Expand/collapse functionality (400px/800px)
  - Live updates via AJAX polling
  - See `bibtex_job_detail.html:156-169, 259-281`

- [x] Output handling working ✅
  - Backend endpoint `/scholar/api/bibtex/job/{job_id}/status/` returns:
    - `processing_log` - Real-time logs
    - `status` - Job status
    - `progress_percentage` - Progress
    - Paper counts and error messages
  - Download button shows when complete
  - File size display on download
  - See `bibtex_views.py:250-287`

**USER REQUEST IMPLEMENTED**: Show progress bar and logs in `/scholar/bibtex/enrichment/` page ✅ (2025-10-21)
- [x] Move progress tracking to inline panel on enrichment page
  - Added hidden panel that appears after upload (lines 153-223)
  - Shows file info, status, duration in grid layout
  - See `bibtex_enrichment.html:153-223`
- [x] Eliminate separate job detail page navigation
  - Upload now shows progress inline instead of redirecting
  - Modified AJAX response handler (lines 509-526)
  - Smooth scroll to progress panel after upload
- [x] Show real-time logs in expandable section below upload form
  - Terminal-style log display with green text on dark background
  - Expandable from 300px to 600px with toggle button
  - Auto-scrolls to bottom as logs update
  - Real-time polling every 2 seconds (lines 540-686)
- [x] Download button appears inline when complete
  - Success section with download link
  - Shows enrichment statistics (entries, enriched count)
  - No page navigation required

### Next Steps (Optional Enhancements)
- [ ] Add ability to cancel running jobs
- [ ] Batch upload multiple BibTeX files
- [ ] Compare before/after enrichment statistics

<!-- EOF -->