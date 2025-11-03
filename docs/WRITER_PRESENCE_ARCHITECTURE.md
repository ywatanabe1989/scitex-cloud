# Writer Presence System Architecture

**Goal:** Show who's online and which section they're editing (non-intrusive awareness)

## Design Decision: Polling vs WebSocket

### Option A: Simple Polling (RECOMMENDED for MVP)
**How it works:**
- Frontend pings `/api/presence/update/` every 30s
- Backend updates `last_seen` timestamp
- Frontend fetches `/api/presence/list/` every 30s
- Display in UI

**Pros:**
- ✅ Works with existing Django setup (no Channels needed)
- ✅ Quick to implement
- ✅ Good enough for presence (30s delay acceptable)
- ✅ No Redis dependency in dev

**Cons:**
- ❌ Not true real-time (30s lag)
- ❌ More API calls at scale

### Option B: WebSocket (Future Enhancement)
**How it works:**
- Django Channels + Redis
- Persistent connection
- Instant updates

**Pros:**
- ✅ True real-time (<1s updates)
- ✅ Efficient at scale

**Cons:**
- ❌ Complex setup
- ❌ Requires Redis
- ❌ More infrastructure

**Decision:** Start with **Option A** (polling), upgrade to WebSocket later if needed.

---

## Implementation Plan

### Backend (Django)

**Model:**
```python
# apps/writer_app/models.py
class WriterPresence(models.Model):
    user = ForeignKey(User, on_delete=CASCADE)
    project = ForeignKey(Project, on_delete=CASCADE)
    current_section = CharField(max_length=100)  # e.g., "manuscript/abstract"
    last_seen = DateTimeField(auto_now=True)
    is_active = BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'project')
        indexes = [
            Index(fields=['project', 'is_active', 'last_seen'])
        ]
```

**API Endpoints:**
```python
# apps/writer_app/views/api_views.py

@require_http_methods(["POST"])
def presence_update(request, project_id):
    """
    Update user's presence in project

    POST body: {"section": "manuscript/abstract"}
    """
    WriterPresence.objects.update_or_create(
        user=request.user or get_visitor_user(request),
        project_id=project_id,
        defaults={
            'current_section': data['section'],
            'is_active': True
        }
    )
    return JsonResponse({'success': True})

@require_http_methods(["GET"])
def presence_list(request, project_id):
    """
    Get list of active users in project

    Returns: [
        {
            'user_id': 1,
            'username': 'alice',
            'section': 'manuscript/abstract',
            'last_seen': '2025-11-03T17:00:00Z',
            'avatar_color': '#4f46e5'
        }
    ]
    """
    active_threshold = timezone.now() - timedelta(minutes=2)
    presences = WriterPresence.objects.filter(
        project_id=project_id,
        is_active=True,
        last_seen__gte=active_threshold
    ).select_related('user')

    return JsonResponse({
        'success': True,
        'users': [
            {
                'user_id': p.user.id,
                'username': p.user.username,
                'section': p.current_section,
                'last_seen': p.last_seen.isoformat(),
                'avatar_color': get_user_color(p.user.id)
            }
            for p in presences
        ]
    })
```

### Frontend (JavaScript)

**Presence Manager:**
```javascript
// apps/writer_app/static/writer_app/js/writer-presence.js

export class PresenceManager {
    constructor(projectId, userId) {
        this.projectId = projectId;
        this.userId = userId;
        this.currentSection = null;
        this.updateInterval = null;
        this.fetchInterval = null;
        this.onlineUsers = [];
    }

    start() {
        // Update our presence every 30s
        this.updateInterval = setInterval(() => {
            this.updatePresence();
        }, 30000);

        // Fetch others' presence every 30s
        this.fetchInterval = setInterval(() => {
            this.fetchPresence();
        }, 30000);

        // Initial update
        this.updatePresence();
        this.fetchPresence();
    }

    async updatePresence() {
        if (!this.currentSection) return;

        await fetch(`/writer/api/project/${this.projectId}/presence/update/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                section: this.currentSection
            })
        });
    }

    async fetchPresence() {
        const response = await fetch(
            `/writer/api/project/${this.projectId}/presence/list/`
        );
        const data = await response.json();

        if (data.success) {
            this.onlineUsers = data.users.filter(u => u.user_id !== this.userId);
            this.updateUI();
        }
    }

    updateUI() {
        // Update section dropdown badge
        const badge = document.getElementById('presence-badge');
        if (badge && this.onlineUsers.length > 0) {
            badge.textContent = `📝 ${this.onlineUsers.length}`;
            badge.style.display = 'inline';
        }

        // Update tooltip with user list
        // TODO: Show "Alice (Abstract), Bob (Methods)" in dropdown
    }

    setSection(sectionId) {
        this.currentSection = sectionId;
        this.updatePresence(); // Immediate update on section change
    }

    stop() {
        clearInterval(this.updateInterval);
        clearInterval(this.fetchInterval);
    }
}
```

**Integration:**
```javascript
// In writer-init.js
import { PresenceManager } from './writer-presence.js';

// After editor initialized
const presenceManager = new PresenceManager(config.projectId, config.userId);
presenceManager.start();

// When section changes
presenceManager.setSection('manuscript/abstract');
```

### UI Design

**Section Dropdown Badge:**
```html
<select id="texfile-selector">
  <!-- Sections... -->
</select>
<span id="presence-badge" style="display:none; margin-left: 8px;">
  📝 3
</span>
```

**Dropdown Tooltip (on hover):**
```
Online (3):
• Alice (Abstract)
• Bob (Methods)
• Carol (Results)
```

**Conflict Warning (when entering occupied section):**
```
⚠️ Alice is editing this section
[Edit anyway] [Choose different section]
```

---

## Color Assignment

**Generate consistent color per user:**
```javascript
function getUserColor(userId) {
    const colors = [
        '#ef4444', '#f59e0b', '#10b981', '#3b82f6',
        '#6366f1', '#8b5cf6', '#ec4899', '#14b8a6'
    ];
    return colors[userId % colors.length];
}
```

**Usage:**
- Avatar border color
- Comment thread color
- Presence indicator color

---

## Implementation Steps

1. **Create Presence model + migration**
2. **Add API endpoints** (update, list)
3. **Create PresenceManager** (writer-presence.js)
4. **Integrate with writer-init.js**
5. **Add UI badges/tooltips**
6. **Test with multiple browser tabs**

---

## Testing Plan

**Test Scenarios:**
1. Open Writer in 2 browser tabs (different users)
2. User A edits Abstract → User B sees "User A (Abstract)"
3. User B enters Abstract → Warning appears
4. User A goes offline → Badge updates after 2min
5. Multiple sections occupied → All shown in tooltip

**Success Criteria:**
- ✅ Presence updates within 30s
- ✅ Users see each other
- ✅ Section conflicts detected
- ✅ UI is non-intrusive
- ✅ Works for visitors too

---

## Future Enhancements (WebSocket Migration)

When ready for real-time:
1. Install Django Channels
2. Create WebSocket consumer
3. Replace polling with WebSocket connection
4. Instant presence updates

**For now:** Polling is perfect for MVP!
