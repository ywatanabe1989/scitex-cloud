"""Shared helpers for section management views."""

# Map doc_type to directory path
DOC_DIR_MAP = {
    "manuscript": "01_manuscript/contents",
    "supplementary": "02_supplementary/contents",
    "revision": "03_revision/contents",
    "shared": "shared",
}

# Core sections that cannot be deleted
CORE_SECTIONS = [
    "abstract",
    "introduction",
    "methods",
    "results",
    "discussion",
    "title",
    "authors",
    "keywords",
    "compiled_pdf",
    "compiled_tex",
    "highlights",
    "conclusion",
    "references",
]
