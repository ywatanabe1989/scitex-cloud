<!-- ---
!-- Timestamp: 2025-10-17 21:02:51
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/SOCIAL.md
!-- --- -->

# GitHub-Style Social Features for Scientific Research

## Current Architecture
**Existing Apps**: `project_app`, `auth_app`, `permissions_app`, `profile_app`

---

## 1. Profile System (apps/profile_app) ✅ BASEMENT READY

### ✅ Implemented
- [x] UserProfile model with comprehensive fields
- [x] Profile edit interface (`/profile/settings/profile/`)
- [x] Appearance settings with light/dark theme
- [x] Profile fields:
  - [x] Institution (e.g., "The University of Melbourne | JSPS")
  - [x] Academic title (e.g., "Overseas Research Fellow")
  - [x] Location (e.g., "Melbourne, Australia")
  - [x] Website URL (e.g., https://ai-ielts.app)
  - [x] ORCID (e.g., https://orcid.org/0000-0001-9541-6073)
  - [x] Bio, research interests, department
  - [x] Social links (Google Scholar, LinkedIn, ResearchGate, Twitter)
- [x] Privacy controls (public/restricted/private)
- [x] Avatar upload
- [x] Japanese academic institution auto-detection

### 🔨 TODO - Profile Display
- [ ] Enhanced public profile page (`/username/`)
  - [x] Basic info display (partial - in user_project_list.html)
  - [ ] **Followers • Following counts** (e.g., "followers • 4 following")
  - [ ] **Join date display** (e.g., "Joined Oct 2025")
  - [ ] Contribution activity graph (GitHub-style green squares)
  - [ ] Pinned repositories section
  - [ ] Recent activity timeline

---

## 2. Social Networking Features 🆕 NEW APP NEEDED

### 🔨 Follow/Unfollow System (Requires: `social_app`)
- [ ] **Database models**:
  ```python
  class UserFollow(models.Model):
      follower = models.ForeignKey(User, related_name='following')
      following = models.ForeignKey(User, related_name='followers')
      created_at = models.DateTimeField(auto_now_add=True)
  ```
- [ ] **Views & API**:
  - [ ] Follow/Unfollow button on profiles
  - [ ] Followers list page (`/username/followers/`)
  - [ ] Following list page (`/username/following/`)
  - [ ] Follow API endpoint
- [ ] **UI Components**:
  - [ ] Follow button (show "Following" when already following)
  - [ ] Follower count badge
  - [ ] Suggested users to follow

### 🔨 Activity Feed & Timeline
- [ ] **Activity tracking**:
  - [ ] Track: commits, project creation, stars, follows
  - [ ] Activity model with polymorphic relationships
- [ ] **Feed views**:
  - [ ] Personal timeline (your activity)
  - [ ] Following feed (activity from people you follow)
  - [ ] Public activity feed (trending)

### 🔨 Search & Discovery
- [ ] User search with filters (institution, research interests, location)
- [ ] Researcher recommendations
- [ ] Institution directory
- [ ] Research interest tags/categories

---

## 3. Repository Social Features

### ✅ Implemented (via project_app)
- [x] Private/public repositories
- [x] Repository list on user profile
- [x] Collaborator permissions (via permissions_app)
- [x] Repository metadata

### 🔨 TODO - Star System
- [ ] **Database**:
  ```python
  class RepositoryStar(models.Model):
      user = models.ForeignKey(User)
      project = models.ForeignKey(Project)
      starred_at = models.DateTimeField(auto_now_add=True)
  ```
- [ ] **Features**:
  - [ ] Star/Unstar button
  - [ ] Star count display
  - [ ] Starred repositories tab on profile
  - [ ] Trending repositories page (most starred)

### 🔨 TODO - Fork System
- [ ] **Database**:
  - [ ] Add `forked_from` ForeignKey to Project model
  - [ ] Fork count tracking
- [ ] **Features**:
  - [ ] Fork button and workflow
  - [ ] Fork count display
  - [ ] Fork network graph
  - [ ] Sync with upstream repository

### 🔨 TODO - Watch/Notifications
- [ ] **Database**:
  ```python
  class RepositoryWatch(models.Model):
      user = models.ForeignKey(User)
      project = models.ForeignKey(Project)
      watch_type = models.CharField(choices=['all', 'releases', 'none'])

  class Notification(models.Model):
      user = models.ForeignKey(User)
      type = models.CharField()  # follow, star, issue, etc.
      content = models.JSONField()
      read = models.BooleanField(default=False)
  ```
- [ ] **Features**:
  - [ ] Watch button with options
  - [ ] Notification center (bell icon)
  - [ ] Email notifications
  - [ ] Notification preferences

---

## 4. Collaboration Features

### 🔨 TODO - Issues System (Research-Focused)
- [ ] **Database models**:
  ```python
  class Issue(models.Model):
      project = models.ForeignKey(Project)
      title = models.CharField(max_length=200)
      body = models.TextField()  # Markdown support
      author = models.ForeignKey(User)
      assignees = models.ManyToManyField(User)
      labels = models.ManyToManyField('IssueLabel')
      milestone = models.ForeignKey('Milestone', null=True)
      status = models.CharField(choices=['open', 'closed'])
  ```
- [ ] **Research-specific labels**:
  - Hypothesis, Methods, Results, Discussion, Citation
- [ ] **Features**:
  - [ ] Create/edit/close issues
  - [ ] Issue comments with @mentions
  - [ ] Issue assignment
  - [ ] Milestones (project phases)

### 🔨 TODO - Pull Requests (Collaborative Research)
- [ ] PR creation interface
- [ ] Diff viewer for code/data changes
- [ ] Review system with approval
- [ ] Research-specific review checklist:
  - Methodology validation
  - Statistical methods review
  - Citation verification

---

## 5. Repository Management

### 🔨 TODO - Git Integration UI
- [ ] **Branch management**:
  - [ ] List all branches
  - [ ] Create/delete branches
  - [ ] Switch branches
  - [ ] Branch comparison view
- [ ] **Tags & Releases**:
  - [ ] Create tags
  - [ ] Release creation workflow
  - [ ] Release notes editor
  - [ ] Attach files to releases
  - [ ] **Zenodo integration** for DOI assignment

---

## 6. Analytics & Insights

### 🔨 TODO - Repository Analytics
- [ ] **Code metrics**:
  - [ ] Language breakdown (Python, R, MATLAB, LaTeX)
  - [ ] Lines of code statistics
  - [ ] Dependency analysis
- [ ] **Activity metrics**:
  - [ ] Commit frequency graph
  - [ ] Contributors activity
  - [ ] Pulse (weekly activity summary)
- [ ] **Impact metrics**:
  - [ ] Citation count (if published)
  - [ ] Stars and forks
  - [ ] Clone statistics

### 🔨 TODO - Contributor Insights
- [ ] Contributors page
- [ ] Contribution graph per user
- [ ] Code ownership analysis
- [ ] Collaboration network visualization

---

## 7. Package/Dependencies (Research Tools)

### 🔨 TODO - Research Packages Registry
- [ ] List Python packages used in project
- [ ] Version tracking
- [ ] Vulnerability scanning
- [ ] Citation suggestions for packages
- [ ] Link to package documentation

---

## Implementation Roadmap

### Phase 1: Social Foundation (PRIORITY - Build on profile_app)
**Goal**: Enable researcher networking
1. Create `social_app` with Follow system
2. Implement Star repositories
3. Add followers/following display to profiles
4. Basic activity log

**Estimated**: 2-3 weeks

### Phase 2: Discovery & Engagement
**Goal**: Help researchers find collaborators
1. User search with filters
2. Activity feed from followed users
3. Trending repositories
4. Suggested connections

**Estimated**: 2 weeks

### Phase 3: Collaboration Tools
**Goal**: Enable collaborative research
1. Fork repositories
2. Issues system
3. Watch/Notifications
4. Pull requests (basic)

**Estimated**: 3-4 weeks

### Phase 4: Advanced Features
**Goal**: Complete research workflow
1. Branch management UI
2. Releases with DOI
3. Advanced PR reviews
4. Analytics dashboard

**Estimated**: 3-4 weeks

---

## Technical Dependencies

### New Apps to Create
1. **`social_app`** - Follow, Star, Watch, Activity, Notifications
2. **`issues_app`** (optional - could be in project_app)
3. **`analytics_app`** (optional - could be in project_app)

### Database Migrations Needed
- UserFollow, RepositoryStar, RepositoryWatch
- Notification, Activity
- Issue, IssueLabel, Milestone
- Add `forked_from` to Project model

### External Integrations
- **Zenodo API** for DOI assignment
- **Email service** for notifications
- **WebSocket** for real-time notifications (already have Channels)

---

## Next Steps

**Immediate Action**: Start with Phase 1 (Social Foundation)
1. Create `social_app` structure
2. Implement UserFollow model
3. Add follow button to user profiles
4. Display followers/following counts

This builds naturally on the `profile_app` foundation we just created!

<!-- EOF -->
