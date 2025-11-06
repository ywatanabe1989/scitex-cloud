#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-04 13:40:34 (ywatanabe)"
# File: ./scripts/maintenance/tree_projects.sh

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

usage() {
    echo "Usage: $0 [APP_NAME] [-h|--help]"
    echo
    echo "Arguments:"
    echo "  APP_NAME           Optional. Specific app name to tree (e.g., writer_app)"
    echo
    echo "Options:"
    echo "  -h, --help         Display this help message"
    echo
    echo "Example:"
    echo "  $0                 # Tree all apps"
    echo "  $0 writer_app      # Tree only writer_app"
}

_tree_frontend() {
    local template_or_static=$1
    local specific_app=$2

    echo_header "$template_or_static: Global"
    tree --gitignore -lh ./$template_or_static

    if [ -n "$specific_app" ]; then
        local app_path="./apps/${specific_app}"
        if [ -d "$app_path" ]; then
            echo_header "$template_or_static: $app_path"
            tree --gitignore -lh $app_path/$template_or_static
        else
            echo_error "App not found: $app_path"
        fi
    else
        for app in ./apps/*_app; do
            echo_header "$template_or_static: $app"
            tree --gitignore -lh $app/$template_or_static
        done
    fi
}


_tree_backend() {
    local backend_type=$1
    local specific_app=$2

    echo_header "$backend_type: Global"
    if [ -d "./$backend_type" ]; then
        tree --gitignore -lh ./$backend_type
    fi

    if [ -n "$specific_app" ]; then
        local app_path="./apps/${specific_app}"
        if [ -d "$app_path" ]; then
            echo_header "$backend_type: $app_path"
            tree --gitignore -lh $app_path/$backend_type
        else
            echo_error "App not found: $app_path"
        fi
    else
        for app in ./apps/*_app; do
            echo_header "$backend_type: $app"
            tree --gitignore -lh $app/$backend_type
        done
    fi
}


tree_templates() { _tree_frontend templates "$1"; }
tree_static() { _tree_frontend static "$1"; }
tree_models() { _tree_backend models "$1"; }
tree_views() { _tree_backend views "$1"; }

main() {
    local specific_app=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            *)
                specific_app="$1"
                shift
                ;;
        esac
    done

    tree_templates "$specific_app"
    tree_static "$specific_app"
    tree_models "$specific_app"
    tree_views "$specific_app"
}

main "$@" 2>&1 | tee "$LOG_PATH"
echo_info "See $LOG_PATH"

# EOF