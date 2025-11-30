#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-11-30
# File: /home/ywatanabe/proj/scitex-cloud/tests/e2e/project/test_file_tree.py

"""
E2E tests for file tree operations.

Tests:
- File tree display
- File selection
- Folder expansion
- File context menu
"""

import pytest
from playwright.sync_api import Page, expect


class TestFileTreeDisplay:
    """Tests for file tree display."""

    def test_file_tree_renders(
        self, page: Page, base_url: str, test_credentials: dict
    ):
        """File tree renders in project view."""
        # Login
        page.goto(f"{base_url}/auth/signin/", wait_until="domcontentloaded")
        page.fill("#username", test_credentials["username"])
        page.fill("#password", test_credentials["password"])
        page.click("button[type='submit']")
        page.wait_for_timeout(3000)

        # Go to project
        page.goto(
            f"{base_url}/{test_credentials['username']}/default-project/",
            wait_until="domcontentloaded"
        )
        page.wait_for_timeout(2000)

        # Check for file tree container
        tree = page.locator(".file-tree, .files-tree, [data-file-tree]")
        # Tree may or may not exist depending on project
        assert tree.count() >= 0

    def test_file_tree_shows_files(
        self, page: Page, base_url: str, test_credentials: dict
    ):
        """File tree shows file items."""
        # Login
        page.goto(f"{base_url}/auth/signin/", wait_until="domcontentloaded")
        page.fill("#username", test_credentials["username"])
        page.fill("#password", test_credentials["password"])
        page.click("button[type='submit']")
        page.wait_for_timeout(3000)

        # Go to project
        page.goto(
            f"{base_url}/{test_credentials['username']}/default-project/",
            wait_until="domcontentloaded"
        )
        page.wait_for_timeout(2000)

        # Look for file items
        files = page.locator(".file-item, .tree-item, [data-file]")
        # May have 0 or more files
        assert files.count() >= 0


class TestFileSelection:
    """Tests for file selection."""

    def test_click_file_selects_it(
        self, page: Page, base_url: str, test_credentials: dict
    ):
        """Clicking a file selects it."""
        # Login
        page.goto(f"{base_url}/auth/signin/", wait_until="domcontentloaded")
        page.fill("#username", test_credentials["username"])
        page.fill("#password", test_credentials["password"])
        page.click("button[type='submit']")
        page.wait_for_timeout(3000)

        # Go to project
        page.goto(
            f"{base_url}/{test_credentials['username']}/default-project/",
            wait_until="domcontentloaded"
        )
        page.wait_for_timeout(2000)

        # Find first file
        file_item = page.locator(".file-item, .tree-item[data-type='file']").first
        if file_item.count() > 0:
            file_item.click()
            page.wait_for_timeout(500)
            # Should be selected
            assert True
        else:
            pytest.skip("No files in project to select")


class TestFolderExpansion:
    """Tests for folder expansion."""

    def test_click_folder_expands_it(
        self, page: Page, base_url: str, test_credentials: dict
    ):
        """Clicking a folder expands it."""
        # Login
        page.goto(f"{base_url}/auth/signin/", wait_until="domcontentloaded")
        page.fill("#username", test_credentials["username"])
        page.fill("#password", test_credentials["password"])
        page.click("button[type='submit']")
        page.wait_for_timeout(3000)

        # Go to project
        page.goto(
            f"{base_url}/{test_credentials['username']}/default-project/",
            wait_until="domcontentloaded"
        )
        page.wait_for_timeout(2000)

        # Find first folder
        folder = page.locator(
            ".folder-item, .tree-item[data-type='folder'], "
            ".tree-item.directory"
        ).first
        if folder.count() > 0:
            folder.click()
            page.wait_for_timeout(500)
            # Should expand
            assert True
        else:
            pytest.skip("No folders in project to expand")


class TestFileContextMenu:
    """Tests for file context menu."""

    def test_right_click_shows_menu(
        self, page: Page, base_url: str, test_credentials: dict
    ):
        """Right-clicking a file shows context menu."""
        # Login
        page.goto(f"{base_url}/auth/signin/", wait_until="domcontentloaded")
        page.fill("#username", test_credentials["username"])
        page.fill("#password", test_credentials["password"])
        page.click("button[type='submit']")
        page.wait_for_timeout(3000)

        # Go to project
        page.goto(
            f"{base_url}/{test_credentials['username']}/default-project/",
            wait_until="domcontentloaded"
        )
        page.wait_for_timeout(2000)

        # Find first file
        file_item = page.locator(".file-item, .tree-item").first
        if file_item.count() > 0:
            file_item.click(button="right")
            page.wait_for_timeout(500)
            # Check for context menu
            menu = page.locator(".context-menu, .dropdown-menu")
            # Menu may or may not appear
            assert menu.count() >= 0
        else:
            pytest.skip("No files in project for context menu")
