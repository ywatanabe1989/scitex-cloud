#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Screenshot Capture - With Sample Data

Captures screenshots with realistic demo data for promotional materials.
Includes interactions like performing searches, selecting papers, etc.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.settings_dev")
import django
django.setup()

from playwright.sync_api import sync_playwright
from scitex import logging

logger = logging.getLogger(__name__)


def capture_scholar_with_search(page, output_dir: Path):
    """Capture Scholar page with search results"""
    logger.info("Capturing Scholar with search results...")

    # Navigate to Scholar
    page.goto("http://127.0.0.1:8000/scholar/#search", wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)

    # Perform a search
    search_input = page.query_selector('input[name="q"]')
    if search_input:
        search_input.fill("deep learning neural networks")
        search_input.press("Enter")

        # Wait for results
        logger.info("Waiting for search results...")
        time.sleep(5)

        # Capture search results
        screenshot_path = output_dir / "scholar_search_with_results.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        logger.info(f"✓ Saved: {screenshot_path}")

        # Select some papers
        checkboxes = page.query_selector_all('.paper-select-checkbox')
        if len(checkboxes) >= 3:
            logger.info("Selecting papers...")
            for i in range(min(3, len(checkboxes))):
                checkboxes[i].check()
            time.sleep(1)

            # Capture with selected papers
            screenshot_path = output_dir / "scholar_papers_selected.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info(f"✓ Saved: {screenshot_path}")

        # Switch abstract view
        all_button = page.query_selector('button[data-mode="all"]')
        if all_button:
            logger.info("Showing full abstracts...")
            all_button.click()
            time.sleep(1)

            screenshot_path = output_dir / "scholar_full_abstracts.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info(f"✓ Saved: {screenshot_path}")


def capture_scholar_bibtex(page, output_dir: Path):
    """Capture BibTeX manager"""
    logger.info("Capturing BibTeX manager...")

    # Navigate to BibTeX tab
    page.goto("http://127.0.0.1:8000/scholar/#bibtex", wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)

    # Capture
    screenshot_path = output_dir / "scholar_bibtex.png"
    page.screenshot(path=str(screenshot_path), full_page=True)
    logger.info(f"✓ Saved: {screenshot_path}")


def capture_scholar_plots(page, output_dir: Path):
    """Capture citation plots"""
    logger.info("Capturing citation plots...")

    # Navigate to plots
    page.goto("http://127.0.0.1:8000/scholar/#plots", wait_until="domcontentloaded", timeout=60000)
    time.sleep(4)  # Wait for plots to render

    # Capture
    screenshot_path = output_dir / "scholar_plots.png"
    page.screenshot(path=str(screenshot_path), full_page=True)
    logger.info(f"✓ Saved: {screenshot_path}")


def capture_writer_page(page, output_dir: Path):
    """Capture Writer page"""
    logger.info("Capturing Writer page...")

    page.goto("http://127.0.0.1:8000/writer/", wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)

    screenshot_path = output_dir / "writer_main.png"
    page.screenshot(path=str(screenshot_path), full_page=True)
    logger.info(f"✓ Saved: {screenshot_path}")


def capture_dashboard(page, output_dir: Path):
    """Capture user dashboard"""
    logger.info("Capturing dashboard...")

    page.goto("http://127.0.0.1:8000/dashboard/", wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)

    screenshot_path = output_dir / "dashboard.png"
    page.screenshot(path=str(screenshot_path), full_page=True)
    logger.info(f"✓ Saved: {screenshot_path}")


def main():
    """Main entry point"""
    from datetime import datetime

    # Create output directory
    output_dir = project_root / "data" / "screenshots" / "demo" / datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("Demo Screenshot Capture")
    logger.info(f"Output: {output_dir}")
    logger.info("=" * 60)

    with sync_playwright() as playwright:
        # Start browser
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            # Login
            logger.info("Logging in...")
            page.goto("http://127.0.0.1:8000/auth/login/", wait_until="domcontentloaded", timeout=60000)
            time.sleep(2)

            page.fill('input[name="username"]', "ywatanabe")
            page.fill('input[name="password"]', "Yusuke8939.")
            page.click('button[type="submit"]')
            time.sleep(3)

            logger.info("Logged in successfully")

            # Capture demo screenshots
            capture_scholar_with_search(page, output_dir)
            capture_scholar_bibtex(page, output_dir)
            capture_scholar_plots(page, output_dir)
            capture_writer_page(page, output_dir)
            capture_dashboard(page, output_dir)

            logger.info("=" * 60)
            logger.info("Demo screenshots captured successfully!")
            logger.info(f"Output directory: {output_dir}")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
