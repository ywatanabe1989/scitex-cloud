#!/bin/bash
# PostgreSQL Setup Script for SciTeX Cloud
# Run this manually: bash tmp/setup_postgres.sh

set -e

echo "=== PostgreSQL Setup for SciTeX Cloud ==="
echo ""
echo "Setting up databases and users..."
echo ""

# Change to a directory postgres user can access to avoid permission warnings
cd /tmp

# Run SQL setup
sudo -u postgres psql << 'EOF'
-- Drop existing databases if they exist (BE CAREFUL!)
DROP DATABASE IF EXISTS scitex_cloud_dev;
DROP DATABASE IF EXISTS scitex_cloud_prod;
DROP USER IF EXISTS scitex_dev;
DROP USER IF EXISTS scitex_prod;

-- Create development database and user
CREATE DATABASE scitex_cloud_dev;
CREATE USER scitex_dev WITH PASSWORD 'scitex_dev_2025';
GRANT ALL PRIVILEGES ON DATABASE scitex_cloud_dev TO scitex_dev;
ALTER DATABASE scitex_cloud_dev OWNER TO scitex_dev;

-- Create production database and user
CREATE DATABASE scitex_cloud_prod;
CREATE USER scitex_prod WITH PASSWORD 'CHANGE_THIS_IN_PRODUCTION';
GRANT ALL PRIVILEGES ON DATABASE scitex_cloud_prod TO scitex_prod;
ALTER DATABASE scitex_cloud_prod OWNER TO scitex_prod;

EOF

# Setup extensions for dev database
sudo -u postgres psql -d scitex_cloud_dev << 'EOF'
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
GRANT ALL ON SCHEMA public TO scitex_dev;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO scitex_dev;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO scitex_dev;
EOF

# Setup extensions for prod database
sudo -u postgres psql -d scitex_cloud_prod << 'EOF'
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
GRANT ALL ON SCHEMA public TO scitex_prod;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO scitex_prod;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO scitex_prod;
EOF

echo ""
echo "✅ PostgreSQL setup complete!"
echo ""
echo "Created databases:"
sudo -u postgres psql -c "\l scitex_cloud_*"
echo ""
echo "Created users:"
sudo -u postgres psql -c "\du scitex_*"
echo ""
echo "Next steps:"

# Check if psycopg2-binary is installed
if python -c "import psycopg2" 2>/dev/null; then
    echo "✅ psycopg2-binary is already installed"
else
    echo "1. Install psycopg2: pip install psycopg2-binary"
fi

echo "2. Update Django settings (if needed)"
echo "3. Run migrations: python manage.py migrate"
