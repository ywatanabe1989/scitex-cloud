# SciTeX UI Components

This directory contains reusable UI components for the SciTeX platform.

## Available Components

### Seekbar Component

A flexible and accessible range slider component for single and dual-handle sliders.

**Files:**
- `/static/css/components/seekbar.css` - Component styles
- `/static/js/components/seekbar.js` - JavaScript functionality

**Features:**
- Single-handle range slider (HTML5 native)
- Dual-handle range slider (JavaScript-enhanced)
- Customizable colors via CSS variables
- Responsive and mobile-friendly
- Keyboard accessible (ARIA compliant)
- Dark mode support
- Touch support for mobile devices
- No external dependencies (pure JavaScript)

---

## Seekbar Component Usage

### 1. Single-Handle Slider (Native HTML5)

Simple range slider using native HTML5 input.

#### HTML
```html
<div class="scitex-seekbar">
    <input type="range" class="scitex-seekbar-input"
           min="0" max="100" value="50" step="1">
</div>

<!-- With labels -->
<div class="scitex-seekbar">
    <label for="volume">Volume</label>
    <input type="range" class="scitex-seekbar-input"
           id="volume" min="0" max="100" value="75">
    <div class="scitex-seekbar-labels">
        <span>0</span>
        <span>100</span>
    </div>
</div>
```

#### JavaScript
```javascript
const slider = document.querySelector('.scitex-seekbar-input');
slider.addEventListener('input', (e) => {
    console.log('Value:', e.target.value);
});
```

---

### 2. Dual-Handle Slider (JavaScript)

Range slider with two handles for selecting a range.

#### HTML (Manual Initialization)
```html
<link rel="stylesheet" href="/static/css/components/seekbar.css">
<script src="/static/js/components/seekbar.js"></script>

<div id="mySeekbar"></div>

<script>
const seekbar = new ScitexSeekbar('#mySeekbar', {
    min: 0,
    max: 100,
    valueMin: 25,
    valueMax: 75,
    step: 1,
    onChange: (values) => {
        console.log('Range:', values.min, '-', values.max);
    }
});
</script>
```

#### HTML (Auto-Initialization)
```html
<!-- Automatically initializes on page load -->
<div data-scitex-seekbar="auto"
     data-min="0"
     data-max="100"
     data-value-min="25"
     data-value-max="75"
     data-step="1">
</div>
```

---

### 3. Configuration Options

```javascript
new ScitexSeekbar('#element', {
    // Range configuration
    min: 0,                    // Minimum value
    max: 100,                  // Maximum value
    valueMin: 25,              // Initial min value
    valueMax: 75,              // Initial max value
    step: 1,                   // Step increment

    // Formatting
    format: (value) => {
        return value.toFixed(1); // Format display value
    },

    // Display options
    showLabels: true,          // Show hover labels
    showValues: false,         // Show value display below

    // Callbacks
    onChange: (values) => {
        // Called when value changes
        console.log(values.min, values.max);
    },
    onUpdate: (values) => {
        // Called continuously during drag
    },
    onStart: (values) => {
        // Called when drag starts
    },
    onEnd: (values) => {
        // Called when drag ends
    }
});
```

---

### 4. API Methods

```javascript
const seekbar = new ScitexSeekbar('#element', options);

// Get current values
const values = seekbar.getValues();
// Returns: { min: 25, max: 75 }

// Set values programmatically
seekbar.setValues(30, 80);

// Reset to initial values
seekbar.reset();

// Destroy instance
seekbar.destroy();
```

---

### 5. CSS Customization

Customize colors using CSS variables:

```css
/* Override default colors */
:root {
    /* Track colors */
    --seekbar-track-bg: #e0e0e0;
    --seekbar-track-active-bg: #506b7a;

    /* Thumb colors */
    --seekbar-thumb-bg: #2c3e50;
    --seekbar-thumb-hover-bg: #34495e;
    --seekbar-thumb-active-bg: #506b7a;

    /* Dimensions */
    --seekbar-track-height: 6px;
    --seekbar-thumb-size: 18px;
}
```

---

### 6. Size Variants

```html
<!-- Small -->
<div class="scitex-seekbar scitex-seekbar-sm">
    <input type="range" class="scitex-seekbar-input" min="0" max="100">
</div>

<!-- Default (no class needed) -->
<div class="scitex-seekbar">
    <input type="range" class="scitex-seekbar-input" min="0" max="100">
</div>

<!-- Large -->
<div class="scitex-seekbar scitex-seekbar-lg">
    <input type="range" class="scitex-seekbar-input" min="0" max="100">
</div>
```

---

### 7. Color Variants

```html
<!-- Primary (default) -->
<div class="scitex-seekbar scitex-seekbar-primary">
    <input type="range" class="scitex-seekbar-input">
</div>

<!-- Success -->
<div class="scitex-seekbar scitex-seekbar-success">
    <input type="range" class="scitex-seekbar-input">
</div>

<!-- Warning -->
<div class="scitex-seekbar scitex-seekbar-warning">
    <input type="range" class="scitex-seekbar-input">
</div>

<!-- Danger -->
<div class="scitex-seekbar scitex-seekbar-danger">
    <input type="range" class="scitex-seekbar-input">
</div>
```

