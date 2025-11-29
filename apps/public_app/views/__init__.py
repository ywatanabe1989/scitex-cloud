"""
Public App Views Package

Exports all view functions for URL routing.

Refactored tools.py into:
- tools_main.py: Main tools index page
- tool_views.py: Individual tool detail pages
"""

from __future__ import annotations

# Landing and marketing pages
from .landing import index, premium_subscription

# Information pages
from .pages import about, publications, donate, fundraising, contributors

# Legal pages
from .legal import contact, privacy_policy, terms_of_use, cookie_policy

# Status pages
from .status import (
    server_status,
    server_status_api,
    server_metrics_history_api,
    server_metrics_export_csv,
    visitor_status,
    visitor_restart_session,
    visitor_expired,
)

# API and developer pages
from .api import api_docs, scitex_api_keys, releases_view

# Research tools - main page
from .tools_main import tools

# Research tools - individual tool pages
from .tool_views import (
    tool_element_inspector,
    tool_asta_citation_scraper,
    tool_image_concatenator,
    tool_qr_code_generator,
    tool_color_picker,
    tool_markdown_renderer,
    tool_text_diff_checker,
    tool_images_to_gif,
    tool_image_converter,
    tool_pdf_merger,
    tool_statistics_calculator,
    tool_pdf_splitter,
    tool_image_resizer,
    tool_repo_concatenator,
    tool_json_formatter,
    tool_images_to_pdf,
    tool_pdf_to_images,
    tool_pdf_compressor,
    tool_video_editor,
    tool_plot_viewer,
    tool_plot_backend_test,
    tool_image_viewer,
    tool_mermaid_renderer,
)

# Utility views
from .utils import donation_success, send_donation_confirmation, demo

__all__ = [
    # Landing
    "index",
    "premium_subscription",
    # Pages
    "about",
    "publications",
    "donate",
    "fundraising",
    "contributors",
    # Legal
    "contact",
    "privacy_policy",
    "terms_of_use",
    "cookie_policy",
    # Status
    "server_status",
    "server_status_api",
    "server_metrics_history_api",
    "server_metrics_export_csv",
    "visitor_status",
    "visitor_restart_session",
    "visitor_expired",
    # API
    "api_docs",
    "scitex_api_keys",
    "releases_view",
    # Tools
    "tools",
    "tool_element_inspector",
    "tool_asta_citation_scraper",
    "tool_image_concatenator",
    "tool_qr_code_generator",
    "tool_color_picker",
    "tool_markdown_renderer",
    "tool_text_diff_checker",
    "tool_images_to_gif",
    "tool_image_converter",
    "tool_pdf_merger",
    "tool_statistics_calculator",
    "tool_pdf_splitter",
    "tool_image_resizer",
    "tool_repo_concatenator",
    "tool_json_formatter",
    "tool_images_to_pdf",
    "tool_pdf_to_images",
    "tool_pdf_compressor",
    "tool_video_editor",
    "tool_plot_viewer",
    "tool_plot_backend_test",
    "tool_image_viewer",
    "tool_mermaid_renderer",
    # Utils
    "demo",
    "donation_success",
    "send_donation_confirmation",
]
