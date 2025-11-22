# Changelog

All notable changes to SciTeX Cloud will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.2-alpha] - 2025-11-22

### Assets & Media
- **Static Assets**: Added comprehensive branding assets (74 files)
  - SciTeX logos in multiple formats (PNG, SVG, PDF)
  - Module-specific icons (Scholar, Writer, Code, Vis, Cloud, Explore)
  - Alignment tool icons (align, distribute)
  - Hero background, favicons, and design assets
- **Landing Page Videos**: Added demo videos for public landing page (~24MB total)
  - Scholar module demonstration (16MB)
  - Writer module demonstration (4.8MB)
  - Code module demonstration (1.4MB)
  - Cloud platform demonstration (1.4MB)
  - Visualization module demonstration (267KB)

### Infrastructure
- Updated .gitignore to track landing page demo videos while excluding user media
- Properly configured TypeScript build artifact exclusion

### Production Deployment
- CI/CD improvements for TypeScript builds
- Production infrastructure fixes
- User management commands and utilities

## [0.3.1-alpha] - 2025-11-22

### UI/UX Improvements
- **Header Logo**: Fixed logo visibility in header, now using standard scitex-logo.png
- **Icon Consistency**: Standardized all navigation icon colors with consistent warm yellowish tone
- **Layout Reorganization**: Moved project selector to prominent position after logo (GitHub-style)
- **Navigation Spacing**: Fixed spacing issues for Scholar, Code, and Vis navigation items
- **Icon Sizing**: Added min-width and flex-shrink properties to prevent icon shrinking
- **Explore Icon**: Changed from SVG to FontAwesome compass icon for better color consistency

### Bug Fixes
- Fixed cramped spacing allocation for IMG-based navigation icons
- Improved icon-to-text gap from 6px to 8px for better readability
- Ensured consistent min-width for all navigation items

## [0.3.0-alpha] - 2025-11-22

### Major Features
- **Sigma Editor Integration**: Major refactor adding Sigma editor for enhanced collaboration
- **Collaboration Features**: Real-time collaboration capabilities across the platform
- **Development Tools**: Enhanced development utilities and debugging tools
- **Hot Reload System**: Implemented django-browser-reload for Python/HTML hot reloading

### Writer Module
- Fixed compilation and section-specific previews
- Added panel resizer with theme-aware editor
- Improved Writer editor controls and UI
- Enhanced section loading and PDF display
- Hierarchical dropdown sections
- Font size adjustment and auto-preview features
- Theme-responsive scrollbars and draggable panel resizer

### Infrastructure & DevOps
- TypeScript build preventive measures
- Fixed visitor pool and Docker build issues
- Improved template creation and directory structure
- Enhanced SSH architecture and implementation
- Production SSL/HTTPS support
- Docker health check improvements
- Comprehensive logging infrastructure

### UI/UX Improvements
- Selection mode for Element Inspector
- Enhanced BibTeX diff display
- Alignment tools and collaboration styling
- Improved figure versioning
- Better landing page design
- Code block styling improvements with syntax highlighting
- Theme-aware components across all modules

### Bug Fixes
- Fixed CSRF token handling in Writer
- Resolved TypeScript compilation issues
- Fixed terminal newline rendering for script output
- Fixed landing page template rendering
- Improved public landing page to reflect Code and Vis availability
- Fixed project template creation

### Documentation
- Updated bulletin board and archived migration docs
- Added SSH architecture documentation
- Cleaned up obsolete documentation
- Updated project rules and organization

### Development Experience
- Implemented TypeScript watch mechanism
- Added preventive TypeScript build measures
- Improved git status API endpoint
- Enhanced Makefile for better development workflow
- Better hot-reload integration for frontend development

### Infrastructure
- Visitor pool system (visitor-001 to visitor-032)
- Demo project pool for anonymous visitors
- Environment variable consolidation to SECRET/ directory
- Standardized SCITEX_CLOUD_ prefix for environment variables

### Removed
- Obsolete temporary files from project root
- Compiled TypeScript outputs cleaned from git tracking
- Old archive directories
- Redundant configuration files

## [0.2.0-alpha] - 2025-10-23

### Documentation & Performance
- Added README.md files for all 18 apps with clear single-responsibility descriptions
- Optimized database queries in search_app (eliminated N+1 queries)
- Optimized database queries in code_app editor view
- Fixed model duplication issues across apps
- Completed core_app → workspace_app migration
- All Django migrations applied successfully
- Authentication verified and working

### App Documentation
Complete documentation for:
- accounts_app, auth_app, code_app, dev_app
- docs_app, donations_app, gitea_app, integrations_app
- organizations_app, permissions_app, project_app, public_app
- scholar_app, search_app, social_app, vis_app, writer_app, workspace_app

## [0.1.2] - 2025-10-23

### Initial Release Features
- Complete SciTeX Cloud platform foundation
- Scholar module for literature management
- Writer module for LaTeX collaboration
- Code module for analysis
- Viz module for visualization
- User authentication and authorization
- Project management system
- Git repository integration via Gitea
- Docker-based deployment

[0.3.0-alpha]: https://github.com/ywatanabe1989/scitex-cloud/compare/v0.2.0...v0.3.0
[0.2.0-alpha]: https://github.com/ywatanabe1989/scitex-cloud/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/ywatanabe1989/scitex-cloud/releases/tag/v0.1.2
