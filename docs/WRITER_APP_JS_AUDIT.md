# Writer App JavaScript Audit

**File**: `/home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/js/writer_app.js`
**Size**: 123KB (2,944 lines)
**Created**: 2025-11-03

## Statistics

- **Functions**: 70+
- **DOM Interactions**: 175 (addEventListener, querySelector, getElementById)
- **API Calls**: 9 (fetch)
- **Storage Operations**: 42 (localStorage, sessionStorage)
- **Structure**: Single DOMContentLoaded block with nested functions

## Function Inventory

### 1. Authentication & Security (1 function)
```
Line    Function                      Purpose
----    --------                      -------
1       getCsrfToken()               Get CSRF token from various sources
```

### 2. History & Undo/Redo (7 functions)
```
Line    Function                      Purpose
----    --------                      -------
138     initializeHistory()          Initialize undo/redo history
145     addToHistory()               Add state to history
172     undo()                       Undo last change
197     redo()                       Redo undone change
222     updateUndoRedoButtons()      Update undo/redo button states
237     saveHistoryToLocalStorage()  Persist history
248     loadHistoryFromLocalStorage() Restore history
```

### 3. Theme & UI State (2 functions)
```
Line    Function                      Purpose
----    --------                      -------
440     updateThemeSelectorOptions()  Update theme dropdown
531     loadState()                   Load app state
555     saveState()                   Save app state
```

### 4. Compilation Panel (1 function)
```
Line    Function                      Purpose
----    --------                      -------
735     setupCompilationPanelToggle() Setup compilation panel
```

### 5. Section Management (10 functions)
```
Line    Function                      Purpose
----    --------                      -------
892     switchToSection()            Switch to different section
913     loadLatexSection()           Load LaTeX for section
964     switchDocumentType()         Switch document type
996     renderSections()             Render section list
1245    addSection()                 Add new section
1269    removeSection()              Remove section
1302    markAsUnsaved()              Mark section as unsaved
1320    markAsSaved()                Mark section as saved
1338    saveCurrentSectionManually() Manual save trigger
1491    saveWordCountToLocalStorage() Save word count
```

### 6. Drag & Drop (6 functions)
```
Line    Function                      Purpose
----    --------                      -------
1081    handleDragStart()            Drag start handler
1089    handleDragEnd()              Drag end handler
1100    handleDragOver()             Drag over handler
1108    handleDrop()                 Drop handler
1139    handleDragLeave()            Drag leave handler
1143    setupDropZones()             Initialize drop zones
```

### 7. Available Sections (1 function)
```
Line    Function                      Purpose
----    --------                      -------
1191    renderAvailableSections()    Render available sections pool
```

### 8. Live Compilation (2 functions)
```
Line    Function                      Purpose
----    --------                      -------
1388    scheduleLiveCompilation()    Schedule live compile
1395    performLiveCompilation()     Execute live compile
```

### 9. LaTeX Conversion (2 functions)
```
Line    Function                      Purpose
----    --------                      -------
1422    convertToLatex()             Convert to LaTeX
1430    convertFromLatex()           Convert from LaTeX
```

### 10. Word Count (6 functions)
```
Line    Function                      Purpose
----    --------                      -------
1464    updateWordCount()            Update word count
1478    updateSectionWordCount()     Update section word count
1491    saveWordCountToLocalStorage() Save word count
1496    loadWordCountFromLocalStorage() Load word count
1512    loadAllWordCountsFromLocalStorage() Load all word counts
1524    updateTotalWordCount()       Update total count
```

### 11. Manuscript Compilation (3 functions)
```
Line    Function                      Purpose
----    --------                      -------
1528    compileManuscript()          Compile manuscript
1583    pollCompilationStatus()      Poll compilation status
1667    exportManuscript()           Export manuscript
```

### 12. User Feedback (2 functions)
```
Line    Function                      Purpose
----    --------                      -------
1700    showSaveStatus()             Show save status
1707    showToast()                  Show toast notification
```

### 13. PDF Management (4 functions)
```
Line    Function                      Purpose
----    --------                      -------
1730    checkForExistingPDF()        Check for existing PDF
1752    checkForDiffPDF()            Check for diff PDF
1803    checkForRunningCompilation() Check running compilation
1833    checkForExistingPDFsPanel()  Check PDFs for panel
```

### 14. PDF Rendering (2 functions)
```
Line    Function                      Purpose
----    --------                      -------
1848    loadPDFsPanel()              Load PDFs in panel
1928    renderPDFWithOutline()       Render PDF with outline
1974    renderOutlineItem()          Render outline item (nested)
```

### 15. Panel Compilation (3 functions)
```
Line    Function                      Purpose
----    --------                      -------
2038    compileManuscriptPanel()     Compile in panel
2098    pollCompilationStatusPanel() Poll status for panel
2157    startTimerInButton()         Start compilation timer
2172    stopTimer()                  Stop timer
```

