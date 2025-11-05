# TypeScript Hot Building in Development

## Architecture
- **Compiler runs**: Inside Docker container at `/app/tsconfig`
- **File sync**: Host ↔ Container (bidirectional via volume mount)
- **Process**: `tsc -p tsconfig.all.json --watch` (auto-starts on container init)
- **Logs**: Synced to `./logs/tsc-watch-all.log` on host

## How It Works
1. Edit `.ts` file on host → syncs to container
2. `tsc --watch` detects change → compiles `.ts` to `.js`
3. Compiled `.js` syncs back to host
4. Django auto-reload picks up changes

## Monitoring
```bash
# View compilation logs on host
tail -f ./logs/tsc-watch-all.log

# Check if watch process is running
docker compose exec web ps aux | grep tsc
```

## Important: Entrypoint Updates
The TypeScript watcher is started by `/entrypoint.sh` which is **copied into the image at build time**.

**Quick fix** (for running container):
```bash
# Copy updated entrypoint to running container
docker cp deployment/docker/docker_dev/entrypoint.sh scitex-cloud-dev-web-1:/entrypoint.sh
docker compose restart web
```

**Permanent fix** (requires rebuild):
```bash
cd deployment/docker/docker_dev
docker compose build web
docker compose up -d
```

## Troubleshooting
- TypeScript errors prevent compilation - check logs
- Fix errors in `.ts` files → watch auto-recompiles
- Watch not starting? Check entrypoint is up-to-date (see above)
- Restart container: `docker compose restart web`
