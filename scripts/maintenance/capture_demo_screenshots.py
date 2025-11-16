#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-16 18:59:48 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/scripts/maintenance/capture_demo_screenshots.py


import os

"""
SciTeX Demo Screenshot Capture Script

Captures screenshots of SciTeX pages after logging in as test-user.

Usage:
    python scripts/maintenance/capture_demo_screenshots.py [OPTIONS]

Options:
    --headless              Run browser in headless mode
    --output-dir PATH       Output directory (default: ./demo)
    --width INT             Viewport width (default: 1920)
    --height INT            Viewport height (default: 1080)

Examples:
    # Visible browser (default)
    python scripts/maintenance/capture_demo_screenshots.py

    # Headless mode
    python scripts/maintenance/capture_demo_screenshots.py --headless

    # Custom output
    python scripts/maintenance/capture_demo_screenshots.py --output-dir ./my-screenshots
"""

import asyncio
import sys
import argparse
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
from playwright.async_api import Page
from playwright.async_api import BrowserContext
from scitex.browser import fill_with_fallbacks_async
from scitex.browser import click_with_fallbacks_async


# ============================================================================
# Configuration
# ============================================================================

BASE_URL = "http://127.0.0.1:8000"
TEST_USER = "ywatanabe"
TEST_PASSWORD = "REDACTED"
DEFAULT_OUTPUT_DIR = "./demo"

# Persistent browser session directory (keeps authentication)
SCITEX_DIR = Path(os.getenv("SCITEX_DIR", Path.home() / ".scitex"))
BROWSER_SESSION_DIR = SCITEX_DIR / "browser" / "screenshot_session"

# Pages to capture after login (24 pages total)
PAGES_TO_CAPTURE = [
    # Landing
    {"path": "/", "name": "homepage"},
    # # Auth
    # {"path": "/auth/signin/", "name": "auth-signin"},
    # {"path": "/auth/signup/", "name": "auth-signup"},
    # {"path": "/auth/signout/", "name": "auth-signout"},
    # Repository Operations
    {"path": "/new/", "name": "new-repository"},
    {"path": f"/{TEST_USER}/", "name": "user-profile"},
    # Social/Explore
    {"path": "/social/explore/", "name": "explore-repos"},
    {"path": "/social/explore/?tab=users", "name": "explore-users"},
    # Specific Repository
    {"path": f"/{TEST_USER}/default-project/", "name": "repo-overview"},
    {"path": f"/{TEST_USER}/default-project/issues/", "name": "repo-issues"},
    {"path": f"/{TEST_USER}/default-project/pulls/", "name": "repo-pulls"},
    {
        "path": f"/{TEST_USER}/default-project/settings/",
        "name": "repo-settings",
    },
    # Writer
    {
        "path": f"/{TEST_USER}/default-project/scitex/writer/01_manuscript/",
        "name": "writer-manuscript",
    },
    # Account Settings
    {"path": "/accounts/settings/profile/", "name": "settings-profile"},
    {"path": "/accounts/settings/account/", "name": "settings-account"},
    {
        "path": "/accounts/settings/appearance/",
        "name": "settings-appearance",
    },
    {
        "path": "/accounts/settings/integrations/",
        "name": "settings-integrations",
    },
    {"path": "/accounts/settings/ssh-keys/", "name": "settings-ssh-keys"},
    {"path": "/accounts/settings/api-keys/", "name": "settings-api-keys"},
    {
        "path": f"/{TEST_USER}/settings/repositories/",
        "name": "user-settings-repositories",
    },
    # Scholar
    {"path": "/scholar/bibtex/", "name": "scholar"},
    # Code
    {"path": "/code/", "name": "code"},
    # Vis
    {"path": "/vis/", "name": "vis"},
    # Writer
    {"path": "/writer/", "name": "writer"},
    # Tools
    {"path": "/tools/", "name": "tools"},
]


# ============================================================================
# Terminal Output Utilities
# ============================================================================


