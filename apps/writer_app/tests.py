from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import DocumentTemplate, Manuscript, CompilationJob
import json


class DocModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.template = DocumentTemplate.objects.create(
            name='Research Article',
            template_type='article',
            latex_template='\\documentclass{article}\n\\begin{document}\n{content}\n\\end{document}',
            description='Standard research article template'
        )
        
        self.manuscript = Manuscript.objects.create(
            owner=self.user,
            title='Test Manuscript',
            slug='test-manuscript',
            content='\\section{Introduction}\nThis is a test.',
            abstract='Test abstract'
        )
    
    def test_document_template_creation(self):
        """Test document template creation"""
        self.assertEqual(self.template.name, 'Research Article')
        self.assertEqual(self.template.template_type, 'article')
        self.assertIn('\\documentclass{article}', self.template.latex_template)
    
    def test_compilation_job_creation(self):
        """Test compilation job creation"""
        job = CompilationJob.objects.create(
            manuscript=self.manuscript,
            initiated_by=self.user,
            compilation_type='full',
            status='completed',
            output_path='/media/output/test.pdf',
            log_file='Compilation successful'
        )
        
        self.assertEqual(job.manuscript, self.manuscript)
        self.assertEqual(job.status, 'completed')
        self.assertIsNotNone(job.created_at)
    


class DocViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create templates
        self.article_template = DocumentTemplate.objects.create(
            name='Article',
            template_type='article',
            latex_template='\\documentclass{article}...'
        )
        
        self.thesis_template = DocumentTemplate.objects.create(
            name='Thesis',
            template_type='thesis',
            latex_template='\\documentclass{thesis}...'
        )
        
        # Create manuscript
        self.manuscript = Manuscript.objects.create(
            owner=self.user,
            title='My Research',
            slug='my-research',
            content='\\section{Introduction}',
            abstract='Research abstract'
        )
    
    def test_writer_editor_page(self):
        """Test writer editor page (at index) - accessible without authentication"""
        response = self.client.get(reverse('writer:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SciTeX Writer')
    
    def test_real_compile_endpoint(self):
        """Test real compile endpoint"""
        # Real compilation requires authentication
        response = self.client.post(reverse('writer:real-compile'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
    
    def test_mock_save_endpoint(self):
        """Test mock save endpoint"""
        response = self.client.post(reverse('writer:mock-save'))
        self.assertEqual(response.status_code, 200)  # Mock endpoint should work without auth