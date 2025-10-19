<!-- ---
!-- Timestamp: 2025-10-20 10:08:45
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/10_SCITEX_SCHOLAR.md
!-- --- -->

### Reference Management Integration

see ~/proj/scitex_repo/src/scitex/scholar/pipelines/

### Guide Users

## **Enrich Mode**

### Step 1.
Users can create *.bib files from AI2

``` plaintex
**You can get BibTeX files from AI2 Scholar QA their optimized LLM**
   - Visit [Scholar QA](https://scholarqa.allen.ai/chat/)
   - Ask literature questions
   - Click "Export All Citations" to save as BibTeX file (*.bib)
```

e.g., 
~/.scitex/scholar/library/seizure_prediction/info/bibliography/seizure_prediction.bib

### Step 2.
Users bib files can be enhanced to metadata-rich version using our scholar pipelines
- [ ] ~/.scitex/scholar/library/seizure_prediction/info/bibliography/seizure_prediction_processed.bib
  - [ ] Check if why this is not saved there
- [ ] /home/ywatanabe/.scitex/scholar/library/seizure_prediction

### **PDF Download Mode**
- [ ] First only open papers
- [ ] Paywalled papers can be obtained by correctly setting authentication
  - [ ] Currently, we have confirmed `OpenAthens + OpenURL` locally
  - [ ] About 70% of papers downloaded (~/.scitex/scholar/library/neurovista)
- [ ] We need to plan how to serve this functionality

---

## **Search Mode**
- [ ] We can offer search functionality from various sources
  - [ ] However, we highly recommend to use the AI2 Scholar QA for bulk & semantic search
- [ ] Search from query
  - [ ] Use external APIs
  - [ ] Use local CrossRef (only in dev; NAS has this)
- [ ] Current we might only accept doi and titles in the pipeline
- [ ] So, we need to update our metadata_engines (ScholarEngine? API)


---

<!-- EOF -->