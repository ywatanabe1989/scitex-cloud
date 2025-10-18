#!/bin/bash
# PostgreSQL Production Database Setup for SciTeX Cloud

set -e

echo "=== SciTeX Cloud Production PostgreSQL Setup ==="
echo ""

# Check if running as postgres user
if [ "$USER" != "postgres" ]; then
    echo "This script should be run as postgres user:"
    echo "  sudo -u postgres bash $0"
    exit 1
fi

# Database configuration
DB_NAME="scitex_cloud_prod"
DB_USER="scitex_prod"
DB_PASS="${SCITEX_CLOUD_DB_PASSWORD_PROD:-CHANGE_THIS_PASSWORD}"

echo "Creating database: $DB_NAME"
echo "Creating user: $DB_USER"
echo ""

# Drop existing database and user if they exist
psql << EOF
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;

-- Create user
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';

-- Create database
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER DATABASE $DB_NAME OWNER TO $DB_USER;
EOF

echo "✅ Database and user created"

# Setup extensions
echo "Installing extensions..."
psql -d $DB_NAME << EOF
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
GRANT ALL ON SCHEMA public TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;
EOF

echo "✅ Extensions installed"

# Verify setup
echo ""
echo "Verifying setup..."
psql << EOF
\l $DB_NAME
\du $DB_USER
\c $DB_NAME
\dx
EOF

echo ""
echo "✅ PostgreSQL production setup complete!"
echo ""
echo "Database credentials:"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $DB_PASS"
echo ""
echo "Next steps:"
echo "1. Update .env file with database credentials"
echo "2. Run: python manage.py migrate"
echo "3. Run: python manage.py createsuperuser"
