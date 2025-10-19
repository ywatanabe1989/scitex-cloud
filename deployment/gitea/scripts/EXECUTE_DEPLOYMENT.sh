#!/bin/bash
# -*- coding: utf-8 -*-
# Gitea Production Deployment - Execute Now
# Run this script to deploy Gitea to production
# ----------------------------------------

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Gitea Production Deployment for SciTeX Cloud"
echo "  Server: $(hostname -I | awk '{print $1}')"
echo "  Domain: git.scitex.ai"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run with sudo"
    echo ""
    echo "Usage:"
    echo "  sudo $0"
    echo ""
    exit 1
fi

# Navigate to project directory
cd /home/ywatanabe/proj/scitex-cloud

# Run the deployment script
exec ./deployment/gitea/deploy-production.sh

# EOF
