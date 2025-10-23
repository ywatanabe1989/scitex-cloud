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


def _load_components():
    """Helper method to load components from JSON file."""
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
    
    return components_data


def _get_base_design_context():
    """Helper method to get base context with components for all design pages."""
    components_data = _load_components()
    
    return {
        "components": components_data.get("components", []),
        "metadata": components_data.get("metadata", {}),
    }


class DesignSystemView(View):
    """Display the SciTeX design system documentation."""

    template_name = "dev_app/design.html"

    def get(self, request):
        """Render the design system page with programmatic component data."""
        components_data = _load_components()

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

    template_name = "dev_app/design_section.html"

    def get(self, request):
        context = _get_base_design_context()
        context.update({
            "section_title": "Colors",
            "section_description": "Color palette and semantic color system for the SciTeX design system.",
            "section_template": "dev_app/design_partial/colors.html",
        })
        return render(request, self.template_name, context)


class DesignTypographyView(View):
    """Display the Typography section of the design system."""

    template_name = "dev_app/design_section.html"

    def get(self, request):
        context = _get_base_design_context()
        context.update({
            "section_title": "Typography",
            "section_description": "Typography system and font guidelines for the SciTeX design system.",
            "section_template": "dev_app/design_partial/typography.html",
        })
        return render(request, self.template_name, context)


class DesignSpacingView(View):
    """Display the Spacing section of the design system."""

    template_name = "dev_app/design_section.html"

    def get(self, request):
        context = _get_base_design_context()
        context.update({
            "section_title": "Spacing",
            "section_description": "Spacing system and layout guidelines for the SciTeX design system.",
            "section_template": "dev_app/design_partial/spacing.html",
        })
        return render(request, self.template_name, context)


class DesignThemeView(View):
    """Display the Theme section of the design system."""

    template_name = "dev_app/design_section.html"

    def get(self, request):
        context = _get_base_design_context()
        context.update({
            "section_title": "Theme",
            "section_description": "Theme system and color mode support for the SciTeX design system.",
            "section_template": "dev_app/design_partial/theme.html",
        })
        return render(request, self.template_name, context)


class DesignComponentsView(View):
    """Display the Components section of the design system."""

    template_name = "dev_app/design_components.html"

    def get(self, request):
        """Render components page with component data."""
        components_data = _load_components()

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


class DesignComponentDetailView(View):
    """Display an individual component page."""

    template_name = "dev_app/design_component_detail.html"

    def get(self, request, component_id):
        """Render individual component page."""
        components_data = _load_components()

        # Find the specific component by ID or slugified name
        component = None
        for c in components_data.get("components", []):
            # Compare by ID directly
            if c.get("id") == component_id:
                component = c
                break
            # Compare by slugified name
            component_name_slug = c.get("name", "").lower().replace(" ", "-").replace("(", "").replace(")", "")
            if component_name_slug == component_id.lower():
                component = c
                break
            # Compare by slugified ID
            component_id_slug = c.get("id", "").lower().replace(" ", "-").replace("(", "").replace(")", "")
            if component_id_slug == component_id.lower():
                component = c
                break

        if not component:
            from django.http import Http404
            raise Http404(f"Component '{component_id}' not found")

        # Get all components for sidebar
        components = components_data.get("components", [])

        context = {
            "component": component,
            "components": components,
            "metadata": components_data.get("metadata", {}),
        }

        return render(request, self.template_name, context)


class DesignGuidelinesView(View):
    """Display the Guidelines section of the design system."""

    template_name = "dev_app/design_section.html"

    def get(self, request):
        context = _get_base_design_context()
        context.update({
            "section_title": "Usage Guidelines",
            "section_description": "Best practices and usage guidelines for the SciTeX design system.",
            "section_template": "dev_app/design_partial/guidelines.html",
        })
        return render(request, self.template_name, context)

# EOF
