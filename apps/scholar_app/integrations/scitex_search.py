#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-22 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/scholar_app/scholar/scitex_search.py
# ----------------------------------------

"""
SciTeX Search Integration for Django Scholar App.

This module integrates the SciTeX Scholar search pipelines with the Django
web application, providing both API endpoints and view functions for paper
metadata retrieval from multiple academic databases.
"""

import asyncio
import logging
from typing import Dict
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings

# Import SciTeX search pipelines
try:
    from scitex.scholar.pipelines.ScholarPipelineSearchSingle import (
        ScholarPipelineSearchSingle,
    )
    from scitex.scholar.pipelines.ScholarPipelineSearchParallel import (
        ScholarPipelineSearchParallel,
    )

    SCITEX_AVAILABLE = True
except ImportError as e:
    SCITEX_AVAILABLE = False
    SCITEX_IMPORT_ERROR = str(e)

from ..models import SearchIndex, SearchQuery

logger = logging.getLogger(__name__)


# ============================================================================
# Global Pipeline Instances (initialized once)
# ============================================================================

_single_pipeline = None
_parallel_pipeline = None


def get_single_pipeline():
    """Get or create the single (sequential) search pipeline instance."""
    global _single_pipeline

    if not SCITEX_AVAILABLE:
        logger.error(f"SciTeX not available: {SCITEX_IMPORT_ERROR}")
        return None

    if _single_pipeline is None:
        try:
            _single_pipeline = ScholarPipelineSearchSingle(
                use_cache=getattr(settings, "SCITEX_SCHOLAR_USE_CACHE", True),
            )
            logger.info("Initialized ScholarPipelineSearchSingle")
        except Exception as e:
            logger.error(f"Failed to initialize single pipeline: {e}")
            return None

    return _single_pipeline


def get_parallel_pipeline():
    """Get or create the parallel search pipeline instance."""
    global _parallel_pipeline

    if not SCITEX_AVAILABLE:
        logger.error(f"SciTeX not available: {SCITEX_IMPORT_ERROR}")
        return None

    if _parallel_pipeline is None:
        try:
            max_workers = getattr(settings, "SCITEX_SCHOLAR_MAX_WORKERS", 5)
            timeout = getattr(settings, "SCITEX_SCHOLAR_TIMEOUT_PER_ENGINE", 30)

            _parallel_pipeline = ScholarPipelineSearchParallel(
                max_workers=max_workers,
                timeout_per_engine=timeout,
                use_cache=getattr(settings, "SCITEX_SCHOLAR_USE_CACHE", True),
            )
            logger.info(
                f"Initialized ScholarPipelineSearchParallel (workers={max_workers})"
            )
        except Exception as e:
            logger.error(f"Failed to initialize parallel pipeline: {e}")
            return None

    return _parallel_pipeline


# ============================================================================
# Django-SciTeX Integration Functions
# ============================================================================


def django_to_scitex_filters(request) -> Dict:
    """
    Convert Django request parameters to SciTeX filter format.

    Args:
        request: Django HttpRequest object

    Returns:
        Dictionary of filters compatible with SciTeX pipelines
    """
    filters = {}

    # Year range
    year_start = request.GET.get("year_from") or request.GET.get("year_start")
    year_end = request.GET.get("year_to") or request.GET.get("year_end")

    if year_start:
        try:
            filters["year_start"] = int(year_start)
        except ValueError:
            pass

    if year_end:
        try:
            filters["year_end"] = int(year_end)
        except ValueError:
            pass

    # Open access
    open_access = request.GET.get("open_access")
    if open_access and open_access.lower() in ["true", "1", "yes"]:
        filters["open_access"] = True

    # Document type
    doc_type = request.GET.get("document_type") or request.GET.get("type")
    if doc_type:
        filters["document_type"] = doc_type

    # Author
    author = request.GET.get("author", "").strip()
    if author:
        filters["author"] = author

    # Journal
    journal = request.GET.get("journal", "").strip()
    if journal:
        filters["journal"] = journal

    # DOI
    doi = request.GET.get("doi", "").strip()
    if doi:
        filters["doi"] = doi

    # PMID
    pmid = request.GET.get("pmid", "").strip()
    if pmid:
        filters["pmid"] = pmid

    # Sorting
    sort_by = request.GET.get("sort_by", "").strip()
    if sort_by:
        filters["sort_by"] = sort_by

    sort_order = request.GET.get("sort_order", "desc").strip()
    if sort_order in ["asc", "desc"]:
        filters["sort_order"] = sort_order

    # Threshold filters
    min_year = request.GET.get("min_year", "").strip()
    if min_year:
        try:
            filters["min_year"] = int(min_year)
        except ValueError:
            pass

    max_year = request.GET.get("max_year", "").strip()
    if max_year:
        try:
            filters["max_year"] = int(max_year)
        except ValueError:
            pass

    min_citations = request.GET.get("min_citations", "").strip()
    if min_citations:
        try:
            filters["min_citations"] = int(min_citations)
        except ValueError:
            pass

    min_impact_factor = request.GET.get("min_impact_factor", "").strip()
    if min_impact_factor:
        try:
            filters["min_impact_factor"] = float(min_impact_factor)
        except ValueError:
            pass

    return filters


