<!-- ---
!-- Timestamp: 2025-10-20
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/01_USER_DATA_ACCESS_INFRASTRUCTURE.md
!-- Priority: P0 - FUNDAMENTAL INFRASTRUCTURE
!-- --- -->

# Fundamental Infrastructure: How Users Work with THEIR Data

**Status:** 80% Complete
**Priority:** P0 (Critical Foundation)
**Assessment:** See `docs/FUNDAMENTAL_INFRASTRUCTURE_ASSESSMENT.md`

---

## Overview

Users need multiple ways to access and work with their data:
1. ✅ **Web UI** - Implemented
2. ✅ **Git operations** (clone/push/pull) - Implemented via Gitea
3. 🚧 **Direct SSH access** - Not yet implemented
4. ❌ **HPC job submission** - Not yet implemented (optional)

---

## COMPLETED ✅

### 1. Gitea Git Hosting (100% Complete)
**Status:** Fully functional in development, ready for production deployment

**What Works:**
- ✅ Gitea running on `localhost:3000`
- ✅ Create git-backed projects via web UI
- ✅ Import from GitHub
- ✅ Local clone management
- ✅ Full API client (`apps/gitea_app/api_client.py`)
- ✅ Fork repositories
- ✅ Pull requests

**Commands that work:**
```bash
# Via web UI at http://localhost:8000
# Create project → Select "Git-backed repository"
# Or import from GitHub

# Then use standard git:
cd ./data/ywatanabe/my-project/
git add .
git commit -m "Update"
git push origin main
```

**Next Step:** Deploy to production
- [ ] Set up `git.scitex.ai` domain
- [ ] PostgreSQL backend
- [ ] SSL certificates
- [ ] Nginx reverse proxy
- **Timeline:** 1 week

**Reference:**
- `deployment/gitea/IMPLEMENTATION_COMPLETE.md`
- `deployment/gitea/README.md`

---

### 2. SSH Key Management (100% Complete)
**Status:** Fully implemented for Git operations

**What Works:**
- ✅ Generate SSH keys (`apps/core_app/ssh_manager.py`)
- ✅ Secure key storage (`data/ssh_keys/user_{id}/`)
- ✅ Integration with Git clone/push/pull
- ✅ Web UI for key management
- ✅ 4096-bit RSA keys with fingerprints
- ✅ Audit trail (created_at, last_used_at)

**User Workflow:**
1. Visit `/settings/ssh-keys/`
2. Click "Generate SSH Key"
3. Copy public key
4. Add to GitHub/GitLab
5. Clone private repos via SSH

**Reference:** `docs/SSH_KEY_MANAGEMENT_DESIGN.md`

---

## IN PROGRESS 🚧

### 3. Production Gitea Deployment (50% Complete)
**Priority:** P0 - IMMEDIATE
**Timeline:** 1 week
**Effort:** Low (infrastructure mostly ready)

**Tasks:**
- [ ] Day 1: Deploy Gitea to production server
- [ ] Day 2: PostgreSQL backend setup
- [ ] Day 3: Nginx + SSL configuration
- [ ] Day 4: Update Django production config
- [ ] Day 5: Migrate existing projects
- [ ] Day 6-7: Testing & documentation

**Deliverables:**
- ✅ `https://git.scitex.ai` accessible
- ✅ All users can push to their repos
- ✅ GitHub import working

**Blocker:** None - ready to start

**Reference:** `TODOS/99_archive/99_GIT_HOSTING.md`

---

## NOT STARTED ❌

### 4. Direct SSH Server Access (0% Complete)
**Priority:** P1 - HIGH (for power users)
**Timeline:** 2 weeks
**Effort:** Medium

**Goal:** Allow users to SSH into the server

```bash
# What users want to do:
ssh ywatanabe@scitex.ai
cd ~/projects/my-research/
vim script.py          # Edit with their favorite editor
emacs README.md        # Use their own dotfiles
git add .
git commit -m "Update"
git push

# Also:
sftp ywatanabe@scitex.ai   # File transfer
rsync -avz ./local/ ywatanabe@scitex.ai:~/project/  # Sync files
```

**Why Important:**
- Power users (Emacs/Vim users) need terminal access
- Essential for `sftp` and `rsync` workflows
- Integration with existing dotfiles
- Differentiating feature vs GitHub/GitLab

**Implementation Requirements:**

#### Week 1: User Account Management
- [ ] Design: System users per Django user vs shared user
- [ ] Implement user provisioning on registration
- [ ] Link SSH keys (already managed by `SSHKeyManager`)
- [ ] Set up user home directories (`/data/{username}/`)
- [ ] Configure disk quotas

#### Week 2: Security & Testing
- [ ] OpenSSH configuration with chroot/jailing
- [ ] Fail2ban for brute force protection
- [ ] Rate limiting
- [ ] Audit logging
- [ ] Test workflows (ssh, sftp, rsync)
- [ ] Documentation

**Security Considerations:**
```bash
# /etc/ssh/sshd_config
Match User scitex_*
    AuthorizedKeysFile /data/ssh_keys/user_%u/authorized_keys
    ChrootDirectory /data/%u  # Optional: jail to user directory
    ForceCommand internal-sftp  # Optional: sftp-only
```

**Questions to Resolve:**
1. Full shell access or sftp-only?
   - **Recommendation:** Full shell (more powerful for researchers)
