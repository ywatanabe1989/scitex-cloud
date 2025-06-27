from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.core_app.models import Document, Project, UserProfile
from apps.cloud_app.models import SubscriptionPlan, Subscription
import json


class JWTAuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_token_obtain_pair(self):
        """Test JWT token generation"""
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_token_refresh(self):
        """Test JWT token refresh"""
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post('/api/v1/auth/token/refresh/', {
            'refresh': str(refresh)
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = self.client.get('/api/v1/documents/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with valid token"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get('/api/v1/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DocumentAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Authenticate client
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create test documents
        self.doc1 = Document.objects.create(
            owner=self.user,
            title='Test Document 1',
            content='Content 1',
            document_type='manuscript'
        )
        self.doc2 = Document.objects.create(
            owner=self.user,
            title='Test Document 2',
            content='Content 2',
            document_type='draft'
        )
        self.other_doc = Document.objects.create(
            owner=self.other_user,
            title='Other User Document',
            content='Other content',
            document_type='manuscript'
        )
    
    def test_list_documents(self):
        """Test listing user's documents"""
        response = self.client.get('/api/v1/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if response is paginated or direct list
        if isinstance(response.data, dict) and 'results' in response.data:
            documents = response.data['results']
        else:
            documents = response.data
            
        self.assertGreaterEqual(len(documents), 2)  # At least our 2 test documents
        titles = [doc['title'] for doc in documents]
        self.assertIn('Test Document 1', titles)
        self.assertIn('Test Document 2', titles)
        self.assertNotIn('Other User Document', titles)
    
    def test_create_document(self):
        """Test creating a new document"""
        data = {
            'title': 'New Document',
            'content': 'New content',
            'document_type': 'manuscript',
            'is_public': True
        }
        response = self.client.post('/api/v1/documents/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Document')
        self.assertEqual(Document.objects.filter(owner=self.user).count(), 3)
    
    def test_get_document_detail(self):
        """Test retrieving document details"""
        response = self.client.get(f'/api/v1/documents/{self.doc1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Document 1')
    
    def test_update_document(self):
        """Test updating a document"""
        data = {
            'title': 'Updated Title',
            'content': self.doc1.content,
            'document_type': self.doc1.document_type
        }
        response = self.client.put(f'/api/v1/documents/{self.doc1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')
    
    def test_delete_document(self):
        """Test deleting a document"""
        response = self.client.delete(f'/api/v1/documents/{self.doc1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Document.objects.filter(id=self.doc1.id).exists())
    
    def test_cannot_access_other_users_document(self):
        """Test that users cannot access other users' documents"""
        response = self.client.get(f'/api/v1/documents/{self.other_doc.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProjectAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Authenticate client
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create test project
        self.project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            description='Test description',
            hypotheses='Test hypotheses',
            status='active'
        )
    
    def test_list_projects(self):
        """Test listing user's projects"""
        response = self.client.get('/api/v1/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if response is paginated or direct list
        if isinstance(response.data, dict) and 'results' in response.data:
            projects = response.data['results']
        else:
            projects = response.data
            
        self.assertGreaterEqual(len(projects), 1)  # At least our test project
        project_names = [proj['name'] for proj in projects]
        self.assertIn('Test Project', project_names)
    
    def test_create_project(self):
        """Test creating a new project"""
        data = {
            'name': 'New Project',
            'description': 'New project description',
            'hypotheses': 'Test hypotheses',
            'status': 'planning'
        }
        response = self.client.post('/api/v1/projects/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Project')
        self.assertEqual(Project.objects.filter(owner=self.user).count(), 2)
    
    def test_update_project_status(self):
        """Test updating project status"""
        data = {
            'name': self.project.name,
            'description': self.project.description,
            'hypotheses': self.project.hypotheses,
            'status': 'completed'
        }
        response = self.client.put(f'/api/v1/projects/{self.project.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')


class UserStatsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Get or create user profile (signal may have already created it)
        self.profile, created = UserProfile.objects.get_or_create(user=self.user)
        
        # Authenticate client
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create subscription
        plan = SubscriptionPlan.objects.create(
            name="Premium",
            plan_type="premium_a",
            price_monthly=29,
            max_projects=10,
            storage_gb=50
        )
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        Subscription.objects.create(
            user=self.user,
            plan=plan,
            status='active',
            current_period_start=now,
            current_period_end=now + timedelta(days=30)
        )
        
        # Create test data
        for i in range(5):
            Document.objects.create(
                owner=self.user,
                title=f'Document {i}',
                is_public=(i % 2 == 0)
            )
        
        for i in range(3):
            Project.objects.create(
                owner=self.user,
                name=f'Project {i}',
                description=f'Description for Project {i}',
                hypotheses=f'Hypothesis for Project {i}',
                status='active' if i < 2 else 'completed'
            )
    
    def test_user_stats_endpoint(self):
        """Test user statistics endpoint"""
        response = self.client.get('/api/v1/profile/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        stats = response.data
        self.assertIn('total_documents', stats)
        self.assertIn('total_projects', stats)
        self.assertIn('documents_by_status', stats)
        self.assertIn('projects_by_status', stats)


class UserProfileAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Get or create user profile (signal may have already created it)
        self.profile, created = UserProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'bio': 'Test bio',
                'institution': 'Test University'
            }
        )
        
        # Authenticate client
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_get_profile(self):
        """Test getting user profile"""
        response = self.client.get('/api/v1/profile/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_update_profile(self):
        """Test updating user profile"""
        data = {
            'bio': 'Updated bio',
        }
        response = self.client.put('/api/v1/profile/me/', data, format='json')
        if response.status_code != status.HTTP_200_OK:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.bio, 'Updated bio')


class APIPermissionsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        # Create documents for user1
        self.doc = Document.objects.create(
            owner=self.user1,
            title='User1 Document',
            content='Content'
        )
        self.project = Project.objects.create(
            owner=self.user1,
            name='User1 Project'
        )
    
    def test_cannot_modify_others_resources(self):
        """Test that users cannot modify other users' resources"""
        # Authenticate as user2
        refresh = RefreshToken.for_user(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Try to update user1's document
        response = self.client.put(f'/api/v1/documents/{self.doc.id}/', {
            'title': 'Hacked Title'
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Try to delete user1's project
        response = self.client.delete(f'/api/v1/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)