---

### 8. Advanced Examples

#### Year Range Filter
```html
<div id="yearFilter"></div>

<script>
const yearFilter = new ScitexSeekbar('#yearFilter', {
    min: 1900,
    max: 2025,
    valueMin: 2000,
    valueMax: 2025,
    step: 1,
    showValues: true,
    format: (value) => value.toString(),
    onChange: (values) => {
        // Update form inputs
        document.querySelector('[name="year_from"]').value = values.min;
        document.querySelector('[name="year_to"]').value = values.max;
        // Submit search
        document.querySelector('form').submit();
    }
});
</script>
```

#### Citation Count Filter (Logarithmic Scale)
```html
<div id="citationFilter"></div>

<script>
const citationFilter = new ScitexSeekbar('#citationFilter', {
    min: 0,
    max: 10000,
    valueMin: 0,
    valueMax: 10000,
    step: 10,
    showValues: true,
    format: (value) => {
        if (value >= 10000) return '10k+';
        if (value >= 1000) return (value / 1000).toFixed(1) + 'k';
        return value.toString();
    },
    onChange: (values) => {
        console.log(`Citations: ${values.min} - ${values.max}`);
    }
});
</script>
```

#### Impact Factor Filter (Decimal Values)
```html
<div id="impactFilter"></div>

<script>
const impactFilter = new ScitexSeekbar('#impactFilter', {
    min: 0,
    max: 50,
    valueMin: 0,
    valueMax: 50,
    step: 0.1,
    showValues: true,
    format: (value) => value.toFixed(1),
    onChange: (values) => {
        console.log(`Impact Factor: ${values.min} - ${values.max}`);
    }
});
</script>
```

---

### 9. Keyboard Accessibility

The dual-handle slider supports keyboard navigation:

- **Arrow Left/Down**: Decrease value by one step
- **Arrow Right/Up**: Increase value by one step
- **Page Down**: Decrease value by 10 steps
- **Page Up**: Increase value by 10 steps
- **Home**: Set to minimum value
- **End**: Set to maximum value
- **Tab**: Move focus between handles

---

### 10. Integration with Forms

```html
<form id="searchForm">
    <div id="yearSlider"></div>
    <input type="hidden" name="year_from" id="yearFrom">
    <input type="hidden" name="year_to" id="yearTo">

    <button type="submit">Search</button>
</form>

<script>
const yearSlider = new ScitexSeekbar('#yearSlider', {
    min: 1900,
    max: 2025,
    valueMin: 2000,
    valueMax: 2025,
    onChange: (values) => {
        document.getElementById('yearFrom').value = values.min;
        document.getElementById('yearTo').value = values.max;
    }
});

// Initialize hidden inputs
const initialValues = yearSlider.getValues();
document.getElementById('yearFrom').value = initialValues.min;
document.getElementById('yearTo').value = initialValues.max;
</script>
```

---

### 11. Integration with noUiSlider (Optional)

If you're already using noUiSlider, you can apply SciTeX styles:

```html
<link rel="stylesheet" href="/static/css/components/seekbar.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/noUiSlider/15.7.0/nouislider.min.css">

<div id="slider" class="scitex-seekbar-nouislider"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/noUiSlider/15.7.0/nouislider.min.js"></script>
<script>
noUiSlider.create(document.getElementById('slider'), {
    start: [20, 80],
    connect: true,
    range: {
        'min': 0,
        'max': 100
    }
});
</script>
```

---

## Browser Compatibility

- **Chrome/Edge**: ✓ Full support
- **Firefox**: ✓ Full support
- **Safari**: ✓ Full support
- **Mobile browsers**: ✓ Touch support included
- **IE11**: ✓ Partial support (no CSS Grid features)

---

## Accessibility

The component follows WCAG 2.1 Level AA guidelines:

- ARIA attributes for screen readers
- Keyboard navigation support
- Focus indicators
- Sufficient color contrast
- Touch-friendly targets (minimum 44x44px)

---

## Performance

- **No dependencies**: Pure JavaScript, no libraries required
- **Lightweight**: ~3KB CSS + ~5KB JS (minified)
- **GPU-accelerated**: Uses CSS transforms for smooth animations
- **Debounced updates**: Efficient event handling

---

## Migration from noUiSlider

If you're currently using noUiSlider and want to migrate:

```javascript
// Before (noUiSlider)
noUiSlider.create(element, {
    start: [20, 80],
    connect: true,
    range: { 'min': 0, 'max': 100 }
});

// After (ScitexSeekbar)
new ScitexSeekbar(element, {
    min: 0,
    max: 100,
    valueMin: 20,
    valueMax: 80
});
```

---

## Other Components

(To be documented as they are added)

- Alerts
- Breadcrumbs
- Dropdowns
- Modals
- Tabs
- Toggles

---

## Contributing

When adding new components to this directory:

1. Create CSS file: `/static/css/components/component-name.css`
2. Create JS file (if needed): `/static/js/components/component-name.js`
3. Document usage in this README
4. Follow SciTeX design system variables
5. Ensure dark mode compatibility
6. Add accessibility features

---

## License

Copyright (c) 2025 SciTeX Development Team
