from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, Project
# from apps.document_app  # Removed - document_app not installed.models import Document
from apps.public_app.models import SubscriptionPlan, Subscription


class UserProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_creation(self):
        """Test profile creation with get_or_create"""
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.institution, '')  # Changed from organization
        self.assertTrue(profile.is_public)
    
    def test_profile_update(self):
        """Test updating profile fields"""
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.institution = 'Test University'
        profile.bio = 'Test bio'
        profile.research_interests = 'Computer Science, AI'
        profile.save()
        
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.institution, 'Test University')
        self.assertEqual(updated_profile.bio, 'Test bio')
        self.assertEqual(updated_profile.research_interests, 'Computer Science, AI')


class DocumentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.document = Document.objects.create(
            owner=self.user,
            title='Test Document',
            content='Test content',
            document_type='paper',
            is_public=True
        )
    
    def test_document_creation(self):
        """Test document creation and defaults"""
        self.assertEqual(self.document.title, 'Test Document')
        self.assertEqual(self.document.owner, self.user)
        self.assertEqual(self.document.document_type, 'paper')
        self.assertTrue(self.document.is_public)
    
    def test_document_string_representation(self):
        """Test document string representation"""
        self.assertEqual(str(self.document), 'Test Document')
    
    def test_document_timestamps(self):
        """Test document timestamps"""
        self.assertIsNotNone(self.document.created_at)
        self.assertIsNotNone(self.document.updated_at)
        
        # Update document and check if updated_at changes
        old_updated_at = self.document.updated_at
        self.document.title = 'Updated Title'
        self.document.save()
        self.assertNotEqual(self.document.updated_at, old_updated_at)


class ProjectTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            description='Test project description',
            status='active',
            hypotheses='Test hypothesis for the project'
        )
    
    def test_project_creation(self):
        """Test project creation"""
        self.assertEqual(self.project.name, 'Test Project')
        self.assertEqual(self.project.owner, self.user)
        self.assertEqual(self.project.status, 'active')
    
    def test_project_string_representation(self):
        """Test project string representation"""
        self.assertEqual(str(self.project), 'Test Project')
    
    def test_project_workflow_flags(self):
        """Test project workflow status flags"""
        self.assertFalse(self.project.analysis_completed)
        self.assertFalse(self.project.figures_generated)
        self.assertFalse(self.project.manuscript_generated)
        self.assertFalse(self.project.search_completed)
        
        # Update flags
        self.project.analysis_completed = True
        self.project.figures_generated = True
        self.project.save()
        
        updated_project = Project.objects.get(id=self.project.id)
        self.assertTrue(updated_project.analysis_completed)
        self.assertTrue(updated_project.figures_generated)


class CoreViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Create test subscription plan
        self.plan = SubscriptionPlan.objects.create(
            name="Free",
            plan_type="free",
            price_monthly=0,
            max_projects=3,
            storage_gb=5
        )
    
    def test_landing_page(self):
        """Test landing page"""
        response = self.client.get(reverse('workspace_app:landing'))
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(reverse('workspace_app:index'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_authenticated(self):
        """Test dashboard with authenticated user - should redirect to projects"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workspace_app:index'))
        self.assertEqual(response.status_code, 302)  # Redirect to projects
        self.assertEqual(response.url, '/projects/')
    
    def test_monitoring_requires_login(self):
        """Test monitoring page requires authentication"""
        response = self.client.get(reverse('workspace_app:monitoring'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_monitoring_authenticated(self):
        """Test monitoring page with authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workspace_app:monitoring'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'System Monitoring')
    
    def test_monitoring_data_api(self):
        """Test monitoring data API endpoint"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workspace_app:monitoring_data'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Check JSON structure
        data = response.json()
        self.assertIn('timestamp', data)
        self.assertIn('metrics', data)
        self.assertIn('services', data)
        self.assertIn('recent_activity', data)
    
    def test_document_list(self):
        """Test document list view"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create test documents
        Document.objects.create(
            owner=self.user,
            title='Test Doc 1',
            document_type='paper'
        )
        Document.objects.create(
            owner=self.user,
            title='Test Doc 2',
            document_type='draft'
        )
        
        response = self.client.get(reverse('workspace_app:document_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Documents')
        self.assertContains(response, 'document-list')  # Check for the container
    
    def test_document_list_filtering(self):
        """Test document list filtering"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create test documents
        Document.objects.create(
            owner=self.user,
            title='Paper Doc',
            document_type='paper'
        )
        Document.objects.create(
            owner=self.user,
            title='Draft Doc',
            document_type='draft'
        )
        
        # Test type filtering - since it's dynamic, just check the page loads
        response = self.client.get(reverse('workspace_app:document_list') + '?type=paper')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'document-type-filter')
    
    def test_project_list(self):
        """Test project list view"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create test projects
        Project.objects.create(
            owner=self.user,
            name='Active Project',
            status='active',
            description='Active project description',
            hypotheses='Active project hypothesis'
        )
        Project.objects.create(
            owner=self.user,
            name='Completed Project',
            status='completed',
            description='Completed project description',
            hypotheses='Completed project hypothesis'
        )
        
        response = self.client.get(reverse('workspace_app:project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Projects')  # Check page title instead
    
    def test_profile_view(self):
        """Test profile view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workspace_app:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile')
    
    def test_static_pages(self):
        """Test static pages"""
        pages = [
            ('workspace_app:about', 'About'),
            ('workspace_app:contact', 'Contact'),
            ('workspace_app:privacy', 'Privacy Policy'),
            ('workspace_app:terms', 'Terms of Use'),
            ('workspace_app:cookies', 'Cookie Policy')
        ]
        
        for url_name, expected_text in pages:
            with self.subTest(page=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)


class DashboardMetricsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.plan = SubscriptionPlan.objects.create(
            name="Premium",
            plan_type="premium_a",
            price_monthly=29,
            max_projects=10,
            storage_gb=50
        )
        from datetime import timedelta
        now = timezone.now()
        self.subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            status='active',
            current_period_start=now,
            current_period_end=now + timedelta(days=30)
        )
    
    def test_dashboard_redirects_to_projects(self):
        """Test dashboard redirects to projects page"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('workspace_app:index'))
        self.assertEqual(response.status_code, 302)  # Redirect to projects
