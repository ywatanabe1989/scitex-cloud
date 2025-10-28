# CSS Architecture Refactoring Plan

**Date:** 2025-10-21
**Status:** Planning Phase
**Goal:** Modularize CSS architecture for better maintainability and scalability

---

## Current State Analysis

### Directory Structure
```
/static/css/
├── base/                    # Bootstrap overrides (1 file)
├── common/                  # Foundation styles (15 files)
│   └── scitex-components.css  # 🔴 MONOLITHIC (9.9KB)
├── components/              # Layout components (6 files)
├── pages/                   # Page-specific styles (5 files)
├── products/                # ⚠️ Possibly unused (1 file)
├── utilities/               # ❌ Empty directory
├── legacy/                  # ⚠️ Old code to be cleaned
├── github_header.css        # ⚠️ Misplaced
└── README.md                # ⚠️ Outdated
```

### Key Issues

1. **Monolithic `scitex-components.css` (9.9KB)**
   - Contains 7 different component systems mixed together
   - Hard to maintain and document
   - Violates single responsibility principle

2. **Inconsistent Organization**
   - `buttons.css` is separate ✅
   - But checkboxes/radios/toggles are inside `scitex-components.css` ❌
   - Confusing for developers

3. **Orphaned/Unused Files**
   - `utilities/` directory is empty
   - `products/products-common.css` may be unused
   - `github_header.css` should be in `components/`

4. **Outdated Documentation**
   - `README.md` doesn't mention `scitex-components.css`
   - Missing dark mode documentation
   - Doesn't reflect current structure

5. **Dark Mode Issues (RESOLVED)**
   - ✅ Form colors fixed for dark mode
   - ✅ Checkbox labels now visible with bluish colors
   - ✅ Search inputs have proper contrast

---

## Target Architecture

### Proposed Structure
```
/static/css/
├── common/                           # Foundation styles
│   ├── variables.css                 # Entry point for all variables
│   ├── colors.css                    # Color palette
│   ├── typography-vars.css           # Font variables
│   ├── spacing.css                   # Spacing scale
│   ├── effects.css                   # Shadows, borders, transitions
│   ├── z-index.css                   # Z-index scale
│   ├── reset.css                     # CSS reset
│   ├── layout.css                    # Layout utilities
│   ├── typography.css                # Typography styles
│   ├── buttons.css                   # Button components
│   ├── forms.css                     # Basic form inputs
│   ├── checkbox.css                # 🆕 Checkbox components
│   ├── radios.css                    # 🆕 Radio components
│   ├── toggles.css                   # 🆕 Toggle switches
│   ├── cards.css                     # Card components
│   ├── scitex-components.css         # 📦 Entry point (imports)
│   ├── main.css                      # Main styles
│   └── settings-layout.css           # Settings page layout
│
├── components/                       # Layout/structural components
│   ├── header.css
│   ├── footer.css
│   ├── hero.css
│   ├── dropdown.css
│   ├── features.css
│   ├── logo.css
│   └── global-header.css             # 🔄 Moved from root
│
├── pages/                            # Page-specific styles
│   ├── index.css
│   ├── landing.css
│   ├── landing-enhanced.css
│   ├── products.css
│   └── repository.css
│
├── apps/                             # 🆕 App-specific styles
│   ├── scholar/                      # Scholar app styles
│   ├── auth/                         # Auth app styles
│   └── ...                           # Other apps
│
├── base/                             # Framework overrides
│   └── bootstrap-override.css
│
├── legacy/                           # ⚠️ To be removed
│
├── theme.css                         # 📦 Main entry (imports all)
├── README.md                         # 🔄 Updated documentation
└── REFACTOR_PLAN.md                  # This file
```

### Modular Component System

**`scitex-components.css`** becomes an aggregator:
```css
/*
 * SciTeX Component System - Entry Point
 * Aggregates all modular component files
 */

/* Import modular components */
@import './buttons.css';
@import './checkbox.css';
@import './radios.css';
@import './toggles.css';
@import './forms.css';
@import './cards.css';
```

