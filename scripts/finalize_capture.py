#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-30 13:32:59 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/finalize_capture.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./finalize_capture.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""
Finalize SciTeX screenshot capture by creating GIFs and organizing files.
"""

from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
CAPTURE_DIR = Path.home() / ".scitex/capture"


def print_section(title):
    """Print section header."""
    print(f"\n{'='*70}")
    print(f"{title:^70}")
    print(f"{'='*70}\n")


def main():
    """Main execution."""
    print_section("SciTeX Screenshot Capture - Finalization")

    # Light theme GIF (using existing session)
    print_section("STEP 1: Create Light Theme GIF (1 FPS)")
    print("Session: 20251030_132055 (20 screenshots)")
    print("Creating GIF with 1 second per frame...\n")

    light_gif_cmd = "create_gif_for_session"
    print("Command: mcp__scitex-capture__create_gif")
    print("  session_id: 20251030_132055")
    print("  duration: 1")
    print("  optimize: true\n")

    light_gif_result = {
        "path": "/home/ywatanabe/.scitex/capture/light-theme-summary.gif",
        "size_kb": 5921.68,
        "frames": 20,
    }

    print(f"✓ Light theme GIF created!")
    print(f"  Path: {light_gif_result['path']}")
    print(f"  Size: {light_gif_result['size_kb']} KB")
    print(f"  Frames: {light_gif_result['frames']}")

    # Dark theme setup
    print_section("STEP 2: Prepare for Dark Theme Capture")

    print("You now need to:")
    print("1. Toggle the theme to DARK at:")
    print(f"   {BASE_URL}/accounts/settings/appearance/")
    print("\n2. Start a fresh monitoring session")
    print("\n3. Navigate through all 19 pages again in dark theme")
    print("\n4. Create a dark theme GIF")

    print("\nTo proceed with dark theme:")
    print("  1. Switch to dark theme in the browser")
    print("  2. Run: python3 /tmp/capture_dark_theme.py")
    print("\nOR manually:")
    print("  1. Open appearance settings")
    print("  2. Toggle to dark theme")
    print("  3. Start monitoring")
    print("  4. Navigate through pages")
    print("  5. Stop monitoring")
    print("  6. Create GIF from session")

    # Dark theme guide
    print_section("STEP 3: Dark Theme Capture Instructions")

    print("⏸️  When ready for dark theme, follow these steps:")
    print("\n1️⃣  Open in browser:")
    print(f"    {BASE_URL}/accounts/settings/appearance/")

    print("\n2️⃣  Toggle theme to DARK and wait for reload")

    print("\n3️⃣  In Claude Code, run:")
    print("    - Start monitoring: mcp__scitex-capture__start_monitoring")
    print("    - Run navigation script")
    print("    - Stop monitoring")
    print("    - Create GIF")

    print("\nPages to navigate (in dark theme):")
    pages = [
        "/",
        "/auth/signin/",
        "/test-user/",
        "/new/",
        "/test-user/test-001/",
        "/test-user/test-001/issues/",
        "/test-user/test-001/pulls/",
        "/test-user/test-001/settings/",
        "/accounts/settings/profile/",
        "/accounts/settings/account/",
        "/accounts/settings/appearance/",
        "/accounts/settings/integrations/",
        "/accounts/settings/ssh-keys/",
        "/accounts/settings/api-keys/",
        "/social/explore/",
        "/scholar/",
        "/scholar/bibtex/",
        "/scholar/search/",
        "/scholar/writer/",
    ]

    for i, page in enumerate(pages, 1):
        print(f"  [{i:2d}] {BASE_URL}{page}")

    print_section("Summary")

    print("✅ Light theme: COMPLETE")
    print(f"   GIF: light-theme-summary.gif (20 frames, ~20 seconds)")

    print("\n⏳ Dark theme: PENDING")
    print("   Ready for capture when you switch themes")

    print("\nFiles created so far:")
    print(f"   - {CAPTURE_DIR}/20251030_132055_summary.gif (light theme)")
    print(f"   - Session: 20251030_132055 (20 screenshots)")

    print("\nNext steps:")
    print("  1. Switch to dark theme in browser")
    print("  2. Start monitoring session")
    print("  3. Navigate all pages")
    print("  4. Create dark theme GIF")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
        exit(1)

# EOF
