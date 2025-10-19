<!-- ---
!-- Timestamp: 2025-10-20 10:17:43
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/01_HOW_USERS_WORK_WITH_THEIR_DATA.md
!-- --- -->

## How Users can work with THEIR data

1. Git Hosting (Gitea)
- [ ] Implement Gitea to host git
  - [ ] Users can use this web app like GitHub/GitLab/Bitbacket
  - [ ] git clone git@scitex.ai

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