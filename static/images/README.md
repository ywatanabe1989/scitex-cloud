# SciTeX Image Assets

This directory contains image assets used in the SciTeX website.

## SVG Icons

We use SVG icons for product representation. These follow a consistent design pattern:

- `scitex-cloud-icon.svg` - Cloud storage and platform icon
- `scitex-code-icon.svg` - Code editor and analysis icon
- `scitex-doc-icon.svg` - Document and LaTeX icon
- `scitex-engine-icon.svg` - AI engine icon
- `scitex-viz-icon.svg` - Data visualization icon
- `scitex-search-icon.svg` - Research search icon

All icons follow these design guidelines:
- Primary color: #4a6baf (SciTeX blue)
- Secondary color: #90b1e2 (SciTeX light blue) at 30% opacity for fills
- 64x64 pixel viewBox
- 3px stroke width for primary outlines

## Usage

These icons are used throughout the site, particularly on the landing page to represent different SciTeX products and modules.

Example usage in HTML:
```html
<img src="/static/images/scitex-cloud-icon.svg" alt="SciTeX Cloud" width="64" height="64">
```

## Notes for Designers

When creating new icons, please maintain consistency with the existing design language:
- Use the SciTeX color palette
- Maintain simple, clean lines
- Use consistent stroke widths
- Avoid gradients or complex effects that may not scale well

---

*Last updated: May 21, 2025*