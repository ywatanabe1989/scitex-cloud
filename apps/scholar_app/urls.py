#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-22 10:40:20 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/scholar_app/urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./apps/scholar_app/urls.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, simple_views, repository_views, api_views, bibtex_views, default_workspace_views

app_name = 'scholar_app'

# Repository API Router
router = DefaultRouter()
router.register(r'repositories', repository_views.RepositoryViewSet, basename='repositories')
router.register(r'connections', repository_views.RepositoryConnectionViewSet, basename='connections')
router.register(r'datasets', repository_views.DatasetViewSet, basename='datasets')

urlpatterns = [
    # Default workspace for logged-in users without project
    path('workspace/', default_workspace_views.user_default_workspace, name='user_default_workspace'),

    # MVP Simple Interface
    path('', simple_views.index, name='index'),
    path('search/', simple_views.index, name='simple_search'),
    # path('search/', simple_views.simple_search, name='simple_search'),
    # path('project/<int:project_id>/search/', simple_views.project_search, name='project_search'),
    # path('project/<int:project_id>/library/', simple_views.project_library, name='project_library'),
    # path('library/', simple_views.personal_library, name='personal_library'),
    # path('features/', simple_views.features, name='features'),
    # path('pricing/', simple_views.pricing, name='pricing'),

    # MVP API endpoints
    path('api/save-paper/', simple_views.save_paper, name='save_paper'),
    path('api/upload-file/', simple_views.upload_file, name='upload_file'),
    path('api/get-citation/', simple_views.get_citation, name='get_citation'),

    # User Preferences API endpoints
    path('api/preferences/', simple_views.get_user_preferences, name='get_user_preferences'),
    path('api/preferences/save/', simple_views.save_user_preferences, name='save_user_preferences'),
    path('api/preferences/sources/', simple_views.save_source_preferences, name='save_source_preferences'),

    # API Key Management endpoints
    path('api-keys/', api_views.api_key_management, name='api_keys'),
    path('api/test-api-key/', api_views.test_api_key, name='test_api_key'),
    path('api/usage-stats/', api_views.api_usage_stats, name='api_usage_stats'),

    # Saved Search API endpoints
    path('api/save-search/', simple_views.save_search, name='save_search'),
    path('api/saved-searches/', simple_views.get_saved_searches, name='get_saved_searches'),
    path('api/saved-searches/<uuid:search_id>/delete/', simple_views.delete_saved_search, name='delete_saved_search'),
    path('api/saved-searches/<uuid:search_id>/run/', simple_views.run_saved_search, name='run_saved_search'),

    # Progressive search API endpoints
    path('api/search/arxiv/', simple_views.api_search_arxiv, name='api_search_arxiv'),
    path('api/search/pubmed/', simple_views.api_search_pubmed, name='api_search_pubmed'),
    path('api/search/semantic/', simple_views.api_search_semantic, name='api_search_semantic'),
    path('api/search/pmc/', simple_views.api_search_pmc, name='api_search_pmc'),
    path('api/search/doaj/', simple_views.api_search_doaj, name='api_search_doaj'),
    path('api/search/biorxiv/', simple_views.api_search_biorxiv, name='api_search_biorxiv'),
    path('api/search/plos/', simple_views.api_search_plos, name='api_search_plos'),

    # Citation Export endpoints
    path('api/export/bibtex/', simple_views.export_bibtex, name='export_bibtex'),
    path('api/export/ris/', simple_views.export_ris, name='export_ris'),
    path('api/export/endnote/', simple_views.export_endnote, name='export_endnote'),
    path('api/export/csv/', simple_views.export_csv, name='export_csv'),
    path('api/export/bulk/', simple_views.export_bulk_citations, name='export_bulk_citations'),
    path('api/export/collection/<uuid:collection_id>/', simple_views.export_collection, name='export_collection'),

    # Personal Library API endpoints
    path('api/library/papers/', simple_views.api_library_papers, name='api_library_papers'),
    path('api/library/collections/', simple_views.api_library_collections, name='api_library_collections'),
    path('api/library/collections/create/', simple_views.api_create_collection, name='api_create_collection'),
    path('api/library/papers/<uuid:paper_id>/update/', simple_views.api_update_library_paper, name='api_update_library_paper'),
    path('api/library/papers/<uuid:paper_id>/remove/', simple_views.api_remove_library_paper, name='api_remove_library_paper'),

    # Research Trend Analysis endpoints
    path('trends/', simple_views.research_trends, name='research_trends'),
    path('api/trends/papers/', simple_views.api_trending_papers, name='api_trending_papers'),
    path('api/trends/topics/', simple_views.api_trending_topics, name='api_trending_topics'),
    path('api/trends/authors/', simple_views.api_trending_authors, name='api_trending_authors'),
    path('api/trends/analytics/', simple_views.api_research_analytics, name='api_research_analytics'),

    # Collaborative Annotation System endpoints
    path('annotations/<uuid:paper_id>/', simple_views.paper_annotations, name='paper_annotations'),
    path('api/annotations/<uuid:paper_id>/', simple_views.api_paper_annotations, name='api_paper_annotations'),
    path('api/annotations/create/', simple_views.api_create_annotation, name='api_create_annotation'),
    path('api/annotations/<uuid:annotation_id>/update/', simple_views.api_update_annotation, name='api_update_annotation'),
    path('api/annotations/<uuid:annotation_id>/delete/', simple_views.api_delete_annotation, name='api_delete_annotation'),
    path('api/annotations/<uuid:annotation_id>/vote/', simple_views.api_vote_annotation, name='api_vote_annotation'),
    path('api/collaboration/groups/', simple_views.api_collaboration_groups, name='api_collaboration_groups'),

    # Paper Similarity Recommendations endpoints
    path('api/recommendations/paper/<uuid:paper_id>/', simple_views.paper_recommendations, name='paper_recommendations'),
    path('api/recommendations/user/', simple_views.user_recommendations, name='user_recommendations'),

    # BibTeX Enrichment
    path('bibtex/enrichment/', bibtex_views.bibtex_enrichment, name='bibtex_enrichment'),
    path('bibtex/upload/', bibtex_views.bibtex_upload, name='bibtex_upload'),
    path('bibtex/job/<uuid:job_id>/', bibtex_views.bibtex_job_detail, name='bibtex_job_detail'),
    # API endpoints
    path('api/bibtex/job/<uuid:job_id>/status/', bibtex_views.bibtex_job_status, name='bibtex_job_status'),
    path('api/bibtex/job/<uuid:job_id>/download/', bibtex_views.bibtex_download_enriched, name='bibtex_download_enriched'),
    path('api/bibtex/job/<uuid:job_id>/urls/', bibtex_views.bibtex_get_urls, name='bibtex_get_urls'),
    path('api/bibtex/job/<uuid:job_id>/diff/', bibtex_views.bibtex_job_diff, name='bibtex_job_diff'),
    path('api/bibtex/job/<uuid:job_id>/cancel/', bibtex_views.bibtex_cancel_job, name='bibtex_cancel_job'),
    path('api/bibtex/resource-status/', bibtex_views.bibtex_resource_status, name='bibtex_resource_status'),

    # Legacy mock endpoints
    path('api/mock/save-paper/', simple_views.mock_save_paper, name='mock_save_paper'),
    path('api/mock/get-citation/', simple_views.mock_get_citation, name='mock_get_citation'),

    # Repository Management API
    path('api/repository/', include(router.urls)),
    path('api/repository/sync/<uuid:sync_id>/status/', repository_views.sync_status, name='sync_status'),
    path('api/repository/stats/', repository_views.user_repository_stats, name='user_repository_stats'),

    # Legacy repository endpoints
    path('api/repositories/', repository_views.list_repositories, name='list_repositories'),
    path('api/repository-connections/create/', repository_views.create_repository_connection, name='create_repository_connection'),

    # Advanced features (for future implementation)
    path('advanced/dashboard/', views.search_dashboard, name='search_dashboard'),
    path('advanced/search/', views.advanced_search, name='advanced_search'),
    path('advanced/paper/<uuid:paper_id>/', views.paper_detail, name='paper_detail'),
    path('advanced/author/<uuid:author_id>/', views.author_profile, name='author_profile'),
    path('advanced/saved/', views.saved_searches, name='saved_searches'),
    path('advanced/trending/', views.trending_papers, name='trending_papers'),
]

# EOF