### 16. TeX Files Management (4 functions)
```
Line    Function                      Purpose
----    --------                      -------
2223    loadTexFilesList()           Load .tex files list
2260    renderTexFilesList()         Render .tex files
2327    switchToTexFile()            Switch to .tex file
2360    updateFileStatus()           Update file status
```

### 17. Editor View (1 function)
```
Line    Function                      Purpose
----    --------                      -------
2494    switchEditorView()           Switch editor view
```

### 18. Draggable Elements (4 functions)
```
Line    Function                      Purpose
----    --------                      -------
2578    makeDraggable()              Make element draggable
2596    dragStart()                  Drag start (nested)
2604    drag()                       Drag handler (nested)
2623    dragEnd()                    Drag end (nested)
```

### 19. Demo Mode (1 function)
```
Line    Function                      Purpose
----    --------                      -------
2661    showCompileDemo()            Show compilation demo
```

### 20. Document Compilation (3 functions)
```
Line    Function                      Purpose
----    --------                      -------
2703    compileDocument()            Compile document
2800    pollCompilationStatus()      Poll status (duplicate?)
2880    updateSaveStatus()           Update save status
```

## Functional Areas (Proposed Modules)

### Module 1: Core/Initialization (~300 lines)
**Purpose**: App initialization, config, CSRF
**Functions**:
- getCsrfToken()
- Initial DOMContentLoaded setup
- Config loading

**Dependencies**: None
**Priority**: High

---

### Module 2: History Management (~350 lines)
**Purpose**: Undo/redo functionality
**Functions**:
- initializeHistory()
- addToHistory()
- undo()
- redo()
- updateUndoRedoButtons()
- saveHistoryToLocalStorage()
- loadHistoryFromLocalStorage()

**Dependencies**: Storage, Current section
**Priority**: High

---

### Module 3: Section Management (~500 lines)
**Purpose**: Section switching, document types, active sections
**Functions**:
- switchToSection()
- loadLatexSection()
- switchDocumentType()
- renderSections()
- addSection()
- removeSection()
- renderAvailableSections()

**Dependencies**: Storage, Editor, LaTeX conversion
**Priority**: Critical

---

### Module 4: Document State (~200 lines)
**Purpose**: Save/unsaved state, local storage
**Functions**:
- markAsUnsaved()
- markAsSaved()
- saveCurrentSectionManually()
- loadState()
- saveState()

**Dependencies**: Storage, UI feedback
**Priority**: High

---

### Module 5: LaTeX Processing (~150 lines)
**Purpose**: LaTeX conversion
**Functions**:
- convertToLatex()
- convertFromLatex()

**Dependencies**: None (pure functions)
**Priority**: Medium

---

### Module 6: Word Count (~250 lines)
**Purpose**: Word counting and tracking
**Functions**:
- updateWordCount()
- updateSectionWordCount()
- saveWordCountToLocalStorage()
- loadWordCountFromLocalStorage()
- loadAllWordCountsFromLocalStorage()
- updateTotalWordCount()

**Dependencies**: Storage, Current section
**Priority**: Medium

---

### Module 7: Compilation (~400 lines)
**Purpose**: Manuscript compilation
**Functions**:
- compileManuscript()
- pollCompilationStatus()
- scheduleLiveCompilation()
- performLiveCompilation()
- compileManuscriptPanel()
- pollCompilationStatusPanel()
- compileDocument()

**Dependencies**: API client, UI feedback
**Priority**: High

---

### Module 8: PDF Management (~350 lines)
**Purpose**: PDF loading and rendering
**Functions**:
- checkForExistingPDF()
- checkForDiffPDF()
- checkForRunningCompilation()
- checkForExistingPDFsPanel()
- loadPDFsPanel()
- renderPDFWithOutline()
- renderOutlineItem()

**Dependencies**: Compilation, UI
**Priority**: Medium

---

### Module 9: File Management (~200 lines)
**Purpose**: .tex files management
**Functions**:
- loadTexFilesList()
- renderTexFilesList()
- switchToTexFile()
- updateFileStatus()

**Dependencies**: API client, UI
**Priority**: Medium

---

### Module 10: Drag & Drop (~200 lines)
**Purpose**: Drag and drop functionality
**Functions**:
- handleDragStart()
- handleDragEnd()
- handleDragOver()
- handleDrop()
- handleDragLeave()
- setupDropZones()

**Dependencies**: Section management
**Priority**: Low

---

### Module 11: UI Components (~250 lines)
**Purpose**: UI elements and feedback
**Functions**:
- showSaveStatus()
- showToast()
- updateThemeSelectorOptions()
- switchEditorView()
- makeDraggable() + nested drag functions

