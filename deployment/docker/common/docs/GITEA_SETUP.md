# Gitea Setup Guide - SciTeX Cloud

**Complete guide for setting up and managing Gitea integration with Django**

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Initial Setup](#initial-setup)
4. [Automated Integration](#automated-integration)
5. [Manual Administration](#manual-administration)
6. [Troubleshooting](#troubleshooting)
7. [Testing](#testing)

---

## Overview

SciTeX Cloud integrates with Gitea to provide Git repository hosting for user projects. The integration is fully automated:

- **User Creation**: Django users automatically get Gitea accounts
- **Repository Management**: Project creation triggers Gitea repository creation
- **User Deletion**: Deleting Django users removes corresponding Gitea users
- **No Manual Steps**: Everything happens via Django signals and Gitea API

---

## Architecture

### Components

```
┌─────────────────┐         ┌──────────────────┐
│  Django (web)   │ ←──────→│  Gitea (gitea)   │
│  Port: 8000     │   API   │  Port: 3000      │
└─────────────────┘         └──────────────────┘
         │                           │
         ↓                           ↓
┌─────────────────┐         ┌──────────────────┐
│  PostgreSQL     │ ←───────│  Shared Database │
│  Port: 5432     │         │                  │
└─────────────────┘         └──────────────────┘
```

### Network Configuration

- **Docker Internal**: Use `http://gitea:3000` for container-to-container communication
- **Host Access**: Use `http://127.0.0.1:3001` for accessing Gitea from host machine
- **SSH**: Port 2222 (configurable via `SCITEX_CLOUD_GITEA_SSH_PORT_DEV`)

---

## Initial Setup

### 1. Start Docker Compose

```bash
cd containers/docker
./start_dev.sh -a start
```

This will:
- Start PostgreSQL, Redis, Gitea, and Django containers
- Initialize Gitea with default admin account
- Run Django migrations

### 2. Access Gitea Web Interface

```bash
# Open in browser
http://127.0.0.1:3001
```

Default credentials:
- Username: `admin`
- Password: `admin`

### 3. Generate Admin API Token

**Option A: Via CLI (Recommended)**

```bash
# Generate token with full admin permissions
docker exec -u git docker_gitea_1 gitea admin user generate-access-token \
  --username admin \
  --token-name "django-admin-token-$(date +%s)" \
  --scopes "write:admin,write:repository,write:organization,write:user"
```

Output example:
```
Access token was successfully created: db1c7023dcb63c92caf86e26a61027fd362f9e8e
```

**Option B: Via Web UI**

1. Login to Gitea: http://127.0.0.1:3001
2. Go to: Settings → Applications → Manage Access Tokens
3. Generate New Token
4. Select scopes: `write:admin`, `write:repository`, `write:organization`, `write:user`
5. Copy the generated token

### 4. Configure Django Environment

Update `SECRET/.env.dev`:

```bash
# Gitea API Configuration
SCITEX_CLOUD_GITEA_URL_DEV=http://gitea:3000
SCITEX_CLOUD_GITEA_TOKEN_DEV=<YOUR_TOKEN_HERE>
SCITEX_CLOUD_GITEA_HTTP_PORT_DEV=3001
SCITEX_CLOUD_GITEA_SSH_PORT_DEV=2222
```

**Important**: Use `http://gitea:3000` (not `127.0.0.1:3001`) for Docker internal networking.

### 5. Restart Django Container

```bash
docker restart docker_web_1
```

### 6. Verify Integration

```bash
# Test Gitea API connection
docker exec docker_web_1 python -c "
import os
os.environ.setdefault('SCITEX_CLOUD_DJANGO_SETTINGS_MODULE', 'config.settings.settings_dev')
import django
django.setup()

from apps.gitea_app.api_client import GiteaClient
client = GiteaClient()
user = client.get_current_user()
print(f'✓ Connected to Gitea as: {user[\"username\"]}')
"
```

Expected output:
```
✓ Connected to Gitea as: admin
```

---

## Automated Integration

### User Creation Flow

When a user signs up in Django:

```python
# apps/auth_app/views.py:47-57
# Automatically creates Gitea user
from apps.gitea_app.services.gitea_sync_service import sync_user_to_gitea
sync_user_to_gitea(user, password)
```

**What happens:**
1. User fills signup form on Django
2. Django creates User object
3. Signal triggers Gitea API call
4. Gitea user created with same username/email
5. User can now push/pull to Gitea repos

### Repository Creation Flow

When a user creates a project:

```python
# apps/project_app/signals.py:75-94
# Automatically creates Gitea repository
repo = client.create_repository(
    name=repo_name,
    owner=instance.owner.username  # Creates under user's account
)
```

**What happens:**
1. User creates project in Django
2. Signal triggers before project is saved
3. Gitea user existence verified
4. Repository created under user's account (e.g., `username/project-name`)
5. Repository cloned to Django data directory
6. Project model updated with Gitea URLs

### User Deletion Flow

When a user account is deleted:

```python
# apps/auth_app/models.py:218-229
# Automatically deletes Gitea user
@receiver(pre_delete, sender=User)
def delete_gitea_user(sender, instance, **kwargs):
    client.delete_user(instance.username)
```

**What happens:**
1. User deletes their account in Django
2. `pre_delete` signal triggered
3. Gitea user and all repositories deleted via API
4. Django user record removed
5. Username becomes available for reuse

---

## Manual Administration

### User Management

**List all Gitea users:**
```bash
docker exec -u git docker_gitea_1 gitea admin user list
```

**Create user manually:**
```bash
docker exec -u git docker_gitea_1 gitea admin user create \
  --username "testuser" \
  --email "test@example.com" \
  --password "testpass123" \
  --must-change-password=false
```

**Delete user manually:**
```bash
docker exec -u git docker_gitea_1 gitea admin user delete \
  --username "testuser"
```

**Change password:**
```bash
docker exec -u git docker_gitea_1 gitea admin user change-password \
  --username "admin" \
  --password "newpassword"
```

### Repository Management

**List repositories:**
```bash
curl -X GET "http://127.0.0.1:3001/api/v1/user/repos" \
  -H "Authorization: token <YOUR_TOKEN>"
```

**Delete repository:**
```bash
curl -X DELETE "http://127.0.0.1:3001/api/v1/repos/{owner}/{repo}" \
  -H "Authorization: token <YOUR_TOKEN>"
```

### Token Management

**List tokens:**
```bash
docker exec -u git docker_gitea_1 gitea admin user list-access-tokens \
  --username admin
```

**Revoke token:**
```bash
docker exec -u git docker_gitea_1 gitea admin user delete-access-token \
  --username admin \
  --token <TOKEN_ID>
```

### Database Access

**Access Gitea database:**
```bash
docker exec -it docker_db_1 psql -U scitex_dev -d scitex_cloud_dev
```

**Useful queries:**
```sql
-- List all Gitea users
SELECT id, name, email, is_admin FROM "user";

-- List all repositories
SELECT id, owner_name, name, is_private FROM repository;

-- List all access tokens
SELECT id, uid, name, created_unix FROM access_token;
```

---

## Troubleshooting

### Issue: "Connection refused" when creating repository

**Symptom:**
```
Failed to create repository: HTTPConnectionPool(host='127.0.0.1', port=3000): Connection refused
```

**Solution:**
Check `SCITEX_CLOUD_GITEA_URL_DEV` in `.env`:
```bash
# Wrong (from inside Docker container)
SCITEX_CLOUD_GITEA_URL_DEV=http://127.0.0.1:3000

# Correct (use Docker service name)
SCITEX_CLOUD_GITEA_URL_DEV=http://gitea:3000
```

### Issue: "Token does not have required scope"

**Symptom:**
```
token does not have at least one of required scope(s), required=[write:admin]
```

**Solution:**
Regenerate token with admin scope:
```bash
docker exec -u git docker_gitea_1 gitea admin user generate-access-token \
  --username admin \
  --token-name "django-admin-token-$(date +%s)" \
  --scopes "write:admin,write:repository,write:organization,write:user"
```

Update `SECRET/.env.dev` with new token and restart:
```bash
docker restart docker_web_1
```

### Issue: "No git URL configured"

**Symptom:**
```
Gitea repository created but clone failed: No git URL configured
```

**Solution:**
Check Gitea ROOT_URL configuration:
```bash
docker exec docker_gitea_1 cat /data/gitea/conf/app.ini | grep ROOT_URL
```

Should be:
```ini
ROOT_URL = http://gitea:3000/
```

If incorrect, restart Gitea:
```bash
docker restart docker_gitea_1
```

### Issue: "Username already taken" after deletion

**Symptom:**
After deleting a Django user, can't recreate with same username.

**Solution:**
This was a bug that has been fixed. The `pre_delete` signal now automatically removes Gitea users. If you encounter this:

1. Check if Gitea user still exists:
```bash
docker exec -u git docker_gitea_1 gitea admin user list
```

2. Manually delete if needed:
```bash
docker exec -u git docker_gitea_1 gitea admin user delete --username "username"
```

### Issue: Gitea won't start

**Symptom:**
```
Gitea is not supposed to be run as root
```

**Solution:**
Always run Gitea commands as `git` user:
```bash
# Wrong
docker exec docker_gitea_1 gitea admin user list

# Correct
docker exec -u git docker_gitea_1 gitea admin user list
```

---

## Testing

### Clean Environment Setup

**1. Delete all test users:**
```bash
# Delete from Django (automatically deletes from Gitea)
docker exec docker_web_1 python -c "
import os
os.environ.setdefault('SCITEX_CLOUD_DJANGO_SETTINGS_MODULE', 'config.settings.settings_dev')
import django
django.setup()

from django.contrib.auth.models import User
User.objects.filter(is_superuser=False).delete()
print('✓ All test users deleted')
"
```

**2. Verify cleanup:**
```bash
# Check Django users
docker exec docker_web_1 python -c "
import os
os.environ.setdefault('SCITEX_CLOUD_DJANGO_SETTINGS_MODULE', 'config.settings.settings_dev')
import django
django.setup()

from django.contrib.auth.models import User
print(f'Django users: {User.objects.count()}')
"

# Check Gitea users
docker exec -u git docker_gitea_1 gitea admin user list
```

### Test User Lifecycle

**1. Create test user via Django:**
```bash
# Via web interface
http://127.0.0.1:8000/auth/signup/

# Or via Django shell
docker exec docker_web_1 python manage.py shell << 'EOF'
from django.contrib.auth.models import User
from apps.gitea_app.services.gitea_sync_service import sync_user_to_gitea

user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
sync_user_to_gitea(user, 'testpass123')
print(f'✓ Created user: {user.username}')
EOF
```

**2. Verify Gitea user created:**
```bash
docker exec -u git docker_gitea_1 gitea admin user list | grep testuser
```

**3. Create test project:**
```bash
# Via web interface
http://127.0.0.1:8000/testuser/

# Click "New Project"
```

**4. Verify repository created:**
```bash
curl -X GET "http://127.0.0.1:3001/api/v1/repos/testuser/test-project" \
  -H "Authorization: token <YOUR_TOKEN>"
```

**5. Delete user:**
```bash
docker exec docker_web_1 python -c "
import os
os.environ.setdefault('SCITEX_CLOUD_DJANGO_SETTINGS_MODULE', 'config.settings.settings_dev')
import django
django.setup()

from django.contrib.auth.models import User
User.objects.get(username='testuser').delete()
print('✓ User deleted')
"
```

**6. Verify Gitea cleanup:**
```bash
# Should not find testuser
docker exec -u git docker_gitea_1 gitea admin user list | grep testuser || echo "✓ User removed from Gitea"
```

### Automated Test Suite

Create a test script `scripts/test_gitea_integration.sh`:

```bash
#!/bin/bash
set -e

echo "=== Testing Gitea Integration ==="

# 1. Create user
echo "1. Creating Django user..."
docker exec docker_web_1 python -c "
import os
os.environ.setdefault('SCITEX_CLOUD_DJANGO_SETTINGS_MODULE', 'config.settings.settings_dev')
import django
django.setup()

from django.contrib.auth.models import User
from apps.gitea_app.services.gitea_sync_service import sync_user_to_gitea

user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
sync_user_to_gitea(user, 'testpass123')
print('✓ Django user created')
"

# 2. Verify Gitea user
echo "2. Verifying Gitea user..."
if docker exec -u git docker_gitea_1 gitea admin user list | grep -q testuser; then
    echo "✓ Gitea user exists"
else
    echo "✗ Gitea user not found"
    exit 1
fi

# 3. Delete user
echo "3. Deleting Django user..."
docker exec docker_web_1 python -c "
import os
os.environ.setdefault('SCITEX_CLOUD_DJANGO_SETTINGS_MODULE', 'config.settings.settings_dev')
import django
django.setup()

from django.contrib.auth.models import User
User.objects.get(username='testuser').delete()
print('✓ Django user deleted')
"

# 4. Verify Gitea cleanup
echo "4. Verifying Gitea cleanup..."
sleep 2  # Give Gitea a moment to process
if docker exec -u git docker_gitea_1 gitea admin user list | grep -q testuser; then
    echo "✗ Gitea user still exists"
    exit 1
else
    echo "✓ Gitea user removed"
fi

echo "=== All tests passed! ==="
```

Run tests:
```bash
chmod +x scripts/test_gitea_integration.sh
./scripts/test_gitea_integration.sh
```

---

## Configuration Reference

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SCITEX_CLOUD_GITEA_URL_DEV` | Gitea URL (Docker internal) | `http://gitea:3000` |
| `SCITEX_CLOUD_GITEA_TOKEN_DEV` | Admin API token | `db1c7023dcb...` |
| `SCITEX_CLOUD_GITEA_HTTP_PORT_DEV` | Host port for Gitea | `3001` |
| `SCITEX_CLOUD_GITEA_SSH_PORT_DEV` | SSH port for Git operations | `2222` |

### Docker Compose Configuration

```yaml
# containers/docker/docker-compose.dev.yml
gitea:
  image: gitea/gitea:latest
  environment:
    - GITEA__server__DOMAIN=gitea
    - GITEA__server__ROOT_URL=http://gitea:3000/
    - GITEA__server__HTTP_PORT=3000
    - GITEA__database__DB_TYPE=postgres
    - GITEA__database__HOST=db:5432
  ports:
    - "3001:3000"  # HTTP
    - "2222:22"    # SSH
```

### API Scopes Required

- `write:admin` - Create/delete users
- `write:repository` - Create/manage repositories
- `write:organization` - Manage organizations
- `write:user` - Update user information

---

## Files Modified for Integration

### Core Integration Files

1. **apps/auth_app/views.py:47-57**
   - User signup with Gitea sync

2. **apps/auth_app/models.py:218-229**
   - User deletion signal for Gitea cleanup

3. **apps/project_app/signals.py:75-94**
   - Repository creation for projects

4. **apps/gitea_app/api_client.py**
   - Gitea API wrapper
   - Methods: `create_repository()`, `delete_user()`

5. **apps/gitea_app/services/gitea_sync_service.py**
   - User sync utilities
   - Methods: `sync_user_to_gitea()`, `ensure_gitea_user_exists()`

### Configuration Files

1. **SECRET/.env.dev**
   - Gitea URL, token, ports

2. **containers/docker/docker-compose.dev.yml**
   - Gitea service definition
   - Network configuration

---

## Production Deployment Notes

### Security Considerations

1. **Token Security**
   - Never commit tokens to git
   - Use environment variables
   - Rotate tokens periodically

2. **Network Isolation**
   - Use Docker internal networking for Django ↔ Gitea
   - Expose only necessary ports
   - Consider using SSL/TLS for production

3. **User Authentication**
   - Consider OAuth2 integration for production
   - Enable 2FA for admin accounts
   - Implement rate limiting

### Scaling

1. **Database**
   - Use dedicated PostgreSQL instance
   - Enable connection pooling
   - Regular backups

2. **Storage**
   - Use external storage for Git LFS
   - Regular repository backups
   - Consider using S3-compatible storage

3. **Performance**
   - Enable Redis caching
   - Configure Gitea caching
   - Monitor repository sizes

---

## References

- [Gitea Documentation](https://docs.gitea.io/)
- [Gitea API Documentation](https://docs.gitea.io/en-us/api-usage/)
- [Django Signals](https://docs.djangoproject.com/en/stable/topics/signals/)
- [Docker Compose Networking](https://docs.docker.com/compose/networking/)

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-27 | 1.0.0 | Initial documentation |
|  |  | - Automated user creation/deletion |
|  |  | - Repository management |
|  |  | - Admin token setup |

---

**Last Updated**: 2025-10-27
**Maintainer**: SciTeX Development Team
**Status**: Production Ready ✓

<!-- EOF -->
