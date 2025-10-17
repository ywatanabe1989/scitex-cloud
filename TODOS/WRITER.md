<!-- ---
!-- Timestamp: 2025-10-17 19:58:50
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/WRITER.md
!-- --- -->

# SciTeX Writer - Improvement Roadmap

## Vision
Create a coordinated ecosystem for scientific writing that excels beyond Overleaf by integrating project management, real-time collaboration, AI assistance, and seamless coordination with Scholar/Code/Viz modules.

**Current Demo:** http://127.0.0.1:8000/ywatanabe1989/neurovista/?mode=writer
**Reference:** ./externals/overleaf

---

## Current Strengths (Already Better Than Overleaf)

✅ **Django 5.2 LTS** - Latest async support for real-time features (upgraded Oct 2025)
✅ **Project-centric design** - Manuscripts linked to research projects
✅ **Comprehensive models** - Version control, branches, merge requests already implemented
✅ **Modular structure** - Sections as separate .tex files (better for collaboration)
✅ **AI integration ready** - AIAssistanceLog model in place
✅ **Scholar integration** - Citation management with BibTeX enrichment
✅ **arXiv pipeline** - Automated submission validation and tracking
✅ **Advanced PDF viewer** - Collapsible outline, zoom, navigation (just implemented!)
✅ **Channels 4.3.1** - Latest WebSocket support for real-time collaboration

---

## Implementation Roadmap

### Phase 1: Real-Time Collaboration (PRIORITY: P0) 🚀
**Goal:** Enable multiple users to edit simultaneously with conflict-free updates
**Timeline:** 2-3 weeks | **Impact:** HIGH | **Effort:** Medium

**Prerequisites:** ✅ Django 5.2 LTS (enhanced async support) | ✅ Channels 4.3.1 installed

