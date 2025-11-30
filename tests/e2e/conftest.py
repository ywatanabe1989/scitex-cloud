#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-11-30
# File: /home/ywatanabe/proj/scitex-cloud/tests/e2e/conftest.py

"""
E2E test fixtures using Playwright.

Provides:
- Browser context configuration
- Page fixtures with console logging
- Authenticated page fixture
- Login helper
"""

import pytest
from pathlib import Path
from playwright.sync_api import Page, BrowserContext, expect


# Session directory for persistent browser state
SESSION_DIR = Path.home() / ".scitex" / "browser" / "test_session"
SESSION_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Browser Configuration
# =============================================================================


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for all E2E tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
        "locale": "en-US",
        "timezone_id": "UTC",
    }


# =============================================================================
# Page Fixtures
# =============================================================================


@pytest.fixture
def page(context: BrowserContext) -> Page:
    """Create new page with console/error logging."""
    page = context.new_page()

    # Capture console messages
    page.on("console", lambda msg: print(f"[CONSOLE:{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))

    yield page
    page.close()


@pytest.fixture
def logged_in_page(page: Page, base_url: str, test_credentials: dict) -> Page:
    """Page with test-user already logged in."""
    login_user(page, base_url, test_credentials)
    return page


# =============================================================================
# Helper Functions
# =============================================================================


def login_user(page: Page, base_url: str, credentials: dict) -> bool:
    """
    Log in a user via the signin page.

    Args:
        page: Playwright page
        base_url: Application base URL
        credentials: Dict with 'username' and 'password'

    Returns:
        True if login successful
    """
    page.goto(f"{base_url}/auth/signin/")
    page.wait_for_load_state("networkidle")

    # Check if already logged in
    if page.locator("body").get_attribute("data-user-authenticated") == "true":
        return True

    # Fill login form
    page.fill("#username", credentials["username"])
    page.fill("#password", credentials["password"])
    page.click("button[type='submit']")

    # Wait for navigation
    page.wait_for_url(lambda url: "/auth/signin" not in url, timeout=10000)

    # Verify logged in
    expect(page.locator("body")).to_have_attribute(
        "data-user-authenticated", "true", timeout=5000
    )
    return True


def logout_user(page: Page, base_url: str) -> bool:
    """
    Log out the current user.

    Args:
        page: Playwright page
        base_url: Application base URL

    Returns:
        True if logout successful
    """
    page.goto(f"{base_url}/auth/signout/")
    page.wait_for_load_state("networkidle")

    # Verify logged out
    expect(page.locator("body")).to_have_attribute(
        "data-user-authenticated", "false", timeout=5000
    )
    return True


# =============================================================================
# Assertion Helpers
# =============================================================================


def assert_toast_message(page: Page, message: str, timeout: int = 5000):
    """Assert a toast notification contains the expected message."""
    toast = page.locator(".toast, .alert, [role='alert']").filter(has_text=message)
    expect(toast).to_be_visible(timeout=timeout)


def assert_form_error(page: Page, field_name: str, error_text: str):
    """Assert a form field has a specific error message."""
    error = page.locator(f"#{field_name} ~ .invalid-feedback, .error-{field_name}")
    expect(error).to_contain_text(error_text)


def assert_page_title(page: Page, title: str):
    """Assert page title contains expected text."""
    expect(page).to_have_title(title)


def assert_url_contains(page: Page, path: str):
    """Assert current URL contains the expected path."""
    expect(page).to_have_url(lambda url: path in url)
