<!-- ---
!-- Timestamp: 2025-10-28 12:38:12
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
  - [ ] Initialize writer workspace button not working
    - [ ] Place it as "initialize with template" in the left panel
  - [ ] Tex files should be linked to the repository
    - [ ] Where is it finding?
- [ ] Editor is something is wrong
  - [ ] Cursor size is x3 height ...

  - [ ] CSS Refactoring needed
  - [ ] View PDF button not working

- [ ] http://127.0.0.1:8000/scholar/search/
  - [ ] Save to project does not get current project
  - [ ] As the logic is now in project_app side, use it

- [ ] http://127.0.0.1:8000/scholar/bibtex/
  - [ ] Save to project
    - [ ] Error: Project has no git repository

- [ ] http://127.0.0.1:8000/new/
  - [ ] Disable cookie to the repository name

- [ ] Project selector in the header
  - [ ] Drop down should include special selection: Create New Project
  - [ ] Remove the two new project buttons in the header
  - [ ] Place a button "Jump" to the dropdown 
    - [ ] What is better naming than "Jump"? Files?
      - [ ] I want to prepare a way to quickly jump to /<username>/<project-name>/

- [ ] http://127.0.0.1:8000/wyusuuke/default-project/
  - [ ] Child directory not shown properly
    - [ ] Side panel and main table are corrupted
  - [ ] The folder icon of the main table too bright
    - [ ] Use color-theme-applied svg images instead

- [ ] http://127.0.0.1:8000/
    - [ ] When hovered, elements have different behaviours in the header
    - [ ] How do you think? THe rich version of the logo is better?
    - [ ] Anyway, we need consistency across header eleemnts, and the web app entirely

<!-- EOF -->