#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-20 14:50:20 (ywatanabe)"
# File: ./deployment/dotenvs/setup_env.sh

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

NC='\033[0m'

LOG_FILE=".setup_env.sh.log"

usage() {
    echo "Usage: source $0 [--env|-e ENV] [-h|--help]"
    echo
    echo "Options:"
    echo "  --env, -e    Specify environment: dev or prod (default: dev)"
    echo "  -h, --help   Display this help message"
    echo
    echo "Example:"
    echo "  source $0 --env dev"
    echo "  source $0 -e prod"
    return 1 2>/dev/null || exit 1
}

setup_environment() {
    set -e

    PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    DOTENVS_DIR="$PROJECT_ROOT/deployment/dotenvs"
    ENV_LINK="$PROJECT_ROOT/.env"
    ENV=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --env|-e)
                ENV="$2"
                shift 2
                ;;
            -h|--help)
                usage
                ;;
            dev|development|prod|production)
                ENV="$1"
                shift
                ;;
            *)
                echo "Error: Unknown argument '$1'"
                usage
                ;;
        esac
    done

    if [ -z "$ENV" ]; then
        if [ -L "$ENV_LINK" ]; then
            current_target=$(readlink "$ENV_LINK")
            if [[ "$current_target" == *"dotenv_prod"* ]]; then
                ENV="prod"
            else
                ENV="dev"
            fi
            echo "Current environment: $ENV"
            echo "Usage: source $0 --env [dev|prod]"
            return 0 2>/dev/null || exit 0
        else
            ENV="dev"
        fi
    fi

    case "$ENV" in
        dev|development)
            ENV="dev"
            ENV_FILE="$DOTENVS_DIR/dotenv_dev"
            ;;
        prod|production)
            ENV="prod"
            ENV_FILE="$DOTENVS_DIR/dotenv_prod"
            ;;
        *)
            echo "Error: Invalid environment '$ENV'"
            usage
            ;;
    esac

    if [ ! -f "$ENV_FILE" ]; then
        echo "Error: Environment file not found: $ENV_FILE"
        return 1 2>/dev/null || exit 1
    fi

    echo "Setting up $ENV environment..."

    if [ -L "$ENV_LINK" ]; then
        rm "$ENV_LINK"
    fi

    ln -sf "$ENV_FILE" "$ENV_LINK"
    echo "Created symlink: .env -> $ENV_FILE"
    echo "Loading environment variables..."
    source "$ENV_FILE"
    echo ""
    echo "SciTeX Cloud - Environment: $ENV"
    echo "Django Settings: $SCITEX_CLOUD_DJANGO_SETTINGS_MODULE"

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
    echo ""

    if command -v pg_isready &> /dev/null; then
        if [ "$ENV" = "dev" ]; then
            DB_HOST="$SCITEX_CLOUD_DB_HOST_DEV"
            DB_PORT="$SCITEX_CLOUD_DB_PORT_DEV"
        else
            DB_HOST="$SCITEX_CLOUD_DB_HOST_PROD"
            DB_PORT="$SCITEX_CLOUD_DB_PORT_PROD"
        fi

        if pg_isready -h "$DB_HOST" -p "$DB_PORT" &> /dev/null; then
            echo "PostgreSQL is ready at $DB_HOST:$DB_PORT"
        else
            echo "PostgreSQL not responding at $DB_HOST:$DB_PORT"
        fi
    fi

    echo ""
    echo "Ready to use! Try:"
    echo "  python manage.py runserver"
    echo "  python manage.py migrate"
    echo ""
}

main() {
    setup_environment "$@"
}

main "$@" 2>&1 | tee "$LOG_FILE"

