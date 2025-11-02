# SciTeX Template Partials

Reusable template components for consistent UI across the platform.

## Directory Structure

```
partials/
├── forms/              # Form components
│   ├── input_with_icon.html
│   └── password_with_toggle.html
├── cards/              # Card components
│   ├── module_card.html
│   └── feature_card.html
├── sections/           # Page sections
├── header.html         # Site header
└── footer.html         # Site footer
```

## Usage Examples

### Form Components

**Input with Icon:**
```django
{% include 'partials/forms/input_with_icon.html' with
   type='email'
   id='email'
   name='email'
   label='Email Address'
   placeholder='Enter your email'
   icon='fa-envelope'
   required=True
   help_text='We will never share your email'
%}
```

**Password with Toggle:**
```django
{% include 'partials/forms/password_with_toggle.html' with
   id='password'
   name='password'
   label='Password'
   placeholder='Enter password'
   required=True
   help_text='Minimum 8 characters'
   minlength=8
%}
```

### Card Components

**Module Card:**
```django
{% include 'partials/cards/module_card.html' with
   name='Scholar'
   icon='images/scitex-scholar-icon.svg'
   tagline='Literature discovery & analysis'
   url='/scholar/'
   size=48
   coming_soon=False
%}
```

**Feature Card:**
```django
{% include 'partials/cards/feature_card.html' with
   icon='🔓'
   title='Open by Default'
   description='Every line of code public. No vendor lock-in.'
   border_color='#28a745'
   icon_size='2rem'
%}
```

## Parameters

### input_with_icon.html
- `type` - Input type (text, email, etc.) [default: 'text']
- `id` - Element ID (required)
- `name` - Form field name (required)
- `label` - Field label [optional]
- `placeholder` - Placeholder text [optional]
- `icon` - FontAwesome icon class (e.g., 'fa-envelope') [optional]
- `required` - Boolean [default: False]
- `minlength`, `maxlength`, `pattern` - Validation [optional]
- `help_text` - Helper text below field [optional]

### password_with_toggle.html
- `id` - Element ID (required)
- `name` - Form field name (required)
- `label` - Field label [optional]
- `placeholder` - Placeholder text [default: 'Enter password']
- `required` - Boolean [default: False]
- `minlength` - Minimum length [default: 8]
- `help_text` - Helper text [optional]

### module_card.html
- `name` - Module name (required)
- `icon` - Icon path relative to static/ [default: 'images/scitex-icon.svg']
- `tagline` - Short description [optional]
- `url` - Link URL (required)
- `size` - Icon size in pixels [default: 48]
- `coming_soon` - Show "Coming Soon" badge [default: False]

### feature_card.html
- `icon` - Emoji or icon [optional]
- `title` - Card title (required)
- `description` - Card content (required)
- `border_color` - Left border color [optional]
- `icon_size` - Icon font size [default: '2rem']
- `title_size` - Title font size [default: '1.2rem']
- `text_size` - Description font size [default: '0.95rem']

## Benefits

- ✅ **Consistency** - Same components across all pages
- ✅ **Maintainability** - Update once, changes everywhere
- ✅ **Reusability** - DRY principle
- ✅ **Documentation** - Clear usage examples
- ✅ **Flexibility** - Customizable via parameters

## Best Practices

1. **Always provide required parameters** - Check README for each component
2. **Use semantic naming** - Match id/name to purpose
3. **Include help_text** - Guide users with helpful hints
4. **Test accessibility** - All components are WCAG compliant
5. **Keep partials small** - Single responsibility principle

## Next Steps

Create more partials as patterns emerge:
- Alert/message components
- Modal dialogs
- Navigation breadcrumbs
- Loading states
- Empty states

---

Created: 2025-10-15
Purpose: Reduce template duplication, improve maintainability