class Colors:
    """ANSI color codes for terminal output"""

    GRAY = "\033[0;90m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    RED = "\033[0;31m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"  # No Color


def log_info(msg: str) -> None:
    """Print info message"""
    print(f"{Colors.GRAY}[INFO] {msg}{Colors.NC}")


def log_success(msg: str) -> None:
    """Print success message"""
    print(f"{Colors.GREEN}[✓] {msg}{Colors.NC}")


def log_warning(msg: str) -> None:
    """Print warning message"""
    print(f"{Colors.YELLOW}[⚠] {msg}{Colors.NC}")


def log_error(msg: str) -> None:
    """Print error message"""
    print(f"{Colors.RED}[✗] {msg}{Colors.NC}")


def log_header(msg: str) -> None:
    """Print section header"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"{msg:^70}")
    print(f"{'='*70}{Colors.NC}\n")


def log_progress(current: int, total: int, msg: str) -> None:
    """Print progress indicator"""
    percent = (current / total) * 100
    bar_len = 30
    filled = int(bar_len * current // total)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(
        f"{Colors.BLUE}[{bar}] {current}/{total} ({percent:.0f}%) {msg}{Colors.NC}"
    )


# ============================================================================
# Core Functions
# ============================================================================


async def login_to_scitex(page: Page, username: str, password: str) -> bool:
    """
    Log in to SciTeX using provided credentials.

    Args:
        page: Playwright page object
        username: Username for login
        password: Password for login

    Returns:
        True if login successful, False otherwise
    """
    log_info(f"Attempting login as '{username}'")

    try:
        # Navigate to login page
        login_url = f"{BASE_URL}/auth/signin/"
        log_info(f"Navigating to {login_url}")
        await page.goto(login_url, wait_until="load", timeout=30_000)

        # Wait for page to settle
        await asyncio.sleep(2)

        # Check if already authenticated
        is_authenticated = await page.evaluate(
            "() => document.body.getAttribute('data-user-authenticated') === 'true'"
        )

        if is_authenticated:
            log_success(
                f"Already logged in (detected via data-user-authenticated)"
            )
            # Navigate away from signin page
            await page.goto(BASE_URL, wait_until="load")
            return True

        # Check if still on signin page (might have been redirected if logged in)
        current_url = page.url
        if "/auth/signin" not in current_url:
            log_success("Already logged in (redirected from signin page)")
            return True

        # # Handle any popups
        # popup_handler = PopupHandler(page)
        # await popup_handler.handle_all_popups()

        # Wait for form to be ready
        log_info("Waiting for login form")
        await page.wait_for_selector("form#login-form", timeout=5_000)

        # Fill login form
        log_info("Entering credentials")

        # Username field - use fallback method
        await fill_with_fallbacks_async(
            page, "input#username", username, verbose=False
        )
        await asyncio.sleep(0.3)

        # Password field - use fallback method
        await fill_with_fallbacks_async(
            page, "input#password", password, verbose=False
        )
        await asyncio.sleep(0.3)

        # Submit login form - use fallback click method
        log_info("Submitting login form")
        await click_with_fallbacks_async(
            page, "button.btn-primary.w-100", verbose=False
        )

        # Wait for navigation
        try:
            await page.wait_for_url(
                lambda url: "/auth/signin" not in url, timeout=10_000
            )
            log_info("Navigation detected after login")
        except:
            log_warning("No navigation detected")

        # Additional wait
        await asyncio.sleep(2)

        # Verify login
        current_url = page.url
        log_info(f"Final URL: {current_url}")

        if "/auth/signin" not in current_url:
            log_success(f"Login successful as '{username}'")
            return True
        else:
            # Check for error messages
            try:
                error_msg = await page.text_content(
                    ".alert-danger, .error-message"
                )
                if error_msg:
                    log_error(f"Login failed: {error_msg}")
            except:
                pass
            log_error("Login failed - still on signin page")
            return False

    except Exception as e:
        log_error(f"Login error: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def capture_page_screenshot(
    page: Page,
    page_info: dict,
    output_dir: Path,
    index: int,
    total: int,
    session_timestamp: str,
) -> Path | None:
    """
    Capture a screenshot of a specific SciTeX page.

    Args:
        page: Playwright page object
        page_info: Dict with 'path' and 'name' keys
        output_dir: Directory to save screenshots
        index: Current page number (for progress)
        total: Total number of pages
        session_timestamp: Session timestamp for consistent naming

    Returns:
        Path to saved screenshot, or None if failed
    """
    page_path = page_info["path"]
    page_name = page_info["name"]
    url = f"{BASE_URL}{page_path}"
    wait_sec = 10.0 if page_path in ["code", "writer"] else 1.0

    # Create filename with session timestamp
    screenshot_filename = f"{session_timestamp}/{index:02d}_{page_name}.png"
    screenshot_path = output_dir / screenshot_filename

    log_progress(index, total, f"Capturing {page_name}")
    log_info(f"  → URL: {url}")

    try:
        # Navigate to page
        await page.goto(url, wait_until="load", timeout=30000)

        # Wait for page to settle (but don't wait for networkidle)
        await asyncio.sleep(wait_sec)

        # Take full-page screenshot
        await page.screenshot(
            path=str(screenshot_path), full_page=True, type="png"
        )

        log_success(f"  → Saved: {DEFAULT_OUTPUT_DIR}/{screenshot_filename}")
        return screenshot_path

    except Exception as e:
        log_error(f"  → Failed to capture {page_name}: {str(e)}")
        return None


async def run_screenshot_capture(
    headless: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
) -> int:
    """
    Main workflow to capture demo screenshots.

    Args:
        headless: Run browser in headless mode
        output_dir: Output directory for screenshots
        viewport_width: Browser viewport width
        viewport_height: Browser viewport height

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    log_header("SciTeX Demo Screenshot Capture")

    # Setup
    output_dir.mkdir(parents=True, exist_ok=True)
    BROWSER_SESSION_DIR.mkdir(parents=True, exist_ok=True)
    session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    log_info(f"Session: {session_timestamp}")
    log_info(f"Output: {output_dir}")
    log_info(f"Base URL: {BASE_URL}")
    log_info(f"Pages: {len(PAGES_TO_CAPTURE)}")
    log_info(f"Viewport: {viewport_width}x{viewport_height}")
    log_info(f"Headless: {headless}")

    # Check if session exists
    if (BROWSER_SESSION_DIR / "Default" / "Cookies").exists():
        log_info(
            "Using existing browser session (authentication may be preserved)"
        )
    else:
        log_info("Creating new browser session")

    context: BrowserContext | None = None
    page: Page | None = None

    try:
        async with async_playwright() as p:
            # Launch browser with persistent context
            log_header("Launching Browser")
            log_info(f"Session dir: {BROWSER_SESSION_DIR}")

            # Use persistent context to keep authentication
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(BROWSER_SESSION_DIR),
                headless=headless,
                viewport={"width": viewport_width, "height": viewport_height},
                args=["--start-maximized"] if not headless else [],
                ignore_https_errors=True,
            )
            log_success("Browser launched with persistent session")

            # Get or create page
            if context.pages:
                page = context.pages[0]
            else:
                page = await context.new_page()

            # Step 1: Check/Perform Login
            log_header("Step 1: Authentication")

            # Check if already authenticated
            await page.goto(BASE_URL, wait_until="load")
            await asyncio.sleep(1)

            is_authenticated = await page.evaluate(
                "() => document.body.getAttribute('data-user-authenticated') === 'true'"
            )

            if is_authenticated:
                log_success("Already authenticated (using persistent session)")
            else:
                log_info("Not authenticated, logging in...")
                login_success = await login_to_scitex(
                    page, TEST_USER, TEST_PASSWORD
                )

                if not login_success:
                    log_error("Cannot proceed without authentication")
                    return 1

            # Step 2: Capture screenshots
            log_header("Step 2: Capturing Screenshots")

            captured: list[Path] = []
            failed: list[str] = []
            total = len(PAGES_TO_CAPTURE)

            for i, page_info in enumerate(PAGES_TO_CAPTURE, 1):
                result = await capture_page_screenshot(
                    page, page_info, output_dir, i, total, session_timestamp
                )

                if result:
                    captured.append(result)
                else:
                    failed.append(page_info["name"])

                # Brief pause between captures
                await asyncio.sleep(0.3)

            # Step 3: Summary
            log_header("Summary")
            log_success(f"Captured: {len(captured)}/{total} screenshots")

            if failed:
                log_warning(f"Failed: {len(failed)} screenshot(s)")
                for failed_name in failed:
                    log_warning(f"  - {failed_name}")

            log_info(f"\nOutput directory: {output_dir}")
            log_info(f"Total files: {len(list(output_dir.glob('*.png')))}")

            return 0 if not failed else 1

    except KeyboardInterrupt:
        log_warning("\nInterrupted by user")
        return 130  # Standard exit code for SIGINT

    except Exception as e:
        log_error(f"Unexpected error: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1

    finally:
        # Cleanup - persistent context handles cleanup differently
        try:
            if context:
                await context.close()
                log_info("Browser session saved (authentication persisted)")
        except Exception as e:
            log_warning(f"Cleanup warning: {e}")


# ============================================================================
# CLI Entry Point
# ============================================================================


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Capture SciTeX demo screenshots after logging in as test-user",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Visible browser (default)
  %(prog)s

  # Headless mode
  %(prog)s --headless

  # Custom output directory
  %(prog)s --output-dir ./screenshots

  # Custom viewport size
  %(prog)s --width 1280 --height 720
        """,
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (default: visible)",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        metavar="PATH",
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )

    parser.add_argument(
        "--width",
        type=int,
        default=1920,
        metavar="INT",
        help="Viewport width in pixels (default: 1920)",
    )

    parser.add_argument(
        "--height",
        type=int,
        default=1080,
        metavar="INT",
        help="Viewport height in pixels (default: 1080)",
    )

    return parser.parse_args()


def main() -> None:
    """CLI entry point"""
    args = parse_args()

    try:
        exit_code = asyncio.run(
            run_screenshot_capture(
                headless=args.headless,
                output_dir=args.output_dir,
                viewport_width=args.width,
                viewport_height=args.height,
            )
        )
        sys.exit(exit_code)

    except KeyboardInterrupt:
        log_warning("\nInterrupted by user")
        sys.exit(130)

    except Exception as e:
        log_error(f"Fatal error: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# EOF
