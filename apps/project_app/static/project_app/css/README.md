# Project App CSS Structure

This directory contains the modular CSS files for the project_app.

## Directory Structure

```
css/
├── project_app.css         # Main import file (use this in templates)
├── project_app.css.backup  # Backup of original monolithic file
├── common.css              # Shared/common styles
├── components/             # Reusable UI components
│   ├── sidebar.css
│   └── file-tree.css
├── pages/                  # Page-specific styles
│   ├── list.css
│   ├── detail.css
│   ├── detail-extra.css
│   ├── create.css
│   ├── edit.css
│   ├── delete.css
│   └── settings.css
├── filer/                  # File management styles
│   ├── browser.css
│   ├── view.css
│   ├── edit.css
│   └── history.css
├── commits/
│   └── detail.css
├── users/
│   ├── bio.css
│   └── profile.css
├── issues/
│   ├── list.css
│   └── detail.css
├── pull_requests/
│   ├── pr-list.css
│   └── pr-detail.css
├── actions/
│   ├── list.css
│   ├── workflow-detail.css
│   ├── workflow-editor.css
│   └── workflow-run-detail.css
└── security/
    └── security.css
```

## Import Order

The main `project_app.css` file imports all modules in a specific order:

1. **Common** - Base styles used everywhere
2. **Components** - Reusable UI components
3. **Pages** - Page-specific layouts
4. **Feature Modules** - Specific features (filer, commits, users, etc.)

**Important:** Import order matters for CSS specificity!

## Usage in Templates

Simply link to the main CSS file in your template:

```html
<link rel="stylesheet" href="{% static 'project_app/css/project_app.css' %}">
```

## Maintenance

- Keep styles in the appropriate file based on their scope
- Common styles shared across multiple pages → `common.css`
- Reusable components → `components/`
- Page-specific styles → appropriate subdirectory
- Maintain import order when adding new files

## Migration Notes

This structure was created by splitting the monolithic `project_app.css` (5775 lines)
into modular files that mirror the template organization.
