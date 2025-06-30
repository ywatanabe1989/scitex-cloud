#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-01 08:51:23 (ywatanabe)"
# File: ./externals/install_externals.sh

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

cd ./externals

# For Scholar
git clone git@github.com:ywatanabe1989/impact_factor

# SciTeX Static Modules
git clone git@github.com:ywatanabe1989/SciTeX-Scholar
git clone git@github.com:ywatanabe1989/SciTeX-Code
git clone git@github.com:ywatanabe1989/SciTeX-Viz
git clone git@github.com:ywatanabe1989/SciTeX-Writer

ln -s SciTeX-Scholar scholar
ln -s SciTeX-Code code
ln -s SciTeX-Viz viz
ln -s SciTeX-Writer writer

cd scholar && git switch develop && cd ..
cd code && git switch develop && cd ..
cd viz && git switch develop && cd ..
cd writer && git switch develop && cd ..

# EOF