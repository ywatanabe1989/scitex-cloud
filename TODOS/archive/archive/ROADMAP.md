<!-- ---
!-- Timestamp: 2025-10-20 00:17:44
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/ROADMAP.md
!-- --- -->

# SciTeX Cloud Development Roadmap

### 🌐 **Git Hosting** (External vs Internal)
- [ ] Gitea

### 📊 **Writer Module** (Active Development)

**Current Work**:
- OT (Operational Transformation) coordinator
- Undo/Redo functionality
- Real-time collaboration

**Dependencies**:
- Permissions system (who can edit?)
- Git hosting (version control for manuscripts)
- ORCID integration (author metadata)

---

## Recommended Implementation Order

### 🎯 Phase 1: Core Social & Discovery (NEXT - 1-2 weeks)

**Priority**: HIGH
**Effort**: LOW-MEDIUM
**Value**: Enable researcher networking

1. ✅ ~~Follow/Unfollow system~~ (DONE)
2. ✅ ~~Star repositories~~ (DONE)
3. **User search with filters** 🔥
   - Search by name, institution, research interests
   - Filter by academic status
   - Suggested connections
4. **Activity feed pages**
   - Personal activity timeline
   - Following feed
   - Trending repositories

**Files**: `SOCIAL.md`, `SEARCH_ENGINE.md`
**Apps**: `social_app` (enhance), create `search_app`

---

### 🎯 Phase 2: Enhanced Permissions (1-2 weeks)

**Priority**: HIGH
**Effort**: MEDIUM
**Value**: Enable fine-grained collaboration

1. **Enhanced ProjectMembership roles**
   - Add role field (Owner, Maintainer, Developer, Reporter, Guest)
   - Module-specific permissions
   - Permission decorators
2. **Guest collaborator system** 🔥
   - Token-based access
   - Time-limited access
   - Email invitations
   - Comment-only permissions
3. **Collaborator management UI**
   - Invite collaborators with role selection
   - Manage existing collaborators
   - Permission matrix view

**Files**: `PERMISSIONS_SYSTEM.md`, `GUEST_COLLABORATORS.md`, `COLLABORATOR_UI.md`
**Apps**: Enhance `permissions_app`

---

### 🎯 Phase 3: Easy Win Integrations (1-2 weeks)

**Priority**: MEDIUM
**Effort**: LOW
**Value**: Professional polish + practical utility

1. **ORCID integration** 🔥 EASIEST
   - OAuth flow
   - Auto-populate author metadata
   - Display ORCID badge
2. **Slack/Discord webhooks** 🔥 EASIEST
   - Project creation notifications
   - Manuscript updates
   - Analysis completion alerts
3. **BibTeX export** 🔥 EASIEST
   - Export project references
   - Format citations properly
   - Download .bib file

**Files**: `INTEGRATIONS.md`
**Apps**: `integrations_app` (already exists, enhance)

---

### 🎯 Phase 4: Repository Features (2-3 weeks)

**Priority**: MEDIUM
**Effort**: MEDIUM-HIGH
**Value**: Complete GitHub experience

1. **Issues system** (research-focused)
   - Create/edit/close issues
   - Labels (Hypothesis, Methods, Results, Discussion)
   - Milestones
   - Comments with @mentions
2. **Watch/Notifications**
   - Watch repositories
   - Notification center
   - Email alerts
3. **Trending & Discovery**
   - Trending repositories (most starred)
   - Recently updated
   - Recommended based on interests

**Files**: `SOCIAL.md`, `REPOSITORY.md`
**Apps**: Enhance `social_app`, possibly create `issues_app`

---

### 🎯 Phase 5: Git Hosting (2-4 weeks)

**Priority**: LOW (nice to have)
**Effort**: HIGH
**Value**: Native forking support

**Option A**: Gitea self-hosted
- Setup PostgreSQL
- Install Gitea at git.scitex.ai
- Configure OAuth with Django
- Implement fork workflow

**Option B**: GitHub integration only
- Import repos from GitHub
- Link to GitHub for forks/PRs
- Simpler, leverages existing infrastructure

**Files**: `GIT_HOSTING.md`, `INTEGRATIONS.md`
**Recommendation**: Start with Option B (GitHub integration)

---

## Cross-Cutting Concerns

### 🔍 Unified Search System (CRITICAL for Phases 1 & 4)

