from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Avg, F, Prefetch
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db import transaction
from django.core.cache import cache
from django.views.decorators.cache import cache_page
# from django.utils.cache import make_template_fragment_key  # Removed - not available in newer Django
import json
import csv
import io
import hashlib
from datetime import datetime, timedelta

from .models import (
    SearchIndex, Author, Journal, Topic, Citation,
    SearchQuery, SearchResult, SavedSearch, RecommendationLog,
    AuthorPaper, SearchFilter
)


def index(request):
    """Search app index view."""
    return render(request, 'scholar_app/index.html')


def features(request):
    """Search features view."""
    return render(request, 'scholar_app/features.html')


def pricing(request):
    """Search pricing view."""
    return render(request, 'scholar_app/pricing.html')


def search_dashboard(request):
    """Main search interface with basic and advanced search capabilities."""
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'simple')
    page = request.GET.get('page', 1)
    
    # Create cache key for search results
    cache_key = None
    if query:
        filters_str = '|'.join([f"{k}:{v}" for k, v in sorted(request.GET.items()) if k not in ['page', 'csrfmiddlewaretoken']])
        cache_key = f"scholar_search:{hashlib.md5(filters_str.encode()).hexdigest()}"
        
        # Try to get cached results
        cached_results = cache.get(cache_key)
        if cached_results and not request.user.is_authenticated:  # Only use cache for anonymous users
            results = cached_results
        else:
            results = SearchIndex.objects.filter(status='active')
    else:
        results = SearchIndex.objects.filter(status='active')
    
    search_query_obj = None
    
    if query and not (cache_key and cached_results):
        # Track the search query
        if request.user.is_authenticated:
            search_query_obj = SearchQuery.objects.create(
                user=request.user,
                query_text=query,
                search_type=search_type,
                filters=dict(request.GET.items()),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        # Perform search based on type
        if search_type == 'simple':
            # Use PostgreSQL full-text search
            search_vector = SearchVector('title', weight='A') + \
                           SearchVector('abstract', weight='B') + \
                           SearchVector('keywords', weight='C')
            search_query = SearchQuery(query)
            
            results = results.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query).order_by('-rank', '-publication_date')
        
        elif search_type == 'semantic':
            # Placeholder for semantic search - would integrate with AI/ML service
            results = results.filter(
                Q(title__icontains=query) | 
                Q(abstract__icontains=query) |
                Q(keywords__contains=[query])
            ).order_by('-relevance_score', '-publication_date')
        
        # Apply filters
        filters = _apply_search_filters(request, results)
        results = filters['queryset']
        
        # Update search query with result count
        if search_query_obj:
            search_query_obj.result_count = results.count()
            search_query_obj.save()
            
        # Cache search results for anonymous users (1 hour)
        if cache_key and not request.user.is_authenticated:
            cache.set(cache_key, results, 3600)
    
    # Get search suggestions
    suggestions = []
    if query and len(query) >= 3:
        suggestions = _get_search_suggestions(query)
    
    # Pagination with optimized queries
    optimized_results = results.select_related('journal').prefetch_related(
        'authors',
        'topics', 
        'citations_received__citing_paper__authors',
        Prefetch('authors', queryset=Author.objects.only('id', 'first_name', 'last_name', 'orcid'))
    ).only(
        'id', 'title', 'abstract', 'publication_date', 'citation_count', 'doi', 
        'is_open_access', 'view_count', 'external_url', 'pdf_url',
        'journal__id', 'journal__name', 'journal__impact_factor'
    )
    
    paginator = Paginator(optimized_results, 20)
    try:
        papers = paginator.page(page)
    except PageNotAnInteger:
        papers = paginator.page(1)
    except EmptyPage:
        papers = paginator.page(paginator.num_pages)
    
    # Track search results for logged-in users
    if search_query_obj and request.user.is_authenticated:
        _track_search_results(search_query_obj, papers.object_list)
    
    # Get trending topics with caching
    trending_topics = cache.get('scholar_trending_topics')
    if not trending_topics:
        trending_topics = list(Topic.objects.select_related().only(
            'id', 'name', 'paper_count', 'description'
        ).order_by('-paper_count')[:10])
        cache.set('scholar_trending_topics', trending_topics, 1800)  # 30 minutes
    
    context = {
        'query': query,
        'search_type': search_type,
        'papers': papers,
        'suggestions': suggestions,
        'trending_topics': trending_topics,
        'filters': filters.get('active_filters', {}) if 'filters' in locals() else {},
        'total_results': results.count() if query else 0,
    }
    
    return render(request, 'scholar_app/search_dashboard.html', context)


