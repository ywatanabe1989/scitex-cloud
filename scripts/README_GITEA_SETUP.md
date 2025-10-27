# Gitea Setup and Troubleshooting Guide

## Overview

This guide explains how to set up Gitea properly for SciTeX Cloud development, including API token configuration and user management.

## Issue: Repository Creation Failed

**Error Message:**
```
Failed to create repository: Request failed: HTTPConnectionPool(host='localhost', port=3000):
Max retries exceeded with url: /api/v1/repos/wataning11/aaa
(Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x...>:
Failed to establish a new connection: [Errno 111] Connection refused'))
```

**Root Cause:**
The user `wataning11` (or other Django users) does not exist in Gitea, so repositories cannot be created for them.

## Solution Steps

### 1. Verify Gitea is Running

```bash
# Check Gitea container status
docker ps | grep gitea

# Test Gitea API
curl http://localhost:3000/api/v1/version
```

### 2. Verify API Token Configuration

```bash
# Run the API check script
/home/ywatanabe/proj/scitex-cloud/.venv/bin/python scripts/check_gitea_api.py
```

Expected output:
```
✓ Connected to Gitea (HTTP 200)
✓ Authenticated successfully
✓ Successfully retrieved repositories
```

### 3. Create Gitea Users Manually

Since the current API token lacks admin scope, you need to create users manually via the Gitea web interface:

1. **Access Gitea Admin Panel:**
   - Navigate to: http://localhost:3000
   - Login with admin credentials (user: `scitex`, check `.env` for password)
   - Go to: Site Administration (top right) → User Accounts

2. **Create Required Users:**
   - Click "Create User Account"
   - Username: `wataning11`
   - Email: `wataning11@example.com`
   - Password: Use `SCITEX_CLOUD_TEST_USER_PASSWORD` from `.env`
   - Uncheck "Require user to change password"
   - Click "Create User Account"

3. **Repeat for other users:**
   - Username: `ywatanabe`
   - Email: `ywatanabe@scitex.ai`
   - Password: Same as above

### 4. Generate Admin Token (Optional)

If you need to automate user creation:

1. **Login to Gitea** as the `scitex` admin user
2. **Navigate to Settings:**
   - Click your profile (top right) → Settings
   - Go to "Applications" tab
3. **Generate New Token:**
   - Token Name: "SciTeX Cloud Dev Admin"
   - Select scopes:
     - ✓ `write:admin` (required for user creation)
     - ✓ `write:repository`
     - ✓ `write:organization`
     - ✓ `write:user`
   - Click "Generate Token"
4. **Update `.env` file:**
   ```bash
   SCITEX_CLOUD_GITEA_TOKEN_DEV=<new_token_here>
   ```
5. **Restart services:**
   ```bash
   cd containers/docker
   ./start_dev.sh -a restart
   ```

### 5. Test Repository Creation

```bash
# Test with the test script
/home/ywatanabe/proj/scitex-cloud/.venv/bin/python scripts/test_repo_creation.py \
    --username wataning11 \
    --repo test-api-repo
```

Expected output:
```
✓ Authenticated as: scitex
✓ User exists: wataning11
✓ Repository does not exist (ready to create)
✓ Repository created successfully!
```

## Scripts Available

### 1. `check_gitea_api.py`
Verifies Gitea API connectivity and authentication.

```bash
/home/ywatanabe/proj/scitex-cloud/.venv/bin/python scripts/check_gitea_api.py
```

### 2. `test_repo_creation.py`
Tests repository creation for a specific user.

```bash
/home/ywatanabe/proj/scitex-cloud/.venv/bin/python scripts/test_repo_creation.py \
    --username <username> \
    --repo <repo_name>
```

## Enhanced `start_dev.sh`

The development startup script now includes:

1. **`verify_gitea_api()`** - Verifies Gitea API connectivity and authentication
2. **`create_gitea_users()`** - Attempts to create test users (requires admin token)

These functions run automatically during `./start_dev.sh -a start`.

## Verification Checklist

- [ ] Gitea container is running and healthy
- [ ] Gitea API is accessible at `http://localhost:3000`
- [ ] API token is valid and configured in `.env`
- [ ] Required users exist in Gitea:
  - [ ] `scitex` (admin)
  - [ ] `wataning11`
  - [ ] `ywatanabe`
  - [ ] `test-user`
- [ ] Can create repositories via API
- [ ] Django users match Gitea users

## Common Issues

### Issue: "User does not exist"
**Solution:** Create the user in Gitea web interface or generate admin token to automate.

### Issue: "Token does not have required scope"
**Solution:** Regenerate token with `write:admin` scope.

### Issue: "Connection refused"
**Solution:**
- Check if Gitea container is running: `docker ps | grep gitea`
- Verify port 3000 is not blocked: `curl http://localhost:3000/api/v1/version`
- Check Docker logs: `docker logs docker_gitea_1`

### Issue: Token mismatch between .env and Django
**Solution:**
- Verify token in `.env`: `grep GITEA_TOKEN .env`
- Restart Django to reload environment: `./start_dev.sh -a restart`

## Environment Variables

Key environment variables in `.env`:

```bash
SCITEX_CLOUD_GITEA_URL_DEV=http://127.0.0.1:3000
SCITEX_CLOUD_GITEA_HTTP_PORT_DEV=3000
SCITEX_CLOUD_GITEA_SSH_PORT_DEV=2222
SCITEX_CLOUD_GITEA_TOKEN_DEV=<your_token_here>
```

## Next Steps

After completing Gitea setup:

1. Test repository creation from Django app
2. Verify project workspace initialization
3. Test Git operations (clone, push, pull)
4. Check repository permissions and access control
