# Scholar App - TypeScript Modules Quick Reference

## Module Index

| Module | Purpose | Exported Functions | Usage |
|--------|---------|-------------------|--------|
| **init/swarm-plots-init.ts** | Initialize SwarmPlots visualization | `initializeSwarmPlots()` | Auto-initializes on DOM ready |
| **bibtex/job-detail-ui.ts** | BibTeX job detail UI | `initJobDetailUI()`, `copyLogToClipboard()`, `toggleLogSize()`, `pollJobStatus()` | Auto-initializes, requires `data-job-id` attribute |
| **shared/collapsible-panels.ts** | Generic collapsible panels | `initializeCollapsiblePanels()`, `togglePanel()`, `expandPanel()`, `collapsePanel()` | Auto-initializes, works with `.collapsible-header` class |
| **search/search-ui.ts** | Search result UI | `toggleAbstractMode()`, `handleSortChange()`, `openAllPaperUrls()` | Auto-initializes, exports to `window` for onclick |

## How to Use

### SwarmPlots Initialization

**Template Setup:**
```html
<!-- Keep Django config inline -->
<script>
  window.SCHOLAR_SEARCH_RESULTS = [
    {% for result in results %}
    { title: "...", year: ..., citations: ... }{% if not forloop.last %},{% endif %}
    {% endfor %}
  ];
</script>

<!-- Load module -->
<script src="{% static 'scholar_app/js/init/swarm-plots-init.js' %}"></script>
```

**Auto-initializes**: Waits for `window.SCHOLAR_SEARCH_RESULTS` and `window.SwarmPlots` module.

---

### Job Detail UI

**Template Setup:**
```html
<!-- Add data attributes to container -->
<div class="container"
     data-job-id="{{ job.id }}"
     data-job-status="{{ job.status }}"
     data-started-at="{% if job.started_at %}{{ job.started_at|date:'c' }}{% endif %}">

  <!-- Log viewer elements -->
  <pre id="processing-log">...</pre>
  <button id="copy-log-btn">Copy Log</button>
  <button id="toggle-log-size">Expand</button>
  <span id="elapsed-time">...</span>
</div>

<!-- Load module -->
<script src="{% static 'scholar_app/js/bibtex/job-detail-ui.js' %}"></script>
```

**Features:**
- Copy log to clipboard: Automatic visual feedback
- Expand/collapse log: 400px ↔ 800px
- Ctrl+A: Select only log content
- Real-time polling: Auto-updates job status every 2 seconds

---

### Collapsible Panels

**Template Setup:**
```html
<div class="collapsible-panel">
  <button class="collapsible-header" data-panel="example">
    <span>Panel Title</span>
    <i class="fas fa-chevron-down collapse-icon"></i>
  </button>
  <div class="collapsible-content" style="display: none; max-height: 0;">
    <div style="padding: 1.5rem;">
      Panel content here...
    </div>
  </div>
</div>

<!-- Load module -->
<script src="{% static 'scholar_app/js/shared/collapsible-panels.js' %}"></script>
```

**CSS (already in template):**
```css
.collapsible-header.expanded {
  background: var(--scitex-color-04) !important;
}

.collapsible-header.expanded ~ .collapsible-content {
  display: block !important;
  max-height: 1000px !important;
}

.collapsible-header.expanded .collapse-icon {
  transform: rotate(180deg);
}
```

---

### Search UI

**Template Setup:**
```html
<!-- Result cards with data attributes -->
<div class="result-card"
     data-year="{{ result.year }}"
     data-citations="{{ result.citations }}"
     data-impact-factor="{{ result.impact_factor }}"
     data-url="{{ result.url }}">

  <!-- Abstract with toggle buttons -->
  <div class="abstract-preview" data-abstract-id="{{ result.id }}" data-mode="truncated">
    {{ result.abstract }}
  </div>

  <!-- Toggle buttons -->
  <button onclick="toggleAbstractMode(this, '{{ result.id }}', 'all')">Show Full</button>
  <button onclick="toggleAbstractMode(this, '{{ result.id }}', 'truncated')">Truncate</button>
  <button onclick="toggleAbstractMode(this, '{{ result.id }}', 'none')">Hide</button>
</div>

<!-- Sort dropdown -->
<select onchange="handleSortChange(this.value)">
  <option value="date_desc">Newest First</option>
  <option value="date_asc">Oldest First</option>
  <option value="citations">Most Cited</option>
  <option value="impact_factor">Highest Impact</option>
</select>

<!-- Load module -->
<script src="{% static 'scholar_app/js/search/search-ui.js' %}"></script>
```

