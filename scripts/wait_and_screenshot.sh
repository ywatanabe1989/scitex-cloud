#!/bin/bash
# Wait for server to be ready, then capture screenshots

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Waiting for SciTeX Cloud to be ready${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Wait for server to be ready
MAX_WAIT=300  # 5 minutes
WAIT_TIME=0
INTERVAL=5

while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    if curl -s http://127.0.0.1:8000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Server is ready!${NC}"
        echo ""
        break
    fi

    echo -e "${YELLOW}Waiting for server... (${WAIT_TIME}s / ${MAX_WAIT}s)${NC}"
    sleep $INTERVAL
    WAIT_TIME=$((WAIT_TIME + INTERVAL))
done

if [ $WAIT_TIME -ge $MAX_WAIT ]; then
    echo -e "${RED}✗ Timeout waiting for server${NC}"
    exit 1
fi

# Give server a bit more time to fully initialize
echo -e "${YELLOW}Giving server time to fully initialize...${NC}"
sleep 10

# Run screenshot capture
echo -e "${GREEN}Starting screenshot capture...${NC}"
echo ""

cd "$PROJECT_ROOT"
"$SCRIPT_DIR/run_screenshots.sh" "$@"
