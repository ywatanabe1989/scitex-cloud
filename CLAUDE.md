<!-- ---
!-- Timestamp: 2025-10-24 12:46:10
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/CLAUDE.md
!-- --- -->


# General Rules

## THE USER IS ONLY ALLOWED TO EDIT THIS FILE. DO NOT MODIFY THIS FILE UNLESS EXPLICITLY ASKED.
## GITIGNORE THIS FILE. NEVER UPLOAD TO GITHUB.

## Autonomous Development
Based on the following conditions, please proceed development autonomously
### Test user
Create and use this user for testing purposes as you want:
- Username: test-user, Password: test
- Username: ywatanabe, Password: Yusuke8939.

### Playwright
- [ ] MCP available
- [ ] Screenshot available


## SciTeX principal
SciTeX is designed to work everywhere; local, cloud, and self-hosting
So, scitex python package should implement core logics and provide simple APIs while django should concentrate on cloud
`scitex` is installed via editable mode via pip from .venv
Especially, ~/proj/scitex-code/{cli,cloud,scholar,writer,project,template} will be highly related
It would be better to place .env file in project root and load it to specify SCITEX_ environment variables

## No comprehensive
- When you say comprehensive, it can be translated into "I will create xxx which is really hard for humans to undersntad"
## Simple Documents
- Keep documents necessary and sufficient. Too much information may do more harm than good.

## Research proposal for this project, SciTeX
See `./docs/BOOST_応募済み申請書_26151429_oubo_20250626.pdf`
However, we are also thinking monetization strategies. `./docs/MONETIZATION_STRATEGY_IMPLEMENTATION.md`

## Project-centric application
The SciTeX ecosystem is project-centric; scholar, code, viz, writer should be linked to a project of the user or a group. However, basic functionalities should be offered to anonymous users or users with no projects associated.

## Environmental Variables
You can check environmental variables by `env | grep SCITEX_` and use them, including passwords and auth info, as you want. Also, you can export new ones. `.venv` or `./deployment/dotenvs/dotenv_{dev,prod}` will be useful
`/home/ywatanabe/proj/scitex-cloud/.venv`

## No fake data
When error raised, show them as alert on the website. Fake operations will raise critical issues.

## Django Directory Structure
Use `./apps/XXX_app/` format
Follow `./apps/README.md`
Do not place any files under project root directory

## Design Theme of the website
See `./apps/dev_app`
See `/dev/design/`

## Debugging Javascripts
Add console.log for debugging

# Requests
## scitex-writer
- [ ] Initialization of workspace creation for writer app fails for new projects for account ywatanabe
  - [ ] Initialize Writer Workspace button does not work in ywatanabe account
    - [ ] 1. create new project, like test-XXX
    - [ ] 2. Navigate to /writer/
    - [ ] 3. Click the Initialize ... button
- [ ] Please fix this. You can login with password "Yusuke8939.".
- [ ] it should create http://127.0.0.1:8000/ywatanabe/scitex/writer/shared
- [ ] The height of the latex code area should be the same as the right side of space
- [ ] This problem is partially due to unorganized directory structure of the writer_app
  - [ ] Organize writer_app as scholar_app
  - [ ] Maybe current mvp_editor.html is the main page; rename it as index.html, just as in scholar_app
  - [ ] See `./apps/README.md`

- [ ] Project directory model and verification:
  - [ ] ~/proj/scitex-code/src/scitex/project

<!-- EOF -->