# TypeScript Build Guide for SciTeX Cloud

## ⚠️ FOR AI AGENTS & DEVELOPERS: READ THIS FIRST

**DO NOT attempt to build TypeScript on the host machine!**

---

## Quick Reference

### ✅ What to Do When You See TypeScript Errors

```bash
# 1. Check the compilation log (accessible from host)
tail -f ./logs/tsc-watch-all.log

# 2. Edit the .ts source file to fix errors
vim apps/writer_app/static/writer_app/ts/index.ts

# 3. Save the file → container auto-compiles → check log again
tail -f ./logs/tsc-watch-all.log

# That's it! No manual build needed.
```

### ❌ What NOT to Do

```bash
# DON'T run these on host:
npm run build         # ❌ Blocked by check-build-environment.js
npm run build:all     # ❌ Blocked by check-build-environment.js
tsc                   # ❌ Will cause permission conflicts
cd tsconfig && npm run build:writer  # ❌ Blocked

# These run automatically in container - you don't need to run them!
```

---

## Architecture

### Auto-Build System
```
┌──────────────────────────────────────────────────────────────┐
│  Container: scitex-cloud-dev-web-1                           │
│                                                              │
│  Process (PID 75-76):                                        │
│    tsc -p tsconfig.all.json --watch --preserveWatchOutput    │
│                                                              │
│  Watches: /app/**/*.ts                                       │
│  Compiles: /app/**/*.js (auto-generated, gitignored)         │
│  Logs: /app/logs/tsc-watch-all.log                          │
│                                                              │
│  Status: ✓ Running automatically since container start      │
└──────────────────────────────────────────────────────────────┘
                            ▲  │
                            │  │ Volume Mount (bidirectional)
                            │  ▼
┌──────────────────────────────────────────────────────────────┐
│  Host: /home/ywatanabe/proj/scitex-cloud                     │
│                                                              │
│  Edit here: apps/*/static/*/ts/**/*.ts                       │
│  Read logs: ./logs/tsc-watch-all.log                         │
│  Build: NO! Let container handle it                          │
└──────────────────────────────────────────────────────────────┘
```

---

## Checking Build Status

### Is the watch process running?
```bash
# From host:
docker exec scitex-cloud-dev-web-1 ps aux | grep tsc

# Expected output:
# root  75  0.0  0.0  2684  1664  sh -c tsc -p tsconfig.all.json --watch
# root  76  24.9 1.0  1221624 269516  node .../tsc -p tsconfig.all.json --watch
```

### View compilation logs
```bash
# From host (recommended - easier):
tail -f ./logs/tsc-watch-all.log

# From inside container:
docker exec scitex-cloud-dev-web-1 tail -f /app/logs/tsc-watch-all.log

# Check for:
# "Found N errors" → Still have errors to fix in .ts files
# "✓ Moved X files" → Compilation successful
```

### Restart watch process if needed
```bash
# Restart container (watch auto-starts via entrypoint.sh)
cd deployment/docker/docker_dev
make ENV=dev restart
```

---

## File Organization

### Source Files (.ts)
```
apps/writer_app/static/writer_app/ts/
├── index.ts              # Main entry point
├── editor/
│   └── index.ts
├── modules/
│   ├── editor.ts
│   └── ... (50+ files)
└── shared/
    └── utils.ts
```

### Compiled Files (.js) - Auto-Generated, Gitignored
```
static/js/                    # DO NOT EDIT THESE
apps/writer_app/static/writer_app/js/
├── index.js                  # Auto-generated from index.ts
├── index.js.map              # Source map
├── index.d.ts                # Type definitions
└── ...
```

---

## Common Scenarios

### Scenario 1: "I found TypeScript errors"
```bash
# ✅ CORRECT:
# 1. Check log to see errors
tail -f ./logs/tsc-watch-all.log

# 2. Edit .ts file to fix
vim apps/writer_app/static/writer_app/ts/index.ts

# 3. Save → watch auto-compiles → check log

# ❌ WRONG:
npm run build  # DON'T! Check will block you
```

### Scenario 2: "Compiled .js file has issues"
```bash
# ✅ CORRECT:
# Never edit .js files! Edit the .ts source instead
vim apps/writer_app/static/writer_app/ts/index.ts  # Edit source

# ❌ WRONG:
vim static/js/index.js  # DON'T edit generated files!
```

### Scenario 3: "Permission denied on .js files"
```bash
# This means someone tried to build on host (wrong!)

# ✅ CORRECT:
# Delete corrupted files, let container rebuild
docker exec scitex-cloud-dev-web-1 rm -rf /app/static/js/collaboration/
# Watch process will auto-rebuild within seconds

# ❌ WRONG:
sudo chown ... # Treating symptom, not cause
```

---

## For AI Agents: Decision Tree

```
When asked to build TypeScript:
├─ Are we fixing TypeScript errors?
│  ├─ YES → Edit .ts files, let watch process compile
│  └─ NO → Check if watch is running: docker exec ... ps aux | grep tsc
│
├─ Do we need to run npm commands?
│  ├─ For linting → npm run lint (host is fine)
│  ├─ For formatting → npm run format (host is fine)
│  └─ For building → NO! Use watch process in container
│
└─ Seeing EACCES errors?
   └─ STOP trying to build on host!
      └─ Read this file again
```

---

## Preventive Measures in Place

1. ✅ **package.json check** - `prebuild` hook blocks host builds
2. ✅ **check-build-environment.js** - Smart detection (Docker vs host)
3. ✅ **Documentation** - This file + RULES/ directory
4. ✅ **.gitignore** - All .js files ignored (can't commit by mistake)
5. ✅ **Logs accessible from host** - No need to enter container

---

## Emergency: Watch Process Not Running?

```bash
# Check if it's running
docker exec scitex-cloud-dev-web-1 ps aux | grep tsc

# If not running, restart container
cd deployment/docker/docker_dev
docker compose restart web

# Watch process auto-starts via /entrypoint.sh
```

---

## Key Takeaways

1. **Never build on host** - The check will stop you
2. **Edit .ts, never .js** - .js files are auto-generated
3. **Watch process is automatic** - No manual intervention needed
4. **Logs are accessible** - Check ./logs/tsc-watch-all.log from host
5. **Errors? Fix .ts source** - Not the compiled .js files

---

**Last Updated:** 2025-11-18
**Related Docs:** RULES/02_TYPESCRIPT_HOT_BUILDING_IN_DEVELOPMENT.md
