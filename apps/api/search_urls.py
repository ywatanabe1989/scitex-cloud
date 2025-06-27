from django.urls import path
from apps.api import search_views

urlpatterns = [
    # SciTeX-Search API endpoints
    path('papers/', search_views.search_papers, name='search-papers'),
    path('papers/<uuid:paper_id>/', search_views.get_paper_details, name='search-paper-details'),
    path('papers/<uuid:paper_id>/citations/', search_views.get_citations, name='search-paper-citations'),
    path('papers/<uuid:paper_id>/export/', search_views.export_bibtex, name='search-export-paper'),
    path('authors/<uuid:author_id>/papers/', search_views.get_author_papers, name='search-author-papers'),
    path('recommendations/', search_views.get_recommendations, name='search-recommendations'),
    path('trending/', search_views.get_trending, name='search-trending'),
    path('track-click/', search_views.track_click, name='search-track-click'),
    path('alerts/', search_views.save_search_alert, name='search-save-alert'),
    path('suggestions/', search_views.get_search_suggestions, name='search-suggestions'),
    
    # Legacy endpoints (for backwards compatibility)
    path('query/', search_views.search_documents, name='search-query'),
    path('analyze/', search_views.analyze_document, name='search-analyze'),
    path('keywords/', search_views.extract_keywords, name='search-keywords'),
    path('similar/<int:doc_id>/', search_views.find_similar, name='search-similar'),
]