def advanced_search(request):
    """Advanced search with multiple filters and options."""
    if request.method == 'POST':
        # Build search query from advanced form
        query_parts = []
        
        # Title search
        if request.POST.get('title'):
            query_parts.append(f"title:{request.POST['title']}")
        
        # Author search
        if request.POST.get('author'):
            query_parts.append(f"author:{request.POST['author']}")
        
        # Abstract search
        if request.POST.get('abstract'):
            query_parts.append(f"abstract:{request.POST['abstract']}")
        
        # Keywords
        if request.POST.get('keywords'):
            query_parts.append(f"keywords:{request.POST['keywords']}")
        
        # Build URL parameters
        params = {
            'q': ' AND '.join(query_parts),
            'type': 'advanced',
        }
        
        # Add date filters
        if request.POST.get('date_from'):
            params['date_from'] = request.POST['date_from']
        if request.POST.get('date_to'):
            params['date_to'] = request.POST['date_to']
        
        # Add other filters
        if request.POST.getlist('document_types'):
            params['doc_types'] = ','.join(request.POST.getlist('document_types'))
        if request.POST.get('journal'):
            params['journal'] = request.POST['journal']
        if request.POST.get('min_citations'):
            params['min_citations'] = request.POST['min_citations']
        if request.POST.get('open_access'):
            params['open_access'] = '1'
        
        # Redirect to search dashboard with parameters
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return redirect(f'/search/dashboard/?{query_string}')
    
    # GET request - show advanced search form
    journals = Journal.objects.order_by('name')
    topics = Topic.objects.filter(parent=None).order_by('name')
    
    context = {
        'journals': journals,
        'topics': topics,
        'document_types': SearchIndex.DOCUMENT_TYPE_CHOICES,
    }
    
    return render(request, 'scholar_app/advanced_search.html', context)


def paper_detail(request, paper_id):
    """View individual paper details with citations and related papers."""
    paper = get_object_or_404(
        SearchIndex.objects.select_related('journal')
        .prefetch_related('authors', 'topics', 'citations_made', 'citations_received'),
        id=paper_id,
        status='active'
    )
    
    # Increment view count
    paper.view_count = F('view_count') + 1
    paper.save(update_fields=['view_count'])
    
    # Get citations
    citations_made = paper.citations_made.select_related('cited_paper').order_by('cited_paper__publication_date')
    citations_received = paper.citations_received.select_related('citing_paper').order_by('-citing_paper__publication_date')
    
    # Get similar papers using advanced similarity algorithm
    similar_papers_with_scores = _calculate_paper_similarity(paper, limit=8)
    related_papers = [sp[0] for sp in similar_papers_with_scores]  # Extract just the papers
    
    # Track view for recommendations
    if request.user.is_authenticated:
        RecommendationLog.objects.create(
            user=request.user,
            source_paper=paper,
            recommended_paper=paper,
            recommendation_type='similar',
            score=1.0,
            clicked=True
        )
    
    context = {
        'paper': paper,
        'citations_made': citations_made,
        'citations_received': citations_received,
        'related_papers': related_papers,
        'can_download': paper.pdf_url or paper.pdf_file,
    }
    
    return render(request, 'scholar_app/paper_detail.html', context)


def author_profile(request, author_id):
    """Author profile with publications and metrics."""
    # Try to get cached author data
    cache_key = f'author_profile_{author_id}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        author = cached_data['author']
        papers = cached_data['papers']
        total_citations = cached_data['total_citations']
        avg_citations = cached_data['avg_citations']
        co_authors = cached_data['co_authors']
    else:
        author = get_object_or_404(Author.objects.select_related().only(
            'id', 'first_name', 'last_name', 'email', 'orcid', 'affiliation', 'h_index'
        ), id=author_id)
    
        # Get all papers by this author with optimized queries
        papers = SearchIndex.objects.filter(
            authors=author,
            status='active'
        ).select_related('journal').prefetch_related(
            Prefetch('authors', queryset=Author.objects.only('id', 'first_name', 'last_name'))
        ).only(
            'id', 'title', 'abstract', 'publication_date', 'citation_count', 'doi',
            'journal__id', 'journal__name'
        ).order_by('-publication_date')
    
        # Calculate metrics
        total_citations = papers.aggregate(total=Count('citations_received'))['total'] or 0
        avg_citations = papers.aggregate(avg=Avg('citation_count'))['avg'] or 0
        
        # Get co-authors with optimized query
        co_authors = Author.objects.filter(
            authorpaper__paper__in=papers
        ).exclude(id=author.id).annotate(
            collaboration_count=Count('authorpaper')
        ).only(
            'id', 'first_name', 'last_name', 'affiliation'
        ).order_by('-collaboration_count')[:20]
        
        # Cache author data for 1 hour
        cache_data = {
            'author': author,
            'papers': list(papers),
            'total_citations': total_citations,
            'avg_citations': avg_citations,
            'co_authors': list(co_authors)
        }
        cache.set(cache_key, cache_data, 3600)
    
    # Get publication timeline
    publication_years = papers.dates('publication_date', 'year', order='DESC')
    
    # Pagination
    paginator = Paginator(papers, 20)
    page = request.GET.get('page', 1)
    
    try:
        papers_page = paginator.page(page)
    except PageNotAnInteger:
        papers_page = paginator.page(1)
    except EmptyPage:
        papers_page = paginator.page(paginator.num_pages)
    
    context = {
        'author': author,
        'papers': papers_page,
        'total_papers': papers.count(),
        'total_citations': total_citations,
        'avg_citations': round(avg_citations, 2),
        'co_authors': co_authors,
        'publication_years': publication_years,
    }
    
    return render(request, 'scholar_app/author_profile.html', context)


