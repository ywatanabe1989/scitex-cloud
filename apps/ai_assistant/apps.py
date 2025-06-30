#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Research Assistant App Configuration
Provides AI-powered research assistance for scientific research projects
"""

from django.apps import AppConfig


class AiAssistantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_assistant'
    verbose_name = 'AI Research Assistant'
    
    def ready(self):
        """Initialize the app when Django starts."""
        pass