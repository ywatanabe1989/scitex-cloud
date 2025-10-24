# SciTeX Programmatic Design System Implementation Plan

**Date:** 2025-10-21
**Status:** Planning Phase
**Approach:** Custom Django App (Option A from PROGRAMMATIC_DESIGN_SYSTEM.md)
**Integration:** Works with modular CSS architecture and component registry

---

## Executive Summary

Based on `PROGRAMMATIC_DESIGN_SYSTEM.md` analysis, we're implementing a **Custom Django App** approach for the following reasons:

**Why Custom Django App:**
✅ Tightly integrated with existing Django architecture
✅ No build process needed (pure Python/Django)
✅ Full control over output and styling
✅ Can leverage existing `/dev/design/` page
✅ Works seamlessly with modular CSS architecture
✅ Auto-generates from CSS component files

**Why NOT other options:**
❌ Storybook - Requires frontend framework, overkill for Django
❌ Fractal - Extra build step, standalone site complexity
❌ Pattern Lab - Atomic design overhead, Node dependency
❌ Zeroheight - External paid service, less control

---

## Architecture Overview

### Current State
```
/dev/design/               # Manual HTML design system page
/static/css/common/        # Modular CSS components
  ├── checkboxes.css
  ├── radios.css
  ├── toggles.css
  ├── buttons.css
  └── forms.css
COMPONENT_REGISTRY.md      # Manual documentation
```

### Target State
```
/dev/design/               # Auto-generated design system
/static/css/common/        # Modular CSS with structured comments
  ├── checkboxes.css      # With @component annotations
  ├── radios.css          # With @variant annotations
  └── ...
components.json            # Auto-generated component registry
management/commands/
  └── generate_design_docs.py  # CSS parser & generator
```

---

## Phase 1: Foundation (Week 1)

### 1.1 Add Structured Comments to CSS Files

Update all component CSS files with parseable annotations:

**Format:**
```css
/*
 * @component Checkbox
 * @description Custom-styled checkboxes with theme support
 * @file /static/css/common/checkboxes.css
 * @darkmode true
 *
 * @variant scitex-checkbox - Base checkbox component
 * @state default - Unchecked state
 * @state checked - Checked with checkmark
 * @state hover - Background highlight
 * @state disabled - Reduced opacity
 *
 * @example
 * <div class="scitex-checkbox-wrapper">
 *   <input type="checkbox" id="cb1" class="scitex-checkbox">
 *   <label for="cb1" class="scitex-checkbox-label">Option 1</label>
 * </div>
 */
```

**Files to Update:**
- ✅ checkboxes.css (already has good header, add @annotations)
- ✅ radios.css (already has good header, add @annotations)
- ✅ toggles.css (already has good header, add @annotations)
- ⚠️ buttons.css (needs enhancement)
- ⚠️ forms.css (needs enhancement)
- ⚠️ cards.css (needs enhancement)

### 1.2 Create Component JSON Schema

**File:** `apps/workspace_app/fixtures/component_schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "components": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "description", "css_file"],
        "properties": {
          "id": { "type": "string" },
          "name": { "type": "string" },
          "description": { "type": "string" },
          "css_file": { "type": "string" },
          "darkmode": { "type": "boolean" },
          "variants": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "name": { "type": "string" },
                "class": { "type": "string" },
                "html": { "type": "string" }
              }
            }
          },
          "states": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "name": { "type": "string" },
                "description": { "type": "string" },
                "html": { "type": "string" }
              }
            }
          },
          "examples": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    }
  }
}
```

---

## Phase 2: CSS Parser (Week 2)

### 2.1 Create Management Command

**File:** `apps/workspace_app/management/commands/generate_design_docs.py`