def citation_network(request, paper_id):
    """Visualize citation relationships for a paper."""
    paper = get_object_or_404(SearchIndex, id=paper_id, status='active')
    
    # Get citation network data
    network_data = _build_citation_network(paper, depth=2)
    
    context = {
        'paper': paper,
        'network_data': json.dumps(network_data),
        'total_nodes': len(network_data['nodes']),
        'total_edges': len(network_data['edges']),
    }
    
    return render(request, 'scholar_app/citation_network.html', context)


@login_required
def saved_searches(request):
    """Manage user's saved searches."""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            # Create new saved search
            SavedSearch.objects.create(
                user=request.user,
                name=request.POST['name'],
                query_text=request.POST['query'],
                search_type=request.POST.get('search_type', 'simple'),
                filters=json.loads(request.POST.get('filters', '{}')),
                email_alerts=request.POST.get('email_alerts') == 'on',
                alert_frequency=request.POST.get('alert_frequency', 'never')
            )
            messages.success(request, 'Search saved successfully!')
            
        elif action == 'delete':
            # Delete saved search
            search_id = request.POST.get('search_id')
            SavedSearch.objects.filter(id=search_id, user=request.user).delete()
            messages.success(request, 'Saved search deleted.')
            
        elif action == 'update':
            # Update saved search
            search_id = request.POST.get('search_id')
            saved_search = get_object_or_404(SavedSearch, id=search_id, user=request.user)
            saved_search.email_alerts = request.POST.get('email_alerts') == 'on'
            saved_search.alert_frequency = request.POST.get('alert_frequency', 'never')
            saved_search.save()
            messages.success(request, 'Saved search updated.')
        
        return redirect('search:saved_searches')
    
    # GET request - show saved searches
    searches = SavedSearch.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'saved_searches': searches,
    }
    
    return render(request, 'scholar_app/saved_searches.html', context)


@login_required
def search_history(request):
    """View user's search history."""
    # Get date range from request
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Base queryset
    queries = SearchQuery.objects.filter(user=request.user)
    
    # Apply date filters
    if date_from:
        queries = queries.filter(created_at__gte=date_from)
    if date_to:
        queries = queries.filter(created_at__lte=date_to)
    
    # Order and paginate
    queries = queries.order_by('-created_at')
    
    paginator = Paginator(queries, 50)
    page = request.GET.get('page', 1)
    
    try:
        search_queries = paginator.page(page)
    except PageNotAnInteger:
        search_queries = paginator.page(1)
    except EmptyPage:
        search_queries = paginator.page(paginator.num_pages)
    
    # Get search statistics
    stats = {
        'total_searches': queries.count(),
        'unique_queries': queries.values('query_text').distinct().count(),
        'avg_results': queries.aggregate(avg=Avg('result_count'))['avg'] or 0,
    }
    
    context = {
        'search_queries': search_queries,
        'stats': stats,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'scholar_app/search_history.html', context)


@login_required
def recommendations(request):
    """AI-powered paper recommendations based on user activity."""
    recommendation_type = request.GET.get('type', 'all')
    
    # Get user's recent interactions
    recent_views = RecommendationLog.objects.filter(
        user=request.user,
        clicked=True
    ).order_by('-created_at')[:100]
    
    # Get recommendations based on type
    if recommendation_type == 'similar':
        recommendations = _get_similar_papers_recommendations(request.user, recent_views)
    elif recommendation_type == 'author_based':
        recommendations = _get_author_based_recommendations(request.user, recent_views)
    elif recommendation_type == 'citation_based':
        recommendations = _get_citation_based_recommendations(request.user, recent_views)
    elif recommendation_type == 'trending':
        recommendations = _get_trending_recommendations(request.user)
    else:
        # Combine all recommendation types
        recommendations = _get_mixed_recommendations(request.user, recent_views)
    
    # Track recommendations shown
    for rec in recommendations:
        RecommendationLog.objects.create(
            user=request.user,
            recommended_paper=rec['paper'],
            recommendation_type=rec['type'],
            score=rec['score'],
            reason=rec['reason']
        )
    
    context = {
        'recommendations': recommendations,
        'recommendation_type': recommendation_type,
    }
    
    return render(request, 'scholar_app/recommendations.html', context)


