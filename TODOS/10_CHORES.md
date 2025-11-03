<!-- ---
!-- Timestamp: 2025-11-03 13:55:17
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/10_CHORES.md
!-- --- -->

- [ ] http://127.0.0.1:8000/auth/verify-email/?email=ywatanabe@scitex.ai
  - [ ] When written, letters are a bit large (or rectangles are a bit small) so that part of letters are not rendered
  - [ ] Color of the letter icon should be re-considerd
  - [ ] Button for resend code should be re-considered

- [ ] "Explorer" in header
  - [ ] Might be confusing
  - [ ] I think this is a necessary functionality as a hub, however, placement of this button here would be not intuitive
  - [ ] Instead users will expect to jump to projects (as now linked in the logo)
  - [ ] I am not sure how to organize them for better UX

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

## Global Header
- [ ] All Public Repositories should not use GitHub Icon; it will be a legal problem
- [ ] You can use scitex icon instead if the svg is appropriate resolution
  - [ ] /home/ywatanabe/proj/scitex-cloud/static/images/vectorstock_38853699/vectorstock_38853699-navy-inverted.svg


##  This should be placed in appropriate place
/home/ywatanabe/proj/scitex-cloud/templates/global_base_partials/codemirror_css.html

<!-- EOF -->