#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import json
from pathlib import Path
from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.http import Http404


def index(request):
    """Dev app index page."""
    return render(request, "dev_app/index.html")


def _load_components():
    """Load components from JSON."""
    components_path = (
        Path(settings.BASE_DIR)
        / "staticfiles" / "dev_app" / "data" / "components.json"
    )
    components_data = {"components": [], "metadata": {}}
    if components_path.exists():
        with open(components_path, "r") as f:
            components_data = json.load(f)
    return components_data


class DesignSystemView(View):
    """Main design system page - shows colors."""
    template_name = "dev_app/design.html"

    def get(self, request):
        components_data = _load_components()
        context = {
            "components": components_data.get("components", []),
            "metadata": components_data.get("metadata", {}),
        }
        return render(request, self.template_name, context)


class DesignSectionView(View):
    """Generic design section page."""
    template_name = "dev_app/design_section.html"

    def get(self, request, section):
        components_data = _load_components()
        sections = {
            "colors": {
                "title": "Colors",
                "description": "Color palette and semantic color system.",
                "partial": "dev_app/design_partial/colors.html",
            },
            "typography": {
                "title": "Typography",
                "description": "Typography system and font guidelines.",
                "partial": "dev_app/design_partial/typography.html",
            },
            "spacing": {
                "title": "Spacing",
                "description": "Spacing system and layout guidelines.",
                "partial": "dev_app/design_partial/spacing.html",
            },
            "theme": {
                "title": "Theme",
                "description": "Theme system and color mode support.",
                "partial": "dev_app/design_partial/theme.html",
            },
            "guidelines": {
                "title": "Usage Guidelines",
                "description": "Best practices and usage guidelines.",
                "partial": "dev_app/design_partial/guidelines.html",
            },
        }
        
        if section not in sections:
            raise Http404(f"Section '{section}' not found")
        
        section_info = sections[section]
        context = {
            "components": components_data.get("components", []),
            "metadata": components_data.get("metadata", {}),
            "section_title": section_info["title"],
            "section_description": section_info["description"],
            "section_template": section_info["partial"],
        }
        return render(request, self.template_name, context)


class DesignComponentsView(View):
    """Components listing page."""
    template_name = "dev_app/design_components.html"

    def get(self, request):
        components_data = _load_components()
        context = {
            "components": components_data.get("components", []),
            "metadata": components_data.get("metadata", {}),
            "total_components": len(components_data.get("components", [])),
        }
        return render(request, self.template_name, context)


class DesignComponentDetailView(View):
    """Individual component page."""
    template_name = "dev_app/design_component_detail.html"

    def get(self, request, component_id):
        components_data = _load_components()
        
        # Find component by ID or slugified name
        component = None
        for c in components_data.get("components", []):
            comp_id = c.get("id", "").lower().replace(" ", "-").replace("(", "").replace(")", "")
            if comp_id == component_id.lower():
                component = c
                break
        
        if not component:
            raise Http404(f"Component '{component_id}' not found")
        
        context = {
            "component": component,
            "components": components_data.get("components", []),
            "metadata": components_data.get("metadata", {}),
        }
        return render(request, self.template_name, context)


# Backward compatibility views using DesignSectionView
class DesignColorsView(DesignSectionView):
    def get(self, request):
        return super().get(request, "colors")


class DesignTypographyView(DesignSectionView):
    def get(self, request):
        return super().get(request, "typography")


class DesignSpacingView(DesignSectionView):
    def get(self, request):
        return super().get(request, "spacing")


class DesignThemeView(DesignSectionView):
    def get(self, request):
        return super().get(request, "theme")


class DesignGuidelinesView(DesignSectionView):
    def get(self, request):
        return super().get(request, "guidelines")

# EOF