@login_required
def export_results(request):
    """Export search results in various formats."""
    if request.method == 'POST':
        export_format = request.POST.get('format', 'csv')
        paper_ids = request.POST.getlist('paper_ids')
        
        if not paper_ids:
            messages.error(request, 'Please select papers to export.')
            return redirect(request.META.get('HTTP_REFERER', '/search/'))
        
        papers = SearchIndex.objects.filter(id__in=paper_ids).select_related('journal').prefetch_related('authors')
        
        if export_format == 'csv':
            return _export_as_csv(papers)
        elif export_format == 'bibtex':
            return _export_as_bibtex(papers)
        elif export_format == 'ris':
            return _export_as_ris(papers)
        elif export_format == 'json':
            return _export_as_json(papers)
        else:
            messages.error(request, 'Invalid export format.')
            return redirect(request.META.get('HTTP_REFERER', '/search/'))
    
    # GET request - show export options
    return render(request, 'scholar_app/export_options.html')


def trending_papers(request):
    """View trending research papers based on various metrics."""
    timeframe = request.GET.get('timeframe', 'week')
    metric = request.GET.get('metric', 'views')
    
    # Calculate date threshold
    if timeframe == 'day':
        date_threshold = timezone.now() - timedelta(days=1)
    elif timeframe == 'week':
        date_threshold = timezone.now() - timedelta(weeks=1)
    elif timeframe == 'month':
        date_threshold = timezone.now() - timedelta(days=30)
    else:
        date_threshold = timezone.now() - timedelta(days=365)
    
    # Get trending papers based on metric
    papers = SearchIndex.objects.filter(
        status='active',
        publication_date__gte=date_threshold
    )
    
    if metric == 'views':
        papers = papers.order_by('-view_count')
    elif metric == 'citations':
        papers = papers.order_by('-citation_count')
    elif metric == 'downloads':
        papers = papers.order_by('-download_count')
    else:  # combined
        papers = papers.extra(
            select={'trending_score': 'view_count * 0.3 + citation_count * 0.5 + download_count * 0.2'}
        ).order_by('-trending_score')
    
    # Get top 50 papers
    papers = papers.select_related('journal').prefetch_related('authors', 'topics')[:50]
    
    # Get trending topics
    trending_topics = Topic.objects.filter(
        searchindex__publication_date__gte=date_threshold
    ).annotate(
        recent_papers=Count('searchindex')
    ).order_by('-recent_papers')[:20]
    
    context = {
        'papers': papers,
        'trending_topics': trending_topics,
        'timeframe': timeframe,
        'metric': metric,
    }
    
    return render(request, 'scholar_app/trending_papers.html', context)


# Helper functions

def _apply_search_filters(request, queryset):
    """Apply search filters from request parameters."""
    active_filters = {}
    
    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        queryset = queryset.filter(publication_date__gte=date_from)
        active_filters['date_from'] = date_from
    if date_to:
        queryset = queryset.filter(publication_date__lte=date_to)
        active_filters['date_to'] = date_to
    
    # Document type filter
    doc_types = request.GET.get('doc_types', '').split(',')
    if doc_types and doc_types[0]:
        queryset = queryset.filter(document_type__in=doc_types)
        active_filters['doc_types'] = doc_types
    
    # Journal filter
    journal = request.GET.get('journal')
    if journal:
        queryset = queryset.filter(journal__id=journal)
        active_filters['journal'] = journal
    
    # Citation count filter
    min_citations = request.GET.get('min_citations')
    if min_citations:
        queryset = queryset.filter(citation_count__gte=int(min_citations))
        active_filters['min_citations'] = min_citations
    
    # Open access filter
    if request.GET.get('open_access'):
        queryset = queryset.filter(is_open_access=True)
        active_filters['open_access'] = True
    
    return {
        'queryset': queryset,
        'active_filters': active_filters
    }


def _get_search_suggestions(query):
    """Get search suggestions based on query."""
    suggestions = []
    
    # Get topic suggestions
    topics = Topic.objects.filter(name__icontains=query)[:5]
    for topic in topics:
        suggestions.append({
            'type': 'topic',
            'text': topic.name,
            'count': topic.paper_count
        })
    
    # Get author suggestions
    authors = Author.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )[:5]
    for author in authors:
        suggestions.append({
            'type': 'author',
            'text': author.full_name,
            'count': author.searchindex_set.count()
        })
    
    return suggestions


