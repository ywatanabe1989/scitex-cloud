#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-08 05:18:05 (ywatanabe)"
# File: ./scripts/maintenance/capture_demo_screenshots.sh

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

NC='\033[0m'

BASE_URL="http://127.0.0.1:8000"
OUTPUT_DIR="$GIT_ROOT/docs/screenshots"

PAGES=(
    "/"
    "/auth/signin/"
    "/auth/signup/"
    "/auth/signout/"
    "/new/"
    "/test-user/"
    "/social/explore/"
    "/social/explore/?tab=users"
    "/test-user/test-001/"
    "/test-user/test-001/issues/"
    "/test-user/test-001/pulls/"
    "/test-user/test-001/settings/"
    "/default-project/scitex/writer/01_manuscript/"
    "/accounts/settings/profile/"
    "/accounts/settings/account/"
    "/accounts/settings/appearance/"
    "/accounts/settings/integrations/"
    "/accounts/settings/ssh-keys/"
    "/accounts/settings/api-keys/"
    "test-uesr/settings/repositories/"
    "/scholar/"
    "/scholar/bibtex/"
    "/scholar/search/"
    "/scholar/writer/"
)

mkdir -p "$OUTPUT_DIR"

# scitex web take-screenshot "http://127.0.0.1:8000/"
# # Hera, I woult like to login maually
# read

page_num=0
for page_path in "${PAGES[@]}"; do
    normalized_url=$(echo "$page_path" | sed 's/[^a-zA-Z0-9]/_/g' | sed 's/__*/_/g' | sed 's/^_//' | sed 's/_$//')
    filename=$(printf "%02d_%s" "$page_num" "$normalized_url")

    scitex web take-screenshot "${BASE_URL}${page_path}" --output "$OUTPUT_DIR" --message "$filename"

    page_num=$((page_num + 1))
done

# EOF