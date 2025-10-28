# CodeMirror Design System Integration

## Overview
This document describes how CodeMirror LaTeX editor is integrated with the SciTeX design system to provide a consistent, polished user experience.

## Implementation Summary

### Files Modified/Created

1. **Created**: `/apps/writer_app/static/writer_app/css/codemirror-styling.css`
   - Main styling file that integrates CodeMirror with design system
   - Applies design system borders, padding, shadows, and spacing
   - Adds "LaTeX" language label at top-left
   - Provides Zenburn-inspired syntax highlighting
   - Supports light and dark modes

2. **Modified**: `/apps/writer_app/templates/writer_app/writer_base.html`
   - Added design system code-blocks.css
   - Added codemirror-styling.css integration
   - Ensures proper CSS load order

## Key Features

### Design System Consistency
- **Borders**: 1px solid with design system colors (`--border-default`)
- **Border Radius**: 6px matching code blocks
- **Box Shadow**: `0 2px 8px rgba(0, 0, 0, 0.08)` for depth
- **Padding**: 2.5rem top (for header), 1.5rem sides (matches design system)
- **Typography**: Uses `--mono-font-family` variable

### Visual Elements
- **Language Label**: "LaTeX" label at top-left using `::before` pseudo-element
- **Header Bar**: Grey background bar at top (2.75rem height) using `::after` pseudo-element
- **Line Numbers**: Styled gutter with proper spacing and colors
- **Active Line**: Subtle background highlight for current line
- **Selection**: Design system consistent selection color

### Theme Support
- **Light Mode**: Clean, professional appearance with good contrast
- **Dark Mode**: Automatically adapts when `[data-theme="dark"]` is set
- **CodeMirror Themes**: User can still switch between Zenburn, Monokai, Dracula (dark) and Eclipse, Neat, Solarized (light)
- **Syntax Highlighting**: Zenburn-inspired colors for LaTeX tokens

### Accessibility
- Proper focus states with visible outlines
- High contrast mode support
- Reduced motion support for animations
- Keyboard navigation fully supported

## CSS Architecture

### Specificity Strategy
The CSS uses `!important` selectively to ensure design system styles take precedence over:
- Default CodeMirror styles
- CDN-loaded theme styles
- Third-party overrides

### Z-Index Layers
```
z-index: 1   - Header bar background (::after)
z-index: 2   - Scroll content area
z-index: 3   - Gutters (line numbers)
z-index: 100 - Language label (::before) and copy button
```

### CSS Variables Used
From design system:
- `--border-default` - Border colors
- `--border-muted` - Subtle borders (dark mode)
- `--bg-page` - Background colors
- `--bg-muted` - Header bar background
- `--bg-subtle` - Active line highlight
- `--bg-selected` - Selection background
- `--text-primary` - Main text color
- `--text-secondary` - Secondary text (copy button)
- `--text-muted` - Muted text (line numbers, label)
- `--mono-font-family` - Monospace font stack
- `--base-font-family` - Sans-serif font (for label)

## Syntax Highlighting

### Light Mode Colors (Zenburn-inspired)
- **Comments**: `#7F9F7F` (green-grey)
- **Commands**: `#DFAF8F` (tan/beige)
- **Keywords**: `#F0DFAF` (light yellow)
- **Strings**: `#CC9393` (salmon)
- **Numbers**: `#8CD0D3` (cyan)
- **Brackets**: `#93E0E3` (light cyan)
- **Math**: `#BFEBBF` (light green)
- **Headers**: `#DCA3A3` (light red)

### Dark Mode
Same colors - Zenburn theme works well in both modes

## Integration with Existing Code

### JavaScript Integration
No changes required to JavaScript! The CSS works with existing CodeMirror initialization:

```javascript
codeMirrorEditor = CodeMirror.fromTextArea(latexEditorTextarea, {
    mode: 'stex',
    theme: initialTheme,  // User's preference still works
    lineNumbers: true,
    lineWrapping: true,
    // ... other options
});
```

### Theme Switching
User can still switch themes via dropdown. Our design system styles complement rather than override theme choices:
- Design system provides: borders, padding, header, label
- CodeMirror theme provides: syntax colors, background
- Both work together harmoniously

### Responsive Design
- Mobile breakpoint at 768px
- Reduced padding on small screens
- Font size adjustment for readability
- Label size reduction

## Optional Enhancements

### Copy Button
CSS classes provided but not implemented:
- `.codemirror-copy-button` - Positioned at top-right
- Add button via JavaScript if desired
- Matches design system button styling

### Custom Language Label
Currently hardcoded to "LaTeX" via CSS:
```css
.CodeMirror::before {
  content: 'LaTeX';
}
```

Could be made dynamic via data attribute if needed:
```html
<div class="codemirror-wrapper" data-language="LaTeX">
  <textarea id="latex-editor-textarea"></textarea>
</div>
```

## Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS Grid and Flexbox used
- CSS custom properties (variables) required
- `::before`/`::after` pseudo-elements used

## Testing Checklist

- [ ] Light mode appearance matches design system
- [ ] Dark mode appearance matches design system
- [ ] "LaTeX" label visible and properly positioned
- [ ] Header bar renders correctly
- [ ] Line numbers properly styled
- [ ] Active line highlighting works
- [ ] Selection color matches design system
- [ ] User theme switching still functional
- [ ] No layout breaks or overflow issues
- [ ] Mobile responsive layout works
- [ ] Focus states visible and accessible
- [ ] Syntax highlighting colors appropriate

## Future Improvements

1. **Copy Button**: Add JavaScript to implement copy functionality
2. **Line Wrapping Indicator**: Visual indicator for wrapped lines
3. **Search Widget Styling**: Style CodeMirror search dialog
4. **Custom Scrollbars**: Match design system scrollbar styling
5. **Minimap**: Add code minimap for large documents
6. **Folding Indicators**: Style code folding gutters

## Maintenance Notes

- Keep CSS in sync with design system color updates
- Test with new CodeMirror versions
- Update Zenburn colors if design system palette changes
- Monitor for conflicts with CDN-loaded themes
- Update documentation if new features added

## References

- Design System Code Blocks: `/static/css/common/code-blocks.css`
- CodeMirror Docs: https://codemirror.net/5/doc/manual.html
- LaTeX Mode: https://codemirror.net/5/mode/stex/
- SciTeX Typography Vars: `/static/css/common/typography-vars.css`
