#!/bin/bash
# Quick screenshot using MCP Playwright tool
# Usage: ./scripts/quick_screenshot.sh [url] [output_name]

URL="${1:-http://127.0.0.1:8000}"
OUTPUT_NAME="${2:-homepage}"
OUTPUT_DIR="data/screenshots/quick"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

mkdir -p "$PROJECT_ROOT/$OUTPUT_DIR"

OUTPUT_PATH="$PROJECT_ROOT/$OUTPUT_DIR/${OUTPUT_NAME}_$(date +%Y%m%d_%H%M%S).png"

echo "Capturing: $URL"
echo "Output: $OUTPUT_PATH"
echo ""

# This is a placeholder - the actual MCP Playwright capture would be done via Claude Code
# For now, let's document the manual approach

cat << 'EOF'
To capture a quick screenshot using MCP Playwright:

1. Ask Claude Code to use the Playwright MCP tool:
   "Use mcp__playwright__browser_navigate to go to http://127.0.0.1:8000/scholar/"
   "Use mcp__playwright__browser_take_screenshot to save the page"

2. Or use the Python scripts:
   ./scripts/run_screenshots.sh
   python scripts/capture_demo_screenshots.py

3. Screenshots will be saved to:
   data/screenshots/YYYYMMDD_HHMMSS/
EOF
