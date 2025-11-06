# TypeScript Watch Mechanism - How Change Detection Works

## Quick Answer
TypeScript watch uses **Node.js `fs.watch` API** to monitor file system events (inotify on Linux). When you save a `.ts` file, the OS notifies Node.js, which triggers recompilation.

## The Stack

```
┌─────────────────────────────────────────────┐
│ 1. File System (Linux kernel inotify)      │
│    Detects: file write, modify, rename     │
└──────────────────┬──────────────────────────┘
                   │ OS notification
                   ↓
┌─────────────────────────────────────────────┐
│ 2. Node.js fs.watch()                       │
│    Wraps inotify in JavaScript API          │
└──────────────────┬──────────────────────────┘
                   │ JavaScript callback
                   ↓
┌─────────────────────────────────────────────┐
│ 3. TypeScript Compiler (tsc --watch)       │
│    • Receives file change event            │
│    • Validates against include patterns    │
│    • Performs incremental compilation      │
└─────────────────────────────────────────────┘
```

## Configuration: What Files Are Watched?

From `tsconfig/tsconfig.all.json`:

```json
{
  "include": [
    "../static/ts/**/*",           // All *.ts in static/ts/
    "../apps/*/static/*/ts/**/*"   // All *.ts in apps/*/static/*/ts/
  ],
  "exclude": [
    "node_modules",
    "../static/js",                // Ignore compiled output
    "../apps/*/static/*/js"
  ]
}
```

**What this means:**
- Watches: `~/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/**/*.ts`
- Watches: `~/proj/scitex-cloud/apps/project_app/static/project_app/ts/**/*.ts`
- Watches: `~/proj/scitex-cloud/static/ts/**/*.ts`
- Ignores: All `.js` files, `node_modules`

## Command Running

```bash
npm run build:all:watch
# → executes: tsc -p tsconfig.all.json --watch
```

**Process:**
1. Initial compilation of all matched files
2. Sets up file watchers on all directories
3. Enters infinite loop, waiting for fs events
4. On change → incremental recompile → back to waiting

## Real Example from Logs

```
8:53:22 AM - Found 0 errors. Watching for file changes.
[You edit: apps/writer_app/static/writer_app/ts/compilation/compilation.ts]
[File saved in your editor]
[inotify triggers fs.watch callback]
8:55:53 AM - File change detected. Starting incremental compilation...
[TypeScript parses only changed file + dependencies]
[Compiles .ts → .js]
8:55:54 AM - Found 0 errors. Watching for file changes.
```

**Time taken: ~1 second** ⚡

## Docker Volume Mount & File System Events

**Critical:** Docker volume mounts preserve inotify events!

```yaml
# docker-compose.yml
volumes:
  - ../../..:/app:cached
```

**How it works:**
1. You edit file on **host** → file system write
2. Linux kernel generates **inotify event**
3. Docker bind mount ensures container sees **same inode**
4. Node.js `fs.watch` in **container** receives the event
5. TypeScript compiler reacts immediately

## Incremental Compilation = Speed

TypeScript watch is **fast** because:
- **Keeps AST in memory** - doesn't re-parse unchanged files
- **Caches type information** - reuses previous type checking results
- **Only recompiles affected files** - changed file + files that import it
- **No disk I/O for unchanged files**

Example:
- Full build: ~10 seconds (all 50+ .ts files)
- Incremental: ~1 second (1 file + a few dependencies)

## Monitoring & Debugging

```bash
# See real-time compilation (on host)
tail -f ./logs/tsc-watch-all.log

# Check what process is watching
docker compose exec web ps aux | grep 'tsc.*watch'

# Output:
# root  58  35.0  1.0  1212676  266364  ?  Sl  08:53  0:15 \
#   node /app/tsconfig/node_modules/.bin/tsc -p tsconfig.all.json --watch

# List all files being watched
docker compose exec web bash -c "cd /app/tsconfig && tsc -p tsconfig.all.json --listFiles" | wc -l
```

## Under the Hood: fs.watch

Node.js provides two APIs:
1. **`fs.watch()`** - Uses OS-level events (inotify/FSEvents/ReadDirectoryChangesW)
2. **`fs.watchFile()`** - Polls via stat() - slower, more reliable

TypeScript uses **`fs.watch()`** by default for performance.

On Linux, this translates to:
```c
// Simplified C pseudocode of what happens
int fd = inotify_init();
inotify_add_watch(fd, "/app/apps/writer_app/static/writer_app/ts/",
                  IN_MODIFY | IN_CLOSE_WRITE);
while (1) {
    read(fd, &event, sizeof(event));  // Blocks until file change
    callback(event.name);              // Triggers TypeScript recompile
}
```

## Performance Characteristics

| Scenario | Detection Time | Compilation Time |
|----------|---------------|------------------|
| Single file change | < 100ms | ~1 sec |
| Multiple file save | < 100ms | ~2-3 sec |
| New file added | < 100ms | ~1 sec |
| File deleted | < 100ms | 0 sec (just removes from watch) |

## Common Issues

### Watch Not Triggering?
```bash
# Check if process is running
docker compose exec web ps aux | grep tsc

# Check system limits (host)
cat /proc/sys/fs/inotify/max_user_watches  # Should be > 8192

# Increase if needed
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Too Many Files?
If watching 1000+ files:
```bash
# TypeScript may need more watchers
# Linux default: 8192
# Recommended for large projects: 524288
```

## Summary

**Change Detection Chain:**
```
Editor Save
  → Linux inotify event
    → Docker bind mount (same inode)
      → Node.js fs.watch callback
        → TypeScript compiler incremental build
          → Compiled .js written to disk
            → Django auto-reload (optional)
```

**Key Insight:** It's **event-driven**, not polling. The OS tells Node.js immediately when a file changes. This is why it's so fast and responsive.
