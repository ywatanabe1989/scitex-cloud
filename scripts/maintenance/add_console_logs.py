#!/usr/bin/env python3
"""
Add debug console.log statements to TypeScript files
Usage: python scripts/add_debug_logs.py
"""

import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent
TS_DIR = BASE_DIR / "apps" / "project_app" / "static" / "project_app" / "ts"

def add_debug_log(file_path: Path) -> bool:
    """Add console.log debug statement at the top of a TypeScript file"""

    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Get relative path for the log message
    rel_path = file_path.relative_to(BASE_DIR)
    log_statement = f'console.log("[DEBUG] {rel_path} loaded");'

    # Check if debug log already exists
    if '[DEBUG]' in content and str(rel_path) in content:
        print(f"✓ {rel_path} - Debug log already exists")
        return False

    # Find where to insert the log
    # After imports, before the first function/const/class
    lines = content.split('\n')
    insert_index = 0

    # Skip comments and imports at the top
    in_block_comment = False
    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track block comments
        if '/*' in stripped:
            in_block_comment = True
        if '*/' in stripped:
            in_block_comment = False
            insert_index = i + 1
            continue

        # Skip empty lines and single-line comments
        if not stripped or stripped.startswith('//'):
            insert_index = i + 1
            continue

        # Skip imports
        if stripped.startswith('import ') or stripped.startswith('export '):
            insert_index = i + 1
            continue

        # Stop at first actual code
        if not in_block_comment:
            break

    # Insert the debug log
    lines.insert(insert_index, '')
    lines.insert(insert_index + 1, log_statement)
    lines.insert(insert_index + 2, '')

    # Write back
    new_content = '\n'.join(lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✓ {rel_path} - Debug log added")
    return True

def main():
    """Process all TypeScript files"""

    if not TS_DIR.exists():
        print(f"Error: TypeScript directory not found: {TS_DIR}")
        return

    # Find all .ts files
    ts_files = list(TS_DIR.rglob("*.ts"))

    if not ts_files:
        print(f"No TypeScript files found in {TS_DIR}")
        return

    print(f"Found {len(ts_files)} TypeScript files\n")

    modified_count = 0
    for ts_file in sorted(ts_files):
        if add_debug_log(ts_file):
            modified_count += 1

    print(f"\n✅ Done! Modified {modified_count} files, {len(ts_files) - modified_count} already had debug logs")

if __name__ == "__main__":
    main()
