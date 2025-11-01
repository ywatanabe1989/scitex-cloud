# Common Scripts

Shared deployment scripts for all container environments.

## Scripts

### Container Lifecycle
- `entrypoint.sh` - Container initialization and startup
- `auto_collectstatic.sh` - Automatic static file collection

### Verification
- `verify_scitex_writer.sh` - Verify SciTeX Writer module
- `verify_uv.sh` - Verify UV package manager

### Maintenance
See `maintenance/README.md` for health check scripts.

## Usage

These scripts are automatically used by Docker containers. Manual execution:

```bash
# From container
./entrypoint.sh

# From host (for verification)
docker exec <container> /app/common/scripts/verify_scitex_writer.sh
```
