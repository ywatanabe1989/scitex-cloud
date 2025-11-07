<!-- ---
!-- Timestamp: 2025-11-05
!-- Author: ywatanabe + Claude
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/10_SCITEX_WRITER_05.md
!-- --- -->

# SciTeX Writer Enhancement Plan

## Overview
Comprehensive improvements to the writer app including section management, bibliography integration, document type switching, and special content handling.

---

## 1. Section Management (Advanced CRUD)

### 1.1 Section Include/Exclude Functionality
- [ ] Implement section include/exclude toggle in UI
- [ ] Add visual indicators for excluded sections (subtle colors)
- [ ] Add +/- buttons or radio controls for include/exclude
- [ ] Implement folding for excluded sections (collapsed by default)
- [ ] Update compilation logic to respect include/exclude settings

### 1.2 Section Ordering
- [ ] Implement drag-and-drop for section reordering
- [ ] Alternative: Add up/down arrow buttons for reordering
- [ ] Save section order to persistent storage
- [ ] Update compilation to follow custom section order

### 1.3 Custom Sections
- [ ] Allow users to add custom sections
- [ ] Implement "Add Section" UI/UX
- [ ] Create new .tex files for custom sections
- [ ] Support deletion of custom sections (with confirmation)
- [ ] Support renaming of custom sections

### 1.4 Section Name Mapping
- [ ] Implement name mapping system (e.g., Abstract → Summary)
- [ ] Create UI for configuring mappings
- [ ] Store mappings in project configuration
- [ ] Apply mappings during compilation for publisher requirements

### 1.5 Section CRUD UI/UX Excellence
- [ ] Design clean, intuitive section management interface
- [ ] Add tooltips and help text for section operations
- [ ] Implement confirmation dialogs for destructive operations
- [ ] Add undo/redo support for section operations
- [ ] Ensure mobile-responsive design

---

## 2. Authors in Frontmatter

- [ ] Research scitex.writer's handling of frontmatter
- [ ] Implement background wrapping of Authors content
- [ ] Automatically insert LaTeX `\begin{}`...`\end{}` structure
- [ ] Ensure preview compilation works with wrapped content
- [ ] Test with various author formats (single, multiple, affiliations)
- [ ] Add validation for author format
- [ ] Handle edge cases (empty authors, special characters)

---

## 3. Bibliography Integration

### 3.1 Research & Implementation
- [ ] Research scitex.scholar bibliography merging logic
  - Location: ~/proj/scitex-code/src/scholar
- [ ] Understand how merging works for multiple .bib files
- [ ] Implement integration with merged bibliography
  - Path: proj-root/scitex/scholar/bib_files/bibliography.bib

### 3.2 Bibliography Cards UI
- [ ] Design card-based UI for bibliography entries
- [ ] Show entry details on cards (author, title, year, venue)
- [ ] Distinguish cited vs uncited entries visually
  - Different colors/badges for cited entries
- [ ] Add search/filter functionality for entries
- [ ] Sort entries (alphabetical, by date, by citation status)

### 3.3 Bibtex File Editing
- [ ] Make bibtex file editable as ordinary text file
- [ ] Add syntax highlighting for .bib files
- [ ] Implement DOI-based entry sync with scholar storage
- [ ] Add "Add from DOI" functionality
- [ ] Validate bibtex syntax on save
- [ ] Show parse errors if bibtex is malformed

### 3.4 Citation Management
- [ ] Track which entries are cited in manuscript
- [ ] Update citation status in real-time as user types
- [ ] Show citation count per entry
- [ ] Highlight unused entries

---

## 4. Citation Autocomplete

- [ ] Implement `\cite{}` command detection in editor
- [ ] Parse bibtex entries for autocomplete suggestions
- [ ] Show autocomplete dropdown with entry details
  - Entry key (citation key)
  - Author names
  - Title
  - Year
- [ ] Implement fuzzy search for citation keys
- [ ] Add keyboard navigation for autocomplete (↑/↓, Enter)
- [ ] Support multiple citations: `\cite{key1,key2}`
- [ ] Test autocomplete performance with large bibliographies

---

## 5. Internal Content Management

- [ ] Identify all internal-only content (word counts, metadata)
- [ ] Create configuration for what to hide from users
- [ ] Update UI to hide internal sections
- [ ] Ensure internal content still functions in background
- [ ] Add admin/debug mode to view internal content (optional)

---

## 6. Document Type Switching

