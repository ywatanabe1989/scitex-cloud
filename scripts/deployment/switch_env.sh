#!/bin/bash
# -*- coding: utf-8 -*-
# SciTeX Cloud - Environment Switcher
# Usage: source scripts/switch_env.sh [dev|prod]

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DOTENVS_DIR="$PROJECT_ROOT/deployment/dotenvs"
ENV_LINK="$PROJECT_ROOT/.env"

# ----------------------------------------
# Determine environment
# ----------------------------------------
if [ $# -eq 0 ]; then
    # No argument - detect from current symlink or default to dev
    if [ -L "$ENV_LINK" ]; then
        current_target=$(readlink "$ENV_LINK")
        if [[ "$current_target" == *"dotenv.prod"* ]]; then
            ENV="prod"
        else
            ENV="dev"
        fi
        echo "Current environment: $ENV"
        echo "Usage: source scripts/switch_env.sh [dev|prod]"
        return 0 2>/dev/null || exit 0
    else
        ENV="dev"
    fi
else
    ENV="$1"
fi

# ----------------------------------------
# Validate environment
# ----------------------------------------
case "$ENV" in
    dev|development)
        ENV="dev"
        ENV_FILE="$DOTENVS_DIR/dotenv.dev"
        ;;
    prod|production)
        ENV="prod"
        ENV_FILE="$DOTENVS_DIR/dotenv.prod"
        ;;
    *)
        echo "Error: Invalid environment '$ENV'"
        echo "Usage: source scripts/switch_env.sh [dev|prod]"
        return 1 2>/dev/null || exit 1
        ;;
esac

# ----------------------------------------
# Check if env file exists
# ----------------------------------------
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Environment file not found: $ENV_FILE"
    return 1 2>/dev/null || exit 1
fi

# ----------------------------------------
# Create/update symlink
# ----------------------------------------
echo "🔄 Switching to $ENV environment..."

# Remove old symlink if exists
if [ -L "$ENV_LINK" ]; then
    rm "$ENV_LINK"
fi

# Create new symlink (relative path)
ln -sf "deployment/dotenvs/dotenv.$ENV" "$ENV_LINK"
echo "✅ Created symlink: .env -> deployment/dotenvs/dotenv.$ENV"

# ----------------------------------------
# Source the environment file
# ----------------------------------------
echo "📦 Loading environment variables..."
source "$ENV_FILE"

# ----------------------------------------
# Display current configuration
# ----------------------------------------
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 SciTeX Cloud - Environment: $ENV"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Django Settings: $DJANGO_SETTINGS_MODULE"
if [ "$ENV" = "dev" ]; then
    echo "Database: $SCITEX_CLOUD_DB_NAME_DEV"
    echo "DB User: $SCITEX_CLOUD_DB_USER_DEV"
    echo "DB Host: $SCITEX_CLOUD_DB_HOST_DEV:$SCITEX_CLOUD_DB_PORT_DEV"
else
    echo "Database: $SCITEX_CLOUD_DB_NAME_PROD"
    echo "DB User: $SCITEX_CLOUD_DB_USER_PROD"
    echo "DB Host: $SCITEX_CLOUD_DB_HOST_PROD:$SCITEX_CLOUD_DB_PORT_PROD"
fi
echo "Logging Level: $SCITEX_LOGGING_LEVEL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ----------------------------------------
# Optional: Test database connection
# ----------------------------------------
if command -v pg_isready &> /dev/null; then
    if [ "$ENV" = "dev" ]; then
        DB_HOST="$SCITEX_CLOUD_DB_HOST_DEV"
        DB_PORT="$SCITEX_CLOUD_DB_PORT_DEV"
    else
        DB_HOST="$SCITEX_CLOUD_DB_HOST_PROD"
        DB_PORT="$SCITEX_CLOUD_DB_PORT_PROD"
    fi

    if pg_isready -h "$DB_HOST" -p "$DB_PORT" &> /dev/null; then
        echo "✅ PostgreSQL is ready at $DB_HOST:$DB_PORT"
    else
        echo "⚠️  PostgreSQL not responding at $DB_HOST:$DB_PORT"
    fi
fi

echo ""
echo "Ready to use! Try:"
echo "  python manage.py runserver"
echo "  python manage.py migrate"
echo ""

# EOF
