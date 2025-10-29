<!-- ---
!-- Timestamp: 2025-10-28 15:08:11
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/CLAUDE.md
!-- --- -->


## AGENTS DO NEVER EDIT THIS FILE
## THE USER IS ONLY ALLOWED TO EDIT THIS FILE. DO NOT MODIFY THIS FILE UNLESS EXPLICITLY ASKED.
## GITIGNORE THIS FILE. NEVER UPLOAD TO GITHUB.
## IN DEVELOPMENT (127.0.0.1:8000), DO NOT RUNSERVER. IT IS HANDLED BY ./start_dev.sh and we confirmed auto-hot-reloading enabled.
---

## Subagents
Time is more than money.
Launch up to eight agents in parallel when beneficial.
## Autonomous Development
Based on the following conditions, please proceed development autonomously
### Test user
Create and use this user for testing purposes as you want:
- Username: test-user, Password: Test-user!
### Playwright
- MCP available
- Screenshot available
- However, since this consumes lots of tokens, please use this only when critical
## No fake data
When error raised, show them as alert on the website. Fake operations will raise critical issues.
## No comprehensive
- When you say comprehensive, it can be translated into "I will create xxx which is really hard for humans to undersntad"
- Keep documents necessary and sufficient. Too much information may do more harm than good.

---

## SciTeX principal
SciTeX is designed to work everywhere; local, cloud, and self-hosting
So, scitex python package should implement core logics and provide simple APIs while django should concentrate on cloud
`scitex` is installed via editable mode via pip from .venv
Especially, ~/proj/scitex-code/{cli,cloud,scholar,writer,project,template} will be highly related
It would be better to place .env file in project root and load it to specify SCITEX_ environment variables

## Research proposal for this project, SciTeX
`./docs/BOOST_応募済み申請書_26151429_oubo_20250626.pdf`
`./docs/MONETIZATION_STRATEGY_IMPLEMENTATION.md`

## Project-centric application
The SciTeX ecosystem is project-centric; scholar, code, viz, writer should be linked to a project of the user or a group. However, basic functionalities should be offered to anonymous users or users with no projects associated.

## Environmental Variables
`./SECRETS/.env.{dev,prod}` will be useful
`env | grep SCITEX_`

## Python Env
`/home/ywatanabe/proj/scitex-cloud/.venv`
When change directory from `.`, deactivate automatically called.

## CSS - Common vs Specific
`./static/css/CSS_RULES.md`

## Django Directory Structure
Use `./apps/XXX_app/` format
Follow `./apps/README.md`
Do not place any files under project root directory

## Design Theme of the website
See `./apps/dev_app`
See `/dev/design/`

## Debugging Javascripts
Add console.log for debugging

---

# Requests
- [ ] http://localhost:8000/writer/
  - [ ] Compilation failed
Compile script not found
  - [ ] Split view does not apply syntax highlight, and even light/dark theme ignored
    - [ ] Is it better to try Monaco Editor + Type script?



  - [ ] The UI/UX of writer is quite aweful compaired to their potentials
    - [ ] Please check it and revise accordingly

- [ ] http://127.0.0.1:8000/scholar/search/
  - [ ] When save button clicked, searched results disappear from the page
    - [ ] This prompt shown but search results disappear
Select Project
Choose a project to save this paper:

  - [ ] To use space effectively, show the Cite, Save, DOI, Engine badges in the same row in each card
  - [ ] Filtering seekbar should use our brand theme colors
  - [ ] Filtering does not show data in online manner
    - [x] Hues for all three scatters should be synced
    - [x] Slider selection should apply filtering in the figures immediately (so, colors changed and the same items across figures change colors as well; shared hue)
  - [ ] Ctrl + Shift + R should not delete the searched results
  - [ ] when searched, it restart searching, infinitely

- [ ] http://127.0.0.1:8000/scholar/bibtex/
  - [ ] No alert saved to...; just show success alert

- [ ] http://127.0.0.1:8000/new/
  - [ ] Disable auto-filling to the repository name

- [ ] Header
  - [ ] Scholar button should be separated button; the left is okay; right should have dropdown and enable selection whether bibtex or search

## WIP
- [ ] http://127.0.0.1:8000/wyusuuke/default-project/
  - [ ] Layout of Root directory is okay
  - [ ] Layout of Child directories (e.g., http://127.0.0.1:8000/wyusuuke/default-project/.git/) not shown properly, corrupted
    - [ ] Side panel and main table are corrupted
  - [ ] The folder icon of the main table too bright
    - [ ] Use color-theme-applied svg images instead

<!-- EOF -->