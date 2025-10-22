<!-- ---
!-- Timestamp: 2025-10-23 07:17:12
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/CLAUDE.md
!-- --- -->


See `./docs/SciTeX-Ecosystem-and-Corresponding-Local-Directories.md` as well

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
See /dev/design/

## Debugging Javascripts
Add console.log for debugging

## Current Urgent Requests
- [x] Visual aesthetics for /scholar/ page
  - [x] Tabs should be like in the filer (github headers?) - DONE: Bottom border indicator style
  - [x] Underscore for selected - DONE: Using scitex-color-03 bottom border
  - [x] Non-selected as darker (in the dark) or lighter (in the light mode) - DONE: color-fg-muted with hover states
  - [x] The input box of the search page should have edge - DONE: 1px solid border with focus states
  - [x] Add edge for search button to keep height the same - DONE: min-height matching and border styling
- [x] Login issue fixed - DONE: Template namespace references updated from core_app to workspace_app
- [x] Core app refactoring completion - DONE: All references updated

## Modules for logged-in users

<!-- EOF -->