"""
Research Tools Main Page

Contains the tools index page with all tool categories.
"""

from __future__ import annotations

from django.shortcuts import render


def tools(request):
    """Research tools page - bookmarklets and utilities for researchers."""
    # Organized by tool type: Text → Image → PDF → Video → Rendering → Developer → Research
    domains = [
        {
            "name": "Text",
            "slug": "text",
            "icon": "📝",
            "description": "Format, compare, and process text content",
            "tools": [
                {
                    "name": "Markdown Renderer",
                    "description": "Real-time Markdown preview with syntax highlighting and table support.",
                    "use_case": "Format README files and documentation for data repositories",
                    "bookmarklet_url": "/tools/markdown-renderer/",
                    "icon": "📝",
                },
                {
                    "name": "Text Diff Checker",
                    "description": "Compare two text blocks side-by-side with highlighted differences.",
                    "use_case": "Compare dataset versions or track changes in results",
                    "bookmarklet_url": "/tools/text-diff-checker/",
                    "icon": "🔄",
                },
                {
                    "name": "JSON Formatter",
                    "description": "Format, validate, and beautify JSON data with syntax highlighting.",
                    "use_case": "Validate plot specifications and configuration files",
                    "bookmarklet_url": "/tools/json-formatter/",
                    "icon": "{ }",
                },
            ],
        },
        {
            "name": "Image",
            "slug": "image",
            "icon": "🖼️",
            "description": "Manipulate and convert images for publications",
            "tools": [
                {
                    "name": "Image & PDF Viewer",
                    "description": "View dimensions, DPI, and unit conversions (mm/inch) for publication figures.",
                    "use_case": "Verify Figure 2 meets journal dimension requirements",
                    "bookmarklet_url": "/tools/image-viewer/",
                    "icon": "📐",
                },
                {
                    "name": "Image Resizer",
                    "description": "Resize and crop images for journal submissions with preset dimensions.",
                    "use_case": "Adjust Figure 2 to exact pixel-perfect journal specs",
                    "bookmarklet_url": "/tools/image-resizer/",
                    "icon": "📏",
                },
                {
                    "name": "Image Converter",
                    "description": "Convert images between PNG, JPG, WEBP, TIFF formats with batch conversion.",
                    "use_case": "Convert PNG figures to TIFF for journal submission",
                    "bookmarklet_url": "/tools/image-converter/",
                    "icon": "🔄",
                },
                {
                    "name": "Image Concatenator",
                    "description": "Combine multiple images into a single tiled multi-panel figure.",
                    "use_case": "Create Figure 1 panel layouts (A, B, C, D)",
                    "bookmarklet_url": "/tools/image-concatenator/",
                    "icon": "🖼️",
                },
                {
                    "name": "Mermaid Diagram Renderer",
                    "description": "Create flowcharts, sequence diagrams, and concept diagrams from text syntax.",
                    "use_case": "Design experimental workflow diagrams for Methods section",
                    "bookmarklet_url": "/tools/mermaid-renderer/",
                    "icon": "🧜‍♀️",
                },
                {
                    "name": "Images to GIF",
                    "description": "Convert image sequences into animated GIF with customizable duration.",
                    "use_case": "Create supplementary animations showing temporal changes",
                    "bookmarklet_url": "/tools/images-to-gif/",
                    "icon": "🎬",
                },
                {
                    "name": "Images to PDF",
                    "description": "Convert multiple images into a single PDF with custom page orientation.",
                    "use_case": "Create supplementary figures PDF from multiple images",
                    "bookmarklet_url": "/tools/images-to-pdf/",
                    "icon": "📄",
                },
                {
                    "name": "PDF to Images",
                    "description": "Extract all pages from PDF as PNG or JPG images with adjustable DPI.",
                    "use_case": "Convert PDF figures to images for presentation slides",
                    "bookmarklet_url": "/tools/pdf-to-images/",
                    "icon": "🖼️",
                },
            ],
        },
        {
            "name": "PDF",
            "slug": "pdf",
            "icon": "📄",
            "description": "Manage and process PDF documents",
            "tools": [
                {
                    "name": "Image & PDF Viewer",
                    "description": "View dimensions, DPI, and unit conversions (mm/inch) for publication figures.",
                    "use_case": "Verify Figure 2 meets journal dimension requirements",
                    "bookmarklet_url": "/tools/image-viewer/",
                    "icon": "📐",
                },
                {
                    "name": "PDF Merger",
                    "description": "Combine multiple PDF files into a single document with drag-to-reorder.",
                    "use_case": "Merge manuscript, figures, and supplements for submission",
                    "bookmarklet_url": "/tools/pdf-merger/",
                    "icon": "📑",
                },
                {
                    "name": "PDF Compressor",
                    "description": "Reduce PDF file size while maintaining quality for email and uploads.",
                    "use_case": "Compress submission files under journal size limits",
                    "bookmarklet_url": "/tools/pdf-compressor/",
                    "icon": "🗜️",
                },
                {
                    "name": "PDF Splitter",
                    "description": "Extract specific pages from PDF files using page ranges.",
                    "use_case": "Extract figures from compiled manuscript for separate upload",
                    "bookmarklet_url": "/tools/pdf-splitter/",
                    "icon": "✂️",
                },
                {
                    "name": "Images to PDF",
                    "description": "Convert multiple images into a single PDF with custom page orientation.",
                    "use_case": "Create supplementary figures PDF from multiple images",
                    "bookmarklet_url": "/tools/images-to-pdf/",
                    "icon": "📄",
                },
                {
                    "name": "PDF to Images",
                    "description": "Extract all pages from PDF as PNG or JPG images with adjustable DPI.",
                    "use_case": "Convert PDF figures to images for presentation slides",
                    "bookmarklet_url": "/tools/pdf-to-images/",
                    "icon": "🖼️",
                },
            ],
        },
        {
            "name": "Video",
            "slug": "video",
            "icon": "🎬",
            "description": "Video and animation processing",
            "tools": [
                {
                    "name": "Video Editor",
                    "description": "Trim videos by time window with browser-based processing.",
                    "use_case": "Edit supplementary videos for journal submission",
                    "bookmarklet_url": "/tools/video-editor/",
                    "icon": "🎬",
                },
                {
                    "name": "Images to GIF",
                    "description": "Convert image sequences into animated GIF with customizable duration.",
                    "use_case": "Create supplementary animations showing temporal changes",
                    "bookmarklet_url": "/tools/images-to-gif/",
                    "icon": "🎬",
                },
            ],
        },
        {
            "name": "Rendering",
            "slug": "rendering",
            "icon": "📈",
            "description": "Create publication-quality plots and diagrams",
            "tools": [
                {
                    "name": "Plot Viewer",
                    "description": "Interactive CSV plot viewer with Nature journal standards. Supports line, scatter, and bar plots with 300 DPI rendering.",
                    "use_case": "Quick data visualization during analysis",
                    "bookmarklet_url": "/tools/plot-viewer/",
                    "icon": "📊",
                },
                {
                    "name": "Plot Backend Test",
                    "description": "Test matplotlib/scitex.plt backend with JSON specifications. Generate publication-quality SVG plots.",
                    "use_case": "Design figures with precise journal specifications",
                    "bookmarklet_url": "/tools/plot-backend-test/",
                    "icon": "🧪",
                },
                {
                    "name": "Mermaid Diagram Renderer",
                    "description": "Create flowcharts, sequence diagrams, and concept diagrams from text syntax.",
                    "use_case": "Design experimental workflow diagrams for Methods section",
                    "bookmarklet_url": "/tools/mermaid-renderer/",
                    "icon": "🧜‍♀️",
                },
                {
                    "name": "Markdown Renderer",
                    "description": "Real-time Markdown preview with syntax highlighting and table support.",
                    "use_case": "Format README files and documentation for data repositories",
                    "bookmarklet_url": "/tools/markdown-renderer/",
                    "icon": "📝",
                },
                {
                    "name": "Color Picker",
                    "description": "Advanced color picker with format conversion and palette generation.",
                    "use_case": "Design consistent color schemes for figure panels",
                    "bookmarklet_url": "/tools/color-picker/",
                    "icon": "🎨",
                },
            ],
        },
        {
            "name": "Developer",
            "slug": "development",
            "icon": "💻",
            "description": "Web development and debugging utilities",
            "tools": [
                {
                    "name": "Element Inspector",
                    "description": "Visual debugging tool with AI-ready output format.",
                    "use_case": "Debug web interface issues in research platforms",
                    "bookmarklet_url": "/tools/element-inspector/",
                    "icon": "🔍",
                },
                {
                    "name": "Repository Concatenator",
                    "description": "Concatenate repository files into AI-ready format for code review.",
                    "use_case": "Prepare analysis scripts for AI code review",
                    "bookmarklet_url": "/tools/repo-concatenator/",
                    "icon": "📦",
                },
                {
                    "name": "Color Picker",
                    "description": "Advanced color picker with format conversion and palette generation.",
                    "use_case": "Design consistent color schemes for figure panels",
                    "bookmarklet_url": "/tools/color-picker/",
                    "icon": "🎨",
                },
                {
                    "name": "QR Code Generator",
                    "description": "Generate QR codes for URLs, DOIs, posters, and presentations.",
                    "use_case": "Add QR codes to conference posters linking to papers",
                    "bookmarklet_url": "/tools/qr-code-generator/",
                    "icon": "📱",
                },
            ],
        },
        {
            "name": "Research",
            "slug": "research",
            "icon": "🔬",
            "description": "Literature management and citation tools",
            "tools": [
                {
                    "name": "Asta AI Citation Scraper",
                    "description": "Automatically collect all BibTeX citations from Asta AI search results.",
                    "use_case": "Build bibliography from AI literature searches",
                    "bookmarklet_url": "/tools/asta-citation-scraper/",
                    "icon": "📚",
                },
                {
                    "name": "Statistics Calculator",
                    "description": "Quick statistical analysis for research data with descriptive stats, t-tests, and correlations.",
                    "use_case": "Verify experimental results before plotting",
                    "bookmarklet_url": "/tools/statistics-calculator/",
                    "icon": "📈",
                },
            ],
        },
    ]

    # Calculate total tools
    total_tools = sum(len(domain["tools"]) for domain in domains)

    context = {
        "domains": domains,
        "total_tools": total_tools,
    }

    return render(request, "public_app/pages/tools.html", context)