**CSS for abstract modes:**
```css
.abstract-preview.mode-truncated {
  max-height: 100px;
  overflow: hidden;
}

.abstract-preview.mode-none {
  display: none;
}
```

## Console Debugging

All modules include detailed console logging:

```javascript
// SwarmPlots Init
[Swarm Plots Init] Starting initialization...
[Swarm Plots Init] Found 42 search results
[Swarm Plots Init] Attempt 1/3
[Swarm Plots Init] SwarmPlots module found, initializing...

// Job Detail UI
[Job Detail UI] Initializing...
[Job Detail UI] Job ID: abc123 Status: processing
[POLL-SCHOLAR] Attempt 0, Job ID: abc123
[POLL-SCHOLAR] Response status: 200
[POLL-SCHOLAR] Status: processing, Has log: true

// Collapsible Panels
[Collapsible Panels] Initializing all panels with selector: .collapsible-header
[Collapsible Panels] Found 5 panels
[Collapsible Panels] Expanding panel

// Search UI
[Search UI] Initializing...
[Search UI] Toggling abstract mode: paper-123 to all
[Search UI] Sorting results by: citations
[Search UI] Found 42 result cards
```

## Common Patterns

### Export Functions to Window
```typescript
// Make functions available globally for onclick handlers
declare global {
    interface Window {
        myFunction: (param: string) => void;
    }
}

window.myFunction = myFunction;
```

### Read Data from DOM
```typescript
const container = document.querySelector('[data-job-id]') as HTMLElement;
const jobId = container?.getAttribute('data-job-id');
```

### Auto-Initialize on DOM Ready
```typescript
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFunction);
} else {
    initFunction(); // DOM already loaded
}
```

### Poll API with Retry
```typescript
function pollData(attempts = 0, maxAttempts = 90): void {
    if (attempts > maxAttempts) return;

    fetch('/api/endpoint')
        .then(response => response.json())
        .then(data => {
            // Process data
            if (data.status !== 'completed') {
                setTimeout(() => pollData(attempts + 1), 2000);
            }
        })
        .catch(error => {
            const backoff = Math.min(5000 + (attempts * 1000), 10000);
            setTimeout(() => pollData(attempts + 1), backoff);
        });
}
```

## File Structure

```
apps/scholar_app/static/scholar_app/
├── ts/                          # TypeScript sources
│   ├── init/
│   │   └── swarm-plots-init.ts
│   ├── bibtex/
│   │   └── job-detail-ui.ts
│   ├── shared/
│   │   └── collapsible-panels.ts
│   └── search/
│       └── search-ui.ts
└── js/                          # Compiled JavaScript (auto-generated)
    ├── init/
    │   ├── swarm-plots-init.js
    │   ├── swarm-plots-init.js.map
    │   ├── swarm-plots-init.d.ts
    │   └── swarm-plots-init.d.ts.map
    ├── bibtex/
    │   └── job-detail-ui.* (same structure)
    ├── shared/
    │   └── collapsible-panels.* (same structure)
    └── search/
        └── search-ui.* (same structure)
```

## TypeScript Compilation

**Automatic (in Docker dev environment):**
- Watch mode runs in container: `tsc -p tsconfig.all.json --watch`
- Compiles on file save automatically
- Monitor: `tail -f logs/tsc-watch-all.log`

**Manual (if needed):**
```bash
make ENV=dev build-ts
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Function not found in onclick | Check function is exported to `window` object |
| Module not initializing | Check console logs, verify DOM elements exist |
| TypeScript not compiling | Check `logs/tsc-watch-all.log` for errors |
| Data attribute missing | Add `data-*` attributes to container element |
| Collapsible panel not working | Verify `.collapsible-header` class and icon with `.collapse-icon` |

## Best Practices

1. **Keep Django config inline**: Never extract Django template tags to TypeScript
2. **Use data attributes**: Pass dynamic values via `data-*` attributes
3. **Auto-initialize**: Modules should initialize automatically on DOM ready
4. **Export for onclick**: Functions used in onclick must be on `window` object
5. **Console logging**: Keep detailed logs for development debugging
6. **Null checks**: Always check `if (element)` before using DOM elements
7. **Type everything**: Use TypeScript types for all parameters and returns
8. **JSDoc comments**: Document all exported functions
