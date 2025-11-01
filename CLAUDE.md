<!-- ---
!-- Timestamp: 2025-11-01 09:34:32
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

## Error cascading
python errors should be cascaded to console.log in javascript (or typescript), and also save logs to ./logs/console.log
Simple stderr as text will enhance the easiness of trouble shooting.
Actually, this rule should be applied to all of this web app

---

# Requests

## Rules for clear system building

## Common vs App
Clearly distinguish common files and app-level files
app-level files should be under ./apps/<app_name>_app/

## Central Logging system
- [ ] Log to one place
  - [ ] ./logs/*.log

## General
- [ ] Single source of truth
- [ ] Smaller files are better than monotholic, large files

## Typescript over Javascript 
- [ ] Migrate Javascript to Typescript
  - [ ] console.log for debugging
  - [ ] switchable log function should be implemented in central

## CSS Rules
- [ ] No inline styles. No exception. Factor out to css files
- [ ] No distributed css files. For one class, only one css file can be applied.

## HTML Rules
- [ ] Use partials to read skelton structure of html pages

## https://127.0.0.1:8000/writer/
- [ ] Refactoring

  - [ ] ./static/ts/writer -> ./apps/writer_app/static/writer_app/ts
  - [ ] ./apps/writer_app/static/writer_app/css
  - [ ] ./apps/writer_app/static/writer_app/js
  - [ ] ./apps/writer_app/static/writer_app/ts
  - [ ] ./apps/writer_app/templates/write_app/

### Writer Advanced (skip this now)
  - [ ] Diff functionality
  - [ ] Multi-user edition

## https://127.0.0.1:8000/search/ (skip this now)
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

## Project Page (skip this now)
- [ ] Root: http://127.0.0.1:8000/test-user/proj-001/
  - [ ] Layout of Root directory is good. 
- [ ] Child: http://127.0.0.1:8000/test-user/proj-001/.git
  - [ ] Layout of Child directories are corrupted
  - [ ] Side panel and main table are corrupted in child directories
- [ ] Why root and children are handled differently?
  - [ ] Is it not possible to share components?

<!-- EOF -->