#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-16 01:54:49 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/dev_app/views.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./apps/dev_app/views.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from django.shortcuts import render
from django.views import View


class DesignSystemView(View):
    """Display the SciTeX design system documentation."""

    template_name = "dev_app/pages/design.html"

    def get(self, request):
        """Render the design system page."""
        return render(request, self.template_name)

# EOF
