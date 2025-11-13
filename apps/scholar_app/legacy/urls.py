from django.urls import path
from . import views, simple_views

app_name = "scholar"

urlpatterns = [
    # MVP Simple Interface
    path("", simple_views.index, name="index"),
    path("search/", simple_views.simple_search, name="simple_search"),
    path("library/", simple_views.personal_library, name="personal_library"),
    path("features/", simple_views.features, name="features"),
    path("pricing/", simple_views.pricing, name="pricing"),
    # MVP API endpoints
    path("api/save-paper/", simple_views.save_paper, name="save_paper"),
    path("api/upload-file/", simple_views.upload_file, name="upload_file"),
    path("api/get-citation/", simple_views.get_citation, name="get_citation"),
    # Saved Search API endpoints
    path("api/save-search/", simple_views.save_search, name="save_search"),
    path(
        "api/saved-searches/",
        simple_views.get_saved_searches,
        name="get_saved_searches",
    ),
    path(
        "api/saved-searches/<uuid:search_id>/delete/",
        simple_views.delete_saved_search,
        name="delete_saved_search",
    ),
    path(
        "api/saved-searches/<uuid:search_id>/run/",
        simple_views.run_saved_search,
        name="run_saved_search",
    ),
    # Progressive search API endpoints
    path("api/search/arxiv/", simple_views.api_search_arxiv, name="api_search_arxiv"),
    path(
        "api/search/pubmed/", simple_views.api_search_pubmed, name="api_search_pubmed"
    ),
    path(
        "api/search/semantic/",
        simple_views.api_search_semantic,
        name="api_search_semantic",
    ),
    path("api/search/pmc/", simple_views.api_search_pmc, name="api_search_pmc"),
    path("api/search/doaj/", simple_views.api_search_doaj, name="api_search_doaj"),
    path(
        "api/search/biorxiv/",
        simple_views.api_search_biorxiv,
        name="api_search_biorxiv",
    ),
    path("api/search/plos/", simple_views.api_search_plos, name="api_search_plos"),
    # Citation Export endpoints
    path("api/export/bibtex/", simple_views.export_bibtex, name="export_bibtex"),
    path("api/export/ris/", simple_views.export_ris, name="export_ris"),
    path("api/export/endnote/", simple_views.export_endnote, name="export_endnote"),
    path("api/export/csv/", simple_views.export_csv, name="export_csv"),
    # Personal Library API endpoints
    path(
        "api/library/papers/",
        simple_views.api_library_papers,
        name="api_library_papers",
    ),
    path(
        "api/library/collections/",
        simple_views.api_library_collections,
        name="api_library_collections",
    ),
    path(
        "api/library/collections/create/",
        simple_views.api_create_collection,
        name="api_create_collection",
    ),
    path(
        "api/library/papers/<uuid:paper_id>/update/",
        simple_views.api_update_library_paper,
        name="api_update_library_paper",
    ),
    path(
        "api/library/papers/<uuid:paper_id>/remove/",
        simple_views.api_remove_library_paper,
        name="api_remove_library_paper",
    ),
    # Paper Similarity Recommendations endpoints
    path(
        "api/recommendations/paper/<uuid:paper_id>/",
        simple_views.paper_recommendations,
        name="paper_recommendations",
    ),
    path(
        "api/recommendations/user/",
        simple_views.user_recommendations,
        name="user_recommendations",
    ),
    # Legacy mock endpoints
    path("api/mock/save-paper/", simple_views.mock_save_paper, name="mock_save_paper"),
    path(
        "api/mock/get-citation/",
        simple_views.mock_get_citation,
        name="mock_get_citation",
    ),
    # Advanced features (for future implementation)
    path("advanced/dashboard/", views.search_dashboard, name="search_dashboard"),
    path("advanced/search/", views.advanced_search, name="advanced_search"),
    path("advanced/paper/<uuid:paper_id>/", views.paper_detail, name="paper_detail"),
    path(
        "advanced/author/<uuid:author_id>/", views.author_profile, name="author_profile"
    ),
    path("advanced/saved/", views.saved_searches, name="saved_searches"),
    path("advanced/trending/", views.trending_papers, name="trending_papers"),
]