def scitex_to_django_paper(scitex_result: Dict, user=None) -> SearchIndex:
    """
    Convert SciTeX search result to Django SearchIndex model.

    Args:
        scitex_result: Result dictionary from SciTeX pipeline
        user: Optional Django user for tracking

    Returns:
        SearchIndex model instance (saved to database)
    """
    # Extract data from SciTeX result format
    title = scitex_result.get("title", "")
    doi = scitex_result.get("doi", "").strip() or None
    pmid = scitex_result.get("pmid", "").strip() or None
    arxiv_id = scitex_result.get("arxiv_id", "").strip() or None

    # Check if paper already exists (by DOI, PMID, or arXiv ID)
    existing_paper = None

    if doi:
        existing_paper = SearchIndex.objects.filter(doi=doi).first()

    if not existing_paper and pmid:
        existing_paper = SearchIndex.objects.filter(pmid=pmid).first()

    if not existing_paper and arxiv_id:
        existing_paper = SearchIndex.objects.filter(arxiv_id=arxiv_id).first()

    # If paper exists, update it; otherwise create new
    if existing_paper:
        paper = existing_paper
    else:
        paper = SearchIndex()

    # Update fields
    paper.title = title if title else "Untitled"
    paper.abstract = scitex_result.get("abstract", "")
    paper.doi = doi
    paper.pmid = pmid
    paper.arxiv_id = arxiv_id

    # Document type (required field)
    paper.document_type = scitex_result.get("document_type", "article")

    # Publication info
    year = scitex_result.get("year")
    if year:
        try:
            paper.publication_date = datetime(int(year), 1, 1).date()
        except (ValueError, TypeError):
            pass

    # Authors (store as comma-separated for now)
    authors = scitex_result.get("authors", [])
    if authors:
        # TODO: Create Author instances and link via AuthorPaper
        pass

    # Journal info - Create or get Journal instance
    journal_name = scitex_result.get("journal", "").strip()
    if journal_name:
        from ..models import Journal

        # Get or create journal by name
        journal, created = Journal.objects.get_or_create(
            name=journal_name,
            defaults={
                "impact_factor": scitex_result.get("impact_factor"),
                # Add other journal fields if available
            },
        )
        # Update impact factor if it's provided and different
        if scitex_result.get("impact_factor") is not None:
            if journal.impact_factor != scitex_result.get("impact_factor"):
                journal.impact_factor = scitex_result.get("impact_factor")
                journal.save()

        paper.journal = journal

    # Metrics
    paper.citation_count = scitex_result.get("citation_count", 0)
    paper.is_open_access = scitex_result.get("is_open_access", False)

    # URLs
    paper.pdf_url = scitex_result.get("pdf_url", "")
    paper.external_url = scitex_result.get("external_url", "")

    # Source tracking (required field)
    source_engines = scitex_result.get("source_engines", [])
    if source_engines:
        paper.source = source_engines[0]  # Use first engine as primary source
    else:
        paper.source = "scitex"  # Default source if none provided

    # Keywords
    keywords = scitex_result.get("keywords", [])
    if keywords:
        paper.keywords = ", ".join(keywords)

    # Set indexed timestamp
    paper.indexed_at = datetime.now()

    # Save to database
    paper.save()

    return paper


def track_search_query(
    request,
    query_text: str,
    search_type: str,
    result_count: int,
    execution_time: float,
    filters: Dict = None,
):
    """
    Track user search query in database for analytics.

    Args:
        request: Django HttpRequest
        query_text: The search query string
        search_type: Type of search performed
        result_count: Number of results returned
        execution_time: Time taken for search in seconds
        filters: Applied filters dictionary
    """
    if not request.user.is_authenticated:
        return

    try:
        SearchQuery.objects.create(
            user=request.user,
            query_text=query_text,
            search_type=search_type,
            filters=filters or {},
            result_count=result_count,
            execution_time=execution_time,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )
    except Exception as e:
        logger.warning(f"Failed to track search query: {e}")


