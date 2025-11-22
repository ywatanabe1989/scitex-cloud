#!/bin/bash
# ============================================
# Check File Sizes - Detect files >300 lines
# ============================================
# Location: /scripts/check_file_sizes.sh
#
# Purpose: Warn about files exceeding the 300-line threshold
# See: GITIGNORED/RULES/06_FILE_SIZE_LIMITS.md
#
# Usage:
#   ./scripts/check_file_sizes.sh           # Show warnings
#   ./scripts/check_file_sizes.sh --quiet   # Exit code only
#   ./scripts/check_file_sizes.sh --verbose # Detailed report

# Colors
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m'

# Configuration
THRESHOLD=300
MODE="${1:-normal}"

# Count files exceeding threshold
count_large_files() {
    local extension="$1"
    local exclude_pattern="$2"

    if [ -n "$exclude_pattern" ]; then
        find apps/ static/ templates/ -name "*.$extension" \
            ! -path "*/node_modules/*" \
            ! -path "*/.tsbuild/*" \
            ! -path "*/.old/*" \
            ! -path "*/legacy/*" \
            ! -path "*/migrations/*" \
            ! -name "*.d.ts" \
            $exclude_pattern \
            -exec wc -l {} + 2>/dev/null | \
            awk -v threshold=$THRESHOLD '$1 > threshold && $2 != "total"' | \
            wc -l
    else
        find apps/ static/ templates/ -name "*.$extension" \
            ! -path "*/node_modules/*" \
            ! -path "*/.tsbuild/*" \
            ! -path "*/.old/*" \
            ! -path "*/legacy/*" \
            ! -path "*/migrations/*" \
            ! -name "*.d.ts" \
            -exec wc -l {} + 2>/dev/null | \
            awk -v threshold=$THRESHOLD '$1 > threshold && $2 != "total"' | \
            wc -l
    fi
}

# Get worst offender for a file type
get_worst_offender() {
    local extension="$1"

    find apps/ static/ templates/ -name "*.$extension" \
        ! -path "*/node_modules/*" \
        ! -path "*/.tsbuild/*" \
        ! -path "*/.old/*" \
        ! -path "*/legacy/*" \
        ! -path "*/migrations/*" \
        ! -name "*.d.ts" \
        -exec wc -l {} + 2>/dev/null | \
        grep -v "total" | \
        sort -rn | \
        head -1
}

# Count files by severity
count_by_severity() {
    local extension="$1"
    local min_lines="$2"

    find apps/ static/ templates/ -name "*.$extension" \
        ! -path "*/node_modules/*" \
        ! -path "*/.tsbuild/*" \
        ! -path "*/.old/*" \
        ! -path "*/legacy/*" \
        ! -path "*/migrations/*" \
        ! -name "*.d.ts" \
        -exec wc -l {} + 2>/dev/null | \
        awk -v min=$min_lines '$1 > min && $2 != "total"' | \
        wc -l
}

