#!/bin/bash
# SciTeX Cloud Process Termination Script
# This script stops all running processes related to the SciTeX Cloud application

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to display help message
show_help() {
    echo -e "${CYAN}SciTeX Cloud Process Termination - Help${NC}"
    echo -e "----------------------------------------"
    echo -e "This script stops all running processes related to the SciTeX Cloud application."
    echo -e ""
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  ./stop.sh [OPTION]"
    echo -e ""
    echo -e "${YELLOW}Options:${NC}"
    echo -e "  -h, --help    Display this help message"
    echo -e "  -f, --force   Force kill processes (more aggressive)"
    echo -e "  -q, --quiet   Suppress output except for errors"
    echo -e ""
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  ./stop.sh             # Normal termination"
    echo -e "  ./stop.sh --force     # Force kill all processes"
    echo -e ""
    exit 0
}

# Process command line arguments
FORCE=false
QUIET=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--help) show_help ;;
        -f|--force) FORCE=true; shift ;;
        -q|--quiet) QUIET=true; shift ;;
        *) echo -e "${RED}Unknown parameter: $1${NC}"; exit 1 ;;
    esac
done

# Function to print messages (respects quiet mode)
print_msg() {
    if [ "$QUIET" = false ]; then
        echo -e "$1"
    fi
}

print_msg "${BLUE}🛑 SciTeX Cloud Process Termination${NC}"
print_msg "---------------------------------------"

# Function to check if a process is running
is_process_running() {
    pgrep -f "$1" > /dev/null
    return $?
}

# Function to terminate processes
terminate_process() {
    local process_name=$1
    local signal="-15"  # Default to SIGTERM
    
    if [ "$FORCE" = true ]; then
        signal="-9"  # Use SIGKILL for force mode
    fi
    
    if is_process_running "$process_name"; then
        print_msg "${YELLOW}Stopping $process_name processes...${NC}"
        pkill $signal -f "$process_name" 2>/dev/null
        sleep 0.5
        
        if is_process_running "$process_name"; then
            print_msg "${RED}Failed to stop $process_name processes. Try with --force option.${NC}"
            FAILED=true
        else
            print_msg "${GREEN}✓ $process_name processes stopped.${NC}"
        fi
    else
        print_msg "${GREEN}✓ No $process_name processes running.${NC}"
    fi
}

# Check for root permissions if needed (for socket removal)
SOCK_FILE=/home/ywatanabe/proj/SciTeX-Cloud/uwsgi.sock
FAILED=false

# Remove socket file if it exists
if [ -S "$SOCK_FILE" ]; then
    print_msg "${YELLOW}Removing uWSGI socket file...${NC}"
    rm -f "$SOCK_FILE" 2>/dev/null
    
    if [ -S "$SOCK_FILE" ]; then
        print_msg "${RED}Failed to remove socket file. You may need sudo privileges.${NC}"
        FAILED=true
    else
        print_msg "${GREEN}✓ Socket file removed.${NC}"
    fi
fi

# Stop Django development server (runserver)
if lsof -ti:8000 >/dev/null 2>&1; then
    print_msg "${YELLOW}Stopping Django development server on port 8000...${NC}"
    PORT_PIDS=$(lsof -ti:8000)
    for PID in $PORT_PIDS; do
        if [ "$FORCE" = true ]; then
            kill -9 $PID 2>/dev/null
        else
            kill $PID 2>/dev/null
        fi
    done
    
    sleep 0.5
    
    if lsof -ti:8000 >/dev/null 2>&1; then
        print_msg "${RED}Failed to stop server on port 8000. Try with --force option.${NC}"
        FAILED=true
    else
        print_msg "${GREEN}✓ Server on port 8000 stopped.${NC}"
    fi
else
    print_msg "${GREEN}✓ No server running on port 8000.${NC}"
fi

# Stop various server processes
terminate_process "uwsgi"
terminate_process "daphne"
terminate_process "celery"
terminate_process "manage.py runserver"

# Summary
if [ "$FAILED" = true ]; then
    print_msg "\n${RED}⚠️ Some processes could not be terminated.${NC}"
    print_msg "${RED}Try running with sudo or using the --force option.${NC}"
    exit 1
else
    print_msg "\n${GREEN}🎉 All SciTeX Cloud processes have been stopped successfully.${NC}"
    exit 0
fi