### 6.1 Document Type Dropdown
- [ ] Implement document type dropdown UI
  - Options: Manuscript, Shared, Revision, Supplementary
- [ ] Currently fixed to "manuscript" - remove hardcoding
- [ ] Update URL structure for document types
  - e.g., `/writer/project/{id}/manuscript/`
  - e.g., `/writer/project/{id}/revision/`

### 6.2 Page Reload on Type Change
- [ ] Implement page reload when document type changes
- [ ] Save current editor state before reload
- [ ] Restore editor state after reload (cursor position, scroll)
- [ ] Show loading indicator during transition
- [ ] Test smooth transitions between document types

### 6.3 Section Dropdown per Document Type
- [ ] Update section dropdown based on selected document type
- [ ] Load appropriate sections for manuscript
- [ ] Load appropriate sections for shared
- [ ] Load appropriate sections for revision
- [ ] Load appropriate sections for supplementary
- [ ] Cache section configurations to avoid repeated API calls

### 6.4 Content Update on Type Change
- [ ] Update editor content when document type changes
- [ ] Update PDF preview area for selected document type
- [ ] Clear preview cache when switching types
- [ ] Ensure correct LaTeX content loaded for each type

---

## 7. WriterService Updates

- [ ] Update WriterService to support all document types
  - Current: Only manuscript
  - Add: Shared, Revision, Supplementary
- [ ] Implement `get_sections_by_doc_type(doc_type)` method
- [ ] Update `read_section(section, doc_type)` to handle all types
- [ ] Update `write_section(section, content, doc_type)` for all types
- [ ] Update `compile_preview()` to support all document types
- [ ] Add document type validation
- [ ] Test all operations with each document type

---

## 8. TypeScript/JavaScript UI Updates

### 8.1 Document Type Switching Logic
- [ ] Update TypeScript to handle document type parameter
- [ ] Implement document type change handler
- [ ] Update API calls to include document type
- [ ] Save selected document type to localStorage
- [ ] Restore document type on page load

### 8.2 Section Management
- [ ] Update section dropdown to filter by document type
- [ ] Implement section switching within document type
- [ ] Cache section content to avoid repeated API calls
- [ ] Implement smooth transitions between sections (local preview)
- [ ] Update PDF viewer when section changes

### 8.3 State Management
- [ ] Centralize state management for:
  - Current document type
  - Current section
  - Editor content
  - Preview PDF path
- [ ] Implement state persistence (localStorage)
- [ ] Handle state restoration on page load
- [ ] Add state validation and error handling

---

## 9. Priority Implementation Order

### Phase 1: Foundation (Week 1)
1. Document type switching (6.1, 6.2)
2. WriterService updates (7)
3. TypeScript UI updates for document types (8.1)

### Phase 2: Section Management (Week 2)
4. Section CRUD UI/UX (1.1, 1.2, 1.3, 1.5)
5. Section name mapping (1.4)
6. Update sections per document type (6.3, 6.4)

### Phase 3: Bibliography (Week 3)
7. Research scitex.scholar (3.1)
8. Bibliography cards UI (3.2)
9. Bibtex editing (3.3)
10. Citation management (3.4)

### Phase 4: Advanced Features (Week 4)
11. Citation autocomplete (4)
12. Authors frontmatter handling (2)
13. Internal content management (5)
14. State management improvements (8.3)

---

## Testing Checklist

- [ ] Test all document types (manuscript, shared, revision, supplementary)
- [ ] Test section CRUD operations
- [ ] Test section ordering and include/exclude
- [ ] Test bibliography integration
- [ ] Test citation autocomplete
- [ ] Test document type switching with state preservation
- [ ] Test with multiple projects
- [ ] Test with large bibliographies (performance)
- [ ] Test error handling for all operations
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Mobile responsiveness testing

---

## Notes

- **Smooth transitions**: Only between sections (using local preview files)
- **Page reload**: Acceptable for document type switching (not frequent)
- **Bibliography as cards**: First step - not LaTeX rendering
- **Authors wrapping**: Background process to ensure preview works
- **DOI sync**: Integration with scholar storage when DOI provided

---

## Questions/Decisions Needed

- [ ] Exact UI/UX design for section management
- [ ] Color scheme for cited vs uncited entries
- [ ] Maximum number of custom sections allowed
- [ ] Section name mapping configuration format
- [ ] Error handling strategy for bibliography parsing

<!-- EOF -->
