#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub App Configuration

Django app configuration for GitHub repository integration with SciTeX Code module.
"""

from django.apps import AppConfig


class GithubAppConfig(AppConfig):
    """GitHub App configuration"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.github_app'
    verbose_name = 'GitHub Integration'
    
    def ready(self):
        """Initialize app when Django starts"""
        try:
            # Import signals
            import apps.github_app.signals
        except ImportError:
            pass