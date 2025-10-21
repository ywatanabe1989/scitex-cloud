<!-- ---
!-- Timestamp: 2025-10-21 22:26:41
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

### ✅ Completed Issues (2025-10-21)

#### Upload UX Improvements
- [x] Upload drag & drop with visual feedback ✅ (2025-10-21)
  - [x] Enhanced drop zone with hover effects - solid border, shadow, scale (1.01x)
  - [x] Border color changes on drag (SciTeX color-03 #6B8FB3)
  - [x] File validation (only .bib files, 50MB limit)
  - See `bibtex_enrichment.html:366-389`

- [x] Upload progress feedback ✅ (2025-10-21)
  - [x] Submit button shows spinner and "Uploading..." text
  - [x] Button disabled during upload
  - [x] AJAX-based upload with JSON response handling
  - [x] Success animation before redirect
  - See `bibtex_enrichment.html:394-427`

- [x] Filename display after upload ✅ (2025-10-21)
  - [x] Shows selected filename prominently with file icon
  - [x] Displays file size in human-readable format (KB/MB)
  - [x] "Change file" button for re-selection
  - [x] Success color indication (green border) when file selected
  - See `bibtex_enrichment.html:54-74, 296-354`

- [x] JavaScript errors fixed ✅ (2025-10-21)
  - [x] Fixed `sortSelect` redeclaration error with defensive initialization
  - [x] Changed `const` to `let` for search-related variables
  - See `simple_search.html:1099-1103, 1482-1493`

#### Progress Display Features (Currently on Job Detail Page)
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

**USER REQUEST**: Show progress bar and logs in `/scholar/` page instead of separate job detail page
- [ ] TODO: Move progress tracking to inline panel on enrichment page
- [ ] TODO: Eliminate separate job detail page navigation
- [ ] TODO: Show real-time logs in expandable section below upload form

### Next Steps (Optional Enhancements)
~~- [ ] Consider adding WebSocket for even faster log updates~~
- [ ] Add ability to cancel running jobs
~~- [ ] Export enrichment logs for debugging~~
- [ ] Batch upload multiple BibTeX files
- [ ] Compare before/after enrichment statistics

<!-- EOF -->