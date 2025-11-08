#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-08 04:53:17 (ywatanabe)"
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

BASE_URL = "http://127.0.0.1:8000"
PAGES = (
    # Landing Page
    "/",
    # Auth
    "/auth/signin/",
    "/auth/signup/",
    "/auth/signout/",
    # Repository
    "/new/",
    "/test-user/",
    "/social/explore/",
    "/social/explore/?tab=users",
    "/test-user/test-001/",
    "/test-user/test-001/issues/",
    "/test-user/test-001/pulls/",
    "/test-user/test-001/settings/",
    "/default-project/scitex/writer/01_manuscript/"
    # Accounts
    "/accounts/settings/profile/",
    "/accounts/settings/account/",
    "/accounts/settings/appearance/",
    "/accounts/settings/integrations/",
    "/accounts/settings/ssh-keys/",
    "/accounts/settings/api-keys/",
    "test-uesr/settings/repositories/",
    # Scholar
    "/scholar/",
    "/scholar/bibtex/",
    "/scholar/search/",
    # Writer
    "/scholar/writer/",
    # Etc
    "/social/explore/",
)

scitex web take-screenshot "http://127.0.0.1:8000"
scitex web take-screenshot "http://localhost:8000"

# EOF