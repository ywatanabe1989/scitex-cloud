# Deployment Note: Plot Viewer Refactoring

## Summary

The `plot-viewer.ts` file has been successfully refactored from a monolithic 593-line file into 9 focused modules totaling 899 lines (all under 256 lines each).

## Changes Made

1. **Created modular structure:**
   - `types.ts` (77 lines) - Type definitions and constants
   - `data.ts` (122 lines) - CSV parsing and plot detection
   - `utils.ts` (64 lines) - Utility functions
   - `controls.ts` (133 lines) - UI controls management
   - `renderers.ts` (230 lines) - Canvas rendering orchestration
   - `plot-drawers.ts` (99 lines) - Individual plot type renderers
   - `export.ts` (24 lines) - Export functionality
   - `PlotViewer.ts` (109 lines) - Main orchestrator class
   - `index.ts` (41 lines) - Barrel exports and initialization

2. **Updated template:**
   - Changed from: `<script src="plot-viewer.js">`
   - Changed to: `<script type="module" src="plot-viewer/index.js">`

3. **Added tsconfig.json:**
   - Created `apps/public_app/static/public_app/tsconfig.json`

4. **Maintained backward compatibility:**
   - All global functions (`toggleSettingsPanel`, `updateSetting`, etc.) still work
   - No breaking changes to external API

## Deployment Steps Required

Due to root-owned files in the `js/tools/` directory, manual deployment is needed:

### Option 1: Docker Build (Recommended)
The Docker build process will handle permissions automatically. Just rebuild:
```bash
make ENV=dev restart
```

### Option 2: Manual Compilation
If you need to compile manually:

```bash
# 1. Navigate to public_app static directory
cd apps/public_app/static/public_app

# 2. Compile TypeScript
npx tsc -p tsconfig.json --outDir /tmp/plot-viewer-js

# 3. Fix ownership and permissions (requires sudo)
sudo chown -R ywatanabe:ywatanabe js/tools/
sudo chmod -R u+w js/tools/

# 4. Remove old and copy new files
rm -rf js/tools/plot-viewer
cp -r /tmp/plot-viewer-js/tools/plot-viewer js/tools/

# 5. Verify
ls -la js/tools/plot-viewer/
```

## Verification

After deployment, verify:

1. **TypeScript compilation:**
   ```bash
   cd apps/public_app/static/public_app
   npx tsc --noEmit
   ```
   Should show no errors for plot-viewer files.

2. **File line counts:**
   All files should be under 256 lines:
   ```bash
   find ts/tools/plot-viewer -name "*.ts" -exec wc -l {} +
   ```

3. **Browser test:**
   - Visit `/tools/plot-viewer/`
   - Upload CSV or click "try with demo data"
   - Verify plot renders correctly
   - Test settings panel functionality

## Files Modified

- `apps/public_app/static/public_app/ts/tools/plot-viewer.ts` (deleted, backed up as `.backup`)
- `apps/public_app/static/public_app/ts/tools/plot-viewer/` (new directory with 8 modules)
- `apps/public_app/templates/public_app/tools/plot-viewer.html` (updated script import)
- `apps/public_app/static/public_app/tsconfig.json` (new file)

## Rollback Plan

If issues arise:

1. Restore original file:
   ```bash
   mv apps/public_app/static/public_app/ts/tools/plot-viewer.ts.backup \
      apps/public_app/static/public_app/ts/tools/plot-viewer.ts
   ```

2. Revert template change:
   ```bash
   git checkout apps/public_app/templates/public_app/tools/plot-viewer.html
   ```

3. Recompile:
   ```bash
   cd apps/public_app/static/public_app
   npx tsc
   ```

## Notes

- Original monolithic file backed up as `plot-viewer.ts.backup` (gitignored)
- All TypeScript files pass type checking
- No runtime functionality changes
- Compiled JavaScript is in `/tmp/plot-viewer-js/` ready for deployment
- README.md included in module directory with full documentation

## Commit

```
commit: e14394d7
message: refactor(public_app): Split plot-viewer.ts into modules
```

---

Delete this file after successful deployment.
