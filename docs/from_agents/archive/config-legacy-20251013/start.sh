#!/bin/bash
# SciTeX Cloud Unified Startup Script
# This script automatically detects and runs startup scripts

set -e  # Exit on any error

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to display help message
show_help() {
    echo -e "${CYAN}SciTeX Cloud Startup Manager - Help${NC}"
    echo -e "----------------------------------------"
    echo -e "This script automatically detects and runs available startup scripts."
    echo -e ""
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  ./server.sh [OPTION|MODE]"
    echo -e ""
    echo -e "${YELLOW}Options:${NC}"
    echo -e "  -h, --help    Display this help message"
    echo -e "  stop          Stop all running SciTeX Cloud processes"
    echo -e ""
    echo -e "${YELLOW}Startup Modes:${NC}"
    echo -e "  dev           Start in development mode"
    echo -e "  windows       Start in Windows/WSL optimized mode"
    echo -e "  prod          Start in production mode"
    echo -e ""
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  ./server.sh                # Interactive mode, menu-based selection"
    echo -e "  ./server.sh dev            # Start in development mode"
    echo -e "  ./server.sh prod           # Start in production mode"
    echo -e "  ./server.sh stop           # Stop all running processes"
    echo -e ""
    echo -e "When no arguments are provided, the script:"
    echo -e "  1. Automatically selects Windows mode if running in WSL"
    echo -e "  2. Presents a menu if multiple options are available"
    echo -e "  3. Runs the only available script if just one exists"
    echo -e ""
    exit 0
}

# Check for help flags and stop command
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
fi

# Check for stop command
if [[ "$1" == "stop" ]]; then
    # If stop.sh exists, run it
    if [ -f "./stop.sh" ]; then
        exec ./stop.sh "${@:2}"
    else
        echo -e "${RED}❌ stop.sh not found in the current directory!${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}🚀 SciTeX Cloud Startup Manager${NC}"
echo "---------------------------------------"

# Function to check if running in WSL
is_wsl() {
    grep -q "Microsoft" /proc/version 2>/dev/null
    return $?
}

# Base script paths
SCRIPT_DIR="./scripts"
BASE_DIR=$(dirname "$0")
cd "$BASE_DIR" # Ensure we're in the project root

# Find available startup scripts
available_scripts=()
if [ -d "$SCRIPT_DIR" ]; then
    for script in "$SCRIPT_DIR"/start_*.sh; do
        if [ -f "$script" ]; then
            available_scripts+=("$script")
        fi
    done
fi

# Add root-level scripts
for script in ./start_*.sh; do
    if [ -f "$script" ]; then
        available_scripts+=("$script")
    fi
done

# Remove duplicates
available_scripts=($(printf "%s\n" "${available_scripts[@]}" | sort -u))

# Count scripts
count=${#available_scripts[@]}

if [ $count -eq 0 ]; then
    echo -e "${RED}❌ No startup scripts found!${NC}"
    exit 1
fi

# Check for argument
if [ $# -gt 0 ]; then
    SELECTED=$1
    for script in "${available_scripts[@]}"; do
        script_name=$(basename "$script" .sh)
        if [[ $script_name == *"$SELECTED"* ]]; then
            echo -e "${GREEN}▶ Running script: $script${NC}"
            chmod +x "$script"
            exec "$script" "${@:2}"
            exit 0
        fi
    done
    echo -e "${RED}❌ No script matching '$SELECTED' found${NC}"
    exit 1
fi

# Check if we should run a dev_windows script
if is_wsl; then
    for script in "${available_scripts[@]}"; do
        if [[ $script == *"windows"* ]]; then
            echo -e "${GREEN}🪟 WSL environment detected, automatically selecting:${NC} $script"
            chmod +x "$script"
            exec "$script"
            exit 0
        fi
    done
fi

# Auto-select if only one option
if [ $count -eq 1 ]; then
    echo -e "${GREEN}▶ Running the only available script:${NC} ${available_scripts[0]}"
    chmod +x "${available_scripts[0]}"
    exec "${available_scripts[0]}"
    exit 0
fi

# Otherwise, present a menu
echo -e "${YELLOW}📋 Available startup scripts:${NC}"
echo ""

# Display menu
for i in "${!available_scripts[@]}"; do
    script="${available_scripts[$i]}"
    script_name=$(basename "$script" .sh)
    
    # Extract and display script description
    description=$(grep -m 1 "# SciTeX" "$script" | cut -d'#' -f2-)
    
    # Default description if none found
    if [ -z "$description" ]; then
        description=" Generic startup script"
    fi
    
    echo -e "$((i+1)). ${BLUE}$script_name${NC} -$description"
done

echo ""
read -p "Enter a number to select a script (1-$count): " selection

# Validate selection
if [[ ! $selection =~ ^[0-9]+$ ]] || [ $selection -lt 1 ] || [ $selection -gt $count ]; then
    echo -e "${RED}❌ Invalid selection${NC}"
    exit 1
fi

# Run selected script
selected_script=${available_scripts[$((selection-1))]}
echo -e "${GREEN}▶ Running:${NC} $selected_script"
chmod +x "$selected_script"
exec "$selected_script"