# ============================================================================
# Django View Functions
# ============================================================================


@require_http_methods(["GET"])
def api_scitex_search(request):
    """
    API endpoint for SciTeX-powered paper search (parallel pipeline).

    Query Parameters:
        q: Search query string (required)
        search_fields: Comma-separated fields to search (title,abstract,keywords)
        year_start: Start year filter
        year_end: End year filter
        open_access: Filter for open access papers (true/false)
        author: Filter by author name
        journal: Filter by journal name
        max_results: Maximum number of results (default: 100)

    Returns:
        JSON response with search results and metadata
    """
    import time

    start_time = time.time()

    # Check if SciTeX is available
    if not SCITEX_AVAILABLE:
        return JsonResponse(
            {
                "error": "SciTeX search engine not available",
                "detail": SCITEX_IMPORT_ERROR,
                "results": [],
            },
            status=503,
        )

    # Get query parameter
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse(
            {"error": 'Query parameter "q" is required', "results": []}, status=400
        )

    # Get search fields
    search_fields_param = request.GET.get("search_fields", "title,abstract")
    search_fields = [f.strip() for f in search_fields_param.split(",")]

    # Get filters
    filters = django_to_scitex_filters(request)

    # Get max results
    try:
        max_results = int(request.GET.get("max_results", 100))
        max_results = min(max_results, 1000)  # Cap at 1000
    except ValueError:
        max_results = 100

    # Get pipeline
    pipeline = get_parallel_pipeline()
    if not pipeline:
        return JsonResponse(
            {"error": "Failed to initialize search pipeline", "results": []}, status=500
        )

    # Execute search
    try:
        logger.info(
            f"SciTeX search: query='{query[:50]}...', fields={search_fields}, filters={filters}"
        )

        # Run async search in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            scitex_result = loop.run_until_complete(
                pipeline.search_async(
                    query=query,
                    search_fields=search_fields,
                    filters=filters,
                    max_results=max_results,
                )
            )
        finally:
            loop.close()

        # Convert results to Django format
        django_results = []

        for scitex_paper in scitex_result.get("results", []):
            # Store in database
            try:
                django_paper = scitex_to_django_paper(
                    scitex_paper,
                    request.user if request.user.is_authenticated else None,
                )

                # Format for API response
                django_results.append(
                    {
                        "id": str(django_paper.id),
                        "title": scitex_paper.get("title", ""),
                        "authors": scitex_paper.get("authors", []),
                        "year": scitex_paper.get("year"),
                        "abstract": scitex_paper.get("abstract", ""),
                        "journal": scitex_paper.get("journal", ""),
                        "impact_factor": scitex_paper.get("impact_factor"),
                        "doi": scitex_paper.get("doi", ""),
                        "pmid": scitex_paper.get("pmid", ""),
                        "arxiv_id": scitex_paper.get("arxiv_id", ""),
                        "citation_count": scitex_paper.get("citation_count", 0),
                        "is_open_access": scitex_paper.get("is_open_access", False),
                        "pdf_url": scitex_paper.get("pdf_url", ""),
                        "external_url": scitex_paper.get("external_url", ""),
                        "source_engines": scitex_paper.get("source_engines", []),
                    }
                )
            except Exception as e:
                logger.error(f"Failed to convert SciTeX result to Django model: {e}")
                # Still include in results even if DB save fails
                django_results.append(
                    {
                        "title": scitex_paper.get("title", ""),
                        "authors": scitex_paper.get("authors", []),
                        "year": scitex_paper.get("year"),
                        "error": "Failed to save to database",
                    }
                )

        # Track search query
        execution_time = time.time() - start_time
        track_search_query(
            request,
            query_text=query,
            search_type="scitex_parallel",
            result_count=len(django_results),
            execution_time=execution_time,
            filters=filters,
        )

        # Return response
        response_data = {
            "query": query,
            "search_fields": search_fields,
            "filters": filters,
            "results": django_results,
            "metadata": {
                **scitex_result.get("metadata", {}),
                "search_time": execution_time,
                "django_stored": len(django_results),
            },
            "stats": pipeline.get_statistics(),
        }

        logger.info(
            f"SciTeX search completed: {len(django_results)} results in {execution_time:.2f}s"
        )

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"SciTeX search failed: {e}", exc_info=True)
        return JsonResponse(
            {"error": "Search failed", "detail": str(e), "results": []}, status=500
        )


