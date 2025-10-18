#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: 2025-10-18
# File: /home/ywatanabe/proj/scitex-cloud/scripts/backup_database.sh
# Description: Backup PostgreSQL and SQLite databases for SciTeX Cloud

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get project root directory (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_ROOT/data/db/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

echo -e "${GREEN}SciTeX Cloud Database Backup${NC}"
echo "=============================="
echo "Timestamp: $TIMESTAMP"
echo "Backup directory: $BACKUP_DIR"
echo ""

# Function to backup PostgreSQL database
backup_postgres() {
    local db_name=$1
    local db_user=$2
    local backup_file="$BACKUP_DIR/${db_name}_${TIMESTAMP}.sql"

    echo -e "${YELLOW}Backing up PostgreSQL: $db_name${NC}"

    if command -v pg_dump &> /dev/null; then
        if pg_isready -q 2>/dev/null; then
            if pg_dump -U "$db_user" "$db_name" > "$backup_file" 2>/dev/null; then
                echo -e "${GREEN}✓ PostgreSQL backup created: $backup_file${NC}"

                # Compress the backup
                gzip "$backup_file"
                echo -e "${GREEN}✓ Compressed: ${backup_file}.gz${NC}"
                return 0
            else
                echo -e "${RED}✗ Failed to backup $db_name (may not exist or no access)${NC}"
                return 1
            fi
        else
            echo -e "${YELLOW}⚠ PostgreSQL is not running, skipping PostgreSQL backup${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ pg_dump not found, skipping PostgreSQL backup${NC}"
        return 1
    fi
}

# Function to backup SQLite database
backup_sqlite() {
    local db_file=$1
    local db_name=$(basename "$db_file" .db)
    local backup_file="$BACKUP_DIR/${db_name}_${TIMESTAMP}.db"

    echo -e "${YELLOW}Backing up SQLite: $db_name${NC}"

    if [ -f "$db_file" ]; then
        cp "$db_file" "$backup_file"
        echo -e "${GREEN}✓ SQLite backup created: $backup_file${NC}"

        # Compress the backup
        gzip "$backup_file"
        echo -e "${GREEN}✓ Compressed: ${backup_file}.gz${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ SQLite database not found: $db_file${NC}"
        return 1
    fi
}

# Main backup process
echo "Starting backup process..."
echo ""

# Backup PostgreSQL databases
echo "=== PostgreSQL Backups ==="
backup_postgres "scitex_cloud_dev" "scitex_dev"
backup_postgres "scitex_cloud_prod" "scitex_prod"
echo ""

# Backup SQLite databases (fallback)
echo "=== SQLite Backups ==="
backup_sqlite "$PROJECT_ROOT/data/db/sqlite/scitex_cloud_dev.db"
backup_sqlite "$PROJECT_ROOT/data/db/sqlite/scitex_cloud_prod.db"
echo ""

# Clean up old backups (keep last 7 days)
echo "=== Cleanup Old Backups ==="
echo "Removing backups older than 7 days..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.db.gz" -mtime +7 -delete
echo -e "${GREEN}✓ Cleanup completed${NC}"
echo ""

# Show backup summary
echo "=== Backup Summary ==="
echo "Recent backups:"
ls -lh "$BACKUP_DIR" | tail -n 10
echo ""
echo "Disk usage:"
du -sh "$BACKUP_DIR"
echo ""

echo -e "${GREEN}Backup completed successfully!${NC}"
echo "Timestamp: $TIMESTAMP"

# EOF
