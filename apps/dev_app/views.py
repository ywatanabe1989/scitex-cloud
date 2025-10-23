#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-22 06:38:29 (ywatanabe)"
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
import json
from pathlib import Path
from django.conf import settings


def index(request):
    """Dev app index page - Developer Tools Hub."""
    return render(request, "dev_app/index.html")


class DesignSystemView(View):
    """Display the SciTeX design system documentation."""

    template_name = "dev_app/design.html"

    def get(self, request):
        """Render the design system page with programmatic component data."""
        # Load components.json
        components_path = (
            Path(settings.BASE_DIR)
            / "staticfiles"
            / "dev_app"
            / "data"
            / "components.json"
        )

        components_data = {"components": [], "metadata": {}}
        if components_path.exists():
            with open(components_path, "r") as f:
                components_data = json.load(f)

        # Organize components by category
        components_by_category = {}
        for component in components_data.get("components", []):
            category = component.get("category", "Other")
            if category not in components_by_category:
                components_by_category[category] = []
            components_by_category[category].append(component)

        context = {
            "components": components_data.get("components", []),
            "components_by_category": components_by_category,
            "metadata": components_data.get("metadata", {}),
            "total_components": len(components_data.get("components", [])),
        }

        return render(request, self.template_name, context)


class DesignColorsView(View):
    """Display the Colors section of the design system."""

    template_name = "dev_app/design_colors.html"

    def get(self, request):
        return render(request, self.template_name)


class DesignTypographyView(View):
    """Display the Typography section of the design system."""

    template_name = "dev_app/design_typography.html"

    def get(self, request):
        return render(request, self.template_name)


class DesignSpacingView(View):
    """Display the Spacing section of the design system."""

    template_name = "dev_app/design_spacing.html"

    def get(self, request):
        return render(request, self.template_name)


class DesignThemeView(View):
    """Display the Theme section of the design system."""

    template_name = "dev_app/design_theme.html"

    def get(self, request):
        return render(request, self.template_name)


class DesignComponentsView(View):
    """Display the Components section of the design system."""

    template_name = "dev_app/design_components.html"

    def get(self, request):
        """Render components page with component data."""
        # Load components.json
        components_path = (
            Path(settings.BASE_DIR)
            / "staticfiles"
            / "dev_app"
            / "data"
            / "components.json"
        )

        components_data = {"components": [], "metadata": {}}
        if components_path.exists():
            with open(components_path, "r") as f:
                components_data = json.load(f)

        # Organize components by category
        components_by_category = {}
        for component in components_data.get("components", []):
            category = component.get("category", "Other")
            if category not in components_by_category:
                components_by_category[category] = []
            components_by_category[category].append(component)

        context = {
            "components": components_data.get("components", []),
            "components_by_category": components_by_category,
            "metadata": components_data.get("metadata", {}),
            "total_components": len(components_data.get("components", [])),
        }

        return render(request, self.template_name, context)


class DesignGuidelinesView(View):
    """Display the Guidelines section of the design system."""

    template_name = "dev_app/design_guidelines.html"

    def get(self, request):
        return render(request, self.template_name)

# EOF
