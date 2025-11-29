"""Section management views.

Modular structure:
- helpers.py: Shared constants (DOC_DIR_MAP, CORE_SECTIONS)
- create.py: section_create_view
- delete.py: section_delete_view
- toggle.py: section_toggle_exclude_view
- move.py: section_move_up_view, section_move_down_view
"""

from .create import section_create_view
from .delete import section_delete_view
from .toggle import section_toggle_exclude_view
from .move import section_move_up_view, section_move_down_view

__all__ = [
    "section_create_view",
    "section_delete_view",
    "section_toggle_exclude_view",
    "section_move_up_view",
    "section_move_down_view",
]
