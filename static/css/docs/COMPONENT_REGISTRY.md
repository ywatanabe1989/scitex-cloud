# SciTeX UI Component Registry

**Last Updated:** 2025-10-21
**Status:** In Development (Phase 1: ~50% complete)
**Purpose:** Centralized inventory of all SciTeX UI components with API documentation

---

## Quick Stats

**Overall Coverage:**
- ✅ Fully Implemented: ~35 components (29%)
- ⚠️ Partially Implemented: ~20 components (17%)
- ❌ Missing: ~65 components (54%)

**Dark Mode Coverage (Existing Components):**
- ✅ Full Support: Forms, Checkboxes, Header, Footer, Hero
- ⚠️ Partial Support: Radios, Toggles, Buttons, Cards
- ❌ No Support: Many missing components

**CRITICAL REQUIREMENT:**
> All new components MUST include both light and dark mode from day one. Dark mode is not optional.

**Related Documentation:**
- See `COMPONENT_GAP_ANALYSIS.md` for detailed coverage analysis
- See `UI_COMPONENT_IDEAL_LIST.md` for complete component hierarchy
- See `REFACTOR_PLAN.md` for implementation roadmap

---

## Table of Contents

1. [Form Components](#form-components)
2. [Button Components](#button-components)
3. [Layout Components](#layout-components)
4. [Feedback Components](#feedback-components)
5. [Navigation Components](#navigation-components)
6. [Data Display Components](#data-display-components)
7. [Missing Components](#missing-components)

---

## Form Components

### Input Fields

**File:** `/static/css/common/forms.css`
**Dark Mode:** ✅ Full support

**Base Classes:**
```html
<input type="text" class="form-control" placeholder="Enter text">
```

**Variants:**
- `.form-control-sm` - Small size
- `.form-control-lg` - Large size
- `.is-valid` - Success state (green border)
- `.is-invalid` - Error state (red border)

**Dark Mode Behavior:**
- Background: `var(--scitex-color-01-light)` (dark bluish)
- Text: `var(--scitex-color-06)` (pale bluish)
- Border: `var(--scitex-color-03)` (medium bluish)
- Focus: Bluish glow effect

**Usage Example:**
```html
<div class="form-group">
  <label for="username" class="form-label">Username</label>
  <input type="text" id="username" class="form-control" placeholder="Enter username">
</div>
```

---

### Checkboxes (Custom)

**File:** `/static/css/common/checkbox.css`
**Dark Mode:** ✅ Full support

**Structure:**
```html
<div class="scitex-checkbox-wrapper">
  <input type="checkbox" id="option1" class="scitex-checkbox">
  <label for="option1" class="scitex-checkbox-label">Option 1</label>
</div>
```

**Component Classes:**
- `.scitex-checkbox` - Hidden native checkbox input
- `.scitex-checkbox-label` - Custom styled label with visual checkbox
- `.scitex-checkbox-wrapper` - Optional wrapper for positioning

**States:**
- Default (unchecked)
- Checked (with checkmark icon)
- Hover (background highlight)
- Disabled (opacity reduced)

**Dark Mode Features:**
- Label text: `var(--scitex-color-06)` (bluish pale gray)
- Checkbox border: `var(--scitex-color-04)` (lighter bluish)
- Checked background: `var(--scitex-color-04)` (bluish accent)
- Hover background: `var(--scitex-color-01)` (dark bluish)

**Visual:**
- Checkbox size: 18px × 18px
- Border radius: 4px
- Margin right: 0.5rem
- Checkmark: SVG inline (white)

---

### Radio Buttons (Segmented Control)

**File:** `/static/css/common/radios.css`
**Dark Mode:** ⚠️ Partial (needs enhancement)

**Structure:**
```html
<div class="scitex-radio-group">
  <input type="radio" id="opt1" name="group" class="scitex-radio">
  <label for="opt1" class="scitex-radio-label">Option 1</label>

  <input type="radio" id="opt2" name="group" class="scitex-radio">
  <label for="opt2" class="scitex-radio-label">Option 2</label>
</div>
```

**Component Classes:**
- `.scitex-radio` - Hidden native radio input
- `.scitex-radio-label` - Button-like label
- `.scitex-radio-group` - Container (segmented control)

**Variants:**
- `.scitex-radio-group-sm` - Smaller size

**States:**
- Default (unchecked) - White background
- Checked - Primary color background, white text
- Hover (unchecked) - Light gray background
- Hover (checked) - Secondary color background

**Responsive:**
- Mobile (<768px): Stacks vertically
- Desktop: Horizontal segmented control

---

### Toggle Switches

**File:** `/static/css/common/toggles.css`
**Dark Mode:** ⚠️ Partial (needs enhancement)

**Structure:**
```html
<div class="scitex-toggle-wrapper">
  <input type="checkbox" id="toggle1" class="scitex-toggle">
  <label for="toggle1" class="scitex-toggle-label">Toggle Option</label>
</div>
```

**Component Classes:**
- `.scitex-toggle` - Hidden checkbox input
- `.scitex-toggle-label` - Button-like toggle label
- `.scitex-toggle-wrapper` - Optional wrapper

**States:**
- Off (unchecked) - White background, bordered
- On (checked) - Primary color background, white text
- Hover (off) - Border highlighted, light background
- Hover (on) - Secondary color background

**Styling:**
- Min width: 80px
- Padding: 0.375rem 0.75rem
- Border radius: 6px

---

### Select Dropdowns

**File:** `/static/css/common/forms.css`
**Dark Mode:** ✅ Full support

**Base Classes:**
```html
<select class="form-control">
  <option>Option 1</option>
  <option>Option 2</option>
</select>
```

**Features:**
- Custom dropdown arrow (SVG)
- Removes default browser styling (`appearance: none`)
- Dark mode: Arrow color changes to bluish

---

## Button Components

### Standard Buttons

**File:** `/static/css/common/buttons.css` + `/static/css/common/scitex-components.css`
**Dark Mode:** ⚠️ Needs dark mode variants

**Base Classes:**
```html
<button class="scitex-btn-primary">Primary Button</button>
<button class="scitex-btn-secondary">Secondary Button</button>
```

**Variants:**
- `.scitex-btn-primary` - Filled primary color
- `.scitex-btn-secondary` - Outlined, transparent background
- `.scitex-btn-sm` - Small size
- `.scitex-btn-lg` - Large size

**States:**
- Default
- Hover - Slight lift animation (translateY -1px), shadow
- Active - Returns to original position
- Disabled (needs implementation)

**Primary Button:**
- Background: `var(--primary-color)` (#1a2332)
- Hover: `var(--secondary-color)` (#34495e)
- Color: White
- Shadow: `0 4px 8px rgba(26, 35, 50, 0.2)`

**Secondary Button:**
- Background: Transparent
- Border: `var(--primary-color)`
- Hover: Fills with `var(--primary-color)`, text becomes white

---

### Badges

**File:** `/static/css/common/buttons.css`
**Dark Mode:** ❌ Not implemented
**Status:** Mentioned but needs verification of implementation

---

## Layout Components

### Cards

**File:** `/static/css/common/cards.css`
**Dark Mode:** ⚠️ Needs verification

**Status:** Basic card system exists, needs full documentation

**Expected Structure:**
```html
<div class="scitex-card">
  <div class="scitex-card-header">Header</div>
  <div class="scitex-card-body">Content</div>
  <div class="scitex-card-footer">Footer</div>
</div>
```

**TODO:** Document actual classes and variants

---

### Dropdowns

**File:** `/static/css/components/dropdown.css`
**Dark Mode:** ❌ Unknown

**TODO:** Document structure and usage

---

### Header

**File:** `/static/css/components/header.css`
**Dark Mode:** ✅ Implemented (needs documentation)

**Purpose:** Main site navigation header

---

### Footer

**File:** `/static/css/components/footer.css`
**Dark Mode:** ✅ Implemented (needs documentation)

**Purpose:** Site footer with links and social icons

---

### Hero Section

**File:** `/static/css/components/hero.css`
**Dark Mode:** ✅ Implemented

**Purpose:** Landing page hero banners

---

## Feedback Components

### Alerts

**Status:** ⚠️ **Mentioned in design system but CSS location unclear**
**Dark Mode:** ❌ Unknown

**TODO:**
1. Locate or create alert component CSS
2. Document alert variants (success, warning, error, info)
3. Add dark mode support

**Expected Variants:**
- `.alert-success` - Green
- `.alert-warning` - Yellow/Orange
- `.alert-error` - Red
- `.alert-info` - Blue

---

## Navigation Components

### Navigation Bar (Reusable)

**Status:** ❌ **Missing**
**Current:** Only header.css exists (not a reusable component)

**Needed Features:**
- Horizontal navigation
- Vertical navigation (sidebar)
- Mobile hamburger menu
- Dropdown submenus
- Active state indicators

---

### Breadcrumbs

**Status:** ❌ **Missing**

**Expected Structure:**
```html
<nav class="scitex-breadcrumb">
  <a href="/">Home</a>
  <span class="separator">/</span>
  <a href="/products">Products</a>
  <span class="separator">/</span>
  <span class="current">Item</span>
</nav>
```

---

### Tabs

**Status:** ❌ **Missing**

**Expected Structure:**
```html
<div class="scitex-tabs">
  <div class="scitex-tab-list">
    <button class="scitex-tab active">Tab 1</button>
    <button class="scitex-tab">Tab 2</button>
  </div>
  <div class="scitex-tab-panel active">Panel 1 content</div>
  <div class="scitex-tab-panel">Panel 2 content</div>
</div>
```

---

### Pagination

**Status:** ❌ **Missing**

**Expected Structure:**
```html
<nav class="scitex-pagination">
  <button class="prev">Previous</button>
  <button class="page active">1</button>
  <button class="page">2</button>
  <button class="page">3</button>
  <button class="next">Next</button>
</nav>
```

---

## Data Display Components

### Tables

**Status:** ❌ **Missing**

**Needed Features:**
- Basic table styling
- Striped rows
- Hoverable rows
- Sortable headers
- Responsive (horizontal scroll on mobile)
- Dark mode support

---

### List Groups

**Status:** ❌ **Missing**

**Expected Structure:**
```html
<ul class="scitex-list-group">
  <li class="scitex-list-item">Item 1</li>
  <li class="scitex-list-item active">Item 2</li>
  <li class="scitex-list-item">Item 3</li>
</ul>
```

---

## Interactive Components

### Modal/Dialog

**Status:** ❌ **Missing**

**Expected Structure:**
```html
<div class="scitex-modal">
  <div class="scitex-modal-overlay"></div>
  <div class="scitex-modal-container">
    <div class="scitex-modal-header">
      <h3>Title</h3>
      <button class="close">×</button>
    </div>
    <div class="scitex-modal-body">Content</div>
    <div class="scitex-modal-footer">
      <button>Cancel</button>
      <button>Confirm</button>
    </div>
  </div>
</div>
```

**Required Features:**
- Backdrop/overlay
- Focus trap
- ESC key to close
- Click outside to close
- Scroll lock on body

---

### Tooltips

**Status:** ❌ **Missing**

**Expected Features:**
- Positioning (top, right, bottom, left)
- Arrow pointer
- Show on hover
- Dark mode variants

---

### Accordion/Collapsible

**Status:** ❌ **Missing**

**Expected Structure:**
```html
<div class="scitex-accordion">
  <div class="scitex-accordion-item">
    <button class="scitex-accordion-header">Section 1</button>
    <div class="scitex-accordion-panel">Content 1</div>
  </div>
</div>
```

---

## Progress & Loading

### Spinners/Loaders

**Status:** ❌ **Missing**

**Expected Variants:**
- Circular spinner
- Linear progress bar
- Dots animation
- Skeleton screens

---

### Progress Bars

**Status:** ❌ **Missing**

**Expected Structure:**
```html
<div class="scitex-progress">
  <div class="scitex-progress-bar" style="width: 60%">60%</div>
</div>
```

**Features:**
- Determinate (with percentage)
- Indeterminate (animated)
- Striped variant
- Color variants (success, warning, error)

---

## File Components

### File Upload

**Status:** ❌ **Missing** (visual styling needed)

**Current:** Basic `<input type="file">` exists in BibTeX enrichment
**Needed:** Styled drag-and-drop zone

**Expected Structure:**
```html
<div class="scitex-file-upload">
  <div class="scitex-dropzone">
    <input type="file" id="file">
    <label for="file">
      <span class="icon">📁</span>
      <span>Click to upload or drag and drop</span>
    </label>
  </div>
  <div class="scitex-file-list">
    <!-- Uploaded files shown here -->
  </div>
</div>
```

---

## Advanced Form Components

### Date Picker

**Status:** ❌ **Missing**

**Recommendation:** Consider using a library (e.g., Flatpickr) with custom SciTeX theme

---

### Autocomplete/Advanced Select

**Status:** ❌ **Missing**

**Features Needed:**
- Search/filter options
- Multi-select
- Tags display
- Async data loading
- Custom option rendering

**Recommendation:** Consider Select2 or similar with SciTeX styling

---

## Utility Classes

**File:** `/static/css/common/scitex-components.css`
**Dark Mode:** N/A (utilities)

**Available Classes:**
- `.scitex-text-primary` - Primary color text
- `.scitex-text-secondary` - Secondary color text
- `.scitex-bg-primary` - Primary background
- `.scitex-bg-secondary` - Secondary background
- `.scitex-border-primary` - Primary border color
- `.scitex-shadow` - Default shadow
- `.scitex-shadow-hover` - Hover shadow with lift effect

---

## CSS Variables Reference

**File:** `/static/css/common/colors.css`

**SciTeX Color Palette:**
```css
--primary-color: #1a2332;     /* Dark Bluish Gray */
--secondary-color: #34495e;   /* Medium Bluish Gray */
--accent-color: #506b7a;      /* Light Bluish Gray */

/* Status Colors */
--success-color: #4a9b7e;
--warning-color: #b8956a;
--error-color: #a67373;
--info-color: #6b8fb3;

/* Neutral Colors */
--light-gray: #f8f9fa;
--mid-gray: #e9ecef;
--dark-gray: #6c757d;

/* Dark Mode Bluish Scale */
--scitex-color-01: #1a2332;        /* Darkest */
--scitex-color-01-light: #232d3d;  /* Slightly lighter */
--scitex-color-02: #34495e;
--scitex-color-03: #506b7a;
--scitex-color-04: #6c8ba0;
--scitex-color-05: #8fa4b0;
--scitex-color-06: #b5c7d1;        /* Text color */
--scitex-color-07: #d4e1e8;        /* Lightest */
```

---

## Missing Components Summary

**High Priority:**
1. Modal/Dialog - Needed for confirmations, forms
2. Alerts - Critical for user feedback
3. Spinners/Loaders - User feedback during async operations
4. Table styling - Data display
5. Tooltips - Additional help text

**Medium Priority:**
6. Tabs - Content organization
7. Pagination - List navigation
8. Breadcrumbs - Navigation context
9. Progress bars - Multi-step processes
10. File upload styling - Better UX

**Low Priority:**
11. Accordion - FAQ sections
12. List groups - Menu items
13. Date picker - Form enhancement
14. Advanced select - Better UX
15. Reusable navbar - Component consistency

---

## Dark Mode Coverage Status

**Full Support (✅):**
- Forms (inputs, textareas, selects)
- Checkboxes
- Header
- Footer
- Hero

**Partial Support (⚠️):**
- Radios (needs enhancement)
- Toggles (needs enhancement)
- Cards (needs verification)

**No Support (❌):**
- Buttons (needs dark variants)
- Badges
- Dropdowns
- All missing components

---

## Next Actions

1. **Complete Dark Mode Coverage**
   - Add dark mode to buttons
   - Enhance radio and toggle dark mode
   - Verify and fix cards dark mode

2. **Create Component API Documentation**
   - Document exact class names
   - Add usage examples for each
   - Include do's and don'ts

3. **Build Missing High-Priority Components**
   - Modal/Dialog
   - Alerts
   - Spinners
   - Table styling
   - Tooltips

4. **Consider Django Template Tags**
   - Reduce HTML duplication
   - Enforce component consistency
   - Easier for team to use

5. **Add to Design System Page**
   - Live interactive examples
   - Copy-paste code snippets
   - Dark mode toggle per component

---

**Maintainers:** Development Team
**Review Cycle:** Monthly
**Related Docs:**
- `/static/css/REFACTOR_PLAN.md`
- `/static/SUGGESTIONS.md`
- `/dev/design/` (live design system)
