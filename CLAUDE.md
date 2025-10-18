<!-- ---
!-- Timestamp: 2025-10-19 09:25:54
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
- [ ] Please fix the icons of the header for the predefined icons to keep consistency across the web pages, including colors
  - [ ] header colors are not good; change to the bluish colors while keeping consistency and responsive to light/dark theme
- design system should use responsive colors; so, if something is aword in the page, it means default setting is not good
  - not only responsible for light/dark theme, but also consider background/text color contrast
    - For example, some of Primary Colors are not visible; this means the colors are not configured in a systematic manner
- The color of the icons in the header should be a bit more bluish when dark mode enabled

## Design page
- Design page should be accessible from the header, preparing an appropriate svg icon
- Quick navigation should be organized in hierarchy
- Quick navigation section should not overlap on contents
- Design system page itself should use the hero component
- When the designpage reloaded, the page is scrolled to middle in height; why? please fix this

## Repository Settings
- Add collaborator not functional
- Update visibility redundant
- Delete this repository should be implemented for actual steps, requiring typing the user and repository name just like in GitHub


## Landing page
~~- [ ] Prepare beautiful backgrounds -> I will take responsibility~~

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

## http://127.0.0.1:8000/ywatanabe/?tab=overview
This is not functional
Projects and Stars as well
Username should be clearly shown as @ywatanabe or something

## Color theme
Occasionally change color theme (light/dark modes) to check visual consistency across pages and components. Consistency is key for sophisticated websites. Visual elegance improves user experiences.
Visual check should be done in 1920*1080 window size.
Since I can see the website in different browser, you can work in headless mode or using porting display is acceptable.

## Header
Repositories would be a bit strange to come first; how do you think? Also, is it necessary in the header?
Notification not working - remove it (also, in the profile page)

## Components
The edge of primary/secondary outline buttons in dark mode is too vivid

## Gitea
- [ ] Gitea is not optional but should be enabled

## Repositories
- [ ] I think when imported, repository name should be kept as is
- [ ] Edit profile and New buttons have strong edges in darkmode

## Design system
When a section selected from the quick navigation panel, the scrolling issue occurs again
When a section selected, it is invisible in the light mode
No edges for Location format

## Footer
- [ ]  Multilingual support
  - [x] English (default)
  - [ ] Portugues (Brasil)
  - [ ] Espanol (America Latina)
  - [ ] Nihongo
  - [ ] Kankokugo (in korean letter)
- [ ] Add social services
- [ ] linkedin, instagram, youtube, X, tiktok, twitch, github

<!-- EOF -->