**Dependencies**: None
**Priority**: Medium

---

### Module 12: Timers & Utilities (~100 lines)
**Purpose**: Timers and helpers
**Functions**:
- startTimerInButton()
- stopTimer()

**Dependencies**: None
**Priority**: Low

---

### Module 13: Demo Mode (~100 lines)
**Purpose**: Demo functionality
**Functions**:
- showCompileDemo()

**Dependencies**: UI
**Priority**: Low

---

### Module 14: Export (~50 lines)
**Purpose**: Export functionality
**Functions**:
- exportManuscript()

**Dependencies**: API client
**Priority**: Low

---

## Data Structures

### Global State Variables (identified in file)
```javascript
// Configuration
- projectId
- username
- projectSlug
- isDemo
- isAnonymous
- writerInitialized

// Section State
- currentSection
- currentDocType
- activeSections
- allAvailableSections
- sectionsData

// History
- undoHistory
- currentHistoryIndex

// Editor
- codeMirrorEditor (if exists)

// Timer
- compilationTimer
- timerInterval
```

## Dependency Map

```
Core/Init
  └─> Everything depends on this

Section Management
  ├─> Document State
  ├─> LaTeX Processing
  ├─> Word Count
  └─> History Management

Compilation
  ├─> Section Management
  ├─> PDF Management
  └─> UI Components

PDF Management
  ├─> Compilation
  └─> UI Components

File Management
  └─> UI Components

History Management
  ├─> Document State
  └─> Storage

Word Count
  └─> Storage

UI Components
  └─> (used by everything)
```

## API Endpoints Used

```
POST /writer/api/initialize-workspace/
POST /writer/api/compile/
GET  /writer/api/compilation-status/<jobId>/
POST /writer/api/export/
GET  /writer/api/pdf/<filename>/
GET  /writer/api/tex-files/
GET  /writer/api/section/<section>/
```

## localStorage Keys

```
history_<projectId>
state_<projectId>
wordCount_<section>_<docType>
sections_<projectId>
activeSections_<projectId>
```

## Refactoring Priority

### Phase 1 (Critical - Core Functionality)
1. **Core/Initialization** - Foundation for everything
2. **Section Management** - Core feature
3. **Compilation** - Core feature
4. **Document State** - Critical for data integrity

### Phase 2 (High - Important Features)
5. **History Management** - Important UX
6. **Word Count** - Important feedback
7. **PDF Management** - Important for previews

### Phase 3 (Medium - Supporting Features)
8. **LaTeX Processing** - Utilities
9. **File Management** - Secondary feature
10. **UI Components** - Can be gradual

### Phase 4 (Low - Nice to Have)
11. **Drag & Drop** - Enhancement
12. **Timers & Utilities** - Small utilities
13. **Demo Mode** - Optional
14. **Export** - Secondary feature

## Breaking Down Strategy

### Recommended Approach

**Option A: Incremental Extraction** (Safer)
1. Extract utilities first (LaTeX, Word Count)
2. Extract UI components
3. Extract core modules one by one
4. Update imports progressively

**Option B: Big Bang Refactor** (Faster but riskier)
1. Create all module files at once
2. Move functions to modules
3. Test everything together

**Recommendation**: **Option A** - Safer and testable

## File Size Targets

| Module | Current Est. | Target | Status |
|--------|--------------|--------|--------|
| Core/Init | ~300 lines | <300 | ✅ Good |
| History Mgmt | ~350 lines | <400 | ✅ Good |
| Section Mgmt | ~500 lines | <500 | ⚠️ At limit |
| Document State | ~200 lines | <300 | ✅ Good |
| LaTeX Processing | ~150 lines | <200 | ✅ Good |
| Word Count | ~250 lines | <300 | ✅ Good |
| Compilation | ~400 lines | <500 | ⚠️ At limit |
| PDF Management | ~350 lines | <400 | ✅ Good |
| File Management | ~200 lines | <300 | ✅ Good |
| Drag & Drop | ~200 lines | <300 | ✅ Good |
| UI Components | ~250 lines | <300 | ✅ Good |
| Timers | ~100 lines | <200 | ✅ Good |
| Demo Mode | ~100 lines | <200 | ✅ Good |
| Export | ~50 lines | <200 | ✅ Good |

**Total**: ~2,900 lines → 14 modules

## Next Steps

1. ✅ Audit complete
2. ⏭️ Create TypeScript module structure
3. ⏭️ Start with utilities extraction (LaTeX, Word Count)
4. ⏭️ Extract UI components
5. ⏭️ Extract core modules
6. ⏭️ Update templates to import modules
7. ⏭️ Test each module
8. ⏭️ Remove original writer_app.js

---

**Audit Completed**: 2025-11-03
**Status**: Ready for refactoring
**Estimated Effort**: 20-30 hours
