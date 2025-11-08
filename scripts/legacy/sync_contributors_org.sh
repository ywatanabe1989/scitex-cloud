#!/bin/bash
# Sync all contributors from SciTeX organization on GitHub
# Usage: ./scripts/sync_contributors_org.sh [org-name]

ORG="${1:-scitex-ai}"

echo "🔍 Fetching repositories from GitHub organization: $ORG"

# Get all repositories in the organization
REPOS=$(gh api orgs/$ORG/repos --paginate --jq '.[].name')

if [ $? -ne 0 ]; then
    echo "❌ Error fetching repositories from GitHub organization"
    echo "   Make sure 'gh' CLI is installed and authenticated"
    exit 1
fi

echo "📚 Found repositories:"
echo "$REPOS" | sed 's/^/   - /'

# Create temporary files in project directory (accessible from Docker)
TEMP_DIR="/home/ywatanabe/proj/scitex-cloud/.tmp_sync"
mkdir -p "$TEMP_DIR"
ALL_CONTRIBUTORS="$TEMP_DIR/all_contributors.json"

echo "[]" > "$ALL_CONTRIBUTORS"

# Fetch contributors from each repository
echo ""
echo "🔄 Fetching contributors from each repository..."

for REPO in $REPOS; do
    echo "   📦 $ORG/$REPO"

    CONTRIBUTORS=$(gh api repos/$ORG/$REPO/contributors --paginate 2>/dev/null)

    if [ $? -eq 0 ] && [ ! -z "$CONTRIBUTORS" ]; then
        CONTRIB_COUNT=$(echo "$CONTRIBUTORS" | jq length)
        echo "      Found $CONTRIB_COUNT contributors"

        # Add repository info to each contributor
        CONTRIBUTORS_WITH_REPO=$(echo "$CONTRIBUTORS" | jq --arg repo "$REPO" 'map(. + {repository: $repo})')

        # Merge with all contributors
        ALL_CONTRIBUTORS_NEW=$(jq -s '.[0] + .[1]' "$ALL_CONTRIBUTORS" <(echo "$CONTRIBUTORS_WITH_REPO"))
        echo "$ALL_CONTRIBUTORS_NEW" > "$ALL_CONTRIBUTORS"
    fi
done

# Aggregate contributions by user
echo ""
echo "📊 Aggregating contributions by user..."

AGGREGATED=$(jq 'group_by(.login) | map({
    login: .[0].login,
    avatar_url: .[0].avatar_url,
    html_url: .[0].html_url,
    total_contributions: map(.contributions) | add,
    repositories: map(.repository),
    repo_count: (map(.repository) | length)
})' "$ALL_CONTRIBUTORS")

echo "$AGGREGATED" > "$TEMP_DIR/aggregated.json"

UNIQUE_CONTRIBUTORS=$(echo "$AGGREGATED" | jq length)
echo "👥 Found $UNIQUE_CONTRIBUTORS unique contributors across all repositories"

# Show top contributors
echo ""
echo "🏆 Top 10 contributors:"
echo "$AGGREGATED" | jq -r 'sort_by(-.total_contributions) | .[:10] | .[] | "   \(.total_contributions) contributions - @\(.login) (\(.repo_count) repos)"'

echo ""
echo "💾 Syncing to database..."

# Execute Django management command via Docker
docker compose -f deployment/docker/docker_dev/docker-compose.yml exec -T web python manage.py shell << EOF
import json

with open('.tmp_sync/aggregated.json', 'r') as f:
    contributors_data = json.load(f)

from apps.public_app.models import Contributor

created_count = 0
updated_count = 0

for contributor in contributors_data:
    username = contributor.get('login')
    total_contributions = contributor.get('total_contributions', 0)
    repo_count = contributor.get('repo_count', 0)
    repositories = contributor.get('repositories', [])

    if not username:
        continue

    # Determine role based on total contributions
    if username == 'ywatanabe1989':
        role = 'creator'
        is_core = True
        display_order = 1
        description = 'Creator & Lead Developer - Architecture, Core Development, Research across all SciTeX projects'
    elif total_contributions >= 100:
        role = 'core'
        is_core = True
        display_order = 10
        description = f'Core Team Member - {total_contributions} contributions across {repo_count} repositories'
    elif total_contributions >= 50:
        role = 'maintainer'
        is_core = False
        display_order = 100
        description = f'Maintainer - {total_contributions} contributions across {repo_count} repositories'
    else:
        role = 'contributor'
        is_core = False
        display_order = 1000
        description = f'{total_contributions} contributions to {", ".join(repositories[:3])}'
        if repo_count > 3:
            description += f' and {repo_count - 3} more'

    # Update or create
    obj, created = Contributor.objects.update_or_create(
        github_username=username,
        defaults={
            'name': username,  # Will be updated with real name if available
            'avatar_url': contributor.get('avatar_url', ''),
            'github_url': contributor.get('html_url', ''),
            'role': role,
            'is_core_team': is_core,
            'contributions': total_contributions,
            'contributions_description': description,
            'display_order': display_order
        }
    )

    if created:
        created_count += 1
        print(f"✅ Created: @{username} ({total_contributions} contributions, {repo_count} repos)")
    else:
        updated_count += 1
        print(f"🔄 Updated: @{username} ({total_contributions} contributions, {repo_count} repos)")

print(f"\\n📊 Summary:")
print(f"   Created: {created_count}")
print(f"   Updated: {updated_count}")
print(f"   Total in database: {Contributor.objects.count()}")
print(f"\\n🎉 Sync complete!")

# Show core team
core_team = Contributor.objects.filter(is_core_team=True).order_by('display_order')
if core_team.exists():
    print(f"\\n👥 Core Team ({core_team.count()}):")
    for member in core_team:
        print(f"   - {member.name} (@{member.github_username}): {member.contributions} contributions")
EOF

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Organization-wide contributor sync complete!"
echo "🌐 View contributors at: http://127.0.0.1:8000/contributors/"
