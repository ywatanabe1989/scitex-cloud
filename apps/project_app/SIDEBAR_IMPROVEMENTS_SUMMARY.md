# Project Sidebar Improvements - GitHub Style

## Summary
Improved the project sidebar to match GitHub's design with:
1. Sidebar folds by default (collapsible)
2. Increased sidebar size when expanded (420px instead of 296px)
3. Enhanced hover effects with color responsiveness
4. Added inline "About" panel with project metadata

## Files Modified

### 1. `/home/ywatanabe/proj/scitex-cloud/apps/project_app/templates/project_app/project_detail.html`

#### Changes Made:

#### A. Grid Layout (Lines 322-357)
```css
/* Changed from 296px default to 48px collapsed by default */
.repo-layout {
    grid-template-columns: 48px 1fr;  /* Start collapsed */
}

.repo-layout.sidebar-expanded {
    grid-template-columns: 420px 1fr;  /* Larger expanded width (was 380px) */
}

.repo-sidebar {
    width: 48px;  /* Start collapsed */
}

.repo-sidebar.expanded {
    width: 420px;  /* Larger width for better readability */
}
```

#### B. Enhanced Hover Effects (Lines 465-505)
```css
.sidebar-item {
    border-radius: 6px;  /* Increased from 4px */
    cursor: pointer;  /* Added */
}

.sidebar-item:hover {
    background: var(--color-accent-subtle);  /* Changed from canvas-subtle */
    color: var(--color-accent-fg);  /* Changed from fg-default */
    transform: translateX(2px);  /* Added movement */
}

.sidebar-link {
    padding: 8px 12px;  /* Increased from 6px 8px */
    border-radius: 6px;  /* Increased from 4px */
    font-weight: 500;  /* Added */
}

.sidebar-link:hover {
    background: var(--color-accent-subtle);  /* Changed */
    transform: translateX(4px);  /* More pronounced movement */
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);  /* Added shadow */
}
```

#### C. File Tree Styling (Lines 521-568)
```css
.file-tree-item {
    padding: 6px 8px;  /* Increased from 4px 6px */
    border-radius: 6px;  /* Increased from 4px */
    margin: 2px 0;  /* Increased from 1px */
}

.file-tree-item:hover {
    background: var(--color-accent-subtle);  /* Changed */
    transform: translateX(2px);  /* Added */
}

.file-tree-item.active {
    background: var(--color-accent-emphasis);  /* More prominent */
    color: #ffffff;  /* White text on active */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);  /* Added shadow */
}

.file-tree-folder {
    gap: 6px;  /* Increased from 4px */
    font-weight: 500;  /* Added */
}

.file-tree-folder:hover {
    transform: translateX(3px);  /* Increased from 2px */
}

.file-tree-file {
    gap: 6px;  /* Increased from 4px */
}

.file-tree-file:hover {
    transform: translateX(3px);  /* Increased from 2px */
}
```

#### D. Sidebar HTML Structure (Lines 850-900)
```html
<!-- Changed toggle button icon and default state -->
<button class="sidebar-toggle-btn" onclick="toggleSidebar()" title="Expand sidebar">
    <span class="sidebar-toggle-icon">▶</span>  <!-- Changed from ◀ -->
</button>

<!-- Increased font size -->
<div id="file-tree" style="font-size: 13px;">  <!-- Was 12px -->
    ...
</div>

<!-- Enhanced About section with stats -->
<div class="sidebar-content">
    <p style="font-size: 13px; line-height: 1.5;">  <!-- Added line-height -->
        {{ project.description }}
    </p>

    <!-- Added stats -->
    <div class="sidebar-item">
        <i class="fas fa-star"></i>
        <span id="sidebar-star-count">0 stars</span>
    </div>
    <div class="sidebar-item">
        <i class="fas fa-code-branch"></i>
        <span id="sidebar-fork-count">0 forks</span>
    </div>

    <!-- Existing items... -->
</div>
```

#### E. JavaScript Updates (Lines 1014-1102)

**initializeSidebar() function:**
```javascript
function initializeSidebar() {
    const toggleBtn = document.getElementById('sidebar-toggle');

    // Always start collapsed
    sidebar.classList.add('collapsed');
    repoLayout.classList.add('sidebar-collapsed');
    toggleBtn.setAttribute('title', 'Expand sidebar');  // Added

    // Rest of function...
}
```

**toggleSidebar() function:**
```javascript
function toggleSidebar() {
    const toggleBtn = document.getElementById('sidebar-toggle');

    if (sidebar.classList.contains('collapsed')) {
        // Expand
        toggleBtn.setAttribute('title', 'Collapse sidebar');  // Added
    } else {
        // Collapse
        toggleBtn.setAttribute('title', 'Expand sidebar');  // Added
    }
}
```

**loadProjectStats() function:**
```javascript
async function loadProjectStats() {
    // ... existing code ...

    // Update sidebar counts (ADDED)
    const sidebarStarCount = document.getElementById('sidebar-star-count');
    const sidebarForkCount = document.getElementById('sidebar-fork-count');
    if (sidebarStarCount) {
        sidebarStarCount.textContent = `${data.stats.star_count} ${data.stats.star_count === 1 ? 'star' : 'stars'}`;
    }
    if (sidebarForkCount) {
        sidebarForkCount.textContent = `${data.stats.fork_count} ${data.stats.fork_count === 1 ? 'fork' : 'forks'}`;
    }
}
```

## Key Features Implemented

### 1. Collapsed by Default
- Sidebar starts at 48px width
- Only shows toggle button when collapsed
- Mimics GitHub's approach of hiding sidebar initially

### 2. Larger Expanded Size
- Expanded width: 420px (up from 296px/380px)
- Better readability for file names and paths
- More comfortable spacing

### 3. Enhanced Hover Effects
- Color changes to accent color on hover
- Smooth transform animations (translateX)
- Box shadows for depth
- Increased border radius (6px) for modern look

### 4. Inline About Panel
- Moved metadata to collapsible About section
- Added star and fork counts
- Better organization of project information
- Syncs with header stats

## Color Responsiveness

All hover states now use:
- `var(--color-accent-subtle)` for background
- `var(--color-accent-fg)` for text
- Smooth transitions (0.2s ease)
- Transform effects for visual feedback

## Responsive Behavior

- Mobile: Sidebar hidden by default
- Desktop: Sidebar collapsed to 48px by default
- User can expand/collapse with toggle button
- State persists in localStorage

## User Experience Improvements

1. **Visual Feedback**: Clear hover states with color and movement
2. **Better Spacing**: Increased padding and margins
3. **Larger Click Targets**: Better touch/click accessibility
4. **Smooth Animations**: All transitions use CSS transitions
5. **State Persistence**: Remembers user's sidebar preference
6. **Tooltip Hints**: Toggle button shows "Expand/Collapse sidebar"

## Testing Recommendations

1. Test sidebar toggle functionality
2. Verify hover effects work in both light/dark modes
3. Check responsive behavior on mobile devices
4. Ensure file tree loads correctly
5. Verify stats synchronization between header and sidebar
6. Test section collapse/expand within sidebar
7. Verify localStorage persistence across page reloads

## Future Enhancements

1. Add keyboard shortcuts (e.g., Ctrl+B to toggle sidebar)
2. Add resizable sidebar (drag to resize)
3. Add search within file tree
4. Add recent files section
5. Add project tags/topics to About section
