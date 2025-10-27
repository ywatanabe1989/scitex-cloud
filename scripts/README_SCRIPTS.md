# Scripts Directory

This directory contains maintenance and verification scripts for SciTeX Cloud development.

## Available Scripts

### 1. Gitea API Verification Scripts

#### `check_gitea_api.py`
**Purpose:** Verify Gitea API connectivity and authentication

**Usage:**
```bash
# From project root
.venv/bin/python scripts/check_gitea_api.py
```

**What it does:**
- Tests basic Gitea API connectivity
- Verifies authentication with configured token
- Lists user repositories
- Tests repository creation endpoint (creates and deletes a test repo)

**Output:** Detailed test results with ✓/✗ indicators

---

#### `test_repo_creation.py`
**Purpose:** Test repository creation flow with cleanup

**Usage:**
```bash
# Default (creates _test_user/_test_repo, then cleans up)
.venv/bin/python scripts/test_repo_creation.py

# Custom user/repo with cleanup
.venv/bin/python scripts/test_repo_creation.py --username _test_user --repo _test_repo

# Skip cleanup (for debugging)
.venv/bin/python scripts/test_repo_creation.py --no-cleanup
```

**Features:**
- Creates test user and repository
- Automatically cleans up after testing
- Users with `_test` prefix are auto-deleted
- Use `--no-cleanup` to inspect created resources

**Output:** Step-by-step creation and cleanup results

---

#### `sync_django_gitea_users.py`
**Purpose:** Sync Django users to Gitea (run inside Docker container)

**Usage:**
```bash
# From project root
cd containers/docker
docker-compose -f docker-compose.dev.yml exec -T web python /app/scripts/sync_django_gitea_users.py
```

**What it does:**
- Queries all active Django users
- Checks if each user exists in Gitea
- Creates missing Gitea accounts
- Reports summary of created/existing/failed users

**Requirements:**
- Must run inside Docker container (has database access)
- Gitea token with `write:admin` scope (for user creation)

**Note:** If token lacks admin scope, provides instructions for manual user creation via Gitea web UI.

---

### 2. Screenshot Capture Scripts

#### `capture_screenshots.py`
**Purpose:** Capture screenshots for documentation

**Usage:**
```bash
.venv/bin/python scripts/capture_screenshots.py
```

See `README_SCREENSHOTS.md` for details.

---

#### `capture_demo_screenshots.py`
**Purpose:** Capture demo screenshots for presentations

**Usage:**
```bash
.venv/bin/python scripts/capture_demo_screenshots.py
```

---

#### `run_screenshots.sh`
**Purpose:** Shell wrapper for screenshot scripts

**Usage:**
```bash
./scripts/run_screenshots.sh
```

---

## Integration with Docker Deployment

### Current Integration

The `start_dev.sh` script (`containers/docker/start_dev.sh`) now includes:

1. **`verify_gitea_api()`** - Called during startup to verify Gitea configuration
2. **`create_gitea_users()`** - Attempts to create test users if token has admin scope

### Recommended Workflow

For Docker-based development:

1. **Start services:**
   ```bash
   cd containers/docker
   ./start_dev.sh -a start
   ```

2. **Verify Gitea API** (automatic during start, or manual):
   ```bash
   cd ../..  # back to project root
   .venv/bin/python scripts/check_gitea_api.py
   ```

3. **Sync users** (if needed):
   ```bash
   cd containers/docker
   docker-compose -f docker-compose.dev.yml exec -T web \
       python /app/scripts/sync_django_gitea_users.py
   ```

### For Deployment Scripts

The scripts in `deployment/scripts/` are for production deployment and maintenance.

The scripts in `scripts/` (this directory) are for:
- **Development:** Testing and verification during development
- **Docker:** Can be run from inside Docker containers
- **CI/CD:** Can be integrated into automated testing

**Compatibility:**
- ✓ Works with Docker deployment (via `docker exec`)
- ✓ Works with manual/systemd deployment (direct execution)
- ✓ Works in CI/CD pipelines

---

## Environment Variables Required

All scripts require these environment variables (loaded from `.env`):

```bash
SCITEX_CLOUD_GITEA_URL_DEV=http://127.0.0.1:3000
SCITEX_CLOUD_GITEA_TOKEN_DEV=<your_token>
SCITEX_CLOUD_TEST_USER_PASSWORD=<test_password>
```

### Getting a Gitea Token

1. Login to Gitea: http://localhost:3000
2. Profile → Settings → Applications
3. Generate new token with scopes:
   - `write:repository` (minimum)
   - `write:admin` (for user creation)
4. Update `.env` with the new token

---

## Troubleshooting

### "Connection refused"
- Check if Gitea is running: `docker ps | grep gitea`
- Verify port 3000 is accessible: `curl http://localhost:3000/api/v1/version`

### "Authentication failed"
- Verify token in `.env`: `grep GITEA_TOKEN .env`
- Check token validity: Run `check_gitea_api.py`

### "User does not exist"
- Create user in Gitea web UI
- Or run `sync_django_gitea_users.py` from Docker container

### "Token does not have required scope"
- Token needs `write:admin` for user creation
- Either regenerate token with admin scope
- Or create users manually in Gitea web UI

---

## Best Practices

1. **Test scripts cleanup after themselves**
   - Use `_test` prefix for temporary resources
   - Scripts automatically delete test resources
   - Use `--no-cleanup` only for debugging

2. **Run sync scripts from Docker**
   - Database access requires Docker network
   - Use `docker-compose exec` to run inside container

3. **Verify before syncing**
   - Always run `check_gitea_api.py` first
   - Confirms Gitea is accessible and token is valid

4. **Keep tokens secure**
   - Never commit `.env` to git
   - Use different tokens for dev/prod
   - Rotate tokens regularly

---

## Adding New Scripts

When adding new maintenance scripts:

1. Place in `scripts/` directory
2. Add `#!/usr/bin/env python3` shebang
3. Make executable: `chmod +x scripts/your_script.py`
4. Load environment: `load_dotenv(Path(__file__).parent.parent / ".env")`
5. Include cleanup logic
6. Update this README
7. Consider integration with `start_dev.sh`

---

## See Also

- `README_GITEA_SETUP.md` - Gitea setup guide
- `README_SCREENSHOTS.md` - Screenshot capture guide
- `containers/docker/README_DEV.md` - Docker development guide
