#!/usr/bin/env python3
"""
Design Token Validation Script

This script enforces the design token architecture rules:
1. Components MUST ONLY use semantic tokens (no _ prefix)
2. Primitive tokens (_ prefix) are ONLY allowed in colors.css
3. All violations are reported with file:line_number

Usage:
    python scripts/validate_design_tokens.py
    python scripts/validate_design_tokens.py --fix
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Patterns to detect primitive token usage (tokens starting with --_)
PRIMITIVE_TOKEN_PATTERN = re.compile(r'var\(--_[a-zA-Z0-9-]+\)')

# Directories to scan for CSS/HTML files
SCAN_DIRS = [
    'static/shared/css/',
    'apps/',
    'templates/',
]

# Files that are ALLOWED to use primitive tokens
ALLOWED_FILES = {
    'static/shared/css/common/colors.css',
}


class Violation:
    """Represents a design token violation"""
    def __init__(self, file_path: str, line_num: int, line_content: str, token: str):
        self.file_path = file_path
        self.line_num = line_num
        self.line_content = line_content.strip()
        self.token = token

    def __str__(self):
        return f"{self.file_path}:{self.line_num} - Uses primitive token {self.token}"


def scan_file(file_path: Path) -> List[Violation]:
    """Scan a single file for primitive token usage violations"""
    violations = []

    # Skip allowed files
    if str(file_path) in ALLOWED_FILES:
        return violations

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                # Find all primitive token references
                matches = PRIMITIVE_TOKEN_PATTERN.findall(line)
                for match in matches:
                    violations.append(Violation(
                        file_path=str(file_path),
                        line_num=line_num,
                        line_content=line,
                        token=match
                    ))
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)

    return violations


def scan_directory(directory: Path) -> List[Violation]:
    """Recursively scan directory for violations"""
    all_violations = []

    # Find all CSS and HTML files
    for pattern in ['**/*.css', '**/*.html']:
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                violations = scan_file(file_path)
                all_violations.extend(violations)

    return all_violations


def main():
    """Main validation logic"""
    print("=" * 80)
    print("SciTeX Design Token Validator")
    print("=" * 80)
    print()
    print("RULES:")
    print("  • Components MUST ONLY use semantic tokens (no _ prefix)")
    print("  • Primitive tokens (_ prefix) are ONLY allowed in colors.css")
    print()
    print("Scanning directories:")
    for scan_dir in SCAN_DIRS:
        print(f"  • {scan_dir}")
    print()

    # Collect all violations
    all_violations = []
    for scan_dir in SCAN_DIRS:
        dir_path = Path(scan_dir)
        if dir_path.exists():
            violations = scan_directory(dir_path)
            all_violations.extend(violations)

    # Report results
    if not all_violations:
        print("✓ No violations found!")
        print()
        print("All components are using semantic tokens correctly.")
        return 0

    # Group violations by file
    violations_by_file = {}
    for violation in all_violations:
        if violation.file_path not in violations_by_file:
            violations_by_file[violation.file_path] = []
        violations_by_file[violation.file_path].append(violation)

    print(f"✗ Found {len(all_violations)} violations in {len(violations_by_file)} files:")
    print()

    for file_path, violations in sorted(violations_by_file.items()):
        print(f"{file_path} ({len(violations)} violations):")
        for violation in violations:
            print(f"  Line {violation.line_num}: {violation.token}")
            print(f"    → {violation.line_content[:80]}")
        print()

    print("=" * 80)
    print("NEXT STEPS:")
    print("  1. Replace primitive tokens (--_*) with semantic tokens")
    print("  2. Refer to static/shared/css/common/colors.css for available semantic tokens")
    print("  3. Use tokens like: --text-primary, --bg-primary, --border-primary, etc.")
    print("=" * 80)

    return 1  # Exit with error code


if __name__ == '__main__':
    sys.exit(main())
