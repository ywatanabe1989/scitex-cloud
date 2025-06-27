# Feature Request: Naming and Branding Strategy for SciTeX

**Date**: 2025-05-23
**Priority**: High
**Category**: Branding & Identity

## Executive Summary

Develop a cohesive naming and branding strategy for the SciTeX ecosystem that:
- Replaces "products" with research-focused terminology
- Creates consistent naming across all components
- Establishes clear branding guidelines
- Ensures namespace availability across platforms

## Current Situation

### Existing Assets
- **Domain**: scitex.ai ✓
- **Email addresses**: admin@, support@, ywatanabe@, YusukeWatanabe@ ✓
- **GitHub Organization**: https://github.com/SciTeX-AI ✓
- **Twitter/X**: @SciTeX (display name), @SciTeX_AI (handle) ✓

### Current Component Names (Need Revision)
- SciTeX-Engine → Needs clearer name
- SciTeX-Doc → Too generic
- SciTeX-Code → Unclear purpose
- SciTeX-Viz → Good but could be clearer
- SciTeX-Search → Clear and good
- SciTeX-Cloud → Clear and good

## Proposed Solutions

### 1. Replace "Products" Terminology

Instead of "Products," use research-focused terms:

| Current | Proposed Options | Recommendation |
|---------|------------------|----------------|
| Products | Tools, Modules, Components | **Modules** |
| Product Page | Module Overview, Tool Details | **Module Overview** |
| Our Products | Research Modules, SciTeX Suite | **Research Modules** |
| Product Features | Module Capabilities | **Module Capabilities** |

**Rationale**: "Modules" emphasizes the modular, integrated nature of the ecosystem while avoiding commercial connotations.

### 2. Improved Component Naming

#### SciTeX-Engine → **SciTeX Studio**
- **Current**: `~/.emacs.d/lisp/emacs-claude-code`
- **Why**: "Studio" conveys an integrated research environment
- **Alternatives**: SciTeX Lab, SciTeX Workshop, SciTeX IDE

#### SciTeX-Doc → **SciTeX Manuscript**
- **Current**: `~/proj/scitex`
- **Why**: Clearly indicates academic paper preparation
- **Alternatives**: SciTeX Papers, SciTeX Publisher, SciTeX Author

#### SciTeX-Code → **SciTeX Compute**
- **Current**: `~/proj/mngs_repo`
- **Why**: Emphasizes computational research capabilities
- **Alternatives**: SciTeX Analysis, SciTeX Tools, SciTeX Python

#### SciTeX-Viz → **SciTeX Figures**
- **Current**: `~/proj/scitex/SigMacro`
- **Why**: Direct reference to publication figures
- **Alternatives**: SciTeX Graphics, SciTeX Plots, SciTeX Visuals

#### SciTeX-Search → **SciTeX Discover**
- **Current**: `~/proj/SciTeX-Search`
- **Why**: Emphasizes discovery and exploration
- **Alternatives**: Keep as SciTeX Search (already good)

#### SciTeX-Cloud → **SciTeX Cloud**
- **Current**: `~/proj/SciTeX-Cloud`
- **Why**: Already clear and appropriate
- **Status**: Keep as is

### 3. Complete Branding Architecture

```
SciTeX
├── SciTeX Studio    (Research Environment)
├── SciTeX Manuscript (Paper Preparation)
├── SciTeX Compute   (Scientific Computing)
├── SciTeX Figures   (Publication Graphics)
├── SciTeX Discover  (Literature Search)
└── SciTeX Cloud     (Web Platform)
```

### 4. Namespace Strategy

#### GitHub Repositories
```
github.com/SciTeX-AI/
├── scitex-studio     (formerly emacs-claude-code)
├── scitex-manuscript (formerly scitex)
├── scitex-compute    (formerly mngs)
├── scitex-figures    (formerly SigMacro)
├── scitex-discover   (formerly SciTeX-Search)
└── scitex-cloud      (current repo)
```

