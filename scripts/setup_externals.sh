#!/bin/bash
# SciTeX-Cloud External Components Setup Script
# Automatically clones and configures all SciTeX ecosystem components

set -e

EXTERNALS_DIR="$(dirname "$0")/../externals"
cd "$EXTERNALS_DIR"

echo "🚀 Setting up SciTeX External Components..."

# SciTeX component repositories
declare -A COMPONENTS=(
    ["SciTeX-Writer"]="https://github.com/ywatanabe1989/SciTeX-Writer.git"
    ["SciTeX-Code"]="https://github.com/ywatanabe1989/SciTeX-Code.git"
    ["SciTeX-Viz"]="https://github.com/ywatanabe1989/SciTeX-Viz.git"
    ["SciTeX-Scholar"]="https://github.com/ywatanabe1989/SciTeX-Scholar.git"
    ["SciTeX-Example-Research-Project"]="https://github.com/ywatanabe1989/SciTeX-Example-Research-Project.git"
)

# Clone or update each component
for component in "${!COMPONENTS[@]}"; do
    if [ -d "$component" ]; then
        echo "📦 Updating $component..."
        cd "$component"
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || echo "⚠️  Could not update $component"
        cd ..
    else
        echo "📥 Cloning $component..."
        git clone "${COMPONENTS[$component]}" "$component"
    fi
done

# Set up SciTeX-Engine (if available)
if [ ! -d "SciTeX-Engine" ]; then
    echo "ℹ️  SciTeX-Engine not available yet (planned component)"
fi

# Create integration status file
cat > integration_status.json << EOF
{
  "timestamp": "$(date -Iseconds)",
  "components": {
    "SciTeX-Writer": {
      "status": "active",
      "integration": "template_system",
      "description": "LaTeX template system for cloud compilation"
    },
    "SciTeX-Code": {
      "status": "ready", 
      "integration": "planned",
      "description": "Python framework for scientific computation"
    },
    "SciTeX-Viz": {
      "status": "ready",
      "integration": "planned", 
      "description": "SigmaPlot visualization wrapper"
    },
    "SciTeX-Scholar": {
      "status": "ready",
      "integration": "planned",
      "description": "Literature search and analysis"
    },
    "SciTeX-Engine": {
      "status": "planned",
      "integration": "external",
      "description": "Emacs-based LLM agent system"
    },
    "SciTeX-Example-Research-Project": {
      "status": "active",
      "integration": "project_template",
      "description": "Complete research project boilerplate and template"
    }
  }
}
EOF

echo "✅ SciTeX External Components setup complete!"
echo "📍 Location: $(pwd)"
echo "📊 Components cloned: $(ls -d SciTeX-* | wc -l)"
echo "🔗 Integration status: $(pwd)/integration_status.json"