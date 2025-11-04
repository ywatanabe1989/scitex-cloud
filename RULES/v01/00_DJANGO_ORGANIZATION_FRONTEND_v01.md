<!-- ---
!-- Timestamp: 2025-11-04 10:51:51
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/RULES/00_DJANGO_ORGANIZATION_FRONTEND.md
!-- --- -->

# Django Organization Rules

**Core Principle:** File structure mirrors HTML structure.

---

## The Three Laws

1. **App-Centric** - App files in their app directory
2. **No Inline Styles** - All CSS/JS in separate files
3. **Structure = Hierarchy** - File paths mirror template includes

---

## Quick Reference

### ✅ Correct Locations

| Type          | Location                                           |
|---------------|----------------------------------------------------|
| App CSS       | `apps/xxx_app/static/xxx_app/css/`                 |
| App TS        | `apps/xxx_app/static/xxx_app/ts/`                  |
| App JS        | `apps/xxx_app/static/xxx_app/js/` (compiled)       |
| App templates | `apps/xxx_app/templates/xxx_app/`                  |
| App partials  | `apps/xxx_app/templates/xxx_app/xxx_partials/`     |
| Global CSS    | `static/css/common/` or `static/css/components/`   |
| Global utils  | `static/ts/utils/` → `static/js/utils/` (compiled) |

### Template Naming Pattern

```
xxx.html
xxx_partials/
  yyy.html
  yyy_partials/
    zzz.html

xxx_partials/
  xxx_yyy.html
  xxx_yyy_partials/
    xxx_yyy_zzz.html
```

**Example:**
```
index.html                           {% include "index_partials/editor.html" %}
  ├── index_partials/
      ├── editor.html                {% include "index_partials/editor_partials/toolbar.html" %}
      └── editor_partials/
          └── toolbar.html
```

Structure shows: index → editor → toolbar (visual hierarchy)

---

## CSS Rules

### ❌ Never
```html
<div style="color: red;">           <!-- Inline style -->
<style>body { margin: 0; }</style>  <!-- Inline block -->
```

### ✅ Always
```html
<link rel="stylesheet" href="{% static 'xxx_app/css/xxx.css' %}">
<div class="text-red">
```

### Naming
- ✅ Use hyphens: `latex-editor.css`, `version-control.css`
- ❌ Avoid underscores: `latex_editor.css`
- ✅ Be descriptive: `index-editor-panels.css`
- ❌ Be vague: `editor-improved.css`, `new.css`

---

## JavaScript/TypeScript

### Source vs Compiled

```
ts/ ← Only .ts files (source)
js/ ← Only .js, .d.ts, .map (compiled output)
```

### Build
```bash
cd frontend && npm run build:writer
```

### Template References
```django
<script src="{% static 'writer_app/js/index.js' %}"></script>
```

---

## Common Mistakes

| ❌ Don't                     | ✅ Do                                        |
|------------------------------|----------------------------------------------|
| App files in `/static/` root | App files in `/apps/xxx_app/static/xxx_app/` |
| Inline `style=""`            | CSS classes                                  |
| `file_name.css`              | `file-name.css`                              |
| Edit `.js` files             | Edit `.ts` source, rebuild                   |
| Skip `build-ts`              | Run before deploy                            |

---

## New Feature Checklist

- [ ] Create `xxx.html` (< 50 lines)
- [ ] Create `xxx_partials/` directory
- [ ] Create `css/xxx.css` (hyphens)
- [ ] Create `ts/xxx.ts` if needed
- [ ] Build: `cd frontend && npm run build:writer`
- [ ] Test: Check browser console for 404s

---

**That's it.** Structure shows relationships. Simple, necessary, sufficient.

<!-- EOF -->