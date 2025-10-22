<!-- ---
!-- Timestamp: 2025-10-22 13:45:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/SERVER_SCRIPT.md
!-- Status: COMPLETED ✅
!-- --- -->

## Requirement
We only need `./start.sh` - no flags needed for standard usage.
All necessary operations should be handled automatically.

## Implementation ✅

The `start.sh` script now automatically handles:
1. ✅ Kill existing processes on port 8000
2. ✅ Run database migrations
3. ✅ Collect static files
4. ✅ Start the server
5. ✅ Tail logs

## Usage

**Standard start (recommended):**
```bash
./start.sh
```
This automatically runs migrations, collects static, starts dev server, and shows logs.

**Quick testing (skip migrations):**
```bash
./start.sh --skip-migrate
```

**Background mode:**
```bash
./start.sh -d
```

**Production mode:**
```bash
./start.sh -p
```

## Changes Made
- Changed defaults: `do_migrate=true` and `do_collect_static=true`
- Added `--skip-migrate` and `--skip-static` flags for opt-out (not recommended)
- Updated help text to reflect automatic behavior
- Simplified usage examples

<!-- EOF -->