#### Sprint 1.1: WebSocket Infrastructure (Week 1) ✅ COMPLETED
- [x] Install Django Channels 4.x + Redis (✅ Channels 4.3.1 ready!)
- [x] Configure Redis channel layer in settings (✅ Already configured!)
- [x] Create `apps/writer_app/consumers.py` for WebSocket handling (✅ Implemented!)
- [x] Implement presence system (show who's online) (✅ Complete!)
- [x] Broadcast user join/leave events (✅ Working!)
- [x] Display active collaborators in sidebar (✅ UI added!)

**Technical (Django 5.2 async features):**
```python
# apps/writer_app/consumers.py
class WriterConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.manuscript_id = self.scope['url_route']['kwargs']['manuscript_id']
        self.room_group_name = f'manuscript_{self.manuscript_id}'

        # Django 5.2: Use async ORM for better performance
        self.manuscript = await Manuscript.objects.aget(id=self.manuscript_id)

        # Join room, broadcast presence
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
```

**UI Changes:**
- Add "👥 N collaborators online" indicator
- Show colored cursor/selection for each user
- "User X is editing Section Y" status

#### Sprint 1.2: Section Locking (Week 2) ✅ COMPLETED
- [x] Implement section-level locks (stored in `CollaborativeSession.locked_sections`)
- [x] Show lock indicators in UI (🔒 icon on section cards)
- [x] Auto-release locks on disconnect (✅ Implemented!)
- [x] Handle lock timeouts (5 min inactivity via session.is_session_active())
- [x] Disable editor for locked sections
- [x] Visual feedback with border colors and opacity

#### Sprint 1.3: Basic Change Broadcasting (Week 2-3) ✅ COMPLETED
- [x] Broadcast text insertions/deletions (✅ Full text sync!)
- [x] Debounce updates (500ms after typing stops)
- [x] Handle network reconnection (✅ Exponential backoff!)
- [x] Show "Syncing..." indicator (✅ Status in save-status!)
- [x] Apply remote changes intelligently (skip if user editing)
- [x] Auto-enable on WebSocket connection

**Metrics:**
- ✅ Latency < 500ms for change propagation (debounced)
- ✅ Supports unlimited concurrent users (Redis-backed)
- ✅ Auto-reconnection with exponential backoff
- ✅ Section-level conflict prevention via locking

**Status:** Phase 1 Real-Time Collaboration MVP - COMPLETE! 🎉

---

### Phase 2: Operational Transforms (PRIORITY: P0) 🔄
**Goal:** Conflict-free concurrent editing
**Timeline:** 2-3 weeks | **Impact:** HIGH | **Effort:** High

#### Sprint 2.1: OT Implementation (Week 1-2)
- [ ] Research OT algorithms (ShareJS, OT.js)
- [ ] Implement text operation types (insert, delete, retain)
- [ ] Vector clock for causality tracking
- [ ] Transform function for concurrent operations

**Algorithm:**
```javascript
// Client-side OT
function transform(op1, op2) {
    // Transform op1 against op2
    // Return transformed operation
}
```

#### Sprint 2.2: Server-Side Coordination (Week 2-3)
- [ ] Central authority for operation ordering
- [ ] Operation queue per manuscript
- [ ] Acknowledgment system
- [ ] Retry logic for failed operations

#### Sprint 2.3: Undo/Redo (Week 3)
- [ ] Per-user undo stack
- [ ] Transform undo operations
- [ ] Redo after undo

**Models used:**
- `DocumentChange.operation_data` - Store OT operations ✅
- `DocumentChange.transform_applied` - Track transformation ✅

---

### Phase 3: Track Changes (PRIORITY: P1) 📝
**Goal:** Visual change tracking with review workflow
**Timeline:** 2 weeks | **Impact:** HIGH | **Effort:** Medium

#### Sprint 3.1: Visual Change Indicators (Week 1)
- [ ] Highlight insertions (green) and deletions (red strikethrough)
- [ ] Show change author and timestamp on hover
- [ ] Filter view: "Show all changes" / "Hide accepted"
- [ ] Change timeline/history panel

**UI Design:**
```
┌─────────────────────────────────────┐
│ Abstract - LaTeX                    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ This paper presents ⁺⁺⁺new⁺⁺⁺ results│
│                      ▲              │
│                   Alice, 2h ago     │
└─────────────────────────────────────┘
```

#### Sprint 3.2: Review Workflow (Week 2)
- [ ] Accept/reject buttons for each change
- [ ] Bulk accept/reject for sections
- [ ] Reviewer assignment
- [ ] Comment threads on changes

**New Model:**
```python
class ChangeComment(models.Model):
    change = ForeignKey(DocumentChange)
    user = ForeignKey(User)
    comment = TextField()
    created_at = DateTimeField()
```

#### Sprint 3.3: Change Export
- [ ] Export changes as LaTeX diff PDF
- [ ] Generate change summary report
- [ ] Track changes statistics per user

---

### Phase 4: AI Writing Assistant (PRIORITY: P1) 🤖
**Goal:** AI-powered writing enhancement
**Timeline:** 2-3 weeks | **Impact:** HIGH (Differentiator) | **Effort:** Medium

#### Sprint 4.1: Context-Aware Suggestions (Week 1)
- [ ] Analyze section context (introduction vs methods)
- [ ] Grammar and clarity improvements
- [ ] Academic style enforcement
- [ ] Suggest transitions between sections

**Integration:**
```python
# Use existing AIAssistanceLog model
def get_ai_suggestion(section_content, section_type, target='clarity'):
    # Call Claude/GPT with context
    # Log in AIAssistanceLog
    # Return suggestions
```

#### Sprint 4.2: Content Generation (Week 2)
- [ ] "Expand this to N words" feature
- [ ] Abstract generation from full paper
- [ ] Introduction from Methods+Results
- [ ] Discussion suggestions from Results

#### Sprint 4.3: Citation Intelligence (Week 2-3)
- [ ] Suggest citations while writing
- [ ] "This claim needs a citation" detection
- [ ] Find relevant papers from Scholar
- [ ] Auto-generate BibTeX from paper titles

**Scholar Integration:**
- Query Scholar module for relevant papers
- Use paper embeddings for relevance matching
- Suggest citations based on context

---

### Phase 5: Scholar Coordination (PRIORITY: P1) 📚
**Goal:** Seamless bibliography management
**Timeline:** 2 weeks | **Impact:** MEDIUM-HIGH | **Effort:** Low-Medium

#### Sprint 5.1: Citation Workflow (Week 1)
- [ ] "Insert citation" button → opens Scholar search
- [ ] Drag-drop from Scholar library → auto-insert `\cite{key}`
- [ ] Show citation context in hover preview
- [ ] Detect unused citations in .bib file

**UI Flow:**
```
User clicks "Cite" → Scholar sidebar opens →
Select paper → Auto-adds to references.bib →
Inserts \cite{author2024} in text
```

#### Sprint 5.2: Smart BibTeX Management (Week 2)
- [ ] Auto-fetch BibTeX from DOI/arXiv ID
- [ ] Detect duplicate entries
- [ ] Normalize author names
- [ ] Update stale entries (journal name changes, etc.)

#### Sprint 5.3: Citation Analytics
- [ ] Citation graph (which papers cite each other)
- [ ] Most-cited papers in your manuscript
- [ ] Missing citations detection
- [ ] Citation style preview (APA, Chicago, Nature)

---

### Phase 6: Enhanced Compilation & Preview (PRIORITY: P2)
**Goal:** Better compilation experience
**Timeline:** 2 weeks | **Impact:** MEDIUM | **Effort:** Medium

#### Sprint 6.1: Multi-Engine Support (Week 1)
- [ ] Support XeLaTeX, LuaLaTeX, pdfLaTeX
- [ ] Draft mode (skip figure rendering for speed)
- [ ] Continuous compilation (auto-compile on save)
- [ ] Compilation queue for multiple jobs

#### Sprint 6.2: Error Handling (Week 1-2)
- [ ] Parse LaTeX error logs
- [ ] Highlight error lines in editor
- [ ] "Jump to error" button
- [ ] Suggest fixes for common errors

#### Sprint 6.3: Live Preview Enhancements (Week 2)
- [ ] Scroll sync: LaTeX line ↔ PDF position
- [ ] Click on PDF → jump to LaTeX source
- [ ] Show compilation progress with detailed steps
- [ ] Preview without full compilation (partial rendering)

---

### Phase 7: Word/Markdown Conversion (PRIORITY: P2)
**Goal:** Accessibility for non-LaTeX users
**Timeline:** 3 weeks | **Impact:** MEDIUM | **Effort:** High

#### Sprint 7.1: Import Pipeline (Week 1-2)
- [ ] DOCX upload and parsing (pypandoc)
- [ ] Preserve formatting (bold, italic, headings)
- [ ] Handle equations (MathML → LaTeX)
- [ ] Extract figures and tables
- [ ] Markdown import with frontmatter

#### Sprint 7.2: Export Pipeline (Week 2-3)
- [ ] LaTeX → DOCX with formatting
- [ ] Figure embedding in Word doc
- [ ] Bibliography formatting
- [ ] Template selection for export style

#### Sprint 7.3: Hybrid Editor (Week 3)
- [ ] Rich text mode toggle
- [ ] Preview LaTeX while editing in rich text
- [ ] Smart LaTeX code completion
- [ ] Equation editor UI

---

## Key Architectural Decisions

### 1. WebSocket vs HTTP Polling?
**Decision:** WebSocket (Django Channels 4.3.1)
- ✅ Lower latency for real-time updates
- ✅ Industry standard for collaboration
- ✅ Scalable with Redis backend
- ✅ Django 5.2 async ORM support (`.aget()`, `.filter().aiterator()`)

### 2. Operational Transforms vs CRDTs?
**Decision:** Operational Transforms
- Better understood, more libraries
- Overleaf uses OT (proven at scale)
- Easier to debug
- Django 5.2: Async transactions for atomic OT operations

### 3. Client-Side vs Server-Side OT?
**Decision:** Hybrid
- Client predicts changes (optimistic UI)
- Server is source of truth (Django 5.2 async views)
- Server resolves conflicts

### 4. File Storage: Database vs Filesystem?
**Current:** Filesystem (paper/ directory) ✅
**Keep it** - Easier for Git integration, backups, external tools
- Django 5.2: Better async file I/O support

### 5. Django 5.2 Specific Advantages
**Async ORM:**
- `await Manuscript.objects.aget(id=x)` - Non-blocking DB queries
- `async for change in DocumentChange.objects.filter(...).aiterator()` - Stream changes
- `await manuscript.asave()` - Async saves for WebSocket handlers

**Performance:**
- Improved QuerySet performance (15-20% faster in benchmarks)
- Better connection pooling
- Optimized template rendering

**New Features:**
- `db_default` for model fields (database-level defaults)
- Enhanced JSON field operations
- Better async middleware support

---

## Success Metrics

### User Engagement
- Concurrent users per manuscript > 3
- Session duration > 30 min
- Collaboration invites sent > 50%

### Feature Adoption
- Track changes usage > 70% of documents
- AI suggestions accepted > 40%
- Scholar citations imported > 60%

### Performance
- WebSocket latency < 200ms
- Compilation time < 30s
- Change sync < 500ms

### Competitive Advantage
- Feature parity with Overleaf Pro (free tier)
- Unique: AI + Scholar + Code + Viz integration
- Faster citation workflow than Overleaf

---

## Next Steps

**Immediate (This Week):**
1. ✅ Upgrade to Django 5.2 LTS (DONE!)
2. ✅ Install Channels 4.3.1 (DONE!)
3. Configure Redis channel layer in settings
4. Create basic WebSocket consumer with Django 5.2 async ORM
5. Implement presence broadcasting

**Short-term (Month 1):**
1. Complete real-time collaboration MVP
2. Add section locking
3. Basic change broadcasting

**Medium-term (Month 2-3):**
1. Operational transforms
2. Track changes UI
3. AI writing assistant integration

**Long-term (Month 4-6):**
1. Scholar citation workflow
2. Word conversion
3. Advanced compilation features

---

## Resources Needed

**Infrastructure:**
- Redis server (for Channels)
- Increased server resources for WebSocket connections
- CDN for static assets (optional)

**External Services:**
- OpenAI/Anthropic API for AI features
- arXiv API credentials
- DOI resolution service

**Development:**
- Frontend: WebSocket client, rich text editor
- Backend: Django Channels, OT algorithm
- Testing: Multi-user testing framework

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| OT bugs causing data loss | HIGH | Extensive testing, operation logging, version snapshots |
| WebSocket scaling issues | MEDIUM | Redis cluster, connection limits per manuscript |
| AI costs | MEDIUM | Rate limiting, caching, user quotas |
| Compilation security | HIGH | Sandboxed compilation (Docker), file size limits |
| Real-time sync conflicts | MEDIUM | Well-tested OT algorithm, conflict UI |

---

### Writing/Collaboration system integrations
see ./INTEGRATIONS.md
see ./PERMISSIONS_SYSTEM.md

- [ ] Email Guest
  - [ ] see ./GUEST_COLLABORATORS.md
  - [ ] see ./PERMISSIONS_SYSTEM.md

<!-- EOF -->