<!-- ---
!-- Timestamp: 2025-10-22 20:51:04
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
  - [ ] Each paper should have checkbox
  - [ ] Export as bibtex

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

- [ ] Paper Cards are too large; use the space effectively

## Impact factor
- [ ] Impact factor not available for "Journal: eLife" indicates a bug
- [ ] Impact factor range from 2 by default is not recommended; from 0 and accept none like arxiv


- [ ] Remove these status section
Search Engine Queue Status
8:49:45 PM
Active Searches
5
Total Results
0


- [ ] Make journal names inclined

<!-- EOF -->