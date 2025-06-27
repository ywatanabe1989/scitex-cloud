from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import EngineConfiguration, EngineSession, EngineRequest


class EngineModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.config = EngineConfiguration.objects.create(
            user=self.user,
            name='Test Configuration'
        )
        self.session = EngineSession.objects.create(
            user=self.user,
            configuration=self.config,
            status='active'
        )
    
    def test_engine_configuration_creation(self):
        """Test engine configuration creation"""
        self.assertEqual(self.config.user, self.user)
        self.assertEqual(self.config.name, 'Test Configuration')
        self.assertTrue(self.config.enable_code_completion)
        self.assertIsNotNone(self.config.created_at)
    
    def test_engine_configuration_string_representation(self):
        """Test engine configuration string representation"""
        expected = f"{self.user.username} - {self.config.name}"
        self.assertEqual(str(self.config), expected)
    
    def test_engine_session_creation(self):
        """Test engine session creation"""
        self.assertEqual(self.session.user, self.user)
        self.assertEqual(self.session.configuration, self.config)
        self.assertEqual(self.session.status, 'active')
        self.assertIsNotNone(self.session.start_time)
    
    def test_engine_request_creation(self):
        """Test engine request creation"""
        request = EngineRequest.objects.create(
            session=self.session,
            request_type='code_complete',
            prompt='Complete this code',
            response='# Completed code here',
            response_time=0.5
        )
        
        self.assertEqual(request.session, self.session)
        self.assertEqual(request.request_type, 'code_complete')
        self.assertEqual(request.prompt, 'Complete this code')
        self.assertIsNotNone(request.created_at)


class EngineViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_engine_index_page(self):
        """Test engine index page"""
        response = self.client.get(reverse('engine:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SciTeX Engine')
    
    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(reverse('engine:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_authenticated(self):
        """Test dashboard with authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('engine:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_configuration_requires_login(self):
        """Test configuration page requires authentication"""
        response = self.client.get(reverse('engine:configuration'))
        self.assertEqual(response.status_code, 302)  # Redirect to login