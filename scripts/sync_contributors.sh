#!/bin/bash
# Sync contributors from GitHub to database
# Usage: ./scripts/sync_contributors.sh [repo]

REPO="${1:-ywatanabe1989/scitex-cloud}"

echo "🔍 Fetching contributors from GitHub: $REPO"

# Fetch contributors data from GitHub
CONTRIBUTORS_JSON=$(gh api repos/$REPO/contributors --paginate)

if [ $? -ne 0 ]; then
    echo "❌ Error fetching contributors from GitHub"
    echo "   Make sure 'gh' CLI is installed and authenticated"
    exit 1
fi

# Save to temp file
TEMP_FILE=$(mktemp)
echo "$CONTRIBUTORS_JSON" > "$TEMP_FILE"

echo "📥 Found $(echo "$CONTRIBUTORS_JSON" | jq length) contributors"
echo "💾 Syncing to database..."

# Execute Django management command via Docker
docker compose -f deployment/docker/docker_dev/docker-compose.yml exec -T web python manage.py shell << EOF
import json
from apps.public_app.models import Contributor

# Read contributors data
with open('$TEMP_FILE', 'r') as f:
    contributors_data = json.load(f)

created_count = 0
updated_count = 0

for contributor in contributors_data:
    username = contributor.get('login')
    contributions = contributor.get('contributions', 0)

    if not username:
        continue

    # Determine role
    if username == 'ywatanabe1989':
        role = 'creator'
        is_core = True
        display_order = 1
        description = 'Architecture, Core Development, Research'
    elif contributions >= 100:
        role = 'core'
        is_core = True
        display_order = 10
        description = ''
    elif contributions >= 50:
        role = 'maintainer'
        is_core = False
        display_order = 100
        description = ''
    else:
        role = 'contributor'
        is_core = False
        display_order = 1000
        description = ''

    # Get name from GitHub API if available
    name = username  # Default to username

    # Update or create
    obj, created = Contributor.objects.update_or_create(
        github_username=username,
        defaults={
            'name': name,
            'avatar_url': contributor.get('avatar_url', ''),
            'github_url': contributor.get('html_url', ''),
            'role': role,
            'is_core_team': is_core,
            'contributions': contributions,
            'contributions_description': description,
            'display_order': display_order
        }
    )

    if created:
        created_count += 1
        print(f"✅ Created: {username} ({contributions} contributions)")
    else:
        updated_count += 1
        print(f"🔄 Updated: {username} ({contributions} contributions)")

print(f"\\n📊 Summary: {created_count} created, {updated_count} updated")
print(f"📊 Total contributors: {Contributor.objects.count()}")
EOF

# Cleanup
rm -f "$TEMP_FILE"

echo "✅ Sync complete!"