---

## Implementation Phases

### Phase 1: Investigation & Git Management ✅

**Tasks:**
- [x] Analyze current CSS file usage
- [x] Check which files are actually imported
- [x] Identify unused files
- [ ] Commit current changes to git
- [ ] Create feature branch: `refactor/css-modular-architecture`

**Git Commands:**
```bash
git add .
git commit -m "feat: Add dark mode support for forms and checkboxes

- Update form colors to bluish theme in dark mode
- Fix checkbox label visibility
- Improve search input contrast
- Add comprehensive dark mode styles to scitex-components.css

📁 Modified files:
- static/css/common/forms.css
- static/css/common/scitex-components.css
- apps/scholar_app/templates/scholar_app/index.html"

git checkout -b refactor/css-modular-architecture
```

---

### Phase 2: Extract Components from `scitex-components.css`

**Tasks:**
1. ✅ Read and analyze `scitex-components.css` structure
2. Create modular files:
   - [ ] `checkbox.css` - Extract checkbox system (lines 157-233)
   - [ ] `radios.css` - Extract radio system (lines 94-156)
   - [ ] `toggles.css` - Extract toggle system (lines 234-284)
3. [ ] Update `scitex-components.css` to be an entry point with imports
4. [ ] Test that imports work correctly

**File Mappings:**
```
scitex-components.css:
  Lines 29-93   → buttons.css (already exists, verify consistency)
  Lines 94-156  → radios.css (NEW)
  Lines 157-233 → checkbox.css (NEW)
  Lines 234-284 → toggles.css (NEW)
  Lines 285-361 → forms.css (verify integration)
  Lines 362-394 → Keep in scitex-components.css (utilities)
  Lines 395-end → Keep in scitex-components.css (responsive)
```

**Template for new files:**
```css
/*
 * SciTeX [Component Name] Component
 * Custom-styled [component description] with theme support
 * 📁 Source: /static/css/common/[filename].css
 * 📖 Docs: /dev/design/#[section]
 *
 * Component Definition:
 * - .scitex-[component]         # Hidden native input
 * - .scitex-[component]-label   # Custom styled label
 * - .scitex-[component]-wrapper # Optional wrapper
 *
 * States:
 * - Default (unchecked)
 * - Checked
 * - Hover
 * - Disabled
 * - Dark mode variants
 */

/* Base styles */
/* ... */

/* Dark mode */
[data-theme="dark"] {
  /* ... */
}
```

---

### Phase 3: Update HTML Templates

**Files to update:**
```
✅ Already using scitex-components.css:
- apps/scholar_app/templates/scholar_app/index.html
- apps/scholar_app/templates/scholar_app/search_dashboard.html

🔍 Check for direct imports:
- templates/partials/global_head_styles.html
- templates/github_base.html
- apps/*/templates/**/*.html
```

**No changes needed** if using `scitex-components.css` (it will auto-import)

---

### Phase 4: Reorganize Misplaced Files

**Tasks:**
1. [ ] Move `github_header.css` → `components/global-header.css`
2. [ ] Update imports in templates
3. [ ] Verify `products/products-common.css` usage
   - If unused: move to `legacy/`
   - If used: keep or move to app-specific location
4. [ ] Delete empty `utilities/` directory (or add utility styles)

**Update templates:**
```html
<!-- OLD -->
<link rel="stylesheet" href="{% static 'css/github_header.css' %}">

<!-- NEW -->
<link rel="stylesheet" href="{% static 'css/components/global-header.css' %}">
```

---

### Phase 5: Programmatic Design System Documentation

**NEW APPROACH:** Auto-generate documentation from CSS files (See `PROGRAMMATIC_IMPLEMENTATION_PLAN.md`)