# Main check
check_files() {
    # Count large files by type
    ts_count=$(count_large_files "ts")
    py_count=$(count_large_files "py")
    css_count=$(count_large_files "css")
    html_count=$(count_large_files "html")

    total=$((ts_count + py_count + css_count + html_count))

    if [ "$MODE" = "--quiet" ]; then
        [ $total -eq 0 ] && exit 0 || exit 1
    fi

    # Always show if there are violations
    if [ $total -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}⚠️  File Size Warning: $total files exceed 300-line threshold${NC}"
        echo -e "${CYAN}   See: GITIGNORED/RULES/06_FILE_SIZE_LIMITS.md${NC}"
        echo ""

        # Show counts by type
        [ $ts_count -gt 0 ] && {
            worst_ts=$(get_worst_offender "ts")
            ts_lines=$(echo "$worst_ts" | awk '{print $1}')
            ts_file=$(echo "$worst_ts" | awk '{print $2}')
            ts_multiplier=$((ts_lines / THRESHOLD))

            # Count critical files (>3000 lines = 10x threshold)
            ts_critical=$(count_by_severity "ts" 3000)

            echo -e "${YELLOW}   TypeScript: $ts_count files${NC}"
            if [ $ts_critical -gt 0 ]; then
                echo -e "${RED}     🔥 $ts_critical CRITICAL (>3000 lines)${NC}"
            fi
            echo -e "${CYAN}     Worst: ${ts_file##*/} (${ts_lines} lines, ${ts_multiplier}x threshold)${NC}"
        }

        [ $py_count -gt 0 ] && {
            worst_py=$(get_worst_offender "py")
            py_lines=$(echo "$worst_py" | awk '{print $1}')
            py_file=$(echo "$worst_py" | awk '{print $2}')
            echo -e "${YELLOW}   Python: $py_count files${NC}"
            echo -e "${CYAN}     Worst: ${py_file##*/} (${py_lines} lines)${NC}"
        }

        [ $css_count -gt 0 ] && {
            worst_css=$(get_worst_offender "css")
            css_lines=$(echo "$worst_css" | awk '{print $1}')
            css_file=$(echo "$worst_css" | awk '{print $2}')
            echo -e "${YELLOW}   CSS: $css_count files${NC}"
            echo -e "${CYAN}     Worst: ${css_file##*/} (${css_lines} lines)${NC}"
        }

        [ $html_count -gt 0 ] && {
            worst_html=$(get_worst_offender "html")
            html_lines=$(echo "$worst_html" | awk '{print $1}')
            html_file=$(echo "$worst_html" | awk '{print $2}')
            echo -e "${YELLOW}   HTML: $html_count files${NC}"
            echo -e "${CYAN}     Worst: ${html_file##*/} (${html_lines} lines)${NC}"
        }

        echo ""
        echo -e "${CYAN}💡 To see full list: ./scripts/check_file_sizes.sh --verbose${NC}"
        echo ""
    else
        if [ "$MODE" = "--verbose" ]; then
            echo ""
            echo -e "${GREEN}✅ All files within 300-line threshold!${NC}"
            echo ""
        fi
    fi

    # Verbose mode - show all violations
    if [ "$MODE" = "--verbose" ] && [ $total -gt 0 ]; then
        echo -e "${CYAN}=== Detailed Report ===${NC}"
        echo ""

        if [ $ts_count -gt 0 ]; then
            echo -e "${YELLOW}TypeScript files (>$THRESHOLD lines):${NC}"
            find apps/ static/ -name "*.ts" \
                ! -path "*/node_modules/*" \
                ! -path "*/.tsbuild/*" \
                ! -path "*/.old/*" \
                ! -path "*/legacy/*" \
                ! -name "*.d.ts" \
                -exec wc -l {} + 2>/dev/null | \
                awk -v threshold=$THRESHOLD '$1 > threshold && $2 != "total"' | \
                sort -rn | \
                head -20 | \
                awk '{printf "  %5d lines: %s\n", $1, $2}'
            echo ""
        fi

        if [ $css_count -gt 0 ]; then
            echo -e "${YELLOW}CSS files (>$THRESHOLD lines):${NC}"
            find apps/ static/ -name "*.css" \
                ! -path "*/node_modules/*" \
                ! -path "*/.old/*" \
                ! -path "*/legacy/*" \
                -exec wc -l {} + 2>/dev/null | \
                awk -v threshold=$THRESHOLD '$1 > threshold && $2 != "total"' | \
                sort -rn | \
                head -20 | \
                awk '{printf "  %5d lines: %s\n", $1, $2}'
            echo ""
        fi

        if [ $html_count -gt 0 ]; then
            echo -e "${YELLOW}HTML files (>$THRESHOLD lines):${NC}"
            find apps/ templates/ -name "*.html" \
                ! -path "*/.old/*" \
                ! -path "*/legacy/*" \
                -exec wc -l {} + 2>/dev/null | \
                awk -v threshold=$THRESHOLD '$1 > threshold && $2 != "total"' | \
                sort -rn | \
                head -20 | \
                awk '{printf "  %5d lines: %s\n", $1, $2}'
            echo ""
        fi
    fi

    return 0
}

# Run check
check_files
