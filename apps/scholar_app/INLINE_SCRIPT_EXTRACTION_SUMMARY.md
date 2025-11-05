# Scholar App - Inline Script Extraction Summary

## Overview

Successfully extracted inline JavaScript logic from scholar_app templates to organized TypeScript modules. This improves code organization, maintainability, and reusability.

## Created TypeScript Modules

### 1. `/apps/scholar_app/static/scholar_app/ts/init/swarm-plots-init.ts`
- **Purpose**: Initialize SwarmPlots visualization with search results
- **Extracted from**: `scholar_search.html` (lines 78-94), `index.html` (lines 107-123)
- **Features**:
  - Waits for both DOM ready and SwarmPlots module availability
  - Retry mechanism with configurable attempts (default: 3)
  - Checks for `window.SCHOLAR_SEARCH_RESULTS` data
  - Console logging for debugging
- **Compiled to**: `/apps/scholar_app/static/scholar_app/js/init/swarm-plots-init.js`

### 2. `/apps/scholar_app/static/scholar_app/ts/bibtex/job-detail-ui.ts`
- **Purpose**: Handle BibTeX job detail page UI interactions
- **Extracted from**: `bibtex_job_detail.html` (lines 265-469)
- **Features**:
  - Copy log to clipboard with visual feedback
  - Expand/collapse log viewer (400px ↔ 800px)
  - Ctrl+A keyboard shortcut for log selection
  - Elapsed time tracking and display
  - Real-time job status polling with exponential backoff
  - Reads job data from `data-job-id` attribute
- **Compiled to**: `/apps/scholar_app/static/scholar_app/js/bibtex/job-detail-ui.js`

### 3. `/apps/scholar_app/static/scholar_app/ts/shared/collapsible-panels.ts`
- **Purpose**: Generic collapsible panel handler
- **Extracted from**: `bibtex_partials/enrich.html` (lines 336-373)
- **Features**:
  - Click to expand/collapse panels
  - Icon rotation animation (0° ↔ 180°)
  - MutationObserver for dynamic height recalculation
  - Smooth transitions with max-height
  - Export functions: `initializeCollapsiblePanels`, `expandPanel`, `collapsePanel`, `togglePanel`
- **Compiled to**: `/apps/scholar_app/static/scholar_app/js/shared/collapsible-panels.js`

### 4. `/apps/scholar_app/static/scholar_app/ts/search/search-ui.ts`
- **Purpose**: Handle search result UI interactions
- **Extracted from**: `search_partials/search.html` (lines 282-358)
- **Features**:
  - `toggleAbstractMode(button, paperId, mode)` - Toggle abstract display (all/truncated/none)
  - `handleSortChange(sortBy)` - Sort results by date/citations/impact factor
  - Functions exported to `window` object for onclick handlers
  - Client-side DOM manipulation for results
- **Compiled to**: `/apps/scholar_app/static/scholar_app/js/search/search-ui.js`

## Inline Scripts That Should Remain

The following inline scripts MUST stay in templates because they contain Django-generated configuration:

### 1. `scholar_bibtex.html` (lines 33-46)
```html
<script>
  window.SCHOLAR_CONFIG = {
    urls: {
      bibtexUpload: '{% url "scholar_app:bibtex_upload" %}',
      resourceStatus: '{% url "scholar_app:bibtex_resource_status" %}',
      scitexSearch: '{% url "scholar_app:api_scitex_search" %}',
      scitexCapabilities: '{% url "scholar_app:api_scitex_capabilities" %}'
    },
    user: {
      isAuthenticated: {% if user.is_authenticated %}true{% else %}false{% endif %}
    }
  };
</script>
```
**Reason**: Django URL template tags and user authentication state

### 2. `scholar_search.html` (lines 34-96)
```html
<script>
  window.SCHOLAR_CONFIG = { ... };
  window.userProjects = [{% for project in user_projects %}...{% endfor %}];
  window.currentProject = {% if current_project %}...{% endif %};
  window.SCHOLAR_SEARCH_RESULTS = [{% for result in results %}...{% endfor %}];
</script>
```
**Reason**: Django context variables, loops, and conditionals

### 3. `index.html` (lines 63-125)
Same as `scholar_search.html` - Django-generated configuration data

### 4. `search_filters_scitex_seekbar.html` (lines 142-145)
```html
<script>
console.log('[SciTeX Seekbar] Alternative filter template loaded');
console.log('[SciTeX Seekbar] Using SciTeX Seekbar component instead of noUiSlider');
</script>
```
**Decision**: Can be REMOVED or kept as debug info

## Template Updates Required

### 1. Update `bibtex_job_detail.html`

**Add data attributes to job container** (after line 25):
```html
<div class="container"
     style="max-width: 1000px; margin: 3rem auto; padding: 2rem;"
     data-job-id="{{ job.id }}"
     data-job-status="{{ job.status }}"
     data-started-at="{% if job.started_at %}{{ job.started_at|date:'c' }}{% endif %}">
```

**Add script tag** (in `{% block extra_js %}` or before `</body>`):
```html
<script src="{% static 'scholar_app/js/bibtex/job-detail-ui.js' %}"></script>
```

**Remove inline script** (lines 265-469):
Delete the entire `<script>` block containing:
- `const jobId = '{{ job.id }}';`
- `copyLogBtn.addEventListener(...)`
- `toggleLogSizeBtn.addEventListener(...)`
- `pollJobStatus()` function
- etc.

