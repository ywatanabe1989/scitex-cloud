#!/usr/bin/env python3
"""
Run Daphne with Django's autoreload mechanism.

This enables django-browser-reload to work properly by using Django's
autoreload system to detect file changes and send events to the browser.
"""
import os
import sys
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.getenv("SCITEX_CLOUD_DJANGO_SETTINGS_MODULE", "config.settings.settings_dev")
)

# Import Django's autoreload after setting up the environment
import django
django.setup()

from django.utils import autoreload


def run_daphne():
    """Run Daphne ASGI server using exec to replace the process."""
    print("🔥 Starting Daphne with Django autoreload...")
    print("   Watching: Python files (.py) and templates (.html)")
    print("   Browser will auto-refresh on file changes")

    # Use os.execvp to replace the current process with Daphne
    # This ensures proper cleanup when autoreload kills the process
    import os
    os.execvp("daphne", [
        "daphne",
        "-b", "0.0.0.0",
        "-p", "8000",
        "config.asgi:application",
    ])


if __name__ == "__main__":
    # Run Daphne with Django's autoreload wrapper
    # This allows django-browser-reload to detect changes and send events
    autoreload.run_with_reloader(run_daphne)