def _track_search_results(search_query, papers):
    """Track search results for analytics."""
    results = []
    for rank, paper in enumerate(papers, 1):
        results.append(SearchResult(
            search_query=search_query,
            paper=paper,
            rank=rank,
            score=getattr(paper, 'rank', 0.0) if hasattr(paper, 'rank') else 0.0
        ))
    
    if results:
        SearchResult.objects.bulk_create(results)


def _build_citation_network(paper, depth=2):
    """Build citation network data for visualization."""
    nodes = []
    edges = []
    visited = set()
    
    def add_node(p, level):
        if p.id in visited or level > depth:
            return
        
        visited.add(p.id)
        nodes.append({
            'id': str(p.id),
            'title': p.title[:50] + '...' if len(p.title) > 50 else p.title,
            'year': p.publication_date.year if p.publication_date else 'Unknown',
            'citations': p.citation_count,
            'level': level
        })
        
        # Add citations
        for citation in p.citations_made.select_related('cited_paper')[:10]:
            edges.append({
                'source': str(p.id),
                'target': str(citation.cited_paper.id),
                'type': 'cites'
            })
            add_node(citation.cited_paper, level + 1)
        
        # Add references
        for citation in p.citations_received.select_related('citing_paper')[:10]:
            edges.append({
                'source': str(citation.citing_paper.id),
                'target': str(p.id),
                'type': 'cited_by'
            })
            add_node(citation.citing_paper, level + 1)
    
    add_node(paper, 0)
    
    return {'nodes': nodes, 'edges': edges}


def _get_similar_papers_recommendations(user, recent_views):
    """Get recommendations based on similar papers using multiple similarity methods."""
    recommendations = []
    viewed_papers = [rv.source_paper for rv in recent_views if rv.source_paper]
    
    if not viewed_papers:
        return recommendations
    
    # Get similarity scores for recent papers
    for paper in viewed_papers[:5]:
        similar_papers = _calculate_paper_similarity(paper, exclude_ids=[p.id for p in viewed_papers])
        
        for sim_paper, score, reason in similar_papers[:3]:
            recommendations.append({
                'paper': sim_paper,
                'type': 'similar',
                'score': score,
                'reason': reason
            })
            
            # Log recommendation for analytics
            RecommendationLog.objects.create(
                user=user,
                source_paper=paper,
                recommended_paper=sim_paper,
                recommendation_type='similar',
                score=score
            )
    
    return recommendations[:20]


def _calculate_paper_similarity(source_paper, exclude_ids=None, limit=10):
    """Calculate similarity between papers using multiple methods."""
    if exclude_ids is None:
        exclude_ids = []
    
    # Get candidate papers from the same domain/topics
    candidates = SearchIndex.objects.filter(
        status='active'
    ).exclude(
        id__in=exclude_ids + [source_paper.id]
    ).select_related('journal').prefetch_related('authors', 'topics')
    
    # Apply intelligent filtering to reduce computation
    candidate_pool = candidates.filter(
        Q(topics__in=source_paper.topics.all()) |
        Q(authors__in=source_paper.authors.all()) |
        Q(journal=source_paper.journal)
    ).distinct()
    
    # If pool is too small, expand to recent papers from related fields
    if candidate_pool.count() < 50:
        recent_papers = candidates.filter(
            publication_date__gte=timezone.now() - timedelta(days=365*2)
        )[:100]
        # Combine querysets using distinct() instead of union() to avoid ORDER BY issues
        candidate_pool = candidates.filter(
            Q(topics__in=source_paper.topics.all()) |
            Q(authors__in=source_paper.authors.all()) |
            Q(journal=source_paper.journal) |
            Q(publication_date__gte=timezone.now() - timedelta(days=365*2))
        ).distinct()
    
    similarity_scores = []
    
    for paper in candidate_pool[:200]:  # Limit for performance
        score, reason = _compute_similarity_score(source_paper, paper)
        if score > 0.1:  # Only include meaningful similarities
            similarity_scores.append((paper, score, reason))
    
    # Sort by similarity score and return top results
    similarity_scores.sort(key=lambda x: x[1], reverse=True)
    return similarity_scores[:limit]