@require_http_methods(["GET"])
def api_scitex_search_single(request):
    """
    API endpoint for SciTeX-powered paper search (single/sequential pipeline).

    Same parameters as api_scitex_search but uses sequential engine querying.
    Better for rate-limited scenarios or when you want predictable behavior.
    """
    import time

    start_time = time.time()

    if not SCITEX_AVAILABLE:
        return JsonResponse(
            {"error": "SciTeX search engine not available", "results": []}, status=503
        )

    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse(
            {"error": 'Query parameter "q" is required', "results": []}, status=400
        )

    # Get filters
    filters = django_to_scitex_filters(request)

    # Get max results
    try:
        max_results = int(request.GET.get("max_results", 100))
        max_results = min(max_results, 1000)  # Cap at 1000
    except ValueError:
        max_results = 100

    pipeline = get_single_pipeline()
    if not pipeline:
        return JsonResponse(
            {"error": "Failed to initialize search pipeline", "results": []}, status=500
        )

    try:
        logger.info(
            f"SciTeX single search: query='{query[:50]}...', filters={filters}, max_results={max_results}"
        )

        # Run async search
        # Note: ScholarPipelineSearchSingle does not accept search_fields parameter
        # It searches across all fields by default
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            scitex_result = loop.run_until_complete(
                pipeline.search_async(
                    query=query, filters=filters, max_results=max_results
                )
            )
        finally:
            loop.close()

        # Convert to Django format
        django_results = []
        for scitex_paper in scitex_result.get("results", []):
            try:
                django_paper = scitex_to_django_paper(
                    scitex_paper,
                    request.user if request.user.is_authenticated else None,
                )
                django_results.append(
                    {
                        "id": str(django_paper.id),
                        "title": scitex_paper.get("title", ""),
                        "authors": scitex_paper.get("authors", []),
                        "year": scitex_paper.get("year"),
                        "abstract": scitex_paper.get("abstract", ""),
                        "journal": scitex_paper.get("journal", ""),
                        "impact_factor": scitex_paper.get("impact_factor"),
                        "doi": scitex_paper.get("doi", ""),
                        "pmid": scitex_paper.get("pmid", ""),
                        "arxiv_id": scitex_paper.get("arxiv_id", ""),
                        "citation_count": scitex_paper.get("citation_count", 0),
                        "is_open_access": scitex_paper.get("is_open_access", False),
                        "pdf_url": scitex_paper.get("pdf_url", ""),
                        "external_url": scitex_paper.get("external_url", ""),
                        "source_engines": scitex_paper.get("source_engines", []),
                    }
                )
            except Exception as e:
                logger.error(f"Failed to process result: {e}")

        execution_time = time.time() - start_time

        # Track search query
        track_search_query(
            request,
            query_text=query,
            search_type="scitex_single",
            result_count=len(django_results),
            execution_time=execution_time,
            filters=filters,
        )

        logger.info(
            f"SciTeX single search completed: {len(django_results)} results in {execution_time:.2f}s"
        )

        return JsonResponse(
            {
                "query": query,
                "filters": filters,
                "results": django_results,
                "metadata": {
                    **scitex_result.get("metadata", {}),
                    "search_time": execution_time,
                    "django_stored": len(django_results),
                    "note": "Single mode searches across all fields by default",
                },
                "stats": pipeline.get_statistics(),
            }
        )

    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        return JsonResponse({"error": str(e), "results": []}, status=500)


@require_http_methods(["GET"])
def api_scitex_capabilities(request):
    """
    API endpoint to get search engine capabilities.

    Returns information about available engines and their supported features.
    """
    if not SCITEX_AVAILABLE:
        return JsonResponse({"available": False, "error": SCITEX_IMPORT_ERROR})

    pipeline = get_parallel_pipeline()
    if not pipeline:
        return JsonResponse(
            {"available": False, "error": "Failed to initialize pipeline"}
        )

    # Get capabilities for all engines
    capabilities = {}
    for engine_name in pipeline.engines:
        capabilities[engine_name] = pipeline.get_engine_capabilities(engine_name)

    return JsonResponse(
        {
            "available": True,
            "engines": capabilities,
            "statistics": pipeline.get_statistics(),
        }
    )


# EOF
