"""
Section configuration for Writer app dropdowns.

Defines hierarchical structure matching scitex.writer backend.
"""

# Hierarchical section structure
SECTION_HIERARCHY = {
    "shared": {
        "label": "Shared",
        "description": "Shared content across all documents",
        "sections": [
            {"id": "shared/title", "name": "title", "label": "Title", "path": "shared/title.tex"},
            {"id": "shared/authors", "name": "authors", "label": "Authors", "path": "shared/authors.tex"},
            {"id": "shared/bibliography", "name": "bibliography", "label": "Bibliography", "path": "shared/bib_files/bibliography.bib"},
        ]
    },
    "manuscript": {
        "label": "Manuscript",
        "description": "Main manuscript content",
        "sections": [
            {"id": "manuscript/abstract", "name": "abstract", "label": "Abstract", "path": "01_manuscript/contents/abstract.tex"},
            {"id": "manuscript/introduction", "name": "introduction", "label": "Introduction", "path": "01_manuscript/contents/introduction.tex"},
            {"id": "manuscript/methods", "name": "methods", "label": "Methods", "path": "01_manuscript/contents/methods.tex"},
            {"id": "manuscript/results", "name": "results", "label": "Results", "path": "01_manuscript/contents/results.tex"},
            {"id": "manuscript/discussion", "name": "discussion", "label": "Discussion", "path": "01_manuscript/contents/discussion.tex"},
            {"id": "manuscript/references", "name": "references", "label": "References", "path": "01_manuscript/contents/bibliography.bib", "view_only": True, "instruction": "Add references using bibliography.bib file"},
            {"id": "manuscript/figures", "name": "figures", "label": "Figures", "path": "01_manuscript/contents/figures/", "is_directory": True},
            {"id": "manuscript/tables", "name": "tables", "label": "Tables", "path": "01_manuscript/contents/tables/", "is_directory": True},
            {"id": "manuscript/highlights", "name": "highlights", "label": "Highlights", "path": "01_manuscript/contents/highlights.tex", "optional": True},
        ]
    },
    "supplementary": {
        "label": "Supplementary",
        "description": "Supplementary materials",
        "sections": [
            {"id": "supplementary/methods", "name": "methods", "label": "Methods", "path": "02_supplementary/contents/methods.tex"},
            {"id": "supplementary/results", "name": "results", "label": "Results", "path": "02_supplementary/contents/results.tex"},
            {"id": "supplementary/figures", "name": "figures", "label": "Figures", "path": "02_supplementary/contents/figures/", "is_directory": True},
            {"id": "supplementary/tables", "name": "tables", "label": "Tables", "path": "02_supplementary/contents/tables/", "is_directory": True},
        ]
    },
    "revision": {
        "label": "Revision",
        "description": "Revision materials (CRUD enabled)",
        "supports_crud": True,
        "sections": [
            # Base sections
            {"id": "revision/introduction", "name": "introduction", "label": "Introduction", "path": "03_revision/contents/introduction.tex"},
            {"id": "revision/conclusion", "name": "conclusion", "label": "Conclusion", "path": "03_revision/contents/conclusion.tex"},
            # Editor comments (dynamic)
            # Reviewer comments (dynamic)
        ]
    }
}


def get_all_sections_flat():
    """
    Get flattened list of all sections.

    Returns:
        List of section dictionaries with category added
    """
    sections = []
    for category, config in SECTION_HIERARCHY.items():
        for section in config["sections"]:
            section_copy = section.copy()
            section_copy["category"] = category
            sections.append(section_copy)
    return sections


def get_sections_by_category(category):
    """
    Get sections for specific category.

    Args:
        category: One of 'shared', 'manuscript', 'supplementary', 'revision'

    Returns:
        List of section dictionaries or None if category not found
    """
    if category in SECTION_HIERARCHY:
        return SECTION_HIERARCHY[category]["sections"]
    return None


def get_category_info(category):
    """
    Get category metadata.

    Args:
        category: One of 'shared', 'manuscript', 'supplementary', 'revision'

    Returns:
        Dictionary with label, description, supports_crud
    """
    if category in SECTION_HIERARCHY:
        config = SECTION_HIERARCHY[category]
        return {
            "label": config.get("label"),
            "description": config.get("description"),
            "supports_crud": config.get("supports_crud", False)
        }
    return None
