#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Directory Views - Content Rendering Module

Handles file content reading and rendering type detection.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Binary file extensions
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico",
    ".pdf", ".zip", ".tar", ".gz", ".7z", ".rar",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".mp3", ".mp4", ".wav", ".avi", ".mov",
    ".exe", ".dll", ".so", ".dylib",
    ".pyc", ".pyo", ".class",
}

# Image extensions for inline display
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}

# Maximum file size for display (1MB)
MAX_DISPLAY_SIZE = 1024 * 1024


def determine_render_type(full_file_path: Path, file_ext: str):
    """
    Determine how to render a file based on extension and content.

    Args:
        full_file_path: Full path to the file
        file_ext: File extension (lowercase)

    Returns:
        tuple: (render_type, file_content, file_html, language)
            render_type: "binary", "image", "pdf", "markdown", "code", "text"
            file_content: Raw file content (or error message for binary)
            file_html: Rendered HTML (for markdown)
            language: Detected programming language (for syntax highlighting)
    """
    file_size = full_file_path.stat().st_size

    # Check file size limit
    if file_size > MAX_DISPLAY_SIZE:
        return (
            "binary",
            f"File too large to display ({file_size:,} bytes). Maximum size: {MAX_DISPLAY_SIZE:,} bytes.",
            None,
            None,
        )

    # Check if file is binary by extension
    if file_ext in BINARY_EXTENSIONS:
        if file_ext in IMAGE_EXTENSIONS:
            return ("image", None, None, None)
        elif file_ext == ".pdf":
            return ("pdf", None, None, None)
        else:
            return ("binary", f"Binary file ({file_size:,} bytes)", None, None)

    # Try to read as text file
    try:
        with open(full_file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        # Detect language for syntax highlighting
        from apps.project_app.services.syntax_highlighting import detect_language
        file_name = full_file_path.name
        language = detect_language(file_ext, file_name)

        # Render based on file type
        if file_ext == ".md":
            import markdown
            file_html = markdown.markdown(
                file_content,
                extensions=["fenced_code", "tables", "nl2br", "codehilite"],
            )
            return ("markdown", file_content, file_html, language)
        elif language:
            return ("code", file_content, None, language)
        else:
            return ("text", file_content, None, None)

    except UnicodeDecodeError:
        # File is binary but wasn't caught by extension check
        return ("binary", f"Binary file ({file_size:,} bytes)", None, None)


# EOF
