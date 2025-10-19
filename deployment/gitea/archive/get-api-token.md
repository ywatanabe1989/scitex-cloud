# How to Get Gitea API Token

For Django integration, you need a Gitea API token.

## Steps

1. **Open Gitea:** http://localhost:3000

2. **Login** with your admin account

3. **Go to Settings:**
   - Click your avatar (top right)
   - Click "Settings"

4. **Applications tab:**
   - Click "Applications" in left sidebar
   - Scroll to "Manage Access Tokens"

5. **Generate Token:**
   - Token Name: `Django Integration`
   - Select permissions: (all for development)
   - Click "Generate Token"

6. **Copy Token** (shown only once!)
   ```
   Example: 1234567890abcdef1234567890abcdef12345678
   ```

7. **Save to Environment:**
   ```bash
   echo 'export GITEA_TOKEN="your_token_here"' >> ~/.bashrc
   source ~/.bashrc
   ```

8. **Test Token:**
   ```bash
   curl -H "Authorization: token $GITEA_TOKEN" \
     http://localhost:3000/api/v1/user
   ```

   Should return your user info.

## For Django Settings

Add to `config/settings/settings_dev.py`:

```python
# Gitea Configuration
GITEA_URL = 'http://localhost:3000'
GITEA_API_URL = 'http://localhost:3000/api/v1'
GITEA_TOKEN = os.environ.get('GITEA_TOKEN', '')
```

## Test in Django Shell

```bash
python manage.py shell
```

```python
import requests
from django.conf import settings

response = requests.get(
    f"{settings.GITEA_API_URL}/user",
    headers={'Authorization': f'token {settings.GITEA_TOKEN}'}
)

print(response.json())
```

Should show your user information!
