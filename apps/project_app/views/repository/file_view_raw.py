"""
File View Raw Mode

Handles raw file serving and downloads.
"""

from django.http import HttpResponse


# Content type mapping by extension
CONTENT_TYPE_MAP = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
}


def serve_raw_file(full_file_path, file_name, file_ext, mode):
    """
    Serve file in raw or download mode.

    Args:
        full_file_path: Full path to the file
        file_name: Name of the file
        file_ext: File extension (lowercase)
        mode: Either 'raw' or 'download'

    Returns:
        HttpResponse: Raw file response
    """
    content_type = CONTENT_TYPE_MAP.get(file_ext, "text/plain; charset=utf-8")

    with open(full_file_path, "rb") as f:
        response = HttpResponse(f.read(), content_type=content_type)

    # For download mode, force download instead of inline display
    disposition = "attachment" if mode == "download" else "inline"
    response["Content-Disposition"] = f'{disposition}; filename="{file_name}"'

    return response
