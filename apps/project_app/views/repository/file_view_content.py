"""
File View Content Rendering

Handles content type detection and rendering.
"""

import markdown
import bleach
from bleach.css_sanitizer import CSSSanitizer

from apps.project_app.services.syntax_highlighting import detect_language


# Binary file extensions
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".tar", ".gz",
    ".ico", ".woff", ".woff2", ".ttf", ".eot", ".webp", ".svg",
}

# Image extensions for inline display
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}

# Maximum file size for display (1MB)
MAX_DISPLAY_SIZE = 1024 * 1024


def determine_render_type(file_ext, file_size):
    """
    Determine how to render the file.

    Args:
        file_ext: File extension (lowercase)
        file_size: File size in bytes

    Returns:
        str: Render type ('binary', 'image', 'pdf', 'text', 'code', 'markdown')
    """
    if file_size > MAX_DISPLAY_SIZE:
        return "binary"

    if file_ext in IMAGE_EXTENSIONS:
        return "image"

    if file_ext == ".pdf":
        return "pdf"

    if file_ext in BINARY_EXTENSIONS:
        return "binary"

    if file_ext == ".md":
        return "markdown"

    return "code"


def render_file_content(full_file_path, file_ext, file_size):
    """
    Read and render file content.

    Args:
        full_file_path: Full path to file
        file_ext: File extension (lowercase)
        file_size: File size in bytes

    Returns:
        dict: Content data with keys:
            - render_type: str
            - file_content: str or None
            - file_html: str or None (for markdown)
            - language: str or None
    """
    render_type = determine_render_type(file_ext, file_size)

    # Handle size limit exceeded
    if file_size > MAX_DISPLAY_SIZE:
        return {
            "render_type": "binary",
            "file_content": f"File too large to display ({file_size:,} bytes). Maximum size: {MAX_DISPLAY_SIZE:,} bytes.",
            "file_html": None,
            "language": None,
        }

    # Handle binary files
    if render_type in ("image", "pdf"):
        return {
            "render_type": render_type,
            "file_content": None,
            "file_html": None,
            "language": None,
        }

    if render_type == "binary":
        return {
            "render_type": "binary",
            "file_content": f"Binary file ({file_size:,} bytes)",
            "file_html": None,
            "language": None,
        }

    # Try to read as text
    try:
        with open(full_file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
    except UnicodeDecodeError:
        return {
            "render_type": "binary",
            "file_content": f"Binary file ({file_size:,} bytes)",
            "file_html": None,
            "language": None,
        }

    # Detect language for syntax highlighting
    file_name = full_file_path.name
    language = detect_language(file_ext, file_name)

    # Handle markdown
    if render_type == "markdown":
        file_html = render_markdown(file_content)
        return {
            "render_type": "markdown",
            "file_content": file_content,
            "file_html": file_html,
            "language": language,
        }

    # Handle code/text
    render_type = "code" if language else "text"
    return {
        "render_type": render_type,
        "file_content": file_content,
        "file_html": None,
        "language": language,
    }


def render_markdown(content):
    """
    Render markdown content to sanitized HTML.

    Args:
        content: Raw markdown content

    Returns:
        str: Sanitized HTML
    """
    # Render markdown to HTML
    raw_html = markdown.markdown(
        content,
        extensions=[
            "fenced_code",
            "tables",
            "nl2br",
            "codehilite",
        ],
    )

    # Sanitize HTML to prevent XSS
    allowed_tags = bleach.ALLOWED_TAGS | {
        "h1", "h2", "h3", "h4", "h5", "h6",
        "p", "br", "hr", "pre", "code", "span", "div",
        "table", "thead", "tbody", "tr", "th", "td",
        "ul", "ol", "li", "dl", "dt", "dd",
        "img", "a", "strong", "em", "del", "ins",
        "blockquote", "details", "summary",
    }

    allowed_attributes = {
        "*": ["class", "id"],
        "a": ["href", "title", "rel"],
        "img": ["src", "alt", "title", "width", "height"],
        "code": ["class"],
        "pre": ["class"],
        "span": ["class", "style"],
        "div": ["class", "style"],
    }

    css_sanitizer = CSSSanitizer(
        allowed_css_properties=["color", "background-color"]
    )

    return bleach.clean(
        raw_html,
        tags=allowed_tags,
        attributes=allowed_attributes,
        css_sanitizer=css_sanitizer,
        strip=False,
    )
