#!/bin/bash
# Wrapper to start Daphne with Django's autoreload
# This enables django-browser-reload to work properly

# Use Django's autoreload mechanism (same as runserver)
# This allows django-browser-reload to detect changes and auto-refresh the browser
exec python /app/deployment/docker/docker_dev/run_daphne_with_autoreload.py
