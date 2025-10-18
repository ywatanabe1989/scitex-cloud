#!/bin/bash
# Stop Gitea development container

set -e

echo "🛑 Stopping Gitea development container..."

if docker ps | grep -q scitex-gitea-dev; then
    docker stop scitex-gitea-dev
    echo "✅ Gitea stopped"
else
    echo "ℹ️  Gitea is not running"
fi
