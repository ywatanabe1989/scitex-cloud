#!/bin/bash
# Build all SciTeX module documentation

set -e

echo "=== Building SciTeX Documentation ==="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to build docs
build_docs() {
    local name=$1
    local path=$2

    echo -e "${BLUE}Building $name documentation...${NC}"

    if [ ! -d "$path" ]; then
        echo -e "${RED}✗ Directory not found: $path${NC}"
        return 1
    fi

    cd "$path"

    if [ ! -f "conf.py" ]; then
        echo -e "${RED}✗ No conf.py found in $path${NC}"
        cd - > /dev/null
        return 1
    fi

    # Build with sphinx
    if sphinx-build -b html . _build/html > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $name documentation built successfully${NC}"
        echo "  Output: $path/_build/html/index.html"
    else
        echo -e "${RED}✗ Failed to build $name documentation${NC}"
        # Try showing the error
        sphinx-build -b html . _build/html 2>&1 | tail -10
    fi

    cd - > /dev/null
    echo ""
}

# Build each module
build_docs "Code/Scholar" "$HOME/proj/scitex_repo/docs"
build_docs "Viz" "$HOME/win/documents/SciTeX-Viz/docs"
build_docs "Writer" "$HOME/proj/neurovista/paper/docs"

echo -e "${GREEN}=== Documentation build complete ===${NC}"
echo ""
echo "To view documentation:"
echo "  - Start Django: python manage.py runserver"
echo "  - Visit: http://localhost:8000/docs/"
