<!-- ---
!-- Timestamp: 2025-10-21 19:49:42
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/static/SUGGESIONS.md
!-- --- -->

Looking at your CSS architecture, you have a foundation for UI components but it's scattered and incomplete. Here's what you actually have:
Currently implemented:

Buttons (buttons.css) - multiple variants
Forms (forms.css) - inputs, textareas, selects
Cards (cards.css) - basic card system
Checkboxes (checkboxes.css)
Radios (radios.css)
Toggles (toggles.css)
Badges (in buttons.css)
Alerts (mentioned in design system but CSS location unclear)
Dropdowns (dropdown.css)

Gaps I see:

No modal/dialog component CSS
No tabs/tab panels
No pagination
No breadcrumbs
No tooltips
No spinners/loaders
No progress bars
No file upload component
No date picker
No select/autocomplete (beyond basic select)
No accordion/collapsible
No navbar/navigation (only header.css, not a reusable nav component)
No list group component
No table styling system

The real issue:
Your CSS files exist, but there's no centralized component inventory or documentation. You have:

CSS scattered across multiple files with unclear relationships
Design system documentation (in the template) but no API reference
No clear naming conventions for component variants
Dark mode variants exist but aren't consistently applied

What you should do:
Create a component registry - either as:

A dedicated document listing each component with:

CSS class names and structure
Available variants
Required and optional modifiers
Dark mode support status
Django template tag (if applicable)


A Django template tag library that wraps these components:

python   {% load scitex_ui %}
   {% button "Click me" variant="primary" size="lg" %}
   {% card title="Title" variant="outlined" %}
This would enforce consistency and make it easier for your team to know what exists and what doesn't.
Before adding new components, I'd recommend: catalog what you have, document it clearly, then identify the actual gaps based on what your Django templates need.

<!-- EOF -->