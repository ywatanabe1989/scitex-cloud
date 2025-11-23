"""search feature views"""

# Import main views
from .views import *

# Import modular views (refactored from monolithic views.py)
from .page_views import (
    index,
    scholar_bibtex,
    scholar_search,
    bibtex_enrichment_view,
    literature_search_view,
    features,
    pricing,
    personal_library,
)

from .preferences import (
    get_user_preferences,
    save_user_preferences,
    save_source_preferences,
)

# Make all imports available at package level
__all__ = [
    # Page views
    "index",
    "scholar_bibtex",
    "scholar_search",
    "bibtex_enrichment_view",
    "literature_search_view",
    "features",
    "pricing",
    "personal_library",
    # Preferences
    "get_user_preferences",
    "save_user_preferences",
    "save_source_preferences",
]
