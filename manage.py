#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-22 08:15:48 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/manage.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./manage.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Django's command-line utility for administrative tasks."""

import sys

def main():
    """Run administrative tasks."""
    # Add base and config directories to Python path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, BASE_DIR)  # Add base directory
    sys.path.insert(0, os.path.join(BASE_DIR, "config"))  # Add config directory
    # No need to add src directory anymore as it's been replaced by apps

    # Use new auto-detection settings module
    # Set SCITEX_CLOUD_ENV=production for production, defaults to development
    settings_module = os.environ.get(
        "SCITEX_CLOUD_DJANGO_SETTINGS_MODULE", "config.settings"
    )
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

# EOF
