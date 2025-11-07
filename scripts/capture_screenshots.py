#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Screenshot Automation Script for SciTeX Cloud

Captures screenshots of all main pages for:
- Understanding the big picture
- Creating demo materials for promotion
- Documentation purposes

Usage:
    python scripts/capture_screenshots.py
    python scripts/capture_screenshots.py --url http://localhost:8000
    python scripts/capture_screenshots.py --output ./screenshots/demo
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Django setup
os.environ.setdefault("SCITEX_CLOUD_DJANGO_SETTINGS_MODULE", "config.settings.settings_dev")
import django
django.setup()

from playwright.sync_api import sync_playwright, Page, Browser
from scitex import logging

logger = logging.getLogger(__name__)

# Screenshot configuration
SCREENSHOT_CONFIG = {
    "base_url": "http://127.0.0.1:8000",
    "output_dir": project_root / "data" / "screenshots" / datetime.now().strftime("%Y%m%d_%H%M%S"),
    "viewport": {"width": 1920, "height": 1080},
    "test_user": {
        "username": "ywatanabe",
        "password": "Yusuke8939.",
    },
}

# Pages to capture
PAGES_TO_CAPTURE = {
    # Public pages
    "public": [
        {"name": "home", "url": "/", "description": "Landing page"},
        {"name": "pricing", "url": "/pricing/", "description": "Pricing page"},
        {"name": "features", "url": "/features/", "description": "Features overview"},
    ],

    # Authentication pages
    "auth": [
        {"name": "login", "url": "/auth/login/", "description": "Login page"},
        {"name": "signup", "url": "/auth/signup/", "description": "Signup page"},
    ],

    # Scholar app
    "scholar": [
        {"name": "scholar_index", "url": "/scholar/", "description": "Scholar main page"},
        {"name": "scholar_search", "url": "/scholar/#search", "description": "Scholar search interface"},
        {"name": "scholar_bibtex", "url": "/scholar/#bibtex", "description": "BibTeX manager"},
        {"name": "scholar_plots", "url": "/scholar/#plots", "description": "Citation plots"},
    ],

    # Writer app
    "writer": [
        {"name": "writer_index", "url": "/writer/", "description": "Writer main page"},
    ],

    # Project app
    "project": [
        {"name": "project_list", "url": "/projects/", "description": "Projects list"},
    ],

    # Profile and dashboard
    "profile": [
        {"name": "dashboard", "url": "/dashboard/", "description": "User dashboard"},
    ],
}


