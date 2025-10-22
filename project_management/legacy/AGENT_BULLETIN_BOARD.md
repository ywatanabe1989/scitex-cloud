# Agent Bulletin Board

Coordination point for Claude Code agents working on SciTeX Cloud.

---

## CLAUDE-2025-10-16-03h (Web Developer & Refactoring)

### Completed
- [x] Shipped V1: Streamlined from 21 → 10 apps with auto-discovery
- [x] Created dev_app with design system at `/dev/design.html`
- [x] Organized templates with `global_*` prefix for shared partials
- [x] Fresh database in `./data/` with clean migrations
- [x] Added all 4 module demos to landing (Scholar, Writer, Code, Viz)
- [x] Created Developer icon (screwdriver SVG)
- [x] Standardized Code features to match other modules
- [x] Added docs_app with Documentation buttons
- [x] Added GitHub fallback for unbuilt Sphinx docs
- [x] Integrated Code demo video (1.4MB)
- [x] Light hero gradient applied
- [x] Balanced icons on demo titles
- [x] Section filtering in design system (default: Colors)

### Stats
- **36 commits** shipped in this session
- **Landing page**: Complete with 4 module demos
- **Design system**: Interactive filtering, Developer icon added
- **Template structure**: Clean skeleton with global partials
- **Auto-discovery**: Apps and URLs auto-register

### Issues Found
- Sphinx docs build failing (autosummary extension errors)
- Viz demo video script created but not executed yet
- Module pages (scholar, code, viz, writer) have 500 errors - need view implementations

### Recommendations
- Build Sphinx docs properly for each module
- Create Viz demo video using `scripts/create_viz_demo_video.sh`
- Fix module landing pages (currently 500 errors)
- Consider adding API documentation
- Test Documentation buttons after Sphinx builds

---

## CLAUDE-2025-10-23-01h (Interactive Support)

### Status
- Responding to user requests and inquiries
- Monitoring codebase state and recent changes
- Ready to assist with bugs, features, refactoring, or other tasks

### Observations
- Git status shows significant scholar_app refactoring in progress
- Multiple new untracked modules: `models/`, `services/`, `views/`, `api/`, `integrations/`, `tests/`
- Legacy code marked for deletion with new modular structure
- Refactoring summary available in `REFACTORING_SUMMARY.md`

### Next Actions
- Awaiting user request
- Ready to assist with ongoing refactoring or new tasks

---

## Next Agent

Please continue with:
1. Fix Sphinx documentation builds for all modules
2. Complete Viz demo video creation
3. Fix 500 errors on module landing pages
4. Test complete user flow from landing → demos → docs
5. Support user with scholar_app refactoring or other tasks

---

*Last updated: 2025-10-23 (UTC)*
