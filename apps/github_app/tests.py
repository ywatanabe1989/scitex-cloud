#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub App Tests

Unit tests for GitHub integration functionality.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import json
from unittest.mock import patch, Mock

from .models import GitHubOAuth2Token, GitHubProfile, GitHubRepository, GitHubConnection
from .services import GitHubAuthService, GitHubAPIService, GitHubSyncService


class GitHubModelTests(TestCase):
    """Test GitHub models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_github_token_creation(self):
        """Test GitHub token model creation"""
        token = GitHubOAuth2Token.objects.create(
            user=self.user,
            access_token='ghs_test_token',
            token_type='bearer',
            scope='repo,user:email',
            github_username='testuser'
        )
        
        self.assertEqual(token.user, self.user)
        self.assertEqual(token.access_token, 'ghs_test_token')
        self.assertEqual(token.github_username, 'testuser')
        self.assertFalse(token.is_expired())
    
    def test_github_profile_creation(self):
        """Test GitHub profile model creation"""
        profile = GitHubProfile.objects.create(
            user=self.user,
            github_id=12345,
            github_username='testuser',
            name='Test User',
            email='test@example.com',
            bio='Test bio',
            company='Test Company'
        )
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.github_username, 'testuser')
        self.assertEqual(profile.get_github_url(), 'https://github.com/testuser')
    
    def test_github_repository_creation(self):
        """Test GitHub repository model creation"""
        profile = GitHubProfile.objects.create(
            user=self.user,
            github_id=12345,
            github_username='testuser'
        )
        
        repo = GitHubRepository.objects.create(
            profile=profile,
            github_id=67890,
            name='test-repo',
            full_name='testuser/test-repo',
            description='Test repository',
            is_private=False,
            default_branch='main',
            clone_url='https://github.com/testuser/test-repo.git',
            ssh_url='git@github.com:testuser/test-repo.git',
            git_url='git://github.com/testuser/test-repo.git',
            github_created_at=timezone.now(),
            github_updated_at=timezone.now()
        )
        
        self.assertEqual(repo.profile, profile)
        self.assertEqual(repo.name, 'test-repo')
        self.assertEqual(repo.get_github_url(), 'https://github.com/testuser/test-repo')


class GitHubServiceTests(TestCase):
    """Test GitHub services"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('apps.github_app.services.requests.post')
    def test_exchange_code_for_token(self, mock_post):
        """Test OAuth2 code exchange"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'ghs_test_token',
            'token_type': 'bearer',
            'scope': 'repo,user:email'
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        token_data = GitHubAuthService.exchange_code_for_token('test_code', 'test_state')
        
        self.assertEqual(token_data['access_token'], 'ghs_test_token')
        self.assertEqual(token_data['token_type'], 'bearer')
        self.assertEqual(token_data['scope'], 'repo,user:email')


class GitHubViewTests(TestCase):
    """Test GitHub views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        response = self.client.get(reverse('github_app:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_authenticated(self):
        """Test dashboard for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('github_app:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'GitHub Integration')
    
    def test_connect_redirect(self):
        """Test GitHub connect redirects to OAuth"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('github_app:connect'))
        self.assertEqual(response.status_code, 302)  # Redirect to GitHub