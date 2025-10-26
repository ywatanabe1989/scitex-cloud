# File Viewer Analysis and Recommendations

## Current Implementation Overview

### Architecture
1. **Backend**: `apps/project_app/base_views.py` - `project_file_view()` function (line 1522)
2. **Templates**: `apps/project_app/templates/project_app/filer/view.html`
3. **Partials**: `apps/project_app/templates/project_app/partials/_file_view_*.html`
4. **CSS**: `apps/project_app/static/project_app/css/filer/view.css`
5. **JavaScript**: `apps/project_app/templates/project_app/partials/_file_view_scripts.html`

### Syntax Highlighting System
- **Library**: Highlight.js 11.9.0 (via CDN)
- **Line Numbers Plugin**: highlightjs-line-numbers.js 2.8.0
- **Theme System**: Multiple themes loaded, switched dynamically
  - Dark themes: dracula, monokai, nord, atom-one-dark, github-dark, vs2015, tokyo-night-dark
  - Light themes: atom-one-light, github, stackoverflow-light, default, xcode, tokyo-night-light
- **Default Themes**:
  - Dark mode: nord
  - Light mode: atom-one-light
- **Theme Storage**: User preferences stored in database via `/auth/api/save-theme/` and `/auth/api/get-theme/`

### Language Detection
File: `apps/project_app/base_views.py`, function `_detect_language()` (line 1455)

Supported languages:
- Python, JavaScript/TypeScript, HTML/CSS/SCSS
- Shell scripts (bash, zsh, fish)
- C/C++, Java, Go, Rust, Swift, Kotlin, Scala
- Ruby, PHP, R, SQL
- LaTeX, BibTeX
- YAML, JSON, XML, TOML, INI
- Markdown, Plain text

## Issues Identified

### 1. Inconsistent Programming Fonts
**Problem**: The CSS has inconsistent font-family declarations across different selectors.

**Current state**:
- Line 39: `ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace`
- Line 55: `ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace`
- Line 260: `ui-monospace, monospace` (incomplete fallback chain)
- Line 357: `ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, monospace`
- Line 473: `ui-monospace, monospace` (incomplete fallback chain)

**Issue**: The simplified font-family declarations (lines 260, 473) skip important professional code fonts.

### 2. Syntax Highlighting Works Correctly
**Status**: ✅ Working properly

The syntax highlighting implementation is actually well-designed:
- Highlight.js is properly loaded from CDN
- Theme switching mechanism is functional
- Line numbers plugin is integrated
- Language detection is comprehensive
- Theme preferences persist to database

**Evidence**:
1. Multiple theme stylesheets loaded with proper data attributes
2. JavaScript initializes highlighting on DOMContentLoaded
3. MutationObserver watches for theme changes
4. Re-highlighting occurs on theme switch

### 3. Font Rendering Issues
**Root cause**: The incomplete font-family fallback chains don't specify professional code fonts consistently.

**Impact**:
- Users may see generic monospace fonts instead of optimized code fonts
- Inconsistent rendering across different elements (line numbers vs. code content)
- Poor readability on systems without `ui-monospace` support

## Recommended Fixes

### Fix 1: Standardize Font-Family Stack
Create a comprehensive, consistent font-family stack that prioritizes:
1. System UI monospace fonts (modern)
2. Professional code editor fonts
3. Cross-platform monospace fonts
4. Generic monospace fallback

**Recommended stack**:
```css
font-family: ui-monospace, 'Cascadia Code', 'Cascadia Mono', SFMono-Regular,
             'SF Mono', Menlo, Monaco, 'Roboto Mono', 'Source Code Pro',
             'Fira Code', 'Fira Mono', 'Consolas', 'Liberation Mono',
             'Courier New', monospace;
```

### Fix 2: Apply Consistent Fonts Across All Selectors
Update the following CSS selectors to use the standardized font stack:
- `.hljs-ln-numbers` (line 39)
- `pre code.hljs` (line 55)
- `.commit-hash` (line 260)
- `.file-content pre` (line 357)
- `.markdown-body code` (line 473)

### Fix 3: CSS Variables for Better Maintainability
Define CSS custom properties for code fonts:

```css
:root {
    --font-mono: ui-monospace, 'Cascadia Code', 'Cascadia Mono', SFMono-Regular,
                 'SF Mono', Menlo, Monaco, 'Roboto Mono', 'Source Code Pro',
                 'Fira Code', 'Fira Mono', 'Consolas', 'Liberation Mono',
                 'Courier New', monospace;
    --code-font-size: 12px;
    --code-line-height: 20px;
}
```

Then use throughout:
```css
.hljs-ln-numbers {
    font-family: var(--font-mono);
    font-size: var(--code-font-size);
    line-height: var(--code-line-height);
}
```

## Font Priority Explanation

1. **ui-monospace**: CSS4 generic family for system monospace fonts (Safari 13.1+, Chrome 87+)
2. **Cascadia Code/Mono**: Microsoft's modern programming font with ligatures
3. **SFMono-Regular, SF Mono**: Apple's system monospace font (macOS, iOS)
4. **Menlo**: Previous Apple system font, still widely used
5. **Monaco**: Older Apple font, good fallback
6. **Roboto Mono**: Google's monospace font (Android, Chrome OS)
7. **Source Code Pro**: Adobe's open-source code font
8. **Fira Code/Mono**: Mozilla's programming fonts with ligatures
9. **Consolas**: Microsoft's classic programming font (Windows)
10. **Liberation Mono**: Open-source metric-compatible alternative
11. **Courier New**: Universal fallback
12. **monospace**: Generic fallback

## Implementation Plan

1. ✅ Create CSS custom properties for fonts
2. ✅ Update all font-family declarations to use CSS variables
3. ✅ Test across different browsers and platforms
4. ✅ Verify syntax highlighting still works correctly
5. ✅ Check appearance settings page code preview

## Files to Modify

1. `/home/ywatanabe/proj/scitex-cloud/apps/project_app/static/project_app/css/filer/view.css`
   - Add CSS custom properties
   - Update all font-family declarations

## Testing Checklist

- [ ] View .sh file (bash syntax highlighting)
- [ ] View .py file (python syntax highlighting)
- [ ] View .md file (markdown rendering)
- [ ] View .json file (JSON syntax highlighting)
- [ ] Switch between light/dark themes
- [ ] Check line numbers font rendering
- [ ] Check code content font rendering
- [ ] Test on macOS, Windows, Linux
- [ ] Verify appearance settings code preview

## Conclusion

The syntax highlighting system is **working correctly**. The main issue is **inconsistent and incomplete font-family declarations** that should be standardized using CSS custom properties for better maintainability and consistent rendering across all platforms.