**Needed by**:
- User discovery (Phase 1)
- Repository search (Phase 4)
- Paper search (Scholar module)
- Code search (Code module)

**Implementation**:
```
apps/search_app/
├── models.py
│   ├── SearchIndex (unified index)
│   └── SearchQuery (query logging)
├── indexers/
│   ├── user_indexer.py
│   ├── repository_indexer.py
│   ├── paper_indexer.py
│   └── code_indexer.py
├── views.py (unified_search, autocomplete)
└── templates/ (search_results.html)
```

**Technology Options**:
1. **PostgreSQL Full-Text Search** (Simple, already have DB)
2. **Elasticsearch** (Powerful, requires separate service)
3. **Meilisearch** (Fast, lightweight, good middle ground)

**Recommendation**: Start with PostgreSQL full-text, migrate to Meilisearch if needed

---

### 📧 Notification System (CRITICAL for Phases 2 & 4)

**Needed by**:
- Guest invitations (Phase 2)
- Follow notifications (Phase 1)
- Star notifications (Phase 1)
- Issue updates (Phase 4)
- Watch notifications (Phase 4)

**Already have**: Channels (WebSocket) for real-time
**Missing**: Email notification queue

**Implementation**:
```
apps/notifications_app/
├── models.py (Notification, EmailQueue)
├── backends/ (email, websocket, slack)
├── tasks.py (celery tasks for async sending)
└── views.py (notification_center, mark_read)
```

---

## Priority Matrix

```
                    HIGH EFFORT          LOW EFFORT
    HIGH VALUE      Phase 4 (Issues)     Phase 1 (Search) 🔥
                    Phase 5 (Git Host)   Phase 3 (ORCID) 🔥

    MEDIUM VALUE    Phase 2 (Perms)      -

    LOW VALUE       -                    -
```

**🔥 Quick Wins** (Do First):
1. User search (Phase 1)
2. ORCID integration (Phase 3)
3. Slack webhooks (Phase 3)

---

## Recommended Execution Plan

### Week 1-2: Search & Discovery ⭐ START HERE
1. Create `search_app` with PostgreSQL full-text search
2. Implement user search (name, institution, interests)
3. Add autocomplete to global search bar
4. Build search results page with filters
5. Add "Suggested users" section on profile

**Deliverable**: Functional user discovery system

### Week 3-4: Easy Integrations
1. ORCID OAuth integration
2. Slack/Discord webhook notifications
3. BibTeX export functionality
4. Update profile settings to connect ORCID

**Deliverable**: Professional integrations that "just work"

### Week 5-6: Enhanced Permissions
1. Add role hierarchy to ProjectMembership
2. Implement guest collaborator tokens
3. Build collaborator management UI
4. Add permission decorators to modules

**Deliverable**: GitLab-style access control

### Week 7-10: Repository Features
1. Issues system (research-focused)
2. Watch/Notifications
3. Trending repositories
4. Activity feed rendering

**Deliverable**: Complete GitHub-style repository experience

---

## File Organization Summary

### Keep Separate (Distinct Features)
- ✅ **SOCIAL.md** - Social networking features
- ✅ **WRITER.md** - Writer module specifics
- ✅ **SCHOLAR.md** - Scholar module specifics (mostly references INTEGRATIONS.md)

### Consolidate/Archive
- ❌ **SEARCH_ENGINE.md** - Empty, merge into SOCIAL.md
- ❌ **REPOSITORY.md** - Empty, content moved to SOCIAL.md
- ✅ **GIT_HOSTING.md** - Keep (infrastructure decision)
- ✅ **INTEGRATIONS.md** - Keep (cross-cutting integrations)
- ✅ **PERMISSIONS_SYSTEM.md** - Keep (detailed permissions design)

### New Master Files
- ✅ **ROADMAP.md** - This file (master plan)
- 📅 **CHANGELOG.md** - Track completed features by date

---

## Next Immediate Action

**Recommendation**: Implement **User Search** (Week 1-2)

This addresses the immediate overlap (search appears in multiple TODOs) and provides high value with reasonable effort.

Create `apps/search_app` with:
1. User search by name/institution/interests
2. Repository search by name/description
3. Unified search results page
4. Autocomplete in global header

Would you like me to start implementing the search system?

<!-- EOF -->