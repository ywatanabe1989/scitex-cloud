<!-- ---
!-- Timestamp: 2025-10-26 19:21:53
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/CLAUDE.md
!-- --- -->


## AGENTS DO NEVER EDIT THIS FILE
## THE USER IS ONLY ALLOWED TO EDIT THIS FILE. DO NOT MODIFY THIS FILE UNLESS EXPLICITLY ASKED.
## GITIGNORE THIS FILE. NEVER UPLOAD TO GITHUB.

---

## Subagents
Time is more than money.
Launch up to eight agents in parallel when beneficial.
## Autonomous Development
Based on the following conditions, please proceed development autonomously
### Test user
Create and use this user for testing purposes as you want:
- Username: test-user, Password: Test-user.
- Username: ywatanabe, Password: REDACTED
### Playwright
- [ ] MCP available
- [ ] Screenshot available
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
- [ ] Cannot creat repository

http://localhost:8000/auth/login/?next=/wataning11/default-project/
- [ ] Warning message: "This repository is private. Please log in to access it."
  - [ ] This is problematic in security
  - [ ] Just behave as if it did not exist

- [ ] http://localhost:8000/wataning11/default-project/
  - [ ] CSS Refactoring needed



- [ ] http://localhost:8000/scholar/#bibtex
- [ ] http://localhost:8000/scholar/#search
  - [ ] CSS Refactoring needed
    - [ ] When selected, tab should be visible
  - [ ] Respect default colors
  - [ ] The edge of double-edged seekbars are a bit too large
  - [ ] The double-edged seekbar should be implemented as a central comopnent

- [ ] http://localhost:8000/writer/
  - [ ] CSS Refactoring needed
  - [ ] Tex files should be linked to the repository
  - [ ] View PDF button not working
  - [ ] Initialize writer workspace button not working

<!-- EOF -->