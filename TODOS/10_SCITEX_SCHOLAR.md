<!-- ---
!-- Timestamp: 2025-10-23 02:11:17
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

### Next Steps (Future Enhancements)

### Search
- [ ] Exporting and selection
  - [ ] The color is violeting our theme in dark mode
    - [ ] /dev/design/
  - [ ] Export selected as Bibtex
    - [ ] Failed to export papers. Please try again.

# Running log
- [ ] Add hook for ScholarSearchEngines and show counts as in bibtex enrichment
  PubMed Loading... 0
  Google Scholar Loading... 0
  arXiv Loading... 0
  Semantic Scholar Loading... 0

- [ ] After Jounal Name, impact factor should be shown

- [ ] Remove save and cite buttons

- [ ] In dark mode, paper cards should have visible edges

## Filter Range
- [ ] Once data retrieved, min/max of metrics (year, citation counts, impact factor) should be determined and plots should be maximized in their range
  - [ ] Cite count is awkward like  Citation Count
0
to
11900
  - [ ] The lower limit of impact factor should be 0 by default

- [ ] No impact factor data available -> OK I see; just handle as nan

- [ ] Enter key in the search box should call the search functionality

- [ ] Remove these status section
Search Engine Queue Status
8:49:45 PM
Active Searches
5
Total Results
0


- [ ] Make journal names inclined

# Open in new tab does not work
Ctrl + click shows two tabs, one is the page itself and the other is the url associated
Right click and open in new tab does only open like this:
http://127.0.0.1:8000/scholar/?q=sharp+wave+ripples&source_crossref=crossref&source_pubmed=pubmed&source_semantic=semantic&source_arxiv=arxiv&source_openalex=openalex&year_from=1900&year_to=2025&min_citations=0&max_citations=448&min_impact_factor=1.8&max_impact_factor=44.7&author=&journal=&doc_type=&study_type=&language=&sort_by=relevance#search

# http://127.0.0.1:8000/scholar/?q=sharp+wave+ripples&source_crossref=crossref&source_pubmed=pubmed&source_semantic=semantic&source_arxiv=arxiv&source_openalex=openalex&year_from=1900&year_to=2025&min_citations=0&max_citations=448&min_impact_factor=1.8&max_impact_factor=44.7&author=&journal=&doc_type=&study_type=&language=&sort_by=relevance#search
result.source?

database, scitex index
unknown authors

<!-- EOF -->