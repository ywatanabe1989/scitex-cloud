# TypeScript Configuration

## Overview

This directory contains TypeScript configurations for the SciTeX Cloud project with **strict TypeScript-only enforcement**.

## Configuration Structure

### Base Configuration (tsconfig.base.json)
Single source of truth with strict settings:
- ✅ **`allowJs: false`** - Rejects .js files, enforces TypeScript-only
- ✅ **`strict: true`** - All strict type-checking enabled
- ✅ Type safety: noImplicitAny, strictNullChecks, etc.
- ✅ Code quality: noUnusedLocals, noUnusedParameters, etc.

### App-Specific Configurations
All extend base config, only override paths:

**tsconfig.json** - Root-level static files
- Compiles: `static/ts/**/*`
- Outputs: `static/js/`

**tsconfig.all.json** - All apps (used by npm run build:all)
- Compiles: `static/ts/**/*` + `apps/*/static/*/ts/**/*`
- Outputs: `.tsbuild/` (temporary, moved by post-build.js)

**tsconfig.project.json** - project_app only
- Compiles: `apps/project_app/static/project_app/ts/**/*`
- Outputs: `apps/project_app/static/project_app/js/`

**tsconfig.writer.json** - writer_app only
- Compiles: `apps/writer_app/static/writer_app/ts/**/*`
- Outputs: `apps/writer_app/static/writer_app/js/`

## Migration Principle

**STRICT TYPESCRIPT-ONLY:**
1. ❌ JavaScript files (.js) cannot be in `ts/` directories
2. ❌ JavaScript files will NOT compile (rejected by `allowJs: false`)
3. ✅ Only TypeScript files (.ts) are accepted
4. ✅ Legacy JavaScript must be in `js-potentially-legacy/` directories

## Build Commands

```bash
# Build all TypeScript files
npm run build:all

# Watch all files (hot-reload)
npm run watch:all

# Build specific app
npm run build:project   # project_app only
npm run build:writer    # writer_app only
npm run build:root      # root static/ only
```

## Compilation Output

TypeScript source (`ts/`) → Temporary (`.tsbuild/`) → Final location (`js/`)

1. **TypeScript compile:** `ts/**/*.ts` → `.tsbuild/**/*.js`
2. **Post-build script:** `.tsbuild/**/*.js` → `js/**/*.js`
3. **Result:** Clean `js/` directories with compiled code

## What Changed (2025-11-05)

### Before
- 4 separate configs with redundant settings
- `allowJs: true` in all configs (allowed .js to sneak in)
- Mixed strict/loose modes
- Duplication of 50+ lines per config

### After
- 1 base config + 3 app-specific extensions
- `allowJs: false` (strict TypeScript-only)
- Unified strict mode across all apps
- ~80% reduction in config duplication

### Impact
- ✅ TypeScript-only enforcement active
- ✅ Build scripts (post-build.js, watch-and-move.js) unaffected
- ✅ 44 type errors caught (previously hidden by loose mode)
- ✅ No .js files can compile from `ts/` directories

## Type Errors

With strict mode enabled, TypeScript catches real issues:

**Common errors to fix:**
1. `string | null` vs `string | undefined` (CSRF tokens)
2. Unused variables (strict unused checks)
3. Missing global type declarations (SCITEX_PROFILE_DATA, etc.)
4. Implicit any types
5. Null/undefined handling

These errors represent **real bugs** that would cause runtime issues. Fix them systematically.

## Directory Structure

```
tsconfig/
├── tsconfig.base.json      # Base config (STRICT, allowJs: false)
├── tsconfig.all.json        # All apps (extends base)
├── tsconfig.json            # Root static (extends base)
├── tsconfig.project.json    # project_app (extends base)
├── tsconfig.writer.json     # writer_app (extends base)
├── package.json             # Build scripts
├── post-build.js            # Moves compiled files to final location
├── watch-and-move.js        # Watch mode with file moving
└── README.md                # This file
```

## Best Practices

1. **Never add `allowJs: true`** to any config
2. **Always extend tsconfig.base.json** for new apps
3. **Fix type errors** instead of relaxing strict mode
4. **Keep build scripts** (.js) outside `ts/` directories
5. **Use proper type definitions** for all global variables

## Troubleshooting

### Error: "Cannot find module '@/utils'"
- Check `paths` mapping in app-specific config
- Verify TypeScript files exist at mapped location

### Error: "Property 'X' does not exist on type 'Window'"
- Add type declaration in `shared/global.d.ts`
- Declare interface extension for Window object

### Compilation succeeds but files not in js/
- Check post-build.js script execution
- Verify output paths in post-build.js match config

### Build scripts causing errors
- Build scripts should be .js files in `tsconfig/` directory
- They should NOT be in `ts/` directories
- They are NOT compiled by TypeScript

## Resources

- [TypeScript Strict Mode](https://www.typescriptlang.org/tsconfig#strict)
- [Module Resolution](https://www.typescriptlang.org/docs/handbook/module-resolution.html)
- [Project References](https://www.typescriptlang.org/docs/handbook/project-references.html)

---

**Last Updated:** 2025-11-05
**Migration Status:** TypeScript-only enforcement ACTIVE
