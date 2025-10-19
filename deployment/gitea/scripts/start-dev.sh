#!/bin/bash
# Start Gitea development container

set -e

echo "🚀 Starting Gitea development container..."

# Check if container exists
if docker ps -a | grep -q scitex-gitea-dev; then
    echo "📦 Container exists, starting..."
    docker start scitex-gitea-dev
else
    echo "📦 Creating new container..."
    docker run -d \
      --name scitex-gitea-dev \
      -p 3000:3000 \
      -p 2222:22 \
      -v gitea-data:/data \
      -e USER_UID=1000 \
      -e USER_GID=1000 \
      gitea/gitea:1.21
fi

echo "⏳ Waiting for Gitea to start..."
sleep 3

echo "✅ Gitea is running!"
echo ""
echo "📍 Access Gitea at: http://localhost:3000"
echo "🔑 SSH port: 2222"
echo ""
echo "To stop: ./deployment/gitea/stop-dev.sh"
