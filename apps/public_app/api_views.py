#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-19 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/public_app/api_views.py
# ----------------------------------------
"""
API views for public_app tools.

Provides backend functionality for browser-based tools that require
server-side processing.
"""

import json
import logging
import tempfile
from typing import Any, Dict, Optional

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger("scitex")

# ----------------------------------------


@csrf_exempt
@require_http_methods(["POST"])
def read_image_metadata(request):
    """
    Read embedded metadata and file info from uploaded image or PDF file.

    Supports PNG, JPEG, and PDF files. Uses scitex.io unified interface.
    Extracts:
    - Embedded metadata (from PNG tEXt chunks, JPEG EXIF, or PDF Subject field)
    - File dimensions (pixels for images, points for PDFs)
    - Page count (for PDFs)

    Returns:
        JSON response with metadata, dimensions, and file info
    """
    try:
        # Check if file was uploaded
        if "image" not in request.FILES:
            return JsonResponse(
                {"error": "No file provided", "has_metadata": False}, status=400
            )

        uploaded_file = request.FILES["image"]
        file_ext = uploaded_file.name.split('.')[-1].lower()

        # Save to temporary file
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{file_ext}"
        ) as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name

        try:
            # Import scitex.io
            from scitex.io import load, read_metadata

            # Determine file type
            is_pdf = file_ext == 'pdf'

            # Extract metadata using scitex.io
            metadata = read_metadata(tmp_path)

            # Load file to get dimensions
            if is_pdf:
                # For PDFs, load with metadata mode to get page info
                pdf_data = load(tmp_path, mode='metadata')

                response_data = {
                    "has_metadata": metadata is not None,
                    "metadata": metadata,
                    "file_type": "pdf",
                    "page_count": pdf_data.get('pages', 0),
                    "dimensions": {
                        "width_pt": None,  # Need first page for this
                        "height_pt": None,
                        "pages": pdf_data.get('pages', 0),
                    },
                    "pdf_metadata": {
                        "title": pdf_data.get('title', ''),
                        "author": pdf_data.get('author', ''),
                        "subject": pdf_data.get('subject', ''),
                        "creator": pdf_data.get('creator', ''),
                    }
                }
            else:
                # For images, load to get dimensions
                img, _ = load(tmp_path, metadata=True)

                response_data = {
                    "has_metadata": metadata is not None,
                    "metadata": metadata,
                    "file_type": "image",
                    "dimensions": {
                        "width": img.width,
                        "height": img.height,
                    }
                }

                img.close()

            if metadata is None:
                response_data["message"] = f"No scitex metadata found in {file_ext.upper()}"
            else:
                response_data["message"] = "Metadata successfully extracted"

            return JsonResponse(response_data)

        finally:
            # Clean up temporary file
            import os

            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except ImportError as e:
        logger.error(f"Failed to import scitex.io: {e}")
        return JsonResponse(
            {
                "error": "Metadata extraction not available (scitex.io not installed)",
                "has_metadata": False,
            },
            status=500,
        )

    except Exception as e:
        logger.error(f"Error reading file metadata: {e}")
        return JsonResponse(
            {"error": f"Failed to read metadata: {str(e)}", "has_metadata": False},
            status=500,
        )


# EOF
