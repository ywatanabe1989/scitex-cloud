# TypeScript Build Instructions for AI Agents

## ⚠️ CRITICAL: DO NOT BUILD TYPESCRIPT ON HOST

**This document prevents common mistakes that waste time and cause permission conflicts.**

---

## Why This Matters

Building TypeScript on the host machine:
- ❌ Creates files owned by host user inside Docker volume-mounted directories
- ❌ Causes permission conflicts (EACCES errors)
- ❌ Breaks the automatic hot-reload workflow
- ❌ Is NOT part of the intended development workflow
- ❌ Wastes time on a non-issue

---

## The Correct Workflow

### ✅ What You SHOULD Do

```bash
# 1. Edit TypeScript files on host
vim apps/writer_app/static/writer_app/ts/index.ts

# 2. File automatically syncs to container via volume mount

# 3. Container's tsc --watch detects change and compiles

# 4. Compiled .js files sync back to host

# 5. Django auto-reload picks up changes

# DONE - No manual build needed!
```

### ❌ What You SHOULD NOT Do

```bash
# DON'T DO THIS - It will fail and waste time:
cd tsconfig
npm run build        # ❌ Blocked by prebuild hook
npm run build:all    # ❌ Blocked by prebuild hook
tsc                  # ❌ Will create permission conflicts

# These commands should ONLY run inside the Docker container
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  HOST MACHINE                                               │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Edit .ts files                                       │ │
│  │  - apps/writer_app/static/writer_app/ts/index.ts     │ │
│  │  - static/shared/ts/types/index.ts                   │ │
│  └───────────────────────────────────────────────────────┘ │
│                           │ Volume Mount (bidirectional)    │
│                           ▼                                 │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│  DOCKER CONTAINER (scitex-cloud-dev-web-1)                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  tsc --watch (runs automatically via entrypoint.sh)  │ │
│  │  - Watches: /app/**/*.ts                             │ │
│  │  - Compiles to: /app/**/*.js                         │ │
│  │  - Logs to: /app/logs/tsc-watch-all.log             │ │
│  └───────────────────────────────────────────────────────┘ │
│                           │ Volume Mount (bidirectional)    │
│                           ▼                                 │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│  HOST MACHINE                                               │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Compiled .js files appear automatically              │ │
│  │  - static/js/index.js (gitignored)                    │ │
│  │  - apps/*/static/*/js/*.js (gitignored)              │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## How to Fix TypeScript Errors (Correct Approach)

### Step 1: Identify Errors
```bash
# Check compilation log
tail -f ./logs/tsc-watch-all.log

# Or check in container
docker exec scitex-cloud-dev-web-1 tail -f /app/logs/tsc-watch-all.log
```

### Step 2: Fix TypeScript Source Files
```bash
# Edit the .ts file on host (NOT .js files!)
vim apps/writer_app/static/writer_app/ts/index.ts

# Example fixes:
# - Add missing type definitions
# - Fix type mismatches
# - Add missing properties to interfaces
# - Import missing modules
```

### Step 3: Watch Auto-Compilation
```bash
# The watch process automatically detects your changes and recompiles
# Check the log to verify compilation succeeded:
tail -f ./logs/tsc-watch-all.log

# Look for:
# "✓ Moved X files" - compilation successful
# "Found N errors" - still have issues to fix
```

---

## Monitoring the Watch Process

### Check if watch process is running
```bash
docker exec scitex-cloud-dev-web-1 ps aux | grep tsc
```

### Restart watch process if needed
```bash
# Restart the entire container (watch process auto-starts)
cd deployment/docker/docker_dev
make ENV=dev restart

# Or just restart web service
docker compose restart web
```

---

## Permission Issues? Here's Why

If you see `EACCES` errors when trying to build on host:

**Root Cause:**
- Compiled `.js` files were created inside Docker (owned by root)
- Host user can't overwrite them
- This is a SYMPTOM of trying to build in the wrong place

**Solution:**
- Don't try to build on host!
- Let the container's watch process handle it
- If files are corrupted, delete them and let container rebuild:
  ```bash
  # Inside container (safe):
  docker exec scitex-cloud-dev-web-1 rm -rf /app/static/js/
  # Watch process will automatically rebuild
  ```

---

## For AI Agents: Quick Reference

```python
# WHEN ASKED TO BUILD TYPESCRIPT:

if location == "host":
    response = "No! Read RULES/TYPESCRIPT_BUILD_INSTRUCTIONS_FOR_AI.md"
    action = "Edit .ts files only, let Docker watch process compile"

elif location == "docker_container":
    response = "Yes, tsc --watch is already running automatically"
    action = "Check logs: tail -f /app/logs/tsc-watch-all.log"

# WHEN SEEING TYPESCRIPT ERRORS:

if error_type == "compilation_error":
    fix = "Edit the .ts source file to fix the error"
    do_not = "Try to build manually or fix .js files"

elif error_type == "EACCES_permission":
    cause = "Someone tried to build on host (wrong!)"
    fix = "Delete corrupted .js files, let container rebuild"
```

---

## Common Mistakes to Avoid

1. **"Let me run npm run build to check for errors"**
   - ❌ Wrong! Check ./logs/tsc-watch-all.log instead

2. **"The .js file has errors, let me fix it"**
   - ❌ Wrong! Never edit .js files - they're auto-generated
   - ✅ Correct! Edit the .ts source file

3. **"I'll compile TypeScript to see if my fix works"**
   - ❌ Wrong! The watch process compiles automatically
   - ✅ Correct! Just save the .ts file and check the log

4. **"Permission denied on .js files, let me fix ownership"**
   - ❌ Wrong! Treating symptom, not cause
   - ✅ Correct! Stop trying to build on host

---

## References

- See: `RULES/02_TYPESCRIPT_HOT_BUILDING_IN_DEVELOPMENT.md`
- See: `RULES/03_TYPESCRIPT_WATCH_MECHANISM.md`
- See: `.gitignore` (all .js files are gitignored)

---

**Remember: If you're an AI agent and you find yourself wanting to run `npm run build` or `tsc` on the host, STOP and re-read this document!**
