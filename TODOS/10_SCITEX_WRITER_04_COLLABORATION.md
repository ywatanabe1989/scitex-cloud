<!-- ---
!-- Timestamp: 2025-11-03 17:45:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/10_SCITEX_WRITER_04_COLLABORATION.md
!-- --- -->

# Writer - Collaboration Vision

## Design Philosophy

**Core Principle:** Enable collaboration without disrupting individual focus

**For scientific writing:**
- ✅ Asynchronous by default (respects timezones, schedules)
- ✅ Review-based workflow (verify before accepting)
- ✅ Clear attribution (who contributed what)
- ✅ Discussion support (debate claims, wording)
- ❌ No live cursors (too distracting)
- ❌ No forced real-time sync (preserve focus)

## Features

### Tier 1: Awareness (Non-Intrusive)
- [ ] Presence indicators
  - [ ] Online badge in dropdown: `📝 3`
  - [ ] Show: "Alice (Abstract), Bob (Methods)"
  - [ ] User avatars + unique colors
  - [ ] Section conflict warning

### Tier 2: Async Collaboration
- [ ] Change notifications
  - [ ] "New changes available" badge
  - [ ] Pull manually
  - [ ] Review before accepting
  
- [ ] Comments system
  - [ ] Select text → add comment
  - [ ] Threaded discussions
  - [ ] Resolve/reopen
  - [ ] Keyboard: Ctrl+/, Ctrl+Shift+/

### Tier 3: Enhanced
- [ ] Voice comments (async audio notes)
- [ ] Guest collaborators (email-only, no account)
- [ ] Video integration (link to Meet/Zoom)

## What NOT to Build
- ❌ Built-in video conferencing
- ❌ Real-time cursors
- ❌ Instant messaging

<!-- EOF -->
