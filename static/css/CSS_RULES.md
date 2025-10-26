<!-- ---
!-- Timestamp: 2025-10-26 13:43:57
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/static/css/CSS_REAFACTORING.md
!-- --- -->

## CSS Refactoring for Central CSS + App/Page-specific CSS files

## THIS FILE MUST NOT BE EDITED BY ANYONE EXCEPT FOR THE USER

## Django is run by container
- [ ] Restarting script written in /home/ywatanabe/proj/scitex-cloud/containers/docker/README_DEV.md

## Consistency for password forms
- [ ] Eye icons on the right of input box
- [ ] Requirements online update
- [ ] Placement of confirmation password input (just below the first one)
- [ ] http://localhost:8000/auth/signup/
- [ ] http://localhost:8000/auth/login/
- [ ] http://localhost:8000/accounts/settings/account/
  - [ ] Default color for requirements instead of red from the beginning
- [ ] Rename login -> signin, log in -> signin from text, url, views, filenames, docs, throught the codebase
  - [ ] You might want to use rename.sh

### http://localhost:8000/accounts/settings/appearance/
- [ ] Dropdown selector has multiple triangles in dark mode. Fix it
- [ ] Code Preview space should have edge
- [ ] Code Preview is not reflecting selected theme immediately (meaningless!)
- [ ] Link format is impossible to visually detect. Please check the central setting. Underline needed.

### Layout
- [ ] CSS should use central css files as much as possible: 
  - [ ] `./static/css/{common.css,common/*.css,components/*.css`
  - [ ] Currently, layout gets broken after refactoring
  - [ ] Please keep all the original css under:
    - [ ] `./apps/xxx_app/static/xxx_app/css/`
    - [ ] However, comment out overriding settings
    - [ ] At the same time, keep using css related to layout, positioning
    - [ ] See the example below:

    Before:
    ``` css
    .writer-container {
        min-height: calc(100vh - 80px);
        display: flex;
        background: var(--scitex-light);
    }
    ```

    After:
    ``` css
    .writer-container {
        min-height: calc(100vh - 80px);
        display: flex;
        /* background: var(--scitex-light); */
    }
    ```

### Verification
- [ ] In the development environment, css update is hot-reloaded
- [ ] Use playwright MCP server, take screenshot, and read the image file for confirmation

<!-- EOF -->