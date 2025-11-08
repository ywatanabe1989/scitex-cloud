#!/bin/bash
# Screenshot Capture Runner for SciTeX Cloud
# Usage: ./scripts/run_screenshots.sh [options]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}SciTeX Cloud - Screenshot Capture${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check if server is running
echo -e "${YELLOW}Checking if Django server is running...${NC}"
if ! curl -s http://127.0.0.1:8000 > /dev/null; then
    echo -e "${YELLOW}Django server not running. Please start it first:${NC}"
    echo -e "${GREEN}  python manage.py runserver${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Server is running${NC}"
echo ""

# Activate virtual environment if exists
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Run the screenshot script
cd "$PROJECT_ROOT"

echo -e "${YELLOW}Starting screenshot capture...${NC}"
echo ""

python scripts/capture_screenshots.py "$@"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}Screenshot capture completed!${NC}"
    echo -e "${GREEN}======================================${NC}"

    # Find the latest screenshot directory
    LATEST_DIR=$(ls -td data/screenshots/*/ | head -1)
    if [ -n "$LATEST_DIR" ]; then
        echo -e "${YELLOW}Screenshots saved to:${NC}"
        echo -e "${BLUE}  $LATEST_DIR${NC}"
        echo ""
        echo -e "${YELLOW}View index:${NC}"
        echo -e "${BLUE}  file://$PROJECT_ROOT/$LATEST_DIR/index.html${NC}"

        # Try to open in browser if available
        if command -v xdg-open &> /dev/null; then
            echo ""
            echo -e "${YELLOW}Opening in browser...${NC}"
            xdg-open "$PROJECT_ROOT/$LATEST_DIR/index.html" 2>/dev/null || true
        fi
    fi
else
    echo ""
    echo -e "${YELLOW}Screenshot capture completed with errors.${NC}"
fi

exit $exit_code
