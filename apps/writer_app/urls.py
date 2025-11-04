#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/writer_app/urls.py
# ----------------------------------------
"""
Writer App URLs - Feature-based organization.

This file serves as the main entry point for writer_app URLs,
delegating to feature-based URL modules following FULLSTACK.md guidelines.

The URL structure is organized by feature domains:
- Dashboard: Main entry points and workspace management
- Editor: Document editing and section management
- Compilation: LaTeX compilation and PDF generation
- Version Control: Git-based version management
- arXiv: arXiv submission and integration
- Collaboration: Real-time collaborative editing

All routes are defined in their respective feature modules under urls/
"""

from django.urls import path, include

app_name = 'writer_app'

urlpatterns = [
    # Dashboard (root /writer/)
    path('', include('apps.writer_app.urls.dashboard')),

    # Feature modules
    path('editor/', include('apps.writer_app.urls.editor')),
    path('compilation/', include('apps.writer_app.urls.compilation')),
    path('version-control/', include('apps.writer_app.urls.version_control')),
    path('arxiv/', include('apps.writer_app.urls.arxiv')),
    path('collaboration/', include('apps.writer_app.urls.collaboration')),
]

# EOF
