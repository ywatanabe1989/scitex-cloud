<!-- ---
!-- Timestamp: 2025-10-20 00:25:35
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
You can check environmental variables by `env | grep SCITEX_` and use them, including passwords and auth info, as you want. Also, you can export new ones. `.env` or `./deployment/dotenvs/dotenv.{dev,prod}` will be useful
`/home/ywatanabe/proj/scitex-cloud/.env`

## No fake data
When error raised, show them as alert on the website. Fake operations will raise critical issues.

## Django Directory Structure
Use `./apps/XXX_app/` format

Do not place any files under project root directory
Instead, place under `./docs`, `./apps`, `./project_management`, `./tests`, `./tmp`, `./data`

## Design Theme of the website
See /dev/design/

## Playwright Automation
Always show what you are thinking as one line of popup

## Current Urgent Requests

## Colors

## Design page

## Repository Settings
- Add collaborator not functional
- Update visibility redundant
- Delete this repository should be implemented for actual steps, requiring typing the user and repository name just like in GitHub

## Light/Dark Theme
Occasionally change color theme (light/dark modes) to check visual consistency across pages and components. Consistency is key for sophisticated websites. Visual elegance improves user experiences.
Visual check should be done in 1920*1080 window size.
Since I can see the website in different browser, you can work in headless mode or using porting display is acceptable.


## Profile 
http://127.0.0.1:8000/profile/settings/profile/
- [ ] Git Platform integration should be separated form general
- [ ] Side bar should be more granular
- [ ] Locatino should be auto-completed with time zone like in github
- [ ] Notifications is not functional - remove it
- [ ] Keys/Tokens should be more organized
  - [ ] SSH Keys should be separated to
  - [ ] Add SSH or GPG Keys
  - [ ] Generate SSH Keys
  - [ ] Register Tokens
- [ ] Email/Password change functionalities should be implemented

## Signup page
http://127.0.0.1:8000/auth/signup/
Password and Confirm Passsword shoul be in a closer
After Confrim Password section, the validators should be shown
Not responsible for theme
These text are not visible in darkmode: SciTeX is completely free to use and all our code is open source. No hidden fees or paid tiers.

## Overview
http://127.0.0.1:8000/ywatanabe/?tab=overview
This is not functional
Projects and Stars as well
Username should be clearly shown as @ywatanabe or something

## Version Control
- [ ] Gitea is not optional but should be enabled

## Footer
- [ ]  Multilingual support
  - [x] English (default)
  - [ ] Portugues (Brasil)
  - [ ] Espanol (America Latina)
  - [ ] Nihongo
  - [ ] Kankokugo (in korean letter)

## Footer
  - [ ] Add social services
  - [ ] linkedin, instagram, youtube, X, tiktok, twitch, github

<!-- EOF -->