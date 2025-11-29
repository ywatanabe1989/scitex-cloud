"""
Individual Tool Detail Page Views

Each function renders a specific tool's detail page.
"""

from __future__ import annotations

from django.shortcuts import render


def tool_element_inspector(request):
    """Element Inspector tool detail page."""
    return render(request, "public_app/tools/element-inspector.html")


def tool_asta_citation_scraper(request):
    """Asta AI Citation Scraper tool detail page."""
    return render(request, "public_app/tools/asta-citation-scraper.html")


def tool_image_concatenator(request):
    """Image Concatenator tool detail page."""
    return render(request, "public_app/tools/image-concatenator.html")


def tool_qr_code_generator(request):
    """QR Code Generator tool detail page."""
    return render(request, "public_app/tools/qr-code-generator.html")


def tool_color_picker(request):
    """Color Picker tool detail page."""
    return render(request, "public_app/tools/color-picker.html")


def tool_markdown_renderer(request):
    """Markdown Renderer tool detail page."""
    return render(request, "public_app/tools/markdown-renderer.html")


def tool_text_diff_checker(request):
    """Text Diff Checker tool detail page."""
    return render(request, "public_app/tools/text-diff-checker.html")


def tool_images_to_gif(request):
    """Images to GIF tool detail page."""
    return render(request, "public_app/tools/images-to-gif.html")


def tool_image_converter(request):
    """Image Converter tool detail page."""
    return render(request, "public_app/tools/image-converter.html")


def tool_pdf_merger(request):
    """PDF Merger tool detail page."""
    return render(request, "public_app/tools/pdf-merger.html")


def tool_statistics_calculator(request):
    """Statistics Calculator tool detail page."""
    return render(request, "public_app/tools/statistics-calculator.html")


def tool_pdf_splitter(request):
    """PDF Splitter tool detail page."""
    return render(request, "public_app/tools/pdf-splitter.html")


def tool_image_resizer(request):
    """Image Resizer tool detail page."""
    return render(request, "public_app/tools/image-resizer.html")


def tool_repo_concatenator(request):
    """Repository Concatenator tool detail page."""
    return render(request, "public_app/tools/repo-concatenator.html")


def tool_json_formatter(request):
    """JSON Formatter tool detail page."""
    return render(request, "public_app/tools/json-formatter.html")


def tool_images_to_pdf(request):
    """Images to PDF tool detail page."""
    return render(request, "public_app/tools/images-to-pdf.html")


def tool_pdf_to_images(request):
    """PDF to Images tool detail page."""
    return render(request, "public_app/tools/pdf-to-images.html")


def tool_pdf_compressor(request):
    """PDF Compressor tool detail page."""
    return render(request, "public_app/tools/pdf-compressor.html")


def tool_video_editor(request):
    """Video Editor tool detail page."""
    return render(request, "public_app/tools/video-editor.html")


def tool_plot_viewer(request):
    """
    Quick CSV Plot Viewer - renders simple CSV plots using Canvas.

    Accepts CSV files with column naming convention:
    ax_{axis_index}_{plot_id}_{plot_type}_{variable}

    Example: ax_00_plot_line_0_line_x, ax_00_plot_line_0_line_y

    Supports: line, scatter, bar plots only.
    For advanced plot types, use the backend plot API.
    """
    return render(request, "public_app/tools/plot-viewer.html")


def tool_plot_backend_test(request):
    """
    Backend Plot Renderer Test - test matplotlib/scitex.plt backend.

    Internal testing tool for the backend plot API.
    """
    return render(request, "public_app/tools/plot-backend-test.html")


def tool_image_viewer(request):
    """
    Image Viewer - Display image with dimension, DPI, and unit conversion info.

    Shows pixel dimensions, DPI, physical size (mm/inch), and conversions
    to help understand figure dimensions for publications.
    """
    return render(request, "public_app/tools/image-viewer.html")


def tool_mermaid_renderer(request):
    """
    Mermaid Diagram Renderer - Create diagrams from text syntax.

    Supports flowcharts, sequence diagrams, Gantt charts, class diagrams,
    pie charts, and git graphs using Mermaid.js syntax.
    """
    return render(request, "public_app/tools/mermaid-renderer.html")