def _compute_similarity_score(paper1, paper2):
    """Compute similarity score between two papers using multiple factors."""
    total_score = 0.0
    reasons = []
    
    # 1. Topic similarity (30% weight)
    common_topics = set(paper1.topics.all()) & set(paper2.topics.all())
    if common_topics:
        topic_score = len(common_topics) / max(paper1.topics.count(), paper2.topics.count(), 1)
        total_score += topic_score * 0.3
        reasons.append(f"{len(common_topics)} shared topics")
    
    # 2. Author overlap (25% weight)
    common_authors = set(paper1.authors.all()) & set(paper2.authors.all())
    if common_authors:
        author_score = len(common_authors) / max(paper1.authors.count(), paper2.authors.count(), 1)
        total_score += author_score * 0.25
        author_names = [f"{a.first_name} {a.last_name}" for a in common_authors]
        reasons.append(f"Common authors: {', '.join(author_names[:2])}")
    
    # 3. Journal similarity (15% weight)
    if paper1.journal and paper2.journal:
        if paper1.journal == paper2.journal:
            total_score += 0.15
            reasons.append(f"Same journal: {paper1.journal.name}")
        elif hasattr(paper1.journal, 'category') and hasattr(paper2.journal, 'category') and paper1.journal.category == paper2.journal.category:
            total_score += 0.05
            reasons.append("Related journal category")
    
    # 4. Citation relationship (20% weight)
    if _papers_have_citation_relationship(paper1, paper2):
        total_score += 0.20
        reasons.append("Citation relationship")
    
    # 5. Text similarity (basic keyword overlap) (10% weight)
    text_score = _calculate_text_similarity(paper1, paper2)
    total_score += text_score * 0.1
    if text_score > 0.3:
        reasons.append("Similar content")
    
    # 6. Temporal proximity bonus
    if paper1.publication_date and paper2.publication_date:
        date_diff = abs((paper1.publication_date - paper2.publication_date).days)
        if date_diff < 365:  # Same year
            total_score += 0.05
        elif date_diff < 365*2:  # Within 2 years
            total_score += 0.02
    
    # 7. Citation count similarity (papers with similar impact)
    cite_diff = abs((paper1.citation_count or 0) - (paper2.citation_count or 0))
    if cite_diff < 10:
        total_score += 0.05
    
    reason_text = "; ".join(reasons) if reasons else "General similarity"
    return min(total_score, 1.0), reason_text


def _papers_have_citation_relationship(paper1, paper2):
    """Check if papers have direct or indirect citation relationships."""
    # Direct citation
    if Citation.objects.filter(citing_paper=paper1, cited_paper=paper2).exists():
        return True
    if Citation.objects.filter(citing_paper=paper2, cited_paper=paper1).exists():
        return True
    
    # Shared citations (co-cited papers)
    paper1_citations = set(Citation.objects.filter(citing_paper=paper1).values_list('cited_paper_id', flat=True))
    paper2_citations = set(Citation.objects.filter(citing_paper=paper2).values_list('cited_paper_id', flat=True))
    
    if len(paper1_citations & paper2_citations) >= 2:  # At least 2 shared citations
        return True
    
    return False


def _calculate_text_similarity(paper1, paper2):
    """Calculate text similarity using keyword overlap."""
    try:
        # Try to use scikit-learn if available
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        # Combine title and abstract for similarity
        text1 = f"{paper1.title or ''} {paper1.abstract or ''}"
        text2 = f"{paper2.title or ''} {paper2.abstract or ''}"
        
        if not text1.strip() or not text2.strip():
            return 0.0
        
        # Use TF-IDF with cosine similarity
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2),
            min_df=1
        )
        
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(similarity)
        
    except ImportError:
        # Fallback to simple word overlap if scikit-learn not available
        return _simple_text_similarity(paper1, paper2)


def _simple_text_similarity(paper1, paper2):
    """Simple text similarity using word overlap (fallback method)."""
    import re
    
    def extract_keywords(text):
        if not text:
            return set()
        # Convert to lowercase, remove punctuation, split into words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        # Remove common stopwords
        stopwords = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
                    'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 
                    'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these', 
                    'those', 'was', 'were', 'been', 'have', 'has', 'had', 'will', 'would',
                    'could', 'should', 'may', 'might', 'can', 'must', 'shall'}
        return set(word for word in words if word not in stopwords and len(word) > 3)
    
    text1 = f"{paper1.title or ''} {paper1.abstract or ''}"
    text2 = f"{paper2.title or ''} {paper2.abstract or ''}"
    
    keywords1 = extract_keywords(text1)
    keywords2 = extract_keywords(text2)
    
    if not keywords1 or not keywords2:
        return 0.0
    
    # Jaccard similarity
    intersection = len(keywords1 & keywords2)
    union = len(keywords1 | keywords2)
    
    return intersection / union if union > 0 else 0.0


