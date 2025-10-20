<!-- ---
!-- Timestamp: 2025-10-20 11:02:40
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/01_HOW_USERS_WORK_WITH_THEIR_DATA.md
!-- --- -->

## How Users can work with THEIR data

1. Git Hosting (Gitea)
- [x] Implement Gitea to host git
  - [x] Users can use this web app like GitHub/GitLab/Bitbucket
  - [x] git clone git@scitex.ai (production deployed at git.scitex.ai)
  - [x] Development environment available
  - [x] Maintenance scripts implemented (check status, list repos, list users)

2. SSH/SFTP/rsync Access
- [ ] Allow users to ssh to the server and work directory there
- [ ] Security
  - [ ] Resource allocation (SLURM)
  - [ ] LDAP? Sorry, I am not good at this
  - [ ] Singularity
- [ ] This enables powerusers, like Emacs users, can directly work with THEIR data
  - [ ] Allow sftp
  - [ ] Allow rsync as well

<!-- EOF -->