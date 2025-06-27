from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Q, F, Count
from datetime import datetime, timedelta
import json

# Legacy functions for backwards compatibility
@api_view(['POST'])
def search_documents(request):
    """Legacy search endpoint - redirects to search_papers."""
    return search_papers(request)

@api_view(['POST'])
def analyze_document(request):
    """Analyze document content."""
    content = request.data.get('content', '')
    # TODO: Implement document analysis
    return Response({
        'keywords': ['research', 'science', 'analysis'],
        'topics': ['Scientific Research'],
        'summary': 'Document analysis placeholder'
    })

@api_view(['POST'])
def extract_keywords(request):
    """Extract keywords from text."""
    text = request.data.get('text', '')
    # TODO: Implement keyword extraction
    return Response({
        'keywords': ['keyword1', 'keyword2', 'keyword3']
    })

@api_view(['GET'])
def find_similar(request, doc_id):
    """Find similar documents."""
    # TODO: Implement similarity search
    return Response({
        'similar_documents': [
            {'id': 1, 'title': 'Similar Document 1', 'similarity': 0.95},
            {'id': 2, 'title': 'Similar Document 2', 'similarity': 0.87}
        ]
    })


class SearchPagination(PageNumberPagination):
    """Custom pagination for search results."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # Allow public search, but track authenticated users
def search_papers(request):
    """
    Main search API endpoint with pagination.
    Supports both GET and POST methods.
    
    Query parameters:
    - q: search query (required)
    - page: page number (default: 1)
    - page_size: results per page (default: 20, max: 100)
    - sort: relevance|date|citations (default: relevance)
    - filter_year: filter by publication year
    - filter_author: filter by author name
    - filter_journal: filter by journal
    - filter_type: article|preprint|thesis|book (comma-separated)
    """
    try:
        # Get search query
        if request.method == 'POST':
            query = request.data.get('q', '').strip()
        else:
            query = request.GET.get('q', '').strip()
        
        if not query:
            return Response(
                {'error': 'Search query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        
        # Get sort parameter
        sort = request.GET.get('sort', 'relevance')
        
        # Get filters
        filter_year = request.GET.get('filter_year')
        filter_author = request.GET.get('filter_author')
        filter_journal = request.GET.get('filter_journal')
        filter_type = request.GET.get('filter_type', '').split(',') if request.GET.get('filter_type') else []
        
        # Search results will be populated by actual research APIs only
        all_results = []
        
        # Apply filters
        if filter_year:
            all_results = [r for r in all_results if str(r['year']) == filter_year]
        if filter_author:
            all_results = [r for r in all_results if any(filter_author.lower() in a['name'].lower() for a in r['authors'])]
        if filter_journal:
            all_results = [r for r in all_results if filter_journal.lower() in r['journal'].lower()]
        if filter_type:
            all_results = [r for r in all_results if r['type'] in filter_type]
        
        # Apply sorting
        if sort == 'date':
            all_results.sort(key=lambda x: x['year'], reverse=True)
        elif sort == 'citations':
            all_results.sort(key=lambda x: x['citations'], reverse=True)
        # Default is relevance, already sorted
        
        # Paginate results
        paginator = Paginator(all_results, page_size)
        
        try:
            results_page = paginator.page(page)
        except PageNotAnInteger:
            results_page = paginator.page(1)
        except EmptyPage:
            results_page = paginator.page(paginator.num_pages)
        
        # Track search if user is authenticated
        if request.user.is_authenticated:
            # TODO: Implement search tracking
            pass
        
        return Response({
            'query': query,
            'total_results': paginator.count,
            'page': results_page.number,
            'total_pages': paginator.num_pages,
            'page_size': page_size,
            'results': list(results_page),
            'filters_applied': {
                'year': filter_year,
                'author': filter_author,
                'journal': filter_journal,
                'type': filter_type
            },
            'sort': sort,
            'search_time': 0.234  # Mock search time
        })
    
    except Exception as e:
        return Response(
            {'error': f'Search failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_paper_details(request, paper_id):
    """
    Get detailed information about a specific paper.
    
    Returns:
    - Full paper metadata
    - Abstract
    - References
    - Related papers
    - Download links
    """
    try:
        # Mock paper details (replace with actual database query)
        paper = {
            'id': paper_id,
            'title': f'Comprehensive Study on {paper_id}: A Deep Learning Approach',
            'authors': [
                {
                    'name': 'John Smith',
                    'id': 'author_1',
                    'affiliation': 'Stanford University',
                    'email': 'jsmith@stanford.edu',
                    'orcid': '0000-0001-2345-6789'
                },
                {
                    'name': 'Jane Doe',
                    'id': 'author_2',
                    'affiliation': 'MIT',
                    'email': 'jdoe@mit.edu'
                }
            ],
            'abstract': '''This paper presents a comprehensive study on deep learning approaches
            for scientific research. We introduce novel methods that significantly improve
            the state-of-the-art results. Our experiments demonstrate the effectiveness
            of the proposed approach across multiple datasets and benchmarks.''',
            'keywords': ['deep learning', 'machine learning', 'artificial intelligence', 'neural networks'],
            'year': 2024,
            'month': 'January',
            'journal': 'Nature Machine Intelligence',
            'volume': '6',
            'issue': '1',
            'pages': '123-145',
            'doi': f'10.1234/{paper_id}',
            'arxiv_id': '2024.1234',
            'pubmed_id': '12345678',
            'citations': 42,
            'references_count': 58,
            'pdf_url': f'/api/papers/{paper_id}/pdf',
            'supplementary_url': f'/api/papers/{paper_id}/supplementary',
            'code_url': 'https://github.com/example/paper-code',
            'dataset_url': 'https://example.com/dataset',
            'type': 'article',
            'license': 'CC BY 4.0',
            'categories': ['cs.LG', 'cs.AI'],
            'metrics': {
                'views': 1523,
                'downloads': 342,
                'shares': 89,
                'altmetric_score': 156
            },
            'versions': [
                {
                    'version': 'v1',
                    'date': '2024-01-01',
                    'changes': 'Initial submission'
                },
                {
                    'version': 'v2',
                    'date': '2024-01-15',
                    'changes': 'Fixed typos, added supplementary material'
                }
            ],
            'related_papers': [
                {
                    'id': 'related_1',
                    'title': 'Related Work on Deep Learning',
                    'year': 2023,
                    'similarity_score': 0.89
                },
                {
                    'id': 'related_2',
                    'title': 'Previous Approach to This Problem',
                    'year': 2022,
                    'similarity_score': 0.76
                }
            ]
        }
        
        # Track view if user is authenticated
        if request.user.is_authenticated:
            # TODO: Implement view tracking
            pass
        
        return Response(paper)
    
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve paper details: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_citations(request, paper_id):
    """
    Get citations for a specific paper.
    
    Query parameters:
    - page: page number (default: 1)
    - page_size: results per page (default: 20)
    - sort: date|citations (default: date)
    """
    try:
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        sort = request.GET.get('sort', 'date')
        
        # Mock citations (replace with actual data)
        all_citations = []
        for i in range(42):
            citation = {
                'id': f'citation_{i+1}',
                'citing_paper': {
                    'id': f'citing_paper_{i+1}',
                    'title': f'Paper citing {paper_id}: Study {i+1}',
                    'authors': [{'name': f'Citing Author {i+1}'}],
                    'year': 2024 - (i % 3),
                    'journal': 'Scientific Journal',
                    'doi': f'10.5678/citing.{i+1}'
                },
                'citation_context': f'As shown in [{paper_id}], the approach demonstrates...',
                'section': 'Related Work' if i % 2 == 0 else 'Methods',
                'sentiment': 'positive' if i % 3 != 0 else 'neutral'
            }
            all_citations.append(citation)
        
        # Sort citations
        if sort == 'date':
            all_citations.sort(key=lambda x: x['citing_paper']['year'], reverse=True)
        
        # Paginate
        paginator = Paginator(all_citations, page_size)
        citations_page = paginator.page(page)
        
        return Response({
            'paper_id': paper_id,
            'total_citations': paginator.count,
            'page': citations_page.number,
            'total_pages': paginator.num_pages,
            'citations': list(citations_page),
            'citation_metrics': {
                'h_index': 12,
                'i10_index': 8,
                'total_citations': 42,
                'citations_per_year': {
                    '2024': 15,
                    '2023': 18,
                    '2022': 9
                }
            }
        })
    
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve citations: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
    """
    Get AI-powered paper recommendations based on user interests.
    
    Request body:
    - based_on: 'papers'|'keywords'|'history' (required)
    - paper_ids: list of paper IDs (if based_on='papers')
    - keywords: list of keywords (if based_on='keywords')
    - limit: number of recommendations (default: 10)
    """
    try:
        based_on = request.data.get('based_on')
        limit = min(int(request.data.get('limit', 10)), 50)
        
        if not based_on:
            return Response(
                {'error': 'based_on parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recommendations = []
        
        if based_on == 'papers':
            paper_ids = request.data.get('paper_ids', [])
            if not paper_ids:
                return Response(
                    {'error': 'paper_ids are required when based_on=papers'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate recommendations based on papers
            for i in range(limit):
                rec = {
                    'id': f'rec_paper_{i+1}',
                    'title': f'Recommended: Advanced Study on Related Topic {i+1}',
                    'authors': [{'name': f'Rec Author {i+1}'}],
                    'year': 2024,
                    'relevance_score': 0.95 - (i * 0.02),
                    'reason': f'Similar methodology to paper {paper_ids[0]}' if i % 2 == 0 else f'Cites paper {paper_ids[0]}',
                    'abstract_snippet': 'This paper extends the work on...'
                }
                recommendations.append(rec)
        
        elif based_on == 'keywords':
            keywords = request.data.get('keywords', [])
            if not keywords:
                return Response(
                    {'error': 'keywords are required when based_on=keywords'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate recommendations based on keywords
            for i in range(limit):
                rec = {
                    'id': f'rec_keyword_{i+1}',
                    'title': f'Paper on {keywords[0]}: Recent Advances {i+1}',
                    'authors': [{'name': f'Keyword Author {i+1}'}],
                    'year': 2024 - (i % 2),
                    'relevance_score': 0.92 - (i * 0.02),
                    'reason': f'Matches keywords: {", ".join(keywords[:2])}',
                    'matched_keywords': keywords[:min(3, len(keywords))]
                }
                recommendations.append(rec)
        
        elif based_on == 'history':
            # Generate recommendations based on user history
            for i in range(limit):
                rec = {
                    'id': f'rec_history_{i+1}',
                    'title': f'Based on Your Reading History: Paper {i+1}',
                    'authors': [{'name': f'History Author {i+1}'}],
                    'year': 2024,
                    'relevance_score': 0.88 - (i * 0.02),
                    'reason': 'Similar to papers you\'ve read recently',
                    'based_on_papers': [f'history_paper_{j}' for j in range(1, 4)]
                }
                recommendations.append(rec)
        
        else:
            return Response(
                {'error': 'Invalid based_on value. Use: papers, keywords, or history'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'based_on': based_on,
            'recommendations': recommendations,
            'count': len(recommendations),
            'generated_at': timezone.now().isoformat()
        })
    
    except Exception as e:
        return Response(
            {'error': f'Failed to generate recommendations: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_click(request):
    """
    Track user clicks on search results for analytics and recommendations.
    
    Request body:
    - paper_id: ID of the clicked paper (required)
    - position: position in search results (required)
    - query: search query that led to this result
    - source: 'search'|'recommendations'|'citations' (default: 'search')
    """
    try:
        paper_id = request.data.get('paper_id')
        position = request.data.get('position')
        
        if not paper_id or position is None:
            return Response(
                {'error': 'paper_id and position are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Implement click tracking in database
        click_data = {
            'user_id': request.user.id,
            'paper_id': paper_id,
            'position': position,
            'query': request.data.get('query'),
            'source': request.data.get('source', 'search'),
            'timestamp': timezone.now().isoformat(),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': request.META.get('REMOTE_ADDR', '')
        }
        
        # Mock response
        return Response({
            'status': 'tracked',
            'click_id': f'click_{timezone.now().timestamp()}'
        })
    
    except Exception as e:
        return Response(
            {'error': f'Failed to track click: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def export_bibtex(request):
    """
    Export papers as BibTeX.
    
    For GET: export single paper
    Query parameters:
    - paper_id: ID of the paper to export
    
    For POST: export multiple papers
    Request body:
    - paper_ids: list of paper IDs to export
    - format: 'bibtex'|'ris'|'endnote' (default: 'bibtex')
    """
    try:
        if request.method == 'GET':
            paper_id = request.GET.get('paper_id')
            if not paper_id:
                return Response(
                    {'error': 'paper_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            paper_ids = [paper_id]
            export_format = 'bibtex'
        else:
            paper_ids = request.data.get('paper_ids', [])
            if not paper_ids:
                return Response(
                    {'error': 'paper_ids are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            export_format = request.data.get('format', 'bibtex')
        
        # Generate export data
        if export_format == 'bibtex':
            entries = []
            for pid in paper_ids:
                entry = f'''@article{{{pid},
  title = {{Comprehensive Study on {pid}: A Deep Learning Approach}},
  author = {{Smith, John and Doe, Jane}},
  journal = {{Nature Machine Intelligence}},
  year = {{2024}},
  volume = {{6}},
  number = {{1}},
  pages = {{123--145}},
  doi = {{10.1234/{pid}}}
}}'''
                entries.append(entry)
            
            content = '\n\n'.join(entries)
            content_type = 'text/plain'
            filename = 'papers.bib'
        
        elif export_format == 'ris':
            entries = []
            for pid in paper_ids:
                entry = f'''TY  - JOUR
AU  - Smith, John
AU  - Doe, Jane
TI  - Comprehensive Study on {pid}: A Deep Learning Approach
JO  - Nature Machine Intelligence
PY  - 2024
VL  - 6
IS  - 1
SP  - 123
EP  - 145
DO  - 10.1234/{pid}
ER  -'''
                entries.append(entry)
            
            content = '\n\n'.join(entries)
            content_type = 'text/plain'
            filename = 'papers.ris'
        
        else:
            return Response(
                {'error': f'Unsupported export format: {export_format}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Return as file download
        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    except Exception as e:
        return Response(
            {'error': f'Export failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_author_papers(request, author_id):
    """
    Get all papers by a specific author.
    
    Query parameters:
    - page: page number (default: 1)
    - page_size: results per page (default: 20)
    - sort: date|citations|title (default: date)
    - year_from: filter papers from year
    - year_to: filter papers until year
    """
    try:
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        sort = request.GET.get('sort', 'date')
        year_from = request.GET.get('year_from')
        year_to = request.GET.get('year_to')
        
        # Mock author info and papers
        author = {
            'id': author_id,
            'name': 'John Smith',
            'affiliation': 'Stanford University',
            'h_index': 25,
            'total_citations': 1842,
            'total_papers': 67,
            'orcid': '0000-0001-2345-6789',
            'interests': ['Machine Learning', 'Computer Vision', 'Deep Learning']
        }
        
        # Generate mock papers
        all_papers = []
        for i in range(67):
            paper = {
                'id': f'author_paper_{i+1}',
                'title': f'Paper {i+1} by {author["name"]}',
                'year': 2024 - (i % 10),
                'journal': 'Conference on Machine Learning' if i % 2 == 0 else 'Journal of AI Research',
                'citations': 100 - i,
                'co_authors': [
                    {'name': f'Co-author {j}', 'id': f'coauthor_{i}_{j}'}
                    for j in range(1, min(i % 4 + 2, 5))
                ],
                'doi': f'10.1234/author.{i+1}'
            }
            all_papers.append(paper)
        
        # Apply year filters
        if year_from:
            all_papers = [p for p in all_papers if p['year'] >= int(year_from)]
        if year_to:
            all_papers = [p for p in all_papers if p['year'] <= int(year_to)]
        
        # Sort papers
        if sort == 'date':
            all_papers.sort(key=lambda x: x['year'], reverse=True)
        elif sort == 'citations':
            all_papers.sort(key=lambda x: x['citations'], reverse=True)
        elif sort == 'title':
            all_papers.sort(key=lambda x: x['title'])
        
        # Paginate
        paginator = Paginator(all_papers, page_size)
        papers_page = paginator.page(page)
        
        return Response({
            'author': author,
            'total_papers': paginator.count,
            'page': papers_page.number,
            'total_pages': paginator.num_pages,
            'papers': list(papers_page),
            'filters_applied': {
                'year_from': year_from,
                'year_to': year_to
            }
        })
    
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve author papers: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_trending(request):
    """
    Get trending papers based on recent activity.
    
    Query parameters:
    - period: 'day'|'week'|'month'|'year' (default: 'week')
    - category: filter by category/field
    - limit: number of results (default: 20, max: 100)
    """
    try:
        period = request.GET.get('period', 'week')
        category = request.GET.get('category')
        limit = min(int(request.GET.get('limit', 20)), 100)
        
        # Calculate time range
        now = timezone.now()
        if period == 'day':
            since = now - timedelta(days=1)
        elif period == 'week':
            since = now - timedelta(weeks=1)
        elif period == 'month':
            since = now - timedelta(days=30)
        elif period == 'year':
            since = now - timedelta(days=365)
        else:
            return Response(
                {'error': 'Invalid period. Use: day, week, month, or year'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mock trending papers
        trending = []
        for i in range(limit):
            paper = {
                'id': f'trending_{i+1}',
                'title': f'Trending Paper {i+1}: Breakthrough in AI Research',
                'authors': [{'name': f'Trending Author {i+1}'}],
                'year': 2024,
                'trending_score': 100 - (i * 2),
                'metrics': {
                    'views_change': f'+{500 - i*10}%',
                    'citations_change': f'+{50 - i}',
                    'downloads_change': f'+{200 - i*5}%',
                    'social_mentions': 100 - i*2
                },
                'category': category if category else ['cs.LG', 'cs.AI', 'stat.ML'][i % 3],
                'abstract_snippet': 'This groundbreaking paper introduces...'
            }
            trending.append(paper)
        
        return Response({
            'period': period,
            'since': since.isoformat(),
            'category': category,
            'trending_papers': trending,
            'count': len(trending),
            'generated_at': now.isoformat()
        })
    
    except Exception as e:
        return Response(
            {'error': f'Failed to get trending papers: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_search_alert(request):
    """
    Save a search alert for the user.
    
    Request body:
    - query: search query to monitor (required)
    - name: name for the alert (required)
    - frequency: 'daily'|'weekly'|'monthly' (default: 'weekly')
    - filters: optional filters (year, author, journal, etc.)
    - email_notifications: boolean (default: True)
    """
    try:
        query = request.data.get('query', '').strip()
        name = request.data.get('name', '').strip()
        
        if not query or not name:
            return Response(
                {'error': 'query and name are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        frequency = request.data.get('frequency', 'weekly')
        if frequency not in ['daily', 'weekly', 'monthly']:
            return Response(
                {'error': 'Invalid frequency. Use: daily, weekly, or monthly'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Save alert to database
        alert = {
            'id': f'alert_{timezone.now().timestamp()}',
            'user_id': request.user.id,
            'name': name,
            'query': query,
            'frequency': frequency,
            'filters': request.data.get('filters', {}),
            'email_notifications': request.data.get('email_notifications', True),
            'created_at': timezone.now().isoformat(),
            'last_run': None,
            'next_run': (timezone.now() + timedelta(days=1 if frequency == 'daily' else 7)).isoformat(),
            'is_active': True
        }
        
        return Response({
            'alert': alert,
            'message': 'Search alert created successfully'
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {'error': f'Failed to create search alert: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_search_suggestions(request):
    """
    Get autocomplete suggestions for search queries.
    
    Query parameters:
    - q: partial query string (required, min 2 characters)
    - type: 'all'|'authors'|'keywords'|'journals' (default: 'all')
    - limit: number of suggestions (default: 10, max: 20)
    """
    try:
        query = request.GET.get('q', '').strip()
        if len(query) < 2:
            return Response(
                {'error': 'Query must be at least 2 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        suggestion_type = request.GET.get('type', 'all')
        limit = min(int(request.GET.get('limit', 10)), 20)
        
        suggestions = {
            'queries': [],
            'authors': [],
            'keywords': [],
            'journals': []
        }
        
        # Mock suggestions based on query
        if suggestion_type in ['all', 'queries']:
            suggestions['queries'] = [
                {
                    'text': f'{query} machine learning',
                    'count': 1234,
                    'type': 'query'
                },
                {
                    'text': f'{query} deep learning applications',
                    'count': 987,
                    'type': 'query'
                },
                {
                    'text': f'{query} neural networks',
                    'count': 654,
                    'type': 'query'
                }
            ][:limit]
        
        if suggestion_type in ['all', 'authors']:
            suggestions['authors'] = [
                {
                    'name': f'{query.title()} Smith',
                    'id': 'author_1',
                    'papers_count': 45,
                    'affiliation': 'MIT',
                    'type': 'author'
                },
                {
                    'name': f'{query.title()} Johnson',
                    'id': 'author_2',
                    'papers_count': 32,
                    'affiliation': 'Stanford',
                    'type': 'author'
                }
            ][:limit]
        
        if suggestion_type in ['all', 'keywords']:
            suggestions['keywords'] = [
                {
                    'keyword': f'{query} learning',
                    'count': 567,
                    'type': 'keyword'
                },
                {
                    'keyword': f'{query} analysis',
                    'count': 432,
                    'type': 'keyword'
                },
                {
                    'keyword': f'{query} optimization',
                    'count': 321,
                    'type': 'keyword'
                }
            ][:limit]
        
        if suggestion_type in ['all', 'journals']:
            suggestions['journals'] = [
                {
                    'name': f'Journal of {query.title()} Research',
                    'abbreviation': f'J{query[:3].upper()}R',
                    'papers_count': 234,
                    'type': 'journal'
                },
                {
                    'name': f'International {query.title()} Review',
                    'abbreviation': f'I{query[:3].upper()}R',
                    'papers_count': 178,
                    'type': 'journal'
                }
            ][:limit]
        
        # Flatten suggestions if type is 'all'
        if suggestion_type == 'all':
            all_suggestions = []
            for category, items in suggestions.items():
                all_suggestions.extend(items)
            # Sort by relevance/count and limit
            all_suggestions = sorted(
                all_suggestions,
                key=lambda x: x.get('count', x.get('papers_count', 0)),
                reverse=True
            )[:limit]
            
            return Response({
                'query': query,
                'suggestions': all_suggestions,
                'count': len(all_suggestions)
            })
        else:
            return Response({
                'query': query,
                'type': suggestion_type,
                'suggestions': suggestions.get(suggestion_type + 's', []),
                'count': len(suggestions.get(suggestion_type + 's', []))
            })
    
    except Exception as e:
        return Response(
            {'error': f'Failed to get suggestions: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )