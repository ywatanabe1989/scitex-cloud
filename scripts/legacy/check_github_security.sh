#!/bin/bash
# Wrapper script for scitex.security module
# This provides backward compatibility for the old shell script interface

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check if scitex package is installed
if ! python -c "import scitex.security" 2> /dev/null; then
    echo "ERROR: scitex.security module not found"
    echo "Install: cd ~/proj/scitex-code && pip install -e ."
    exit 1
fi

# Call the Python module with arguments
cd "$PROJECT_ROOT"
python -m scitex.security.cli check --save "$@"