#### Package Names
- **PyPI**: `scitex-compute` (currently `mngs`)
- **npm**: `@scitex/studio`, `@scitex/cloud`
- **Emacs**: `scitex-studio.el`
- **Docker**: `scitex/studio`, `scitex/cloud`, etc.

#### Social Media Handles
- **Twitter/X**: @SciTeX_AI ✓
- **LinkedIn**: /company/scitex-ai
- **YouTube**: @SciTeXAI
- **Instagram**: @scitex.ai
- **Mastodon**: @scitex@scholar.social

### 5. Taglines and Messaging

**Main Tagline**: "Accelerate Scientific Discovery"

**Module-Specific Taglines**:
- Studio: "Your AI-Powered Research Environment"
- Manuscript: "From Draft to Publication"
- Compute: "Scientific Computing Made Simple"
- Figures: "Publication-Ready Visualizations"
- Discover: "Find What Others Miss"
- Cloud: "All Your Research, One Platform"

### 6. Visual Identity Guidelines

#### Logo Variations
- Full: "SciTeX" with icon
- Icon only: For small spaces
- Monochrome: For documents
- Module badges: Small icons for each module

#### Color Associations
- Studio: Blue (#4169E1) - Productivity
- Manuscript: Green (#28a745) - Growth
- Compute: Orange (#fd7e14) - Energy
- Figures: Purple (#6f42c1) - Creativity
- Discover: Teal (#20c997) - Discovery
- Cloud: Navy (#0d47a1) - Reliability

### 7. Website Updates

#### Navigation Changes
```html
<!-- Current -->
<nav>
  <a href="/products">Products</a>
</nav>

<!-- Proposed -->
<nav>
  <a href="/modules">Research Modules</a>
</nav>
```

#### Landing Page Copy
```
<!-- Current -->
"Check out our products"

<!-- Proposed -->
"Explore our research modules"
"Discover the SciTeX suite"
"Access powerful research tools"
```

### 8. Documentation Updates

Update all references:
- "Product documentation" → "Module documentation"
- "Product features" → "Module capabilities"
- "Product support" → "Module support"
- "Product updates" → "Module updates"

### 9. Legal Considerations

#### Trademark Strategy
1. Register "SciTeX" as primary mark
2. Consider registering key module names
3. Secure international domains (.com, .org, .io)

#### Domain Protection
- scitex.com (try to acquire)
- scitex.org (for open source)
- scitex.cloud (specific to cloud module)
- Regional: scitex.eu, scitex.asia

### 10. Implementation Checklist

- [ ] Update all website navigation from "Products" to "Modules"
- [ ] Rename GitHub repositories to new scheme
- [ ] Update PyPI package name (with redirect)
- [ ] Create visual assets for each module
- [ ] Update all documentation
- [ ] Implement 301 redirects for old URLs
- [ ] Update email signatures
- [ ] Create brand guidelines document
- [ ] Register additional social media handles
- [ ] Update all marketing materials

## Benefits

1. **Clarity**: Each module name clearly indicates its purpose
2. **Consistency**: Unified naming across all platforms
3. **Research Focus**: Terminology aligns with academic values
4. **Memorability**: Shorter, clearer names are easier to remember
5. **Scalability**: Naming scheme allows for future modules

## Migration Plan

### Phase 1: Immediate (No Breaking Changes)
1. Update website copy ("products" → "modules")
2. Create brand guidelines document
3. Design module icons

### Phase 2: Short Term (1 month)
1. Register new social media handles
2. Create GitHub repository redirects
3. Update documentation

### Phase 3: Long Term (3 months)
1. Migrate PyPI package with proper deprecation
2. Update all external references
3. Complete visual identity rollout

## Success Metrics

- User feedback on clarity of names
- Reduced support questions about module purposes
- Increased social media engagement
- Consistent brand recognition

## Conclusion

This naming strategy positions SciTeX as a serious research platform while making each module's purpose immediately clear. The shift from "products" to "modules" reinforces the academic, non-commercial nature of the project.