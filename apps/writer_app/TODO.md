<!-- ---
!-- Timestamp: 2025-10-30 12:54:30
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/apps/writer_app/TODO.md
!-- --- -->

## AGENTS DO NEVER EDIT THIS FILE
## THE USER IS ONLY ALLOWED TO EDIT THIS FILE. DO NOT MODIFY THIS FILE UNLESS EXPLICITLY ASKED.
## GITIGNORE THIS FILE. NEVER UPLOAD TO GITHUB.
## IN DEVELOPMENT (127.0.0.1:8000), DO NOT RUNSERVER. IT IS HANDLED BY ./start_dev.sh and we confirmed auto-hot-reloading enabled.

- [ ] http://localhost:8000/writer/

- [x] Code syntax highlighter switch
  - [ ] Colors not updated on dropdown selection

- [ ] Allow mouse scroll in the editor

- [ ] Slider should be prepared between the panels to change width (ratio) between them
- [ ] Place "Grip" in the middle to drag
- [ ] The width of slider should be 0pt

- [ ] The scrollbar of the PDF view should be theme-responsible

- [ ] Font size slider should change fonts sizes of latex code and pdf


## /writer/
- [ ] Dropdowns should have correct entries
  - [ ] Shared (not that no contents subdirectory exists)
    - [ ] Title
    - [ ] Authors
    - [ ] Bibliography
  - [ ] Manuscript
    - [ ] Abstract
    - [ ] Introduction
    - [ ] Methods
    - [ ] Results
    - [ ] Discussion
    - [ ] References (only PDF view. Instruct how to add references.)
    - [ ] Figures
    - [ ] Tables
      - [ ] Optional
        - [ ] Highlights
  - [ ] Supplementary
    - [ ] Methods
    - [ ] Results
    - [ ] Figures
    - [ ] Tables
  - [ ] Revision # must be able to CRUD
    - [ ] Editor - Comment 01
    - [ ] Editor - Comment 01 - Response
    - [ ] Editor - Comment 01 - Revision
    - [ ] Editor - Comment 02
    - [ ] Editor - Comment 02 - Response
    - [ ] Editor - Comment 03 - Revision
    - [ ] ...
    - [ ] Reviewer#01 - Comment 01
    - [ ] Reviewer#01 - Comment 01 - Response
    - [ ] Reviewer#01 - Comment 01 - Revision
    - [ ] Reviewer#01 - Comment 02
    - [ ] Reviewer#01 - Comment 02 - Response
    - [ ] Reviewer#01 - Comment 02 - Revision
    - [ ] ...
    - [ ] Reviewer#02 - Comment 01
    - [ ] Reviewer#02 - Comment 01 - Response
    - [ ] Reviewer#02 - Comment 01 - Revision
    - [ ] ...

## Suggestions
What's Working Well ✅
Layout & Structure:

Clean split-pane design with LaTeX source on left, PDF preview on right
Good dark theme implementation - easy on the eyes for long editing sessions
Nice header with module navigation (Explore, Scholar, Code, Viz, Writer)
Proper toolbar with undo/redo, font size control, auto-save, compile, and download

Functionality Visible:

Real-time preview working
File management (test-003, Manuscript, Abstract tabs)
Compile button prominently placed
Save status indicator ("Saved")
Line numbers in editor

Professional Touch:

Footer with community links and social media
Language selector
Repository/user search bar
Dark/light mode toggle (moon icon)

Suggestions for Further Improvement
Editor Experience:

Syntax highlighting - The LaTeX code looks a bit monochrome. Add more color distinction for:

Commands (\begin, \end, \pdfbookmark)
Environments ({abstract})
Comments (%%)
Parameters and arguments


Font size - Consider bumping up from 16px to 14-16px for the code (currently looks readable though)
Gutter improvements:

Git change indicators
Breakpoint/bookmark support
Fold indicators for long sections



Preview Panel:
4. Sync indicators - Visual feedback showing which line in source corresponds to preview
5. Zoom controls for the PDF preview
6. Error indicators - If compilation fails, show errors inline
Workflow:
7. Status bar at bottom showing:

Word count
Line/column position
Compilation status
File encoding


Quick actions - Keyboard shortcuts displayed (tooltips on hover)

Nice-to-Have:
9. Minimap on the right edge of the editor (like VS Code)
10. Search/replace functionality visible or easily accessible
Overall Assessment
This is looking quite professional! The core functionality is there. Now it's about polish and power-user features. Are you planning to add collaborative editing features next, or focusing on enhancing the single-user experience first?

<!-- EOF -->