# CSS Refactoring Plan for SciTeX-Cloud

## Current Issues

Based on our analysis, the current CSS organization has several issues:

1. **Duplicate Files**: Multiple versions of the same CSS files exist across directories
2. **Inconsistent Structure**: Mix of CSS file locations, naming conventions, and import patterns
3. **Parallel Structures**: CSS is split between `/static/css/` and `/static/common/css/`
4. **Unclear Entry Points**: Multiple CSS entry files like `index.css`, `main.css`, etc.
5. **Mixed Naming Conventions**: Inconsistent file naming across the codebase

## Refactoring Goals

1. Create a single, clear CSS structure with no duplications
2. Establish consistent naming conventions
3. Set up a clean import hierarchy with one main entry point
4. Organize CSS in a logical, modular way
5. Separate core styles from app-specific styles
6. Ensure backward compatibility with current templates

## Proposed CSS Structure

```
/static/
  /css/
    index.css                  # Single entry point for all CSS
    /base/                     # Global base styles
      _variables.css           # Design tokens and colors
      _reset.css               # CSS reset
      _typography.css          # Typography
      _layout.css              # Layout utilities
      _global.css              # Global styles
    /components/               # Reusable UI components
      _header.css
      _footer.css
      _hero.css
      _features.css
      _cards.css
      _buttons.css
      _forms.css
      _dropdown.css
    /utilities/                # Utility classes
      _spacing.css             # Margin/padding utilities
      _accessibility.css       # Accessibility enhancements
      _darkmode.css            # Dark mode theme
    /pages/                    # Page-specific styles
      _landing.css
      _repository.css
      _design-system.css
    /apps/                     # App-specific styles
      _cloud-app.css
      _code-app.css
      _doc-app.css
      _engine-app.css
      _search-app.css
      _viz-app.css
    /.old/                     # Legacy files (for reference)
```

## Refactoring Steps

### Phase 1: Preparation

1. **Create Backup**
   - Create `.old` directories within each CSS folder
   - Move duplicate files to `.old` directories for reference

2. **Analyze Template Dependencies**
   - Review all templates that include CSS
   - Document current CSS dependencies

### Phase 2: Restructure Files

1. **Create New Directory Structure**
   - Set up directories as per the proposed structure
   - Add empty placeholder files where needed

2. **Consolidate Core CSS Files**
   - Combine duplicate variables into a single source of truth
   - Merge component styles from different locations
   - Create updated import structure in `index.css`

3. **Normalize File Naming**
   - Standardize on kebab-case for all files (e.g., `site-header.css` not `siteHeader.css`)
   - Prefix partial files with underscore (e.g., `_buttons.css`)

### Phase 3: Update References

1. **Update Main Index File**
   - Ensure `index.css` imports all necessary files in the correct order
   - Add comments for clarity and future maintenance

2. **Test and Verify**
   - Check all pages to ensure styles are correctly applied
   - Fix any issues that arise from the restructuring

### Phase 4: Cleanup

1. **Remove Redundant Files**
   - After verifying functionality, remove duplicate files
   - Maintain `.old` directory for reference

2. **Update Documentation**
   - Create CSS coding standards document
   - Document CSS architecture for future developers

## Implementation Order

1. First, refactor the base styles (variables, reset, typography)
2. Next, consolidate component styles
3. Then, organize utility classes
4. Finally, manage page-specific and app-specific styles

## Backward Compatibility

- Maintain current import paths in the interim using symlinks where necessary
- Keep legacy CSS files until all templates are updated to use the new structure
- Add clear deprecation notices to legacy files

## Post-Refactoring Tasks

1. **Update Templates**: Gradually update templates to import from the new structure
2. **Documentation**: Create detailed documentation of the new CSS architecture
3. **Linting**: Add CSS linting rules to maintain consistency
4. **Code Review**: Review the refactored CSS to ensure quality and consistency

## Timeline

- Expected refactoring time: 1-2 days
- Testing and verification: 1 day
- Total estimated time: 2-3 days