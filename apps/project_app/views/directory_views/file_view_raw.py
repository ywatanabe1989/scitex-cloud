#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Directory Views - Raw/Download Mode Module

Handles serving raw file content and downloads.
"""

from __future__ import annotations

from pathlib import Path
from django.http import HttpResponse


def handle_raw_mode(full_file_path: Path, file_name: str, file_ext: str, mode: str):
    """
    Handle raw/download mode - serve file directly.

    Args:
        full_file_path: Full path to the file
        file_name: Name of the file
        file_ext: File extension (lowercase)
        mode: "raw" for inline display, "download" for attachment

    Returns:
        HttpResponse with file content
    """
    # Determine content type based on file extension
    content_type_map = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
        ".ico": "image/x-icon",
        ".json": "application/json",
        ".xml": "application/xml",
        ".zip": "application/zip",
        ".tar": "application/x-tar",
        ".gz": "application/gzip",
    }

    content_type = content_type_map.get(file_ext, "text/plain; charset=utf-8")

    with open(full_file_path, "rb") as f:
        response = HttpResponse(f.read(), content_type=content_type)
        # For download mode, force download instead of inline display
        disposition = "attachment" if mode == "download" else "inline"
        response["Content-Disposition"] = f'{disposition}; filename="{file_name}"'
        return response


# EOF
