<!-- ---
!-- Timestamp: 2025-11-03 09:04:54
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

## Django Directory Structure
Use `./apps/XXX_app/` format
Follow `./apps/README.md`
Do not place any files under project root directory

## CSS - Common vs Specific
`./static/css/CSS_RULES.md`

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

## Current Top Priority - Improve /writer/ and show synergy with /scholar/
./TODOS/10_SCITEX_WRITER_01.md

## https://127.0.0.1:8000/search/ (skip this now)
./TODOS/10_SCITEX_SCHOLAR_01.md

## Project Page (skip this now)
- [ ] Root: http://127.0.0.1:8000/test-user/proj-001/
  - [ ] Layout of Root directory is good. 
- [ ] Child: http://127.0.0.1:8000/test-user/proj-001/.git
  - [ ] Layout of Child directories are corrupted
  - [ ] Side panel and main table are corrupted in child directories
- [ ] Why root and children are handled differently?
  - [ ] Is it not possible to share components?

<!-- EOF -->