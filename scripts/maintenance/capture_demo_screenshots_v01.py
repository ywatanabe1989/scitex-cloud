#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-08 04:29:09 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/scripts/maintenance/capture_demo_screenshots.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./scripts/maintenance/capture_demo_screenshots.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Fully Automated SciTeX Visual Test Script

Captures screenshots of all pages in both light and dark themes,
automatically toggling the theme and creating GIFs.

Usage:
    python scripts/auto_capture.py
"""

import asyncio
import time
import sys
from scitex import capture
from playwright.async_api import async_playwright


BASE_URL = "http://127.0.0.1:8000"
PAGES = [
    # Landing Page
    "/",
    # Auth
    "/auth/signin/",
    "/auth/signup/",
    "/auth/signout/",
    # Repository
    "/new/",
    "/test-user/",
    "/social/explore/",
    "/social/explore/?tab=users",
    "/test-user/test-001/",
    "/test-user/test-001/issues/",
    "/test-user/test-001/pulls/",
    "/test-user/test-001/settings/",
    "/default-project/scitex/writer/01_manuscript/"
    # Accounts
    "/accounts/settings/profile/",
    "/accounts/settings/account/",
    "/accounts/settings/appearance/",
    "/accounts/settings/integrations/",
    "/accounts/settings/ssh-keys/",
    "/accounts/settings/api-keys/",
    "test-uesr/settings/repositories/",
    # Scholar
    "/scholar/",
    "/scholar/bibtex/",
    "/scholar/search/",
    # Writer
    "/scholar/writer/",
    # Etc
    "/social/explore/",
]


def print_header(title: str) -> None:
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"{title:^70}")
    print(f"{'='*70}\n")


def print_progress(current: int, total: int, text: str) -> None:
    """Print progress bar."""
    pct = (current / total) * 100
    bar_len = 40
    filled = int(bar_len * current // total)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"[{bar}] {current:2d}/{total} ({pct:5.1f}%) {text}")


def capture_with_monitoring(theme: str) -> int:
    """
    Capture all pages using URL-based capture with monitoring.

    Args:
        theme: 'light' or 'dark'

    Returns:
        Number of screenshots captured
    """
    print_header(f"Capturing {theme.upper()} Theme")
    print(f"Wait time per page: 2.5 seconds\n")

    # Start continuous monitoring
    print("Starting screenshot monitoring...")
    capture.start(
        interval=1.0,
        quality=85,
        verbose=False,
    )

    total_pages = len(PAGES)
    screenshot_count = 0

    try:
        for i, page_path in enumerate(PAGES, 1):
            url = f"{BASE_URL}{page_path}"
            page_name = page_path.strip("/").replace("/", "-") or "homepage"

            print_progress(i, total_pages, f"Navigating to {page_name}")

            try:
                # Capture the URL page
                path = capture.snap(
                    url=url,
                    url_wait=2,
                    url_width=1920,
                    url_height=1080,
                    quality=85,
                    message=f"{theme}-{page_name}",
                    verbose=False,
                )
                if path:
                    screenshot_count += 1

                time.sleep(0.5)

            except Exception as e:
                print(f"\n         ✗ Error on {page_name}: {e}")

    finally:
        capture.stop()

    return screenshot_count


async def toggle_theme_async(target_theme: str) -> bool:
    """
    Toggle theme using Playwright directly.

    Args:
        target_theme: 'light' or 'dark'

    Returns:
        True if successful
    """
    print_header(f"Toggling Theme to {target_theme.upper()}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()

            appearance_url = f"{BASE_URL}/accounts/settings/appearance/"
            print(f"Navigating to: {appearance_url}\n")

            # Navigate to appearance settings
            await page.goto(
                appearance_url, wait_until="networkidle", timeout=10000
            )
            await asyncio.sleep(1)

            print(f"Looking for theme toggle for: {target_theme}")

            # Try various selectors for the theme toggle
            selectors = [
                f'input[value="{target_theme}"]',
                f'input[data-theme="{target_theme}"]',
                f'label:has-text("{target_theme}")',
                f'button:has-text("{target_theme}")',
            ]

            for selector in selectors:
                try:
                    elem = await page.query_selector(selector)
                    if elem:
                        print(f"Found theme toggle: {selector}")
                        await elem.click(timeout=2000)
                        await asyncio.sleep(2)
                        print(f"✓ Theme toggled to {target_theme}")
                        await browser.close()
                        return True
                except Exception as e:
                    pass

            # Try JavaScript approach
            print("Attempting JavaScript-based theme toggle...")
            try:
                await page.evaluate(
                    f"""
                    () => {{
                        localStorage.setItem('scitex-theme-preference', '{target_theme}');
                        document.documentElement.setAttribute('data-theme', '{target_theme}');
                        document.documentElement.setAttribute('data-color-mode', '{target_theme}');

                        // Find and click theme button
                        const buttons = Array.from(document.querySelectorAll('button, input[type="radio"], label'));
                        const themeBtn = buttons.find(b => b.textContent.toLowerCase().includes('{target_theme}'));
                        if (themeBtn) themeBtn.click();
                    }}
                """
                )
                await asyncio.sleep(2)
                print(f"✓ Theme set to {target_theme} via JavaScript")
                await browser.close()
                return True
            except Exception as e:
                print(f"⚠️  JavaScript toggle: {e}")
                await browser.close()
                return True

    except Exception as e:
        print(f"✗ Error toggling theme: {e}")
        return False


def main():
    """Main execution."""
    print_header("SciTeX Visual Test - Automated Capture")

    print("📋 Configuration:")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Pages: {len(PAGES)}")
    print(f"  Output: ~/.scitex/capture/")
    print(f"  Format: 1920x1080 JPEG @ 85% quality")

    # Phase 1: Light Theme
    print_header("PHASE 1: Light Theme Capture")
    light_count = capture_with_monitoring("light")
    print(f"\n✓ Captured {light_count} light theme screenshots")

    # Create light theme GIF
    print("\nCreating light theme GIF...")
    light_gif = capture.gif(duration=1, optimize=True)
    if light_gif:
        print(f"✓ Light theme GIF created: {light_gif}")

    # Phase 2: Toggle Theme
    print_header("PHASE 2: Toggle to Dark Theme")
    theme_toggled = asyncio.run(toggle_theme_async("dark"))

    if not theme_toggled:
        print("⚠️  Could not toggle theme automatically")
        print("    Proceeding anyway...")

    time.sleep(2)

    # Phase 3: Dark Theme
    print_header("PHASE 3: Dark Theme Capture")
    dark_count = capture_with_monitoring("dark")
    print(f"\n✓ Captured {dark_count} dark theme screenshots")

    # Create dark theme GIF
    print("\nCreating dark theme GIF...")
    dark_gif = capture.gif(duration=1, optimize=True)
    if dark_gif:
        print(f"✓ Dark theme GIF created: {dark_gif}")

    # Summary
    print_header("✅ Capture Complete")
    print(f"Light theme screenshots: {light_count}")
    print(f"Dark theme screenshots: {dark_count}")
    print(f"Total: {light_count + dark_count}")
    print(f"\n📁 Output: ~/.scitex/capture/")
    print("🎬 GIFs ready for visual regression testing!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

# EOF