def _get_author_based_recommendations(user, recent_views):
    """Get recommendations based on authors."""
    recommendations = []
    viewed_papers = [rv.source_paper for rv in recent_views if rv.source_paper]
    
    # Get favorite authors
    authors = Author.objects.filter(
        searchindex__in=viewed_papers
    ).annotate(
        view_count=Count('searchindex')
    ).order_by('-view_count')[:10]
    
    for author in authors:
        papers = SearchIndex.objects.filter(
            authors=author
        ).exclude(
            id__in=[p.id for p in viewed_papers]
        ).order_by('-publication_date')[:2]
        
        for paper in papers:
            recommendations.append({
                'paper': paper,
                'type': 'author_based',
                'score': 0.7,
                'reason': f'By {author.full_name}'
            })
    
    return recommendations[:20]


def _get_citation_based_recommendations(user, recent_views):
    """Get recommendations based on citations."""
    recommendations = []
    viewed_papers = [rv.source_paper for rv in recent_views if rv.source_paper]
    
    for paper in viewed_papers[:3]:
        # Get highly cited papers that cite this paper
        citing_papers = SearchIndex.objects.filter(
            citations_made__cited_paper=paper,
            citation_count__gte=10
        ).exclude(
            id__in=[p.id for p in viewed_papers]
        ).order_by('-citation_count')[:3]
        
        for citing_paper in citing_papers:
            recommendations.append({
                'paper': citing_paper,
                'type': 'citation_based',
                'score': 0.75,
                'reason': f'Cites "{paper.title[:50]}..."'
            })
    
    return recommendations[:20]


def _get_trending_recommendations(user):
    """Get trending paper recommendations."""
    recommendations = []
    
    # Get trending papers from last week with optimized queries
    last_week = timezone.now() - timedelta(weeks=1)
    trending = SearchIndex.objects.filter(
        publication_date__gte=last_week,
        status='active'
    ).select_related('journal').prefetch_related(
        Prefetch('authors', queryset=Author.objects.only('id', 'first_name', 'last_name'))
    ).only(
        'id', 'title', 'abstract', 'publication_date', 'citation_count', 'view_count',
        'journal__id', 'journal__name'
    ).order_by('-view_count', '-citation_count')[:20]
    
    for paper in trending:
        recommendations.append({
            'paper': paper,
            'type': 'trending',
            'score': 0.6,
            'reason': 'Trending this week'
        })
    
    return recommendations


def _get_mixed_recommendations(user, recent_views):
    """Get mixed recommendations from all sources."""
    all_recommendations = []
    
    # Get recommendations from each type
    all_recommendations.extend(_get_similar_papers_recommendations(user, recent_views)[:5])
    all_recommendations.extend(_get_author_based_recommendations(user, recent_views)[:5])
    all_recommendations.extend(_get_citation_based_recommendations(user, recent_views)[:5])
    all_recommendations.extend(_get_trending_recommendations(user)[:5])
    
    # Sort by score and remove duplicates
    seen_papers = set()
    unique_recommendations = []
    
    for rec in sorted(all_recommendations, key=lambda x: x['score'], reverse=True):
        if rec['paper'].id not in seen_papers:
            seen_papers.add(rec['paper'].id)
            unique_recommendations.append(rec)
    
    return unique_recommendations[:20]


