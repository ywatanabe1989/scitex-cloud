#!/usr/bin/env node
/**
 * Check if TypeScript build is running in correct environment
 *
 * ALLOWED: Inside Docker container
 * BLOCKED: On host machine
 *
 * Why? Building on host causes permission conflicts with volume-mounted files.
 */

const fs = require('fs');
const path = require('path');

// Method 1: Check if /.dockerenv exists (standard Docker indicator)
const isInDocker = fs.existsSync('/.dockerenv');

// Method 2: Check if we're in /app directory (container path)
const isInAppDir = process.cwd().startsWith('/app');

// Method 3: Check if running as root (container usually runs as root)
const isRoot = process.getuid && process.getuid() === 0;

const inContainer = isInDocker || isInAppDir || isRoot;

if (!inContainer) {
  console.error(`
╔═══════════════════════════════════════════════════════════════════════╗
║  ⚠️  WARNING: TypeScript build should run INSIDE Docker container!   ║
╚═══════════════════════════════════════════════════════════════════════╝

❌ Building on host will cause permission conflicts and is not the intended workflow.

✅ CORRECT WORKFLOW:
   1. Edit .ts files on host (they auto-sync to container)
   2. Container's "tsc --watch" compiles automatically
   3. Compiled .js files sync back to host
   4. Check compilation: tail -f ./logs/tsc-watch-all.log

📚 See: RULES/02_TYPESCRIPT_HOT_BUILDING_IN_DEVELOPMENT.md
📚 See: RULES/TYPESCRIPT_BUILD_INSTRUCTIONS_FOR_AI.md

To check watch process status:
  docker exec scitex-cloud-dev-web-1 ps aux | grep tsc

To view compilation logs from host:
  tail -f ./logs/tsc-watch-all.log

If you REALLY need to build on host (not recommended):
  npm run force-build

`);
  process.exit(1);
}

// In container - allow build and show helpful info
console.log(`
╔═══════════════════════════════════════════════════════════════════════╗
║  ✓ Running in Docker container - TypeScript build allowed            ║
╚═══════════════════════════════════════════════════════════════════════╝

📋 AUTO BUILD INFO:
   - tsc --watch is running automatically in this container
   - Watches all .ts files and compiles on change
   - Check status: ps aux | grep tsc
   - View logs: tail -f /app/logs/tsc-watch-all.log
   - Logs also accessible from host: ./logs/tsc-watch-all.log

💡 TIP: You usually don't need to run manual builds!
   The watch process handles compilation automatically.
   Only run manual builds for:
   - Initial setup
   - After TypeScript config changes
   - Production deployment

`);
process.exit(0);
