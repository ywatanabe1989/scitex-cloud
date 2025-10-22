<!-- ---
!-- Timestamp: 2025-10-22 01:55:59
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

### Next Steps (Optional Enhancements)
- [ ] Add ability to cancel running jobs
- [ ] Batch upload multiple BibTeX files
- [ ] Compare before/after enrichment statistics


### Speed up is due to cache
### We need to handle multiple jobs due to computational limits

### Login not accepted now
This should be working but ... why?
username: ywatanabe
pw: Yusuke8939.

### From project
no need for this page: http://127.0.0.1:8000/ywatanabe/django-gitea-demo/?mode=scholar
instead, redirect to /scholar/ as well, filling the page to the latest project

### Open All URLS functionality ✅
- [x] When bibtex updated or after enrichment try to open new URLs from doi and URL fields
- [x] when doi is available we should prioritize doi, adding https://doi.org/ as prefix
- [x] By opening all by new tabs, users can effectively download PDF files
- **Implemented:** Added "Open All URLs" button with dynamic count display
- **Features:** Confirmation dialog, staggered tab opening (100ms delay), error handling
- **API:** `/scholar/api/bibtex/job/<id>/urls/` endpoint extracts and returns URLs/DOIs

<!-- EOF -->