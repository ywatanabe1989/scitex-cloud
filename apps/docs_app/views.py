#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-cloud/apps/docs_app/views.py

from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.conf import settings
from pathlib import Path
import os


# Documentation paths for each module
DOC_PATHS = {
    "scholar": "externals/SciTeX-Scholar/docs/_build/html",
    "code": "externals/SciTeX-Code/docs/_build/html",
    "viz": "externals/SciTeX-Viz/docs/_build/html",
    "writer": "externals/SciTeX-Writer/docs/_build/html",
}


def docs_index(request):
    """Documentation landing page showing all available modules."""
    context = {
        "modules": [
            {
                "name": "Scholar",
                "slug": "scholar",
                "description": "Literature search and reference management",
                "icon": "scitex-scholar-icon.svg",
                "available": _check_docs_available("scholar"),
            },
            {
                "name": "Code",
                "slug": "code",
                "description": "Research computing and analysis utilities",
                "icon": "scitex-code-icon.svg",
                "available": _check_docs_available("code"),
            },
            {
                "name": "Viz",
                "slug": "viz",
                "description": "Publication-quality visualization tools",
                "icon": "scitex-viz-icon.svg",
                "available": _check_docs_available("viz"),
            },
            {
                "name": "Writer",
                "slug": "writer",
                "description": "LaTeX manuscript preparation and management",
                "icon": "scitex-writer-icon.svg",
                "available": _check_docs_available("writer"),
            },
        ]
    }
    return render(request, "docs_app/docs_index.html", context)


def docs_scholar(request):
    """Redirect to Scholar documentation main page."""
    return _serve_module_docs(request, "scholar", "index.html")


def docs_code(request):
    """Redirect to Code documentation main page."""
    return _serve_module_docs(request, "code", "index.html")


def docs_viz(request):
    """Redirect to Viz documentation main page."""
    return _serve_module_docs(request, "viz", "index.html")


def docs_writer(request):
    """Redirect to Writer documentation main page."""
    return _serve_module_docs(request, "writer", "index.html")


def docs_page(request, module, page):
    """Serve a specific documentation page."""
    return _serve_module_docs(request, module, page)


def _check_docs_available(module):
    """Check if documentation is built and available for a module."""
    if module not in DOC_PATHS:
        return False

    doc_path = Path(settings.BASE_DIR) / DOC_PATHS[module]
    return doc_path.exists() and (doc_path / "index.html").exists()


def _serve_module_docs(request, module, page="index.html"):
    """Serve documentation files for a specific module."""
    if module not in DOC_PATHS:
        raise Http404("Module documentation not found")

    # Construct the full path to the documentation file
    doc_base = Path(settings.BASE_DIR) / DOC_PATHS[module]
    doc_file = doc_base / page

    # Security: ensure the path is within the documentation directory
    try:
        doc_file = doc_file.resolve()
        doc_base = doc_base.resolve()
        if not str(doc_file).startswith(str(doc_base)):
            raise Http404("Invalid documentation path")
    except (ValueError, OSError):
        raise Http404("Invalid documentation path")

    # Check if file exists
    if not doc_file.exists():
        raise Http404(f"Documentation page not found: {page}")

    # Read and serve the file
    if doc_file.suffix == ".html":
        with open(doc_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Wrap in SciTeX template
        context = {
            "module": module,
            "module_name": module.capitalize(),
            "doc_content": content,
            "page": page,
        }
        return render(request, "docs_app/docs_page.html", context)
    else:
        # Serve static files (CSS, JS, images) directly
        content_types = {
            ".css": "text/css",
            ".js": "application/javascript",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".woff": "font/woff",
            ".woff2": "font/woff2",
            ".ttf": "font/ttf",
        }
        content_type = content_types.get(doc_file.suffix, "application/octet-stream")

        with open(doc_file, "rb") as f:
            return HttpResponse(f.read(), content_type=content_type)