```python
from django.core.management.base import BaseCommand
from django.conf import settings
import json
import re
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Generate component documentation from CSS files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='apps/workspace_app/fixtures/components.json',
            help='Output JSON file path'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )

    def handle(self, *args, **options):
        css_dirs = [
            'static/css/common/',
            'static/css/components/',
        ]

        components = []

        for css_dir in css_dirs:
            if not os.path.exists(css_dir):
                continue

            for css_file in Path(css_dir).glob('*.css'):
                if options['verbose']:
                    self.stdout.write(f"Parsing {css_file}...")

                component = self.parse_css_file(css_file)
                if component:
                    components.append(component)
                    if options['verbose']:
                        self.stdout.write(
                            self.style.SUCCESS(f"  ✓ Extracted {component['name']}")
                        )

        # Write to JSON
        output = {'components': components}
        output_path = options['output']

        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)

        self.stdout.write(
            self.style.SUCCESS(
                f"Generated docs for {len(components)} components → {output_path}"
            )
        )

    def parse_css_file(self, filepath):
        """Parse CSS file and extract component metadata"""
        with open(filepath, 'r') as f:
            content = f.read()

        # Extract structured comment block
        comment_pattern = r'/\*\s*\n(.*?)\*/'
        match = re.search(comment_pattern, content, re.DOTALL)

        if not match:
            return None

        comment = match.group(1)

        # Parse @annotations
        component = {
            'id': self.extract_annotation(comment, 'component', filepath.stem),
            'name': self.extract_annotation(comment, 'component', filepath.stem.title()),
            'description': self.extract_annotation(comment, 'description', ''),
            'css_file': f'/static/css/{filepath.relative_to("static/css")}',
            'darkmode': self.extract_boolean(comment, 'darkmode'),
            'variants': self.extract_variants(comment),
            'states': self.extract_states(comment),
            'examples': self.extract_examples(comment),
        }

        return component

    def extract_annotation(self, text, key, default=''):
        """Extract @key value from comment"""
        pattern = rf'@{key}\s+(.+?)(?:\n|$)'
        match = re.search(pattern, text)
        return match.group(1).strip() if match else default

    def extract_boolean(self, text, key):
        """Extract boolean @key"""
        pattern = rf'@{key}\s+(true|false)'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).lower() == 'true' if match else False

    def extract_variants(self, text):
        """Extract @variant annotations"""
        variants = []
        pattern = r'@variant\s+(.+?)\s+-\s+(.+?)(?:\n|$)'
        for match in re.finditer(pattern, text):
            variants.append({
                'name': match.group(1).strip(),
                'description': match.group(2).strip(),
            })
        return variants

    def extract_states(self, text):
        """Extract @state annotations"""
        states = []
        pattern = r'@state\s+(\w+)\s+-\s+(.+?)(?:\n|$)'
        for match in re.finditer(pattern, text):
            states.append({
                'name': match.group(1).strip(),
                'description': match.group(2).strip(),
            })
        return states

    def extract_examples(self, text):
        """Extract @example code blocks"""
        examples = []
        # Match @example followed by indented code block
        pattern = r'@example\s*\n((?:[ \t]+.+\n?)+)'
        for match in re.finditer(pattern, text):
            example_code = match.group(1)
            # Remove leading spaces from each line
            dedented = '\n'.join(line.strip() for line in example_code.split('\n'))
            examples.append(dedented.strip())
        return examples
```

### 2.2 Run Command

```bash
python manage.py generate_design_docs --verbose
```

**Expected Output:**
```
Parsing static/css/common/checkboxes.css...
  ✓ Extracted Checkbox
Parsing static/css/common/radios.css...
  ✓ Extracted Radio Button
Parsing static/css/common/toggles.css...
  ✓ Extracted Toggle Switch
...
Generated docs for 9 components → apps/workspace_app/fixtures/components.json
```

---

## Phase 3: Template Updates (Week 2-3)

### 3.1 Update Design System View

**File:** `apps/workspace_app/views.py`

```python
from django.shortcuts import render
import json
from pathlib import Path


def design_system(request):
    """Auto-generated design system from components.json"""
    components_file = Path('apps/workspace_app/fixtures/components.json')

    if components_file.exists():
        with open(components_file, 'r') as f:
            data = json.load(f)
            components = data.get('components', [])
    else:
        components = []

    # Group components by category
    categories = {
        'Form Components': [],
        'Button Components': [],
        'Layout Components': [],
        'Navigation Components': [],
    }

    for component in components:
        # Categorize based on component name or metadata
        category = component.get('category', 'Other Components')
        if category not in categories:
            categories[category] = []
        categories[category].append(component)

    return render(request, 'workspace_app/design_system.html', {
        'categories': categories,
        'total_components': len(components),
    })
```

### 3.2 Auto-Generated Template

**File:** `apps/workspace_app/templates/workspace_app/design_system.html`

```html
{% extends "base.html" %}
{% load static %}

{% block content %}
<div class="design-system">
  <header class="design-header">
    <h1>SciTeX Design System</h1>
    <p>Auto-generated from CSS component files</p>
    <div class="stats">
      <span>{{ total_components }} Components</span>
      <button id="theme-toggle" class="btn btn-sm">Toggle Dark Mode</button>
    </div>
  </header>

  <!-- Auto-generated component sections -->
  {% for category, components in categories.items %}
  <section class="design-category" id="{{ category|slugify }}">
    <h2>{{ category }}</h2>

    {% for component in components %}
    <article class="component-doc" id="{{ component.id }}">
      <header class="component-header">
        <h3>{{ component.name }}</h3>
        {% if component.darkmode %}
        <span class="badge dark-mode-badge">🌙 Dark Mode</span>
        {% endif %}
        <a href="#{{ component.id }}" class="permalink">#</a>
      </header>

      <p class="component-description">{{ component.description }}</p>

      <!-- Variants -->
      {% if component.variants %}
      <div class="component-variants">
        <h4>Variants</h4>
        {% for variant in component.variants %}
        <div class="variant-item">
          <strong>{{ variant.name }}</strong>
          <p>{{ variant.description }}</p>
        </div>
        {% endfor %}
      </div>
      {% endif %}

      <!-- States -->
      {% if component.states %}
      <div class="component-states">
        <h4>States</h4>
        <ul>
          {% for state in component.states %}
          <li><strong>{{ state.name }}</strong> - {{ state.description }}</li>
          {% endfor %}
        </ul>
      </div>
      {% endif %}

      <!-- Examples -->
      {% if component.examples %}
      <div class="component-examples">
        <h4>Usage Examples</h4>
        {% for example in component.examples %}
        <div class="example-preview">
          <div class="preview-render">
            {{ example|safe }}
          </div>
          <details class="code-block">
            <summary>View Code</summary>
            <pre><code class="language-html">{{ example }}</code></pre>
            <button class="copy-btn" data-clipboard-text="{{ example }}">Copy</button>
          </details>
        </div>
        {% endfor %}
      </div>
      {% endif %}

      <!-- CSS File Reference -->
      <div class="component-meta">
        <small>📁 <code>{{ component.css_file }}</code></small>
      </div>
    </article>
    {% endfor %}
  </section>
  {% endfor %}
</div>

<script src="{% static 'js/design-system.js' %}"></script>
{% endblock %}
```

