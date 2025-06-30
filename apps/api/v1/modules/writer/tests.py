from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
import json

class WriterCollaborationTestCase(TestCase):
    """Test cases for Writer collaborative editing features"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', 
            email='test2@example.com',
            password='testpass123'
        )
        
        # Test document ID
        self.document_id = 'test_doc_123'
        
        # Clear cache
        cache.clear()
    
    def test_start_collaboration_session(self):
        """Test starting a collaborative editing session"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.post(f'/api/v1/writer/documents/{self.document_id}/start_collaboration/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['session_id'], self.document_id)
        self.assertIn('collaboration_url', data)
        self.assertEqual(len(data['active_users']), 1)
        self.assertEqual(data['active_users'][0]['username'], 'testuser1')
    
    def test_multiple_users_collaboration(self):
        """Test multiple users joining collaboration session"""
        # User 1 starts collaboration
        self.client.force_authenticate(user=self.user1)
        response1 = self.client.post(f'/api/v1/writer/documents/{self.document_id}/start_collaboration/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # User 2 joins collaboration
        self.client.force_authenticate(user=self.user2)
        response2 = self.client.post(f'/api/v1/writer/documents/{self.document_id}/start_collaboration/')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        data = response2.json()
        self.assertEqual(len(data['active_users']), 2)
        usernames = [user['username'] for user in data['active_users']]
        self.assertIn('testuser1', usernames)
        self.assertIn('testuser2', usernames)
    
    def test_save_document_content(self):
        """Test saving document content with version control"""
        self.client.force_authenticate(user=self.user1)
        
        content = "\\documentclass{article}\\begin{document}Hello World\\end{document}"
        response = self.client.post(
            f'/api/v1/writer/documents/{self.document_id}/save_content/',
            data={
                'content': content,
                'comment': 'Initial version'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['version'], 1)
        self.assertIn('timestamp', data)
        self.assertEqual(data['message'], 'Document saved successfully')
    
    def test_get_document_content(self):
        """Test retrieving document content"""
        self.client.force_authenticate(user=self.user1)
        
        # First save some content
        content = "Test document content"
        self.client.post(
            f'/api/v1/writer/documents/{self.document_id}/save_content/',
            data={'content': content}
        )
        
        # Then retrieve it
        response = self.client.get(f'/api/v1/writer/documents/{self.document_id}/get_content/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['content'], content)
        self.assertEqual(data['document_id'], self.document_id)
        self.assertEqual(data['last_author'], 'testuser1')
        self.assertEqual(data['version'], 1)
    
    def test_collaboration_status(self):
        """Test getting collaboration status"""
        self.client.force_authenticate(user=self.user1)
        
        # Test when no collaboration session exists
        response = self.client.get(f'/api/v1/writer/documents/{self.document_id}/get_collaboration_status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertFalse(data['is_collaborative'])
        self.assertEqual(len(data['active_users']), 0)
        
        # Start collaboration session
        self.client.post(f'/api/v1/writer/documents/{self.document_id}/start_collaboration/')
        
        # Test with active collaboration
        response = self.client.get(f'/api/v1/writer/documents/{self.document_id}/get_collaboration_status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['is_collaborative'])
        self.assertEqual(len(data['active_users']), 1)
    
    def test_document_sharing(self):
        """Test document sharing functionality"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.post(
            f'/api/v1/writer/documents/{self.document_id}/share_document/',
            data={
                'permissions': 'write',
                'expires_in': 48
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('share_url', data)
        self.assertIn('share_token', data)
        self.assertEqual(data['permissions'], 'write')
        self.assertIn('expires_at', data)
    
    def test_document_export_latex(self):
        """Test LaTeX document export"""
        self.client.force_authenticate(user=self.user1)
        
        # Save some content first
        content = "\\documentclass{article}\\begin{document}Test\\end{document}"
        self.client.post(
            f'/api/v1/writer/documents/{self.document_id}/save_content/',
            data={'content': content}
        )
        
        # Export as LaTeX
        response = self.client.get(
            f'/api/v1/writer/documents/{self.document_id}/export_document/',
            {'format': 'latex'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['format'], 'latex')
        self.assertEqual(data['content'], content)
        self.assertIn('filename', data)
    
    def test_document_export_pdf(self):
        """Test PDF document export"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(
            f'/api/v1/writer/documents/{self.document_id}/export_document/',
            {'format': 'pdf'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['format'], 'pdf')
        self.assertIn('download_url', data)
        self.assertIn('filename', data)
    
    def test_document_export_invalid_format(self):
        """Test export with invalid format"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(
            f'/api/v1/writer/documents/{self.document_id}/export_document/',
            {'format': 'invalid'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('error', data)
    
    def test_version_numbering(self):
        """Test version numbering system"""
        self.client.force_authenticate(user=self.user1)
        
        # Save multiple versions
        for i in range(3):
            content = f"Version {i+1} content"
            response = self.client.post(
                f'/api/v1/writer/documents/{self.document_id}/save_content/',
                data={'content': content, 'comment': f'Version {i+1}'}
            )
            data = response.json()
            self.assertEqual(data['version'], i+1)
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access collaboration features"""
        # Don't authenticate
        
        response = self.client.post(f'/api/v1/writer/documents/{self.document_id}/start_collaboration/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.post(f'/api/v1/writer/documents/{self.document_id}/save_content/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.get(f'/api/v1/writer/documents/{self.document_id}/get_content/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def tearDown(self):
        """Clean up after tests"""
        cache.clear()


class WriterManuscriptTestCase(TestCase):
    """Test cases for basic Writer manuscript functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com', 
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_manuscripts(self):
        """Test getting user manuscripts"""
        response = self.client.get('/api/v1/writer/documents/manuscripts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('manuscripts', data)
        self.assertIn('count', data)
        self.assertEqual(data['count'], len(data['manuscripts']))
    
    def test_create_manuscript(self):
        """Test creating new manuscript"""
        response = self.client.post(
            '/api/v1/writer/documents/create_manuscript/',
            data={
                'title': 'Test Manuscript',
                'template': 'ieee'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        
        self.assertIn('manuscript', data)
        self.assertEqual(data['manuscript']['title'], 'Test Manuscript')
        self.assertEqual(data['manuscript']['template'], 'ieee')
        self.assertEqual(data['manuscript']['status'], 'draft')
    
    def test_get_templates(self):
        """Test getting available templates"""
        response = self.client.get('/api/v1/writer/documents/templates/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('templates', data)
        self.assertGreater(len(data['templates']), 0)
        
        # Check template structure
        template = data['templates'][0]
        self.assertIn('id', template)
        self.assertIn('name', template)
        self.assertIn('description', template)
        self.assertIn('category', template)
    
    def test_get_versions(self):
        """Test getting manuscript version history"""
        manuscript_id = 'test_manuscript_123'
        response = self.client.get(f'/api/v1/writer/documents/{manuscript_id}/versions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['manuscript_id'], manuscript_id)
        self.assertIn('versions', data)
        self.assertGreater(len(data['versions']), 0)
        
        # Check version structure
        version = data['versions'][0]
        self.assertIn('version', version)
        self.assertIn('timestamp', version)
        self.assertIn('author', version)
        self.assertIn('changes', version)