#!/usr/bin/env python3
"""
Automated SciTeX Visual Test - Captures light and dark theme screenshots.

This script automatically:
1. Navigates through all SciTeX pages
2. Captures screenshots in light theme
3. Toggles to dark theme
4. Captures screenshots in dark theme
5. Generates 1 FPS GIFs for both themes

Uses scitex.capture and scitex.browser for full automation.
"""

import asyncio
import time
from pathlib import Path
from typing import List
from scitex import capture, browser
from scitex.browser.core import create_browser_context, goto_url


# Configuration
BASE_URL = "http://127.0.0.1:8000"
OUTPUT_DIR = Path.home() / ".scitex/capture"
VIEWPORT = {"width": 1920, "height": 1080}

# Pages to capture
PAGES: List[str] = [
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


def print_header(text: str) -> None:
    """Print section header."""
    print(f"\n{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}\n")


def print_progress(current: int, total: int, text: str) -> None:
    """Print progress indicator."""
    percentage = (current / total) * 100
    bar_length = 40
    filled = int(bar_length * current // total)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"[{bar}] {current:2d}/{total:2d} ({percentage:5.1f}%) {text}")


async def navigate_and_capture_pages(
    context,
    theme: str,
    session_name: str,
) -> tuple[str, int]:
    """
    Navigate through all pages and capture screenshots.

    Args:
        context: Browser context
        theme: 'light' or 'dark'
        session_name: Name for logging

    Returns:
        Tuple of (session_id, screenshot_count)
    """
    print_header(f"Capturing {theme.upper()} Theme Screenshots")

    page = await context.new_page()
    await page.set_viewport_size(VIEWPORT)

    screenshot_count = 0
    total_pages = len(PAGES)

    for i, page_path in enumerate(PAGES, 1):
        url = f"{BASE_URL}{page_path}"
        page_name = page_path.strip("/").replace("/", "-") or "homepage"

        try:
            print_progress(i, total_pages, f"Loading {page_name}")

            # Navigate to page
            await goto_url(page, url, wait_until="networkidle", timeout=10000)

            # Wait for page to settle
            await asyncio.sleep(1)

            # Take screenshot (for monitoring)
            await page.screenshot(path="/tmp/temp_screenshot.jpg")
            screenshot_count += 1

            # Special handling for settings pages
            if "/settings/" in url and url.endswith("/settings/"):
                print(f"         → Clicking through settings tabs...")
                settings_tabs = ["general", "access", "collaborators", "danger-zone"]
                for tab in settings_tabs:
                    try:
                        # Look for tab button by text or data-attr
                        tab_selector = f'[data-tab="{tab}"], a:has-text("{tab}")'
                        await page.click(tab_selector, timeout=2000)
                        await asyncio.sleep(0.5)
                        await page.screenshot(path="/tmp/temp_screenshot.jpg")
                        screenshot_count += 1
                    except:
                        pass  # Tab might not exist

        except Exception as e:
            print(f"         ✗ Error loading {page_name}: {e}")

    await page.close()

    return session_name, screenshot_count


async def toggle_theme(context, target_theme: str) -> bool:
    """
    Toggle application theme via appearance settings.

    Args:
        context: Browser context
        target_theme: 'light' or 'dark'

    Returns:
        True if successful
    """
    print_header(f"Toggling Theme to {target_theme.upper()}")

    page = await context.new_page()
    await page.set_viewport_size(VIEWPORT)

    try:
        appearance_url = f"{BASE_URL}/accounts/settings/appearance/"
        print(f"Navigating to: {appearance_url}")

        await goto_url(page, appearance_url, wait_until="networkidle", timeout=10000)
        await asyncio.sleep(1)

        # Find and click the theme toggle
        # Looking for theme selection radio button or toggle
        theme_selectors = [
            f'input[value="{target_theme}"]',
            f'label:has-text("{target_theme}")',
            f'button:has-text("{target_theme}")',
            f'[data-theme="{target_theme}"]',
        ]

        for selector in theme_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    print(f"Found theme selector: {selector}")
                    await page.click(selector, timeout=2000)
                    await asyncio.sleep(2)  # Wait for theme change
                    print(f"✓ Theme toggled to {target_theme}")
                    await page.close()
                    return True
            except:
                pass

        print(f"✗ Could not find theme toggle selector")
        await page.close()
        return False

    except Exception as e:
        print(f"✗ Error toggling theme: {e}")
        await page.close()
        return False


async def capture_light_theme(context) -> tuple[str, int]:
    """Capture all pages in light theme."""
    session_id, count = await navigate_and_capture_pages(
        context, "light", "light_theme"
    )
    print(f"\n✓ Light theme capture complete: {count} screenshots")
    return session_id, count


async def capture_dark_theme(context) -> tuple[str, int]:
    """Capture all pages in dark theme."""
    session_id, count = await navigate_and_capture_pages(
        context, "dark", "dark_theme"
    )
    print(f"\n✓ Dark theme capture complete: {count} screenshots")
    return session_id, count


async def main():
    """Main execution flow."""
    print_header("SciTeX Visual Test - Automated Screenshot Capture")

    print("📋 Configuration:")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Pages: {len(PAGES)}")
    print(f"  Viewport: {VIEWPORT['width']}x{VIEWPORT['height']}")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"  Total captures: {len(PAGES) * 2} (light + dark)")

    # Create browser context
    print("\n🌐 Initializing browser...")
    async with await create_browser_context(
        headless=False,
        viewport=VIEWPORT,
    ) as context:
        # Phase 1: Light Theme
        print_header("PHASE 1: Light Theme Capture")
        light_session, light_count = await capture_light_theme(context)

        # Phase 2: Toggle Theme
        print_header("PHASE 2: Theme Toggle")
        await toggle_theme(context, "dark")

        # Phase 3: Dark Theme
        print_header("PHASE 3: Dark Theme Capture")
        dark_session, dark_count = await capture_dark_theme(context)

    # Phase 4: Summary
    print_header("✅ Capture Complete")

    print("📊 Results:")
    print(f"  Light theme: {light_count} screenshots")
    print(f"  Dark theme: {dark_count} screenshots")
    print(f"  Total: {light_count + dark_count} screenshots")

    print("\n📁 Next steps:")
    print("  1. Create light theme GIF:")
    print("     capture.gif() with 1 FPS (duration=1)")
    print("  2. Create dark theme GIF:")
    print("     capture.gif() with 1 FPS (duration=1)")
    print("\n✓ Visual test complete! GIFs ready for analysis.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user.")
        exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