def _export_as_csv(papers):
    """Export papers as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Title', 'Authors', 'Journal', 'Year', 'DOI', 'Abstract', 'Citations'])
    
    # Write data
    for paper in papers:
        authors = ', '.join([author.full_name for author in paper.authors.all()])
        writer.writerow([
            paper.title,
            authors,
            paper.journal.name if paper.journal else '',
            paper.publication_date.year if paper.publication_date else '',
            paper.doi or '',
            paper.abstract[:500] + '...' if len(paper.abstract) > 500 else paper.abstract,
            paper.citation_count
        ])
    
    # Create response
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="scitex_papers_{datetime.now().strftime("%Y%m%d")}.csv"'
    return response


def _export_as_bibtex(papers):
    """Export papers as BibTeX."""
    output = io.StringIO()
    
    for paper in papers:
        # Determine entry type
        if paper.document_type == 'article':
            entry_type = '@article'
        elif paper.document_type == 'book':
            entry_type = '@book'
        elif paper.document_type == 'conference':
            entry_type = '@inproceedings'
        else:
            entry_type = '@misc'
        
        # Generate citation key
        first_author = paper.authors.first()
        year = paper.publication_date.year if paper.publication_date else 'YYYY'
        citation_key = f"{first_author.last_name if first_author else 'Unknown'}{year}"
        
        # Write BibTeX entry
        output.write(f"{entry_type}{{{citation_key},\n")
        output.write(f"  title = {{{paper.title}}},\n")
        
        # Authors
        authors = ' and '.join([author.full_name for author in paper.authors.all()])
        if authors:
            output.write(f"  author = {{{authors}}},\n")
        
        # Journal/Publisher
        if paper.journal:
            output.write(f"  journal = {{{paper.journal.name}}},\n")
        
        # Year
        if paper.publication_date:
            output.write(f"  year = {{{paper.publication_date.year}}},\n")
        
        # DOI
        if paper.doi:
            output.write(f"  doi = {{{paper.doi}}},\n")
        
        # URL
        if paper.external_url:
            output.write(f"  url = {{{paper.external_url}}},\n")
        
        output.write("}\n\n")
    
    # Create response
    response = HttpResponse(output.getvalue(), content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="scitex_papers_{datetime.now().strftime("%Y%m%d")}.bib"'
    return response


def _export_as_ris(papers):
    """Export papers as RIS format."""
    output = io.StringIO()
    
    type_mapping = {
        'article': 'JOUR',
        'book': 'BOOK',
        'chapter': 'CHAP',
        'conference': 'CONF',
        'thesis': 'THES',
        'report': 'RPRT',
        'dataset': 'DATA',
        'preprint': 'UNPB',
    }
    
    for paper in papers:
        # Type
        output.write(f"TY  - {type_mapping.get(paper.document_type, 'GEN')}\n")
        
        # Title
        output.write(f"TI  - {paper.title}\n")
        
        # Authors
        for author in paper.authors.all():
            output.write(f"AU  - {author.last_name}, {author.first_name}\n")
        
        # Journal
        if paper.journal:
            output.write(f"JO  - {paper.journal.name}\n")
        
        # Year
        if paper.publication_date:
            output.write(f"PY  - {paper.publication_date.year}\n")
        
        # DOI
        if paper.doi:
            output.write(f"DO  - {paper.doi}\n")
        
        # Abstract
        if paper.abstract:
            output.write(f"AB  - {paper.abstract}\n")
        
        # Keywords
        if paper.keywords:
            for keyword in paper.keywords:
                output.write(f"KW  - {keyword}\n")
        
        # URL
        if paper.external_url:
            output.write(f"UR  - {paper.external_url}\n")
        
        output.write("ER  - \n\n")
    
    # Create response
    response = HttpResponse(output.getvalue(), content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="scitex_papers_{datetime.now().strftime("%Y%m%d")}.ris"'
    return response


def _export_as_json(papers):
    """Export papers as JSON."""
    data = []
    
    for paper in papers:
        paper_data = {
            'id': str(paper.id),
            'title': paper.title,
            'abstract': paper.abstract,
            'authors': [
                {
                    'name': author.full_name,
                    'orcid': author.orcid,
                    'affiliation': author.affiliation
                }
                for author in paper.authors.all()
            ],
            'journal': paper.journal.name if paper.journal else None,
            'publication_date': paper.publication_date.isoformat() if paper.publication_date else None,
            'doi': paper.doi,
            'pmid': paper.pmid,
            'arxiv_id': paper.arxiv_id,
            'keywords': paper.keywords,
            'topics': [topic.name for topic in paper.topics.all()],
            'citation_count': paper.citation_count,
            'is_open_access': paper.is_open_access,
            'url': paper.external_url,
        }
        data.append(paper_data)
    
    # Create response
    response = HttpResponse(
        json.dumps(data, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="scitex_papers_{datetime.now().strftime("%Y%m%d")}.json"'
    return response


@require_http_methods(["POST"])
def autocomplete(request):
    """AJAX endpoint for search autocomplete."""
    query = request.POST.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    suggestions = _get_search_suggestions(query)
    
    return JsonResponse({'suggestions': suggestions})


@require_http_methods(["POST"])
@login_required
def track_click(request):
    """AJAX endpoint to track search result clicks."""
    result_id = request.POST.get('result_id')
    
    if result_id:
        SearchResult.objects.filter(
            id=result_id,
            search_query__user=request.user
        ).update(
            clicked=True,
            click_timestamp=timezone.now()
        )
    
    return JsonResponse({'status': 'ok'})


@require_http_methods(["POST"])
@login_required
def recommendation_feedback(request):
    """AJAX endpoint to track recommendation feedback."""
    recommendation_id = request.POST.get('recommendation_id')
    feedback = request.POST.get('feedback')
    feedback_text = request.POST.get('feedback_text', '')
    
    if recommendation_id and feedback:
        RecommendationLog.objects.filter(
            id=recommendation_id,
            user=request.user
        ).update(
            feedback=feedback,
            feedback_text=feedback_text,
            interacted_at=timezone.now()
        )
    
    return JsonResponse({'status': 'ok'})