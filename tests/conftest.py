#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest configuration and fixtures for E2E testing.
"""

import pytest
import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Create necessary directories for Django logging
logs_dir = project_root / "logs"
logs_dir.mkdir(exist_ok=True)

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.settings_dev")

# Override Django logging to use simple configuration for tests
os.environ["DJANGO_LOG_LEVEL"] = "ERROR"

# Setup Django with simplified logging
import django
from django.conf import settings

# Override logging configuration before Django setup
if hasattr(settings, 'LOGGING'):
    settings.LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    }

django.setup()


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the application."""
    return os.getenv("BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for all tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
        "locale": "en-US",
        "timezone_id": "America/New_York",
    }


@pytest.fixture(scope="function")
def context(browser):
    """Create new browser context for each test (isolation)."""
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context):
    """Create new page for each test."""
    page = context.new_page()

    # Enable console logging capture
    page.on("console", lambda msg: print(f"[BROWSER {msg.type}] {msg.text}"))

    # Enable error capture
    page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))

    yield page
    page.close()


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_users():
    """Cleanup test users after all tests complete."""
    yield

    # Skip cleanup if running tests from host (database not accessible)
    # When running in Docker, cleanup will work properly
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        deleted_count, _ = User.objects.filter(
            username__startswith="test_user_"
        ).delete()

        if deleted_count > 0:
            print(f"\n✓ Cleaned up {deleted_count} test user(s)")
    except Exception as e:
        print(f"\n⚠ Skipping cleanup (database not accessible from host): {e}")


@pytest.fixture
def test_user_data(timestamp):
    """Generate test user data."""
    return {
        "username": f"test_user_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def timestamp():
    """Generate unique timestamp for test data."""
    import time
    return int(time.time())
