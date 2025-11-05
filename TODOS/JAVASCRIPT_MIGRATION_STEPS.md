<!-- ---
!-- Timestamp: 2025-11-06 06:42:50
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/JAVASCRIPT_MIGRATION_STEPS.md
!-- --- -->

Migration from javascript to typescript is not complete yet. Please understand the rules:

``` plaintext
/home/ywatanabe/proj/scitex-cloud/RULES:
drwxr-xr-x  3 ywatanabe ywatanabe 4.0K Nov  5 22:05 .
drwxr-xr-x 32 ywatanabe ywatanabe 4.0K Nov  5 23:05 ..
-rw-r--r--  1 ywatanabe ywatanabe  44K Nov  4 13:50 00_DJANGO_ORGANIZATION_FULLSTACK.md
-rw-r--r--  1 ywatanabe ywatanabe 9.8K Nov  4 14:14 01_DJANGO_ORGANIZATION_FULLSTACK_CHECKLIST.md
-rw-r--r--  1 ywatanabe ywatanabe 1.4K Nov  5 19:56 02_TYPESCRIPT_HOT_BUILDING_IN_DEVELOPMENT.md
-rw-r--r--  1 ywatanabe ywatanabe 6.3K Nov  5 21:25 03_TYPESCRIPT_WATCH_MECHANISM.md
-rw-r--r--  1 ywatanabe ywatanabe 6.8K Nov  5 22:05 04_CONSOLE_LOG_FEEDBACK_IN_DEVELOPMENT.md
```


## How to migrate

1. Writing pure javascirpt is prohibited.
2. Old javascript codes are moved to js-potentiall-legacy directories
3. When not found error raised:
   1. Check subdirectories. Typescript is more organized. Type script structure is correct and follow all the time.
   2. If only legacy javascript found, please implement typescript equivalent (and improvement), update path in template if needed, and recompile typescript.
3. No inline <script> tag accepted in html files. However, exception is when Django template tags are included and necessary. If there is room for improvement - factoring out to typescript -,, please work on that.

## Example
Error found:

```
GET http://127.0.0.1:8000/static/project_app/js/profile.js net::ERR_ABORTED 404 (Not Found)
```

Then, we might find:

`/static/project_app/js-potentially-legacy/profile.js`

but also, we realize 

`/static/project_app/ts/users/profile.ts`.

In that case, the ts is correct!

## Systematic Migration Procedure

Check files manually one by one, from root to app level:

### Phase 1: Root-Level Static Files
Location: `./static/`

```bash
# Check TypeScript sources
ls -la static/ts/

# Check compiled JavaScript
ls -la static/js/

# Check legacy JavaScript (if exists)
ls -la static/js-potentially-legacy/
```

**For each file:**
1. ✅ Check if TypeScript source exists in `static/ts/`
2. ✅ Check if compiled correctly to `static/js/`
3. ✅ Verify templates reference correct path (organized subdirectory structure)
4. ❌ If only legacy JS exists → Implement TypeScript equivalent

### Phase 2: App-Level Static Files
Location: `apps/*/static/*/`

Check each app systematically:
- `apps/accounts_app/static/accounts_app/`
- `apps/auth_app/static/auth_app/`
- `apps/code_app/static/code_app/`
- `apps/core_app/static/core_app/`
- `apps/dev_app/static/dev_app/`
- `apps/project_app/static/project_app/` ← **Priority (largest app)**
- `apps/scholar_app/static/scholar_app/`
- `apps/writer_app/static/writer_app/`

**For each app:**
```bash
# Example for project_app
ls -la apps/project_app/static/project_app/ts/
ls -la apps/project_app/static/project_app/js/
ls -la apps/project_app/static/project_app/js-potentially-legacy/
```

**For each file in the app:**
1. ✅ Check TypeScript source exists in `ts/` subdirectory
2. ✅ Check compiled correctly to `js/` subdirectory
3. ✅ Find all templates that reference this file:
   ```bash
   grep -r "js/filename.js" apps/*/templates/
   ```
4. ✅ Verify template paths match TypeScript structure (subdirectories)
5. ❌ If only legacy JS exists → Create TypeScript version with improvements

### Phase 3: Template Verification
```bash
# Find all JavaScript references in templates
find apps/*/templates -name "*.html" -exec grep -l "\.js['\"]" {} \;

# Check for flat paths (potential issues)
grep -r "js/[^/]*\.js" apps/*/templates/ | grep -v "js-potentially-legacy"
```

**Verification checklist per reference:**
- [ ] Does TypeScript source exist?
- [ ] Is template path using organized subdirectory structure?
- [ ] Does compiled JS file exist at referenced path?
- [ ] Is the file in `.gitignore` (compiled) or tracked (legacy source)?

### Phase 4: Migration Priority Order

1. **Critical (breaks functionality):** Files causing 404 errors
2. **High priority:** Frequently used shared modules (project_app, core_app)
3. **Medium priority:** Feature-specific modules (writer_app, scholar_app)
4. **Low priority:** Admin/utility modules (dev_app, auth_app)

### Migration Status Tracking

Create a checklist for each app:

```markdown
## project_app
- [x] ts/shared/project_app.ts → js/shared/project_app.js
- [x] ts/shared/sidebar.ts → js/shared/sidebar.js
- [x] ts/users/profile.ts → js/users/profile.js
- [x] ts/repository/file_view.ts → js/repository/file_view.js
- [x] ts/repository/file_edit.ts → js/repository/file_edit.js
- [ ] ts/issues/form.ts → js/issues/form.js (needs migration)
- [ ] ...
```

<!-- EOF -->