---

## Phase 4: Interactive Features (Week 3-4)

### 4.1 Theme Toggle Script

**File:** `static/js/design-system.js`

```javascript
// Dark mode toggle
document.getElementById('theme-toggle')?.addEventListener('click', () => {
  const html = document.documentElement;
  const currentTheme = html.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

  html.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
});

// Copy code buttons
document.querySelectorAll('.copy-btn').forEach(btn => {
  btn.addEventListener('click', async (e) => {
    const code = e.target.dataset.clipboardText;
    await navigator.clipboard.writeText(code);

    e.target.textContent = '✓ Copied!';
    setTimeout(() => {
      e.target.textContent = 'Copy';
    }, 2000);
  });
});

// Syntax highlighting
if (window.Prism) {
  Prism.highlightAll();
}
```

### 4.2 Live Component Previewer

Add interactive component manipulation:

```javascript
// Live variant switcher
document.querySelectorAll('.variant-switcher').forEach(switcher => {
  switcher.addEventListener('change', (e) => {
    const preview = e.target.closest('.component-doc').querySelector('.preview-render');
    const variantClass = e.target.value;

    // Update preview with new variant
    preview.className = variantClass;
  });
});
```

---

## Integration with Existing Work

### How it Connects

1. **Modular CSS Files** (Already done)
   - checkboxes.css, radios.css, toggles.css
   - Add @annotations to these files

2. **Component Registry** (Already documented)
   - Use COMPONENT_REGISTRY.md as reference
   - Auto-generate from CSS files

3. **Dark Mode** (Already implemented)
   - Live toggle in design system
   - Show both themes side-by-side

4. **Gap Analysis** (Already done)
   - Generate TODO list for missing components
   - Track completion percentage

---

## Implementation Checklist

### Week 1: Foundation
- [ ] Add @annotations to checkboxes.css
- [ ] Add @annotations to radios.css
- [ ] Add @annotations to toggles.css
- [ ] Add @annotations to buttons.css
- [ ] Add @annotations to forms.css
- [ ] Create component JSON schema

### Week 2: Parser
- [ ] Create `generate_design_docs.py` management command
- [ ] Test CSS parsing with current files
- [ ] Generate initial components.json
- [ ] Validate JSON against schema

### Week 3: Templates
- [ ] Update design system view
- [ ] Create auto-generated template
- [ ] Add theme toggle
- [ ] Add code copy buttons

### Week 4: Enhancement
- [ ] Add live component previewer
- [ ] Add variant switcher
- [ ] Add state visualizer
- [ ] Add search/filter functionality

---

## Benefits

✅ **No Manual Documentation**
- Components.json auto-generated from CSS
- Developers only update CSS comments
- Documentation always in sync

✅ **Single Source of Truth**
- CSS files contain all information
- No separate docs to maintain
- Changes propagate automatically

✅ **Django-Native**
- Pure Python, no build tools
- Works with existing Django templates
- Leverage Django template system

✅ **Developer Friendly**
- Familiar @annotation syntax
- Run single command to regenerate
- Instant feedback loop

✅ **Interactive**
- Live theme switching
- Copy code snippets
- View all variants/states

---

## Future Enhancements

### Phase 5: Component Database (Optional)

Move from JSON to Django models for advanced features:

```python
class ComponentDoc(models.Model):
    component_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    css_file = models.CharField(max_length=255)
    darkmode_support = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ComponentVariant(models.Model):
    component = models.ForeignKey(ComponentDoc, related_name='variants', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=200)
    html_example = models.TextField()

class ComponentState(models.Model):
    component = models.ForeignKey(ComponentDoc, related_name='states', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
```

Benefits:
- Search functionality
- Version history
- Usage analytics
- API endpoints

---

## Success Metrics

**After Implementation:**
- ⏱️ 0 seconds to update docs (automatic)
- 📝 100% documentation coverage (from CSS)
- 🎨 Live theme preview (both modes)
- 📋 Copy-paste ready examples
- 🔍 Searchable component library

---

**Last Updated:** 2025-10-21
**Status:** Ready for implementation
**Next Step:** Add @annotations to existing CSS files