2. Chroot jail or open access?
   - **Recommendation:** No chroot initially (simplicity)
3. System user per Django user?
   - **Recommendation:** Yes (cleaner isolation)

**Reference:** `docs/FUNDAMENTAL_INFRASTRUCTURE_ASSESSMENT.md` (GAP 1)

---

### 5. SLURM/HPC Integration (0% Complete)
**Priority:** P3 - OPTIONAL (for HPC deployments)
**Timeline:** 3-4 weeks
**Effort:** High

**Goal:** Submit computational jobs to HPC cluster

```python
# What users want:
# Via web UI: Submit job to HPC cluster
# Django generates SLURM script:
"""
#!/bin/bash
#SBATCH --job-name=my-analysis
#SBATCH --mem=8G
#SBATCH --cpus-per-task=4

singularity exec \
  --bind /data/$USER:/data \
  /shared/containers/scitex-compute.sif \
  python /data/project/scripts/analysis.py
"""
```

**Why Important (for some users):**
- Heavy computational workloads (ML, simulations)
- Access to institutional HPC resources
- Cost savings vs cloud computing

**Why Low Priority:**
- Not all users need HPC
- Can be added later without breaking changes
- Complex integration (SLURM, Singularity, job monitoring)

**Implementation Tasks:**
- [ ] Week 1: SLURM API client + job submission
- [ ] Week 2: Singularity container building
- [ ] Week 3: Web UI (job submission form, monitoring)
- [ ] Week 4: Testing + documentation

**Prerequisites:**
- Access to HPC cluster with SLURM
- Singularity installed on HPC
- Network connectivity Django ↔ HPC

**Reference:**
- `docs/INSTITUTIONAL_DEPLOYMENT_ARCHITECTURE.md`
- `project_management/cloud-integration-roadmap.md`

---

### 6. LDAP Authentication (0% Complete)
**Priority:** P4 - OPTIONAL (institutional deployments)
**Timeline:** 1 week
**Effort:** Medium

**Goal:** Integrate with institutional LDAP/Active Directory

```python
# Single Sign-On with institutional credentials
# config/settings/settings_prod.py
AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

**Why Important (for institutions):**
- Users don't want another password
- IT departments require centralized auth
- Compliance and audit requirements

**Why Low Priority:**
- Django auth works fine for general use
- Can be added without breaking changes
- Only needed for institutional deployments

**Implementation Tasks:**
- [ ] Install django-auth-ldap
- [ ] Configure LDAP backend
- [ ] Test with institutional LDAP
- [ ] User profile sync
- [ ] Fallback to local auth

**Reference:** Standard Django-LDAP integration

---

## Summary & Recommendations

### Current State (80% Complete)
✅ **What's Done:**
- Git hosting (Gitea) - fully implemented
- SSH keys for Git - fully implemented
- Hybrid architecture designed
- Project models updated
- GitHub import working

### Immediate Actions (This Week)

**MUST DO:** Deploy Gitea to Production
- **Priority:** P0
- **Timeline:** 1 week
- **Blocker:** None
- **Impact:** Unlocks fundamental infrastructure
- **Tasks:** See "Production Gitea Deployment" section above

### Next Actions (Weeks 2-3)

**SHOULD DO:** Implement Direct SSH Access
- **Priority:** P1 (if you want power users)
- **Timeline:** 2 weeks
- **Blocker:** None
- **Impact:** HIGH for Emacs/Vim users
- **Tasks:** See "Direct SSH Server Access" section above

### Future (Optional)

**COULD DO:** SLURM/HPC Integration
- **Priority:** P3
- **Timeline:** 3-4 weeks
- **When:** Only if targeting HPC users
- **Blocker:** Need access to HPC cluster

**COULD DO:** LDAP Authentication
- **Priority:** P4
- **Timeline:** 1 week
- **When:** Only for institutional deployments
- **Blocker:** None

---

## Questions to Answer

Before proceeding, clarify:

1. **User Base:**
   - [ ] Personal/Small Team (1-10 users)
   - [ ] Institutional (10-100 users)
   - [ ] Large Scale (100+ users)

2. **Access Patterns:**
   - [ ] Web UI only
   - [ ] Web UI + Git (✅ already implemented)
   - [ ] Web UI + Git + SSH (needs implementation)
   - [ ] Web UI + Git + SSH + HPC (future)

3. **Timeline:**
   - [ ] Deploy Gitea to production this week?
   - [ ] Add SSH access next? (2 weeks)
   - [ ] HPC integration needed? (3-4 weeks)

---

## Links

**Documentation:**
- `docs/FUNDAMENTAL_INFRASTRUCTURE_ASSESSMENT.md` - Full analysis
- `deployment/gitea/IMPLEMENTATION_COMPLETE.md` - Gitea status
- `docs/SSH_KEY_MANAGEMENT_DESIGN.md` - SSH keys
- `docs/INSTITUTIONAL_DEPLOYMENT_ARCHITECTURE.md` - HPC design

**Implementation:**
- `apps/gitea_app/api_client.py` - Gitea API wrapper
- `apps/core_app/ssh_manager.py` - SSH key management
- `deployment/gitea/` - Gitea deployment scripts

**Archive:**
- `TODOS/99_USER_EXPERIENCE.md` - Original TODO (can be archived)
- `TODOS/99_archive/99_GIT_HOSTING.md` - Production deployment guide

<!-- EOF -->
