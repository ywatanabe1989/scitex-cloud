#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-03 09:23:52 (ywatanabe)"
# File: ./scripts/maintenance/tree_templates_and_static.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
echo_header() { echo_info "=== $1 ==="; }
# ---------------------------------------

_tree_base() {
    local template_or_static=$1
    echo_header "$template_or_static: Global"
    tree ./$template_or_static
    for app in ./apps/*_app; do
        echo_header "$Templates: $app"
        tree $app/$template_or_static
    done
}

tree_templates() { _tree_base templates; }
tree_static() { _tree_base static; }

main() {
    tree_templates
    tree_static
}

main "$@" | tee "$LOG_PATH"
echo_info "See $LOG_PATH"

# EOF