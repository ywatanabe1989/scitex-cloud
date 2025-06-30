<!-- ---
!-- Timestamp: 2025-07-01 07:29:22
!-- Author: ywatanabe
!-- File: /ssh:scitex:/home/ywatanabe/proj/scitex-cloud/CLAUDE.md
!-- --- -->

See `./docs/SciTeX-Ecosystem-and-Corresponding-Local-Directories.md` as well

## Research proposal for this project, SciTeX
See `./docs/BOOST_応募済み申請書_26151429_oubo_20250626.pdf`
However, we are also thinking monetization strategies. `./docs/MONETIZATION_STRATEGY_IMPLEMENTATION.md`

## External pip packages / shell scripts

Core functionalities should be handled under `./externals` as independent, **static** modules:
./externals/SciTeX-Scholar/
./externals/SciTeX-Code/
./externals/SciTeX-Viz/
./externals/SciTeX-Writer/

**Static** means that these modules does not always have AI integration by themselves. However, by incorporating with AI agents, like cloud code, they will have significant impacts while reducing degree of freedom for expected behaviours. (e.g., agents to use SciTeX-Writer for manuscript preparation)

In this SciTeX-Cloud, we focus on providing web interface for web-based users. So, factor out existing logic to the modules as externals are highly recommended while keeping Django code as a platform.

## Project-centric application
The SciTeX ecosystem is project-centric; scholar, code, viz, writer should be linked to a project of the user or a group. However, basic functionalities should be offered to anonymous users or users with no projects associated.

## API Keys
API keys should be handled with user models through dashboard or user settings.

## No fake data
When error raised, show them as alert on the website. Fake operations will raise critical issues.

## Django Directory Structure
Use `./apps/XXX_app/` format

Do not place any files under project root directory
Instead, place under `./docs`, `./apps`, `./project_management`, `./tests`, `./tmp`

## Design Theme of the website
See /design/

<!-- EOF -->