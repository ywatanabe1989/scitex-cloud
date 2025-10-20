#!/bin/bash
# -*- coding: utf-8 -*-
# Template for maintenance scripts
# This file shows the standard pattern for all maintenance scripts

set -euo pipefail

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
ERR_PATH="$THIS_DIR/.$(basename $0).err"
echo > "$LOG_PATH"
echo > "$ERR_PATH"

# Color codes
BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }
echo_header() { echo -e "${BLUE}$1${NC}"; }

# Main function
main() {
    echo_header "=== Script Name ==="
    echo

    # Your script logic here

    echo -e "\nLogs: $LOG_PATH (stdout) | $ERR_PATH (stderr)"
}

# Run main with separated stdout/stderr logging
main "$@" > >(tee -a "$LOG_PATH") 2> >(tee -a "$ERR_PATH" >&2)

# EOF
