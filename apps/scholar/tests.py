from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import SearchQuery, SearchResult, SearchIndex, Author, Journal


class SearchModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create paper index entries
        from datetime import date
        self.paper1 = SearchIndex.objects.create(
            title='Machine Learning in Science',
            abstract='This paper explores ML applications...',
            publication_date=date(2023, 1, 15),
            doi='10.1234/ml2023',
            relevance_score=1.0
        )
        
        self.paper2 = SearchIndex.objects.create(
            title='Deep Learning for Image Analysis',
            abstract='Deep learning techniques for medical imaging...',
            publication_date=date(2023, 3, 20),
            doi='10.1234/dl2023',
            relevance_score=1.0
        )
    
    def test_paper_index_creation(self):
        """Test paper index creation"""
        self.assertEqual(self.paper1.title, 'Machine Learning in Science')
        self.assertEqual(self.paper1.doi, '10.1234/ml2023')
        self.assertIsNotNone(self.paper1.created_at)
    
    def test_search_query_creation(self):
        """Test search query creation"""
        query = SearchQuery.objects.create(
            user=self.user,
            query_text='machine learning',
            filters={'year': 2023, 'field': 'computer science'}
        )
        
        self.assertEqual(query.user, self.user)
        self.assertEqual(query.query_text, 'machine learning')
        self.assertEqual(query.filters['year'], 2023)
    
    def test_search_result_creation(self):
        """Test search result creation"""
        query = SearchQuery.objects.create(
            user=self.user,
            query_text='machine learning'
        )
        
        result = SearchResult.objects.create(
            search_query=query,
            paper=self.paper1,
            score=0.95,
            rank=1
        )
        
        self.assertEqual(result.search_query, query)
        self.assertEqual(result.paper, self.paper1)
        self.assertEqual(result.score, 0.95)


class SearchViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test papers
        from datetime import date
        SearchIndex.objects.create(
            title='Quantum Computing Advances',
            abstract='Recent advances in quantum computing...',
            publication_date=date(2023, 5, 1),
            relevance_score=1.0
        )
        
        SearchIndex.objects.create(
            title='Neural Networks in Biology',
            abstract='Applications of neural networks in biological research...',
            publication_date=date(2023, 4, 15),
            relevance_score=1.0
        )
    
    def test_search_index_page(self):
        """Test search index page"""
        response = self.client.get(reverse('scholar:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SciTeX Scholar')
    
    def test_search_functionality(self):
        """Test search functionality"""
        response = self.client.get(
            reverse('scholar:simple_search'),
            {'q': 'quantum'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search Results')
        self.assertContains(response, 'quantum')
    
    def test_search_with_sources(self):
        """Test search with source selection"""
        response = self.client.get(
            reverse('scholar:simple_search'),
            {
                'q': 'neural',
                'sources': 'arxiv'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'neural')
    
    def test_empty_search(self):
        """Test empty search query"""
        response = self.client.get(
            reverse('scholar:simple_search'),
            {'q': ''}
        )
        self.assertEqual(response.status_code, 200)
        # Should show the home page without results
        self.assertNotContains(response, 'Search Results')