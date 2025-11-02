#!/bin/bash
# Enable HTTPS in nginx configuration (non-interactive)

set -e

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
SITE_CONF="$THIS_DIR/sites-available/scitex_cloud_prod.conf"
SITE_CONF_BAK="$THIS_DIR/.old/scitex_cloud_prod.conf.backup_$(date +%Y%m%d_%H%M%S)"

# Backup
mkdir -p "$THIS_DIR/.old"
cp "$SITE_CONF" "$SITE_CONF_BAK"

# Comment out HTTP server blocks (lines 44-165, 298-325)
sed -i '44,165s/^/# /' "$SITE_CONF"
sed -i '298,325s/^/# /' "$SITE_CONF"

# Uncomment HTTP→HTTPS redirect (lines 23-38)
sed -i '23,38s/^# //' "$SITE_CONF"

# Uncomment HTTPS server blocks (lines 170-293, 330-369)
sed -i '170,293s/^# //' "$SITE_CONF"
sed -i '330,369s/^# //' "$SITE_CONF"

echo "✅ HTTPS enabled in $SITE_CONF"

# EOF
