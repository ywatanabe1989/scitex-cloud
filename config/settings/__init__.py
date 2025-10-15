"""
Django settings auto-loader for SciTeX Cloud.

This module automatically loads the appropriate settings based on:
1. DJANGO_SETTINGS_MODULE environment variable
2. SCITEX_ENV environment variable
3. Default to development if not specified

Usage:
    Development: export SCITEX_ENV=development (or leave unset)
    Production:  export SCITEX_ENV=production
"""

import os
import sys

# Determine which settings to use
env = os.environ.get('SCITEX_ENV', 'development').lower()

if env == 'production':
    from .production import *
elif env == 'development':
    from .development import *
else:
    # Fallback to development
    print(f"Warning: Unknown SCITEX_ENV '{env}', defaulting to development")
    from .development import *

# Display which settings are loaded (only in development)
if DEBUG:
    print(f" SciTeX Cloud settings loaded: {env.upper()}")