**Tasks:**
1. [ ] Add @annotations to existing CSS files (checkboxes, radios, toggles, buttons, forms)
2. [ ] Create `generate_design_docs.py` management command
3. [ ] Generate `components.json` from CSS files
4. [ ] Update `/dev/design/` view to use auto-generated data
5. [ ] Create auto-generating template with theme toggle
6. [ ] Add interactive features (code copy, variant switcher)

**Benefits:**
- ✅ Zero manual documentation (auto-generated from CSS)
- ✅ Single source of truth (CSS files)
- ✅ Always in sync (regenerate on change)
- ✅ Live theme switching
- ✅ Copy-paste code examples

**CSS Annotation Format:**
```css
/*
 * @component Checkbox
 * @description Custom-styled checkboxes
 * @darkmode true
 * @variant scitex-checkbox - Base component
 * @state checked - Checked with checkmark
 * @example
 * <div class="scitex-checkbox-wrapper">
 *   <input type="checkbox" id="cb1" class="scitex-checkbox">
 *   <label for="cb1" class="scitex-checkbox-label">Label</label>
 * </div>
 */
```

---

### Phase 6: Update Documentation

**Tasks:**
1. [ ] Update `README.md` with new structure
2. [ ] Document dark mode system
3. [ ] Add component usage guidelines
4. [ ] Document import patterns
5. [ ] Add migration guide for developers

**README.md sections to add:**
- Dark mode theming system
- Component module system
- Import strategy (entry points)
- How to add new components
- App-specific styles location

---

### Phase 7: Cleanup & Legacy Removal

**Tasks:**
1. [ ] Review `legacy/` directory contents
2. [ ] Confirm files are truly unused
3. [ ] Move to archive or delete
4. [ ] Remove `.old/` subdirectories
5. [ ] Clean up `.bak` files

**Files to review:**
```
legacy/
├── collaborative-editor.css  # Check if used
├── darkmode.css              # OLD - replaced by theme system
├── darkmode-old.css          # DELETE
├── header-override.css       # Check if used
├── main.css                  # OLD - verify unused
├── theme-deprecated.css      # DELETE
└── viz-interface.css         # Check if used
```

---

### Phase 8: Testing & Validation

**Tasks:**
1. [ ] Test all pages in light mode
2. [ ] Test all pages in dark mode
3. [ ] Verify form components work correctly
4. [ ] Check checkbox/radio/toggle functionality
5. [ ] Test on different browsers (Chrome, Firefox, Safari)
6. [ ] Mobile responsiveness check
7. [ ] Performance audit (file size, load time)

**Testing checklist:**
- [ ] Scholar search page (checkboxes, toggles)
- [ ] Auth signup/login forms
- [ ] Settings pages
- [ ] Landing page
- [ ] Repository pages
- [ ] Design system page

---

### Phase 9: Deployment & Monitoring

**Tasks:**
1. [ ] Run Django collectstatic
2. [ ] Clear browser cache
3. [ ] Deploy to staging
4. [ ] Test on staging environment
5. [ ] Monitor for CSS-related errors
6. [ ] Get user feedback
7. [ ] Deploy to production

**Commands:**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Test locally
./server.sh

