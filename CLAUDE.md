<!-- ---
!-- Timestamp: 2025-10-23 05:20:14
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/CLAUDE.md
!-- --- -->

 <!-- ---
!-- Timestamp: 2025-10-23 03:23:49
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/CLAUDE.md
!-- --- -->


See `./docs/SciTeX-Ecosystem-and-Corresponding-Local-Directories.md` as well

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
Follow `./apps/README.md'
Do not place any files under project root directory

## Design Theme of the website
See /dev/design/

## Current Urgent Requests
- [ ] Refactor structures of apps
  - Use git effectively
  - Work collaborately with other agents using ./project_management/BULLETIN_BOARD.md

- [ ] Root cause is that core_app and cloud_app have too many responsibilities
  - [ ] core_app
  - [ ] cloud_app 

- [ ] Could you explain what core_app is, and what cloud_app is as well?
  - [ ] Each app must be explanined in one sentence. Otherwise, they have too many responsibilities.
- [ ] Each app should have thier own README.md

<!-- EOF -->