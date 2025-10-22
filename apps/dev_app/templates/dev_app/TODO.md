<!-- ---
!-- Timestamp: 2025-10-22 01:32:23
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/apps/dev_app/templates/dev_app/TODO.md
!-- --- -->

**Fill the checkboxes of this TODO file if implemented correctly**


## Guidelines
Do not think individual problem just for the specific place. Instead, take problems as those in how css defined, how css components defined, how responsibility applied, systematically

`/dev/design/` is the central testing/demonstrating page for other pages
So, before working on other pages, please make this page complete and professional

## Issue reports and Requests
- [ ] NOT VISIBLE:
- [ ] Change:
  - [ ] Writer Icon in SVG - Redesigned to match ✍️ emoji (pen + hand writing on paper)
- [ ] Flatten Usage Guidelines (this page itself is guideline and self-explanatory examples)
  - [ ] Icons (or should we moved to the layout components as Icon?)
  - [ ] Hero variants (or should we moved to the Layout Components/Hero?)


"Form Components" should be renamed as "Form and Selection" and sorted as follows:

Button
Toggle Button (Checkbox)
Segmented Radio Control
Checkbox
Select Dropdown
File Upload
Form Input



### Side Panel
- [ ] Expand by default
- [ ] Remove contents counts
- [ ] Badge to Visual Identify; remove Data Display


### Selection Components
- [ ] Button
- [ ] Checkbox
- [ ] Radio Button
- [ ] Drop down (Dropdown should not be navigation component)

- Coverage checklist

# UI Components Hierarchy

<!-- ### 2.3 Form Layout??
 !-- 
 !-- - **Form Group** (label + input + hint)
 !-- - **Form Row** (horizontal layout)
 !-- - **Form Section** (grouped related fields)
 !-- - **Fieldset** (grouped with legend)
 !-- - **Input Group** (prepend/append additions) -->

### 2.4 Validation & Feedback

- **Error Message** (inline)
- **Helper Text** (hint/description)
- **Validation Icons** (checkmark, error)
- **Input State** (error, success, warning, disabled)

---

## 3. Data Display Components

### 3.1 Table/Grid

- **Table** (basic)
- **Data Grid** (with sorting, filtering)
- **Table Row**
- **Table Cell/Header**
- **Sortable Column Header**
- **Pagination** (table control)

### 4.1 Notifications

- **Alert** (info, success, warning, error)
- **Toast/Notification** (temporary)
- **Snackbar** (bottom notification)
- **Banner** (page-level announcement)

### 4.2 Progress & Status

- **Progress Bar** (linear)
- **Progress Ring** (circular)
- **Spinner/Loader** (indeterminate)
- **Status Badge** (online/offline, etc.)
- **Log** (see http://127.0.0.1:8000/ywatanabe/django-gitea-demo/?mode=writer)

### 4.3 Confirmation & Interaction

- **Modal/Dialog**
- **Confirmation Dialog**
- **Alert Dialog**
- **Tooltip**
- **Popover**

---

### Special
- **Code Block** (syntax highlighting)
- **Help/Onboarding** (tooltips, popovers)

---

## Implementation Priority

### Phase 1 (Essential)

1. Buttons (all variants)
2. Form inputs (text, email, password, textarea)
3. Checkboxes & Radios
4. Selects & Dropdowns
5. Labels & Form Groups
6. Alerts & Validation Messages
7. Cards
8. Links

### Phase 2 (Common)

9. Modals/Dialogs
10. Toasts/Notifications
11. Tabs
12. Pagination
13. Tables
14. Progress Bars
15. Breadcrumbs
16. Navbars
17. Badges
18. Tooltips

---

Variants:
- [ ] Size (sm, md, lg)
- [ ] Color/Status (primary, secondary, danger)
- [ ] State (default, hover, focus, active, disabled)

Documentation:
- [ ] Usage guidelines
- [ ] Code examples
- [ ] Design system page entry
- [ ] Django template tag (if applicable)

<!-- EOF -->