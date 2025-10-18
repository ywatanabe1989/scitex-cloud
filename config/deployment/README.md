<!-- ---
!-- Timestamp: 2025-10-18 10:29:09
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/config/deployment/README.md
!-- --- -->

# SciTeX Cloud Deployment Guide

## Database Initialization

### Production Database Setup

The production database uses SQLite by default (configurable to PostgreSQL via environment variables).

**Database Location:**
```
/home/ywatanabe/proj/scitex-cloud/data/scitex_cloud_prod.db
```

**Initialize Production Database:**

1. Run migrations to create all tables:
```bash
cd /home/ywatanabe/proj/scitex-cloud
DJANGO_SETTINGS_MODULE=config.settings.settings_prod python manage.py migrate
```

2. Create a superuser account:
```bash
cd /home/ywatanabe/proj/scitex-cloud
DJANGO_SETTINGS_MODULE=config.settings.settings_prod python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.create_superuser('ywatanabe', 'ywata1989@gmail.com', 'YOUR_PASSWORD_HERE')
print(f'Created superuser: {user.username}')
"
```

3. Verify authentication:
```bash
cd /home/ywatanabe/proj/scitex-cloud
DJANGO_SETTINGS_MODULE=config.settings.settings_prod python manage.py shell -c "
from django.contrib.auth import authenticate
user = authenticate(username='ywatanabe', password='YOUR_PASSWORD_HERE')
print(f'Auth successful: {user is not None}')
"
```

**Reset User Password:**

```bash
cd /home/ywatanabe/proj/scitex-cloud
DJANGO_SETTINGS_MODULE=config.settings.settings_prod python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='ywatanabe')
user.set_password('NEW_PASSWORD')
user.save()
print('Password reset complete')
"
```

### Known Issues

**Profile App Conflicts:**
The `auth_app`, `core_app`, and `profile_app` may have signal conflicts when creating users. If you encounter `IntegrityError: UNIQUE constraint failed: core_app_userprofile.user_id`, this is due to duplicate profile creation signals. The user is still created successfully despite the error.

### Database Configuration

**SQLite (Default):**
- Location: `BASE_DIR/data/scitex_cloud_prod.db`
- No additional setup required

**PostgreSQL (Optional):**
Set the following environment variables:
```bash
export DB_PASSWORD="your_secure_password"
export DB_NAME="scitex_cloud"
export DB_USER="scitex"
export DB_HOST="localhost"
export DB_PORT="5432"
```

## Nginx Configuration

Nginx configuration files location:
```
/ssh:ywatanabe@scitex|sudo:scitex:/etc/nginx
```

<!-- EOF -->