class ScreenshotCapture:
    """Automated screenshot capture for SciTeX Cloud"""

    def __init__(self, base_url: str = None, output_dir: Path = None):
        self.base_url = base_url or SCREENSHOT_CONFIG["base_url"]
        self.output_dir = output_dir or SCREENSHOT_CONFIG["output_dir"]
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.browser = None
        self.page = None
        self.context = None

        logger.info(f"Screenshot output directory: {self.output_dir}")

    def start_browser(self, playwright):
        """Start browser and create context"""
        logger.info("Starting browser...")
        self.browser = playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context(
            viewport=SCREENSHOT_CONFIG["viewport"]
        )
        self.page = self.context.new_page()
        logger.info("Browser started successfully")

    def login(self):
        """Login to the application"""
        logger.info("Logging in...")

        username = SCREENSHOT_CONFIG["test_user"]["username"]
        password = SCREENSHOT_CONFIG["test_user"]["password"]

        try:
            # Navigate to login page
            self.page.goto(f"{self.base_url}/auth/login/", wait_until="domcontentloaded", timeout=60000)
            time.sleep(2)

            # Fill login form
            self.page.fill('input[name="username"]', username)
            self.page.fill('input[name="password"]', password)

            # Submit form
            self.page.click('button[type="submit"]')

            # Wait for redirect after login
            time.sleep(3)

            logger.info(f"Logged in as {username}")
            return True

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    def capture_page(self, category: str, page_info: dict, wait_time: int = 2):
        """Capture screenshot of a single page"""
        name = page_info["name"]
        url = page_info["url"]
        description = page_info.get("description", "")

        logger.info(f"Capturing {category}/{name}: {description}")

        try:
            # Navigate to page with longer timeout and less strict wait condition
            full_url = f"{self.base_url}{url}"
            self.page.goto(full_url, wait_until="domcontentloaded", timeout=60000)

            # Wait for page to settle
            time.sleep(wait_time)

            # Try to wait for network idle, but don't fail if it times out
            try:
                self.page.wait_for_load_state("networkidle", timeout=5000)
            except:
                pass  # Continue even if network idle times out

            # Take screenshot
            category_dir = self.output_dir / category
            category_dir.mkdir(exist_ok=True)

            screenshot_path = category_dir / f"{name}.png"
            self.page.screenshot(path=str(screenshot_path), full_page=True)

            logger.info(f"✓ Saved: {screenshot_path}")

            # Also save viewport screenshot (for thumbnails)
            thumbnail_path = category_dir / f"{name}_thumb.png"
            self.page.screenshot(path=str(thumbnail_path), full_page=False)

            return True

        except Exception as e:
            logger.error(f"✗ Failed to capture {category}/{name}: {e}")
            return False

    def capture_all_pages(self, categories: list = None):
        """Capture screenshots of all configured pages"""
        logger.info("=" * 60)
        logger.info("Starting screenshot capture session")
        logger.info("=" * 60)

        # Filter categories if specified
        if categories:
            pages = {k: v for k, v in PAGES_TO_CAPTURE.items() if k in categories}
        else:
            pages = PAGES_TO_CAPTURE

        total_pages = sum(len(pages_list) for pages_list in pages.values())
        captured = 0
        failed = 0

        # Capture public pages (no login required)
        if "public" in pages or "auth" in pages:
            for category in ["public", "auth"]:
                if category not in pages:
                    continue

                for page_info in pages[category]:
                    if self.capture_page(category, page_info):
                        captured += 1
                    else:
                        failed += 1

        # Login for authenticated pages
        needs_auth = any(cat in pages for cat in ["scholar", "writer", "project", "profile"])
        if needs_auth:
            if not self.login():
                logger.error("Failed to login, skipping authenticated pages")
                return captured, failed

            # Wait a bit after login
            time.sleep(2)

        # Capture authenticated pages
        for category, pages_list in pages.items():
            if category in ["public", "auth"]:
                continue  # Already captured

            for page_info in pages_list:
                if self.capture_page(category, page_info):
                    captured += 1
                else:
                    failed += 1

        logger.info("=" * 60)
        logger.info(f"Screenshot capture complete!")
        logger.info(f"Total: {total_pages} | Captured: {captured} | Failed: {failed}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("=" * 60)

        return captured, failed

    def create_index_html(self):
        """Create an HTML index file to view all screenshots"""
        logger.info("Creating index.html...")

        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SciTeX Cloud - Screenshots</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 2rem;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 {
            color: #2c3e50;
            margin-bottom: 0.5rem;
            font-size: 2.5rem;
        }
        .subtitle {
            color: #7f8c8d;
            margin-bottom: 2rem;
            font-size: 1.1rem;
        }
        .category {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .category-title {
            color: #34495e;
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #3498db;
            text-transform: capitalize;
        }
        .screenshots-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
        }
        .screenshot-card {
            background: #fafafa;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .screenshot-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .screenshot-card img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-bottom: 1px solid #e0e0e0;
        }
        .screenshot-info {
            padding: 1rem;
        }
        .screenshot-name {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }
        .screenshot-description {
            color: #7f8c8d;
            font-size: 0.9rem;
        }
        .screenshot-link {
            display: inline-block;
            margin-top: 0.5rem;
            color: #3498db;
            text-decoration: none;
            font-size: 0.85rem;
        }
        .screenshot-link:hover {
            text-decoration: underline;
        }
        .stats {
            background: #ecf0f1;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            display: flex;
            gap: 2rem;
        }
        .stat-item {
            color: #34495e;
        }
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #3498db;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SciTeX Cloud - Screenshots</h1>
        <p class="subtitle">Generated on {timestamp}</p>

        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">{total_categories}</div>
                <div>Categories</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{total_screenshots}</div>
                <div>Screenshots</div>
            </div>
        </div>

        {categories_html}
    </div>
</body>
</html>
"""

        categories_html = ""
        total_screenshots = 0

        # Generate HTML for each category
        for category in sorted(self.output_dir.iterdir()):
            if not category.is_dir():
                continue

            category_name = category.name
            screenshots = []

            # Find all non-thumbnail screenshots
            for screenshot in sorted(category.glob("*.png")):
                if "_thumb" in screenshot.name:
                    continue

                # Find corresponding page info
                page_name = screenshot.stem
                page_info = None
                for pages_list in PAGES_TO_CAPTURE.values():
                    for p in pages_list:
                        if p["name"] == page_name:
                            page_info = p
                            break

                description = page_info["description"] if page_info else ""
                thumb_path = category / f"{page_name}_thumb.png"

                screenshots.append({
                    "name": page_name,
                    "path": str(screenshot.relative_to(self.output_dir)),
                    "thumb": str(thumb_path.relative_to(self.output_dir)) if thumb_path.exists() else str(screenshot.relative_to(self.output_dir)),
                    "description": description,
                })
                total_screenshots += 1

            if not screenshots:
                continue

            # Create category section
            category_html = f"""
        <div class="category">
            <h2 class="category-title">{category_name}</h2>
            <div class="screenshots-grid">
"""

            for screenshot in screenshots:
                category_html += f"""
                <div class="screenshot-card">
                    <img src="{screenshot['thumb']}" alt="{screenshot['name']}">
                    <div class="screenshot-info">
                        <div class="screenshot-name">{screenshot['name'].replace('_', ' ').title()}</div>
                        <div class="screenshot-description">{screenshot['description']}</div>
                        <a href="{screenshot['path']}" class="screenshot-link" target="_blank">View full size →</a>
                    </div>
                </div>
"""

            category_html += """
            </div>
        </div>
"""
            categories_html += category_html

        # Fill in the template
        html_content = html_content.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_categories=len([d for d in self.output_dir.iterdir() if d.is_dir()]),
            total_screenshots=total_screenshots,
            categories_html=categories_html,
        )

        # Write index.html
        index_path = self.output_dir / "index.html"
        index_path.write_text(html_content)

        logger.info(f"✓ Created index.html: {index_path}")
        return index_path

    def cleanup(self):
        """Close browser and cleanup"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        logger.info("Browser closed")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Capture screenshots of SciTeX Cloud pages")
    parser.add_argument("--url", default=SCREENSHOT_CONFIG["base_url"],
                        help="Base URL of the application")
    parser.add_argument("--output", type=Path, default=SCREENSHOT_CONFIG["output_dir"],
                        help="Output directory for screenshots")
    parser.add_argument("--categories", nargs="+", choices=list(PAGES_TO_CAPTURE.keys()),
                        help="Specific categories to capture (default: all)")

    args = parser.parse_args()

    # Create screenshot capture instance
    capture = ScreenshotCapture(base_url=args.url, output_dir=args.output)

    try:
        with sync_playwright() as playwright:
            # Start browser
            capture.start_browser(playwright)

            # Capture all pages
            captured, failed = capture.capture_all_pages(categories=args.categories)

            # Create index HTML
            if captured > 0:
                index_path = capture.create_index_html()
                logger.info(f"\nView screenshots: file://{index_path}")

    except Exception as e:
        logger.error(f"Screenshot capture failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        capture.cleanup()

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