# Deploy (adjust based on deployment method)
git push origin refactor/css-modular-architecture
# Create PR and merge after review
```

---

## Success Criteria

### Functional
- ✅ All pages render correctly in light mode
- ✅ All pages render correctly in dark mode
- ✅ Forms are fully functional
- ✅ Checkboxes/radios/toggles work as expected
- ✅ No visual regressions

### Architectural
- ✅ CSS files are modular and focused
- ✅ Import structure is clear and documented
- ✅ Component files follow consistent patterns
- ✅ Documentation is up-to-date
- ✅ Legacy code is removed

### Performance
- ✅ No increase in total CSS file size
- ✅ Page load times remain same or improve
- ✅ CSS caching works correctly

---

## Rollback Plan

If issues arise:

1. **Immediate rollback:**
   ```bash
   git checkout develop
   python manage.py collectstatic --noinput
   ```

2. **Partial rollback:**
   - Keep dark mode fixes
   - Revert modular structure
   - Restore monolithic `scitex-components.css`

3. **Fix forward:**
   - Identify specific issue
   - Fix in feature branch
   - Re-test and deploy

---

## Dependencies

### Files that import CSS:
- `templates/partials/global_head_styles.html` - Global CSS imports
- `templates/github_base.html` - GitHub-style pages
- App-specific base templates

### Python files (collectstatic):
- `settings.py` - STATIC_ROOT, STATICFILES_DIRS
- Deployment scripts

---

## Notes

### Dark Mode Implementation (Completed)
- ✅ Forms now use bluish colors (`--scitex-color-06`) in dark mode
- ✅ Checkboxes have proper visibility
- ✅ Search inputs have better contrast
- ✅ All theme variables properly defined

### Component Extraction Strategy
- Extract by component type (checkbox, radio, toggle)
- Maintain dark mode styles in same file
- Use `@import` for aggregation
- Keep utilities and responsive code in entry point

### Future Enhancements
- Consider CSS modules or CSS-in-JS for true component isolation
- Implement CSS purging for production builds
- Add CSS linting with stylelint
- Set up automated visual regression testing

### Component Inventory & Documentation (Based on SUGGESTIONS.md)

**Currently Implemented Components:**
- ✅ Buttons (buttons.css) - multiple variants
- ✅ Forms (forms.css) - inputs, textareas, selects
- ✅ Cards (cards.css) - basic card system
- ✅ Checkboxes (checkbox.css) - custom styled with dark mode
- ✅ Radios (radios.css) - segmented control pattern
- ✅ Toggles (toggles.css) - button-like switches
- ✅ Badges (in buttons.css)
- ✅ Dropdowns (dropdown.css)
- ⚠️ Alerts (mentioned in design system but CSS location unclear)

**Missing Components (Future Development):**
- ❌ Modal/Dialog component
- ❌ Tabs/Tab panels
- ❌ Pagination
- ❌ Breadcrumbs
- ❌ Tooltips
- ❌ Spinners/Loaders
- ❌ Progress bars
- ❌ File upload component (visual styling)
- ❌ Date picker
- ❌ Advanced select/autocomplete
- ❌ Accordion/Collapsible
- ❌ Reusable navbar/navigation component
- ❌ List group component
- ❌ Table styling system

**Critical Issues to Address:**
1. **No centralized component inventory** - Components exist but not catalogued
2. **Inconsistent dark mode coverage** - Not all components have dark mode variants
3. **No API documentation** - Class names and usage patterns undocumented
4. **No Django template tag library** - Components require manual HTML construction

**Recommended Next Phase (Phase 10):**
Create a comprehensive component registry document:
- Component name and purpose
- CSS class names and structure
- Available variants (size, color, state)
- Required and optional modifiers
- Dark mode support status (✅/❌)
- Usage examples (HTML + Django template)
- Dependencies (required CSS/JS)

**Long-term Enhancement:**
Consider Django template tag library for component consistency:
```python
{% load scitex_ui %}
{% button "Click me" variant="primary" size="lg" %}
{% card title="Title" variant="outlined" %}
{% checkbox id="opt1" label="Option 1" %}
```

---

## Timeline Estimate

- **Phase 1:** 30 minutes (Investigation & Git)
- **Phase 2:** 2 hours (Extract components)
- **Phase 3:** 30 minutes (Update templates)
- **Phase 4:** 1 hour (Reorganize files)
- **Phase 5:** 2 hours (Design documentation)
- **Phase 6:** 1 hour (Update README)
- **Phase 7:** 1 hour (Cleanup legacy)
- **Phase 8:** 2 hours (Testing)
- **Phase 9:** 1 hour (Deployment)

**Total:** ~11 hours

---

## References

- Design system: `/dev/design/`
- Current CSS: `/static/css/`
- Issue tracker: Track progress in GitHub issues
- Related PR: Link PR when created

---

**Last Updated:** 2025-10-21
**Owner:** Development Team
**Priority:** High - Improves maintainability
