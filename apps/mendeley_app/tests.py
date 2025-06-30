from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

from .models import (
    MendeleyOAuth2Token, MendeleyProfile, MendeleyDocument, 
    MendeleyGroup, MendeleyFolder, MendeleySyncLog
)
from .services import (
    MendeleyAuthService, MendeleyAPIService, MendeleySyncService,
    MendeleyIntegrationService, MendeleyAPIError
)


class MendeleyModelsTest(TestCase):
    """Test Mendeley models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_mendeley_oauth_token_creation(self):
        """Test MendeleyOAuth2Token model creation"""
        token = MendeleyOAuth2Token.objects.create(
            user=self.user,
            access_token='test_access_token',
            refresh_token='test_refresh_token',
            token_type='bearer',
            scope='all',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        self.assertEqual(str(token), f"Mendeley Token for {self.user.username}")
        self.assertFalse(token.is_expired())
        self.assertTrue(token.is_expiring_soon(hours=2))
        
    def test_mendeley_profile_creation(self):
        """Test MendeleyProfile model creation"""
        profile = MendeleyProfile.objects.create(
            user=self.user,
            mendeley_id='test_mendeley_id',
            first_name='Test',
            last_name='User',
            email='test@example.com'
        )
        
        self.assertEqual(profile.get_display_name(), 'Test User')
        self.assertTrue(profile.needs_sync())
        self.assertEqual(profile.get_document_count(), 0)
        
    def test_mendeley_document_creation(self):
        """Test MendeleyDocument model creation"""
        profile = MendeleyProfile.objects.create(
            user=self.user,
            mendeley_id='test_mendeley_id'
        )
        
        document = MendeleyDocument.objects.create(
            profile=profile,
            mendeley_id='test_doc_id',
            title='Test Document',
            document_type='journal',
            year=2023,
            authors=[
                {'first_name': 'John', 'last_name': 'Doe'},
                {'first_name': 'Jane', 'last_name': 'Smith'}
            ]
        )
        
        self.assertEqual(document.get_authors_display(), 'John Doe, Jane Smith')
        self.assertTrue(document.can_import_to_scholar())
        self.assertEqual(document.get_publication_date(), '2023')


class MendeleyServicesTest(TestCase):
    """Test Mendeley services"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    @patch('apps.mendeley_app.services.USE_ZOTERO_FALLBACK', False)
    @patch('apps.mendeley_app.services.requests.post')
    def test_mendeley_auth_service_token_exchange(self, mock_post):
        """Test token exchange in MendeleyAuthService"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'token_type': 'bearer',
            'expires_in': 3600,
            'scope': 'all'
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        token_data = MendeleyAuthService.exchange_code_for_token('test_code')
        
        self.assertEqual(token_data['access_token'], 'test_access_token')
        self.assertEqual(token_data['token_type'], 'bearer')
        
    def test_zotero_fallback_token_exchange(self):
        """Test token exchange with Zotero fallback"""
        # Test with default Zotero fallback (USE_ZOTERO_FALLBACK = True)
        token_data = MendeleyAuthService.exchange_code_for_token('test_api_key')
        
        self.assertEqual(token_data['access_token'], 'test_api_key')
        self.assertEqual(token_data['token_type'], 'api_key')
        self.assertEqual(token_data['scope'], 'all')
        
    def test_mendeley_api_service_initialization(self):
        """Test MendeleyAPIService initialization"""
        # Create token for user
        MendeleyOAuth2Token.objects.create(
            user=self.user,
            access_token='test_token',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        api_service = MendeleyAPIService(self.user)
        self.assertIsNotNone(api_service.token)
        
    def test_mendeley_sync_service_initialization(self):
        """Test MendeleySyncService initialization"""
        sync_service = MendeleySyncService(self.user)
        self.assertEqual(sync_service.user, self.user)


class MendeleyViewsTest(TestCase):
    """Test Mendeley views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_mendeley_dashboard_anonymous(self):
        """Test dashboard access for anonymous user"""
        response = self.client.get(reverse('mendeley_app:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
    def test_mendeley_dashboard_authenticated(self):
        """Test dashboard access for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('mendeley_app:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mendeley Integration')
        
    def test_documents_list_without_profile(self):
        """Test documents list without Mendeley profile"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('mendeley_app:documents'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mendeley profile not found')
        
    def test_documents_list_with_profile(self):
        """Test documents list with Mendeley profile"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create profile and documents
        profile = MendeleyProfile.objects.create(
            user=self.user,
            mendeley_id='test_id'
        )
        
        MendeleyDocument.objects.create(
            profile=profile,
            mendeley_id='doc1',
            title='Test Document 1',
            document_type='journal'
        )
        
        response = self.client.get(reverse('mendeley_app:documents'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Document 1')
        
    def test_api_profile_status_no_connection(self):
        """Test API profile status without connection"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('mendeley_app:api_profile_status'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertFalse(data['connected'])
        self.assertEqual(data['documents_count'], 0)


class MendeleyIntegrationTest(TestCase):
    """Test Mendeley integration with Scholar module"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.profile = MendeleyProfile.objects.create(
            user=self.user,
            mendeley_id='test_id'
        )
        
        self.document = MendeleyDocument.objects.create(
            profile=self.profile,
            mendeley_id='doc1',
            title='Test Paper',
            document_type='journal',
            year=2023,
            abstract='Test abstract',
            authors=[{'first_name': 'John', 'last_name': 'Doe'}]
        )
        
    def test_import_document_to_scholar(self):
        """Test importing document to Scholar module"""
        # Import actual models instead of mocking to avoid Django FK issues
        from apps.scholar_app.models import SearchIndex, Author
        
        result = MendeleyIntegrationService.import_document_to_scholar(self.document)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, SearchIndex)
        self.document.refresh_from_db()
        self.assertTrue(self.document.is_imported)
        self.assertEqual(self.document.scholar_paper, result)
        
    def test_bulk_import_documents(self):
        """Test bulk import of documents"""
        # Create multiple documents
        doc2 = MendeleyDocument.objects.create(
            profile=self.profile,
            mendeley_id='doc2',
            title='Test Paper 2',
            document_type='journal'
        )
        
        with patch.object(MendeleyIntegrationService, 'import_document_to_scholar') as mock_import:
            mock_import.return_value = MagicMock()
            
            imported_count = MendeleyIntegrationService.bulk_import_documents(
                self.user, 
                [str(self.document.id), str(doc2.id)]
            )
            
            self.assertEqual(imported_count, 2)
            self.assertEqual(mock_import.call_count, 2)


class MendeleySyncLogTest(TestCase):
    """Test MendeleySyncLog functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.profile = MendeleyProfile.objects.create(
            user=self.user,
            mendeley_id='test_id'
        )
        
    def test_sync_log_creation_and_completion(self):
        """Test sync log creation and completion"""
        log = MendeleySyncLog.objects.create(
            profile=self.profile,
            sync_type='documents',
            items_processed=10,
            items_created=8,
            items_updated=2
        )
        
        # Test success rate calculation
        self.assertEqual(log.get_success_rate(), 100.0)
        
        # Test completion
        log.mark_completed('success')
        self.assertEqual(log.status, 'success')
        self.assertIsNotNone(log.completed_at)
        self.assertIsNotNone(log.duration_seconds)
        
    def test_sync_log_error_handling(self):
        """Test sync log error handling"""
        log = MendeleySyncLog.objects.create(
            profile=self.profile,
            sync_type='profile'
        )
        
        log.add_error('Test error message', {'detail': 'error details'})
        
        self.assertEqual(log.status, 'failed')
        self.assertEqual(log.error_message, 'Test error message')
        self.assertEqual(log.error_details['detail'], 'error details')