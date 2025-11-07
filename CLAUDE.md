<!-- ---
!-- Timestamp: 2025-11-06 09:29:38
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/CLAUDE.md
!-- --- -->

## AGENTS DO NEVER EDIT THIS FILE
## THE USER IS ONLY ALLOWED TO EDIT THIS FILE. DO NOT MODIFY THIS FILE UNLESS EXPLICITLY ASKED.
## GITIGNORE THIS FILE. NEVER UPLOAD TO GITHUB.
## IN DEVELOPMENT (127.0.0.1:8000), DO NOT RUNSERVER. IT IS HANDLED BY `make ENV=dev restart` and we confirmed auto-hot-reloading enabled.

## Developmental Environment
We are using docker containers for developmental server as well. Please check ./deployment/docker/docker_dev/ for detals. Makefiles would be also useful. Also, we are not accepting direct call of `python manage.py` to avoid confusion. Please use docker.

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
STRICTLY FOLLOW `./RULES/00_DJANGO_ORGANIZATION_FULLSTACK.md`.


## Design Theme of the website
See `./apps/dev_app`
See `/dev/design/`

## Debugging Javascripts
Add console.log for debugging

## Strict Typescript over javascript
./RULES/02_TYPESCRIPT_HOT_BUILDING_IN_DEVELOPMENT.md
./RULES/03_TYPESCRIPT_WATCH_MECHANISM.md
./RULES/JAVASCRIPT_MIGRATION_STEPS.md
./RULES/JAVASCRIPT_TYPESCRIPT_MIGRATION_STATUS.md

---

# Requests

<!-- EOF -->