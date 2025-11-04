# JavaScript Directory - COMPILED OUTPUT

**⚠️ DO NOT EDIT FILES IN THIS DIRECTORY ⚠️**

This directory contains **auto-generated** JavaScript compiled from TypeScript sources.

---

## Source Files

All JavaScript in this directory is compiled from TypeScript sources in `../ts/`

### Build Process

```bash
# From: apps/project_app/static/project_app/
npx tsc

# Watch mode (auto-recompile):
npx tsc --watch
```

---

## File Mapping

| Compiled JS | TypeScript Source | Template |
|-------------|-------------------|----------|
| `file_view.js` | `../ts/file_view.ts` | `file_view.html` |
| `issues_detail.js` | `../ts/issues_detail.ts` | `issues_detail.html` |
| `pr_detail.js` | `../ts/pr_detail.ts` | `pr_detail.html` |
| _(21 files total)_ | | |

---

## Generated Files

For each `xxx.ts` source file, TypeScript generates:

- `xxx.js` - Compiled JavaScript (ES2020)
- `xxx.d.ts` - Type definitions for IDE support
- `xxx.js.map` - Source map for debugging

---

## To Make Changes

1. **Edit**: TypeScript source in `../ts/xxx.ts`
2. **Compile**: Run `npx tsc` or use watch mode
3. **Test**: Refresh browser - Django serves the compiled JS
4. **Commit**: Commit both `.ts` source and `.js` compiled files

---

## Why Commit Compiled JS?

1. **Production ready** - Django serves JS directly, no build step needed
2. **Easy deployment** - Just `git pull` and run
3. **Source maps** - Debugging links back to TypeScript sources

---

**Remember:** Always edit `../ts/` sources, never edit this directory!

<!-- EOF -->
