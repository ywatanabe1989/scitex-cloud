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
            "code-blocks": {
                "title": "Code Blocks",
                "description": "Code syntax highlighting and code block styles.",
                "partial": "dev_app/design_partial/code.html",
            },
            "terminal-log": {
                "title": "Terminal Log",
                "description": "Terminal-style log display for process monitoring.",
                "partial": "dev_app/design_partial/terminal-log.html",
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
    """Route to individual component pages."""

    def get(self, request, component_id):
        """Route to the appropriate component template."""
        # Map component IDs to template names
        component_map = {
            "toggle-button-checkbox": "dev_app/components/toggle_button_checkbox.html",
            "form-input": "dev_app/components/form_input.html",
            "button": "dev_app/components/button.html",
            "file-upload": "dev_app/components/file_upload.html",
            "segmented-radio-control": "dev_app/components/segmented_radio_control.html",
            "badge": "dev_app/components/badge.html",
            "checkbox": "dev_app/components/checkbox.html",
            "select-dropdown": "dev_app/components/select_dropdown.html",
            "module-icons": "dev_app/components/module_icons.html",
            "card": "dev_app/components/card.html",
            "tabs": "dev_app/components/tabs.html",
            "dropdown-menu": "dev_app/components/dropdown_menu.html",
            "sidebar-navigation": "dev_app/components/sidebar_navigation.html",
            "breadcrumb": "dev_app/components/breadcrumb.html",
            "navbar": "dev_app/components/navbar.html",
            "hero": "dev_app/components/hero.html",
        }
        
        template_name = component_map.get(component_id.lower())
        if not template_name:
            raise Http404(f"Component '{component_id}' not found")
        
        components_data = _load_components()
        context = {
            "components": components_data.get("components", []),
            "metadata": components_data.get("metadata", {}),
        }
        
        return render(request, template_name, context)


# Backward compatibility views using DesignSectionView
class DesignColorsView(DesignSectionView):
    def get(self, request):
        return super().get(request, "colors")


class DesignTypographyView(DesignSectionView):
    def get(self, request):
        return super().get(request, "typography")


class DesignCodeBlocksView(DesignSectionView):
    def get(self, request):
        return super().get(request, "code-blocks")


class DesignSpacingView(DesignSectionView):
    def get(self, request):
        return super().get(request, "spacing")


class DesignThemeView(DesignSectionView):
    def get(self, request):
        return super().get(request, "theme")


class DesignGuidelinesView(DesignSectionView):
    def get(self, request):
        return super().get(request, "guidelines")


class DesignTerminalLogView(DesignSectionView):
    def get(self, request):
        return super().get(request, "terminal-log")

# EOF
