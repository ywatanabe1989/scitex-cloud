<!-- ---
!-- Timestamp: 2025-10-27 17:24:51
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/10_SCITEX_SCHOLAR.md
!-- --- -->

## ATTENTION
DON'T TELL A LIE
YOU **MUST** confirm your statement with visual check or user confirmation
Django server is running with hot reloading
User is checking the webpage with Ctrl + Shift + R to clear cache

## SciTeX Scholar Module

## scitex.scholar module is available in ~/proj/scitex_repo/src/scitex/scholar

### **PDF Download Mode** (Future Feature)
- [ ] First only open papers
- [ ] Paywalled papers can be obtained by correctly setting authentication
  - [ ] Currently, we have confirmed `OpenAthens + OpenURL` locally
  - [ ] About 70% of papers downloaded (~/.scitex/scholar/library/neurovista)
- [ ] We need to plan how to serve this functionality
- [ ] Yes, but your instinct is right; the index html should be index.html instead of index.html
  - [ ] So, after index.html implemented, please 

### http://127.0.0.1:8000/scholar/#bibtex
- [ ] Not enriched

  - [ ] Save selected to: project (button + dropdown, just in the enrichment tab)
  - [ ] Download selected as Bibtex
    - [ ] Not working
  - [ ] Recent History (just in the enrichment tab)
  - [ ] Abstract should not be truncated but written in a weak color and provide show abstract toggle (all, truncated, none)
    - [ ] Global only, no-individual toggles
    - [ ] One toggle button [Abstract All] -> [Abstract Short] -> [Abstract Hide] -> [Abstract All] ...

- [x] Keep the last results rendered even when Ctrl + Shift + R
- [x] Sort by dropdown is really good for one dimensional sorting.
  - [x] impact factor
  - [x] publication year asc
  - [x] publication year dec
  - [x] citation count
- [ ] Left side Panel
  - [ ] Scroll bar of the serach control should be theme-responsive
  - [ ] Slider should use scitex color
  - [ ] Default slide range should be nanmin/nanmax of the samples
  - [ ] Scatter swarm plots should be renponsive to min/max of the slider
  - [ ] Citations should be divided by comma by every three digits
  - [ ] impact factor badges should use the impact-factor-badge color (yellow + black)
- [ ] After search completed, the UIs not updated (like selection checkbox)
  - [ ] But when Ctrl + Shift + R, yes, perfect

# Running log
- [ ] Add hook for ScholarSearchEngines and show counts as in bibtex enrichment
  PubMed Loading... 0
  Google Scholar Loading... 0
  arXiv Loading... 0
  Semantic Scholar Loading... 0

# Open in new tab does not work
Ctrl + click shows two tabs, one is the page itself and the other is the url associated
Right click and open in new tab does only open like this:
http://127.0.0.1:8000/scholar/?q=sharp+wave+ripples&source_crossref=crossref&source_pubmed=pubmed&source_semantic=semantic&source_arxiv=arxiv&source_openalex=openalex&year_from=1900&year_to=2025&min_citations=0&max_citations=448&min_impact_factor=1.8&max_impact_factor=44.7&author=&journal=&doc_type=&study_type=&language=&sort_by=relevance#search

# http://127.0.0.1:8000/scholar/?q=sharp+wave+ripples&source_crossref=crossref&source_pubmed=pubmed&source_semantic=semantic&source_arxiv=arxiv&source_openalex=openalex&year_from=1900&year_to=2025&min_citations=0&max_citations=448&min_impact_factor=1.8&max_impact_factor=44.7&author=&journal=&doc_type=&study_type=&language=&sort_by=relevance#search
result.source?

database, scitex index
unknown authors

<!-- EOF -->