### 2. Update `bibtex_partials/enrich.html`

**Add script tag** (after line 296):
```html
<script src="{% static 'scholar_app/js/shared/collapsible-panels.js' %}"></script>
```

**Remove inline script** (lines 336-373):
Delete the `<script>` block that contains:
```javascript
document.addEventListener('DOMContentLoaded', function() {
  const headers = document.querySelectorAll('.collapsible-header');
  headers.forEach(header => { ... });
});
```

The module now auto-initializes on DOM ready.

### 3. Update `scholar_search.html`

**Add script tag** (in `{% block extra_js %}` after line 114):
```html
<script src="{% static 'scholar_app/js/init/swarm-plots-init.js' %}"></script>
```

**Update inline script** (lines 34-96):
- **KEEP** lines 34-75: Django config, userProjects, currentProject, SCHOLAR_SEARCH_RESULTS
- **REMOVE** lines 77-95: SwarmPlots initialization logic (the `document.addEventListener` block)

**Result**:
```html
<script>
  // Django template variables for JavaScript
  window.SCHOLAR_CONFIG = { ... };
  window.userProjects = [ ... ];
  window.currentProject = ...;

  {% if query and results %}
  window.SCHOLAR_SEARCH_RESULTS = [ ... ];
  {% endif %}
  // SwarmPlots initialization now handled by swarm-plots-init.js
</script>
```

### 4. Update `index.html`

**Add script tag** (in `{% block extra_js %}` after line 28):
```html
<script src="{% static 'scholar_app/js/init/swarm-plots-init.js' %}"></script>
```

**Update inline script** (lines 63-125):
- **KEEP** lines 63-104: Django config and data
- **REMOVE** lines 106-124: SwarmPlots initialization logic

### 5. Update `search_partials/search.html`

**Add script tag** (after line 279):
```html
<script src="{% static 'scholar_app/js/search/search-ui.js' %}"></script>
```

**Remove inline script** (lines 282-358):
Delete the entire `<script>` block containing:
- `function toggleAbstractMode(...)`
- `function handleSortChange(...)`

These functions are now exported to `window` object by the module and available for onclick handlers.

### 6. Optional: Remove debug script from `search_filters_scitex_seekbar.html`

**Remove lines 142-145**:
```html
<script>
console.log('[SciTeX Seekbar] Alternative filter template loaded');
console.log('[SciTeX Seekbar] Using SciTeX Seekbar component instead of noUiSlider');
</script>
```

## Benefits

1. **Code Organization**: Logic separated from templates into reusable modules
2. **Type Safety**: TypeScript provides type checking and IntelliSense
3. **Maintainability**: Easier to find and modify JavaScript logic
4. **Debugging**: Better stack traces and console.log statements
5. **Reusability**: Functions can be imported and used in other modules
6. **Testing**: TypeScript modules are easier to unit test
7. **Documentation**: JSDoc comments provide inline documentation

## Verification Steps

1. **Check compiled files exist**:
   ```bash
   ls -la apps/scholar_app/static/scholar_app/js/init/
   ls -la apps/scholar_app/static/scholar_app/js/bibtex/ | grep job-detail
   ls -la apps/scholar_app/static/scholar_app/js/shared/ | grep collapsible
   ls -la apps/scholar_app/static/scholar_app/js/search/ | grep search-ui
   ```

2. **Monitor TypeScript compilation**:
   ```bash
   tail -f logs/tsc-watch-all.log
   ```

3. **Test in browser**:
   - Visit http://127.0.0.1:8000/scholar/search/ and check SwarmPlots initialization
   - Visit http://127.0.0.1:8000/scholar/bibtex/ and test collapsible panels
   - Visit a job detail page and test log copying, expand/collapse
   - Test abstract toggling and result sorting

4. **Check console logs**:
   - Open browser DevTools → Console
   - Look for messages like:
     - `[Swarm Plots Init] Starting initialization...`
     - `[Job Detail UI] Initializing...`
     - `[Collapsible Panels] Initializing all panels...`
     - `[Search UI] Initializing...`

## TypeScript Compilation Status

All four TypeScript files compiled successfully:
- ✅ `swarm-plots-init.ts` → `swarm-plots-init.js`
- ✅ `job-detail-ui.ts` → `job-detail-ui.js`
- ✅ `collapsible-panels.ts` → `collapsible-panels.js`
- ✅ `search-ui.ts` → `search-ui.js`

TypeScript watch mode is running in Docker container and will auto-compile on file changes.

## Design Decisions

1. **Kept Django config inline**: All Django template tags, URL generation, and context variables remain in templates
2. **Used data attributes**: Job detail reads from `data-job-id` instead of inline variables
3. **Auto-initialization**: All modules auto-initialize on DOM ready
4. **Exported to window**: Functions used in onclick handlers are exported to `window` object
5. **Console logging**: All debug statements preserved for development
6. **Retry mechanisms**: SwarmPlots init uses retry logic for race conditions
7. **Error handling**: Try-catch blocks for clipboard API and fetch calls

## Next Steps

1. Update the 6 templates as documented above
2. Test all functionality in the browser
3. Remove old inline scripts after verifying new modules work
4. Consider extracting more inline scripts from other templates
5. Add unit tests for the TypeScript modules (optional)

## Notes

- The TypeScript watcher runs automatically in Docker dev environment
- Compilation happens in real-time when `.ts` files are modified
- Source maps are generated for debugging in browser DevTools
- Type declaration files (`.d.ts`) are generated for IDE support
