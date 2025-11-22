#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-25 14:21:37 (ywatanabe)"
# File: ./static/rsync_static_files.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }
# ---------------------------------------

rsync -avz --delete \
    /home/ywatanabe/proj/scitex-cloud/static/ \
    ywatanabe@162.43.35.139:/home/ywatanabe/proj/scitex-cloud/static/ \
    2>&1 | grep -v "protocol version
  mismatch\|bash.d\|completion.src\|decrypt" || true

# Create a tarball locally
cd /home/ywatanabe/proj/scitex-cloud
tar czf /tmp/static.tar.gz static/

# Copy to remote
scp /tmp/static.tar.gz \
    ywatanabe@162.43.35.139:/home/ywatanabe/proj/scitex-cloud

rm /tmp/static.tar.gz

# EOF
