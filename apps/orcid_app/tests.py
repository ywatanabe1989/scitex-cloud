#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORCID App Tests

This module contains tests for the ORCID integration functionality.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock
import json

from .models import OrcidProfile, OrcidOAuth2Token, OrcidPublication, OrcidWork, OrcidSyncLog
from .services import OrcidAuthService, OrcidAPIService, OrcidSyncService, validate_orcid_id, format_orcid_id


class OrcidModelsTestCase(TestCase):
    """Test ORCID models functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.orcid_id = '0000-0000-0000-0000'
        
    def test_orcid_oauth2_token_creation(self):
        """Test ORCID OAuth2 token creation"""
        token = OrcidOAuth2Token.objects.create(
            user=self.user,
            access_token='test-access-token',
            refresh_token='test-refresh-token',
            scope='/authenticate /read-limited',
            expires_at=timezone.now() + timedelta(hours=1),
            orcid_id=self.orcid_id
        )
        
        self.assertEqual(token.user, self.user)
        self.assertEqual(token.orcid_id, self.orcid_id)
        self.assertFalse(token.is_expired())
        self.assertIn('Bearer', token.get_authorization_header())
    
    def test_token_expiry_check(self):
        """Test token expiry checking"""
        # Create expired token
        expired_token = OrcidOAuth2Token.objects.create(
            user=self.user,
            access_token='expired-token',
            expires_at=timezone.now() - timedelta(hours=1),
            orcid_id=self.orcid_id
        )
        
        self.assertTrue(expired_token.is_expired())
        self.assertTrue(expired_token.is_expiring_soon(hours=2))
    
    def test_orcid_profile_creation(self):
        """Test ORCID profile creation"""
        profile = OrcidProfile.objects.create(
            user=self.user,
            orcid_id=self.orcid_id,
            given_name='John',
            family_name='Doe',
            credit_name='John Doe, PhD',
            biography='Test researcher'
        )
        
        self.assertEqual(profile.get_display_name(), 'John Doe, PhD')
        self.assertEqual(profile.get_orcid_url(), f'https://orcid.org/{self.orcid_id}')
        self.assertTrue(profile.needs_sync())
    
    def test_orcid_publication_creation(self):
        """Test ORCID publication creation"""
        profile = OrcidProfile.objects.create(
            user=self.user,
            orcid_id=self.orcid_id
        )
        
        publication = OrcidPublication.objects.create(
            profile=profile,
            title='Test Publication',
            publication_type='journal-article',
            publication_year=2023,
            journal='Test Journal',
            doi='10.1000/test.doi',
            orcid_put_code='12345',
            authors=[
                {'credit-name': 'John Doe', 'orcid': self.orcid_id},
                {'credit-name': 'Jane Smith'}
            ]
        )
        
        self.assertEqual(publication.title, 'Test Publication')
        self.assertEqual(publication.get_authors_display(), 'John Doe, Jane Smith')
        self.assertTrue(publication.can_import_to_scholar())
    
    def test_sync_log_creation(self):
        """Test sync log creation and management"""
        profile = OrcidProfile.objects.create(
            user=self.user,
            orcid_id=self.orcid_id
        )
        
        sync_log = OrcidSyncLog.objects.create(
            profile=profile,
            sync_type='profile',
            items_processed=1
        )
        
        # Test marking as completed
        sync_log.mark_completed('success')
        self.assertEqual(sync_log.status, 'success')
        self.assertIsNotNone(sync_log.completed_at)
        self.assertIsNotNone(sync_log.duration_seconds)


class OrcidUtilsTestCase(TestCase):
    """Test ORCID utility functions"""
    
    def test_validate_orcid_id(self):
        """Test ORCID ID validation"""
        valid_ids = [
            '0000-0000-0000-0000',
            '0000-0000-0000-000X',
            '1234-5678-9012-345X'
        ]
        
        invalid_ids = [
            '0000-0000-0000-00000',  # Too long
            '0000-0000-0000-00',     # Too short
            'invalid-id',            # Invalid format
            '0000_0000_0000_0000',   # Wrong separators
        ]
        
        for orcid_id in valid_ids:
            self.assertTrue(validate_orcid_id(orcid_id), f"Should be valid: {orcid_id}")
        
        for orcid_id in invalid_ids:
            self.assertFalse(validate_orcid_id(orcid_id), f"Should be invalid: {orcid_id}")
    
    def test_format_orcid_id(self):
        """Test ORCID ID formatting"""
        test_cases = [
            ('0000000000000000', '0000-0000-0000-0000'),
            ('000000000000000X', '0000-0000-0000-000X'),
            ('0000-0000-0000-0000', '0000-0000-0000-0000'),  # Already formatted
        ]
        
        for input_id, expected in test_cases:
            self.assertEqual(format_orcid_id(input_id), expected)


class OrcidViewsTestCase(TestCase):
    """Test ORCID views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_dashboard_view_unauthenticated(self):
        """Test dashboard view requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('orcid_app:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_view_no_profile(self):
        """Test dashboard view with no ORCID profile"""
        response = self.client.get(reverse('orcid_app:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_token'])
        self.assertFalse(response.context['has_profile'])
    
    def test_dashboard_view_with_profile(self):
        """Test dashboard view with ORCID profile"""
        # Create token and profile
        token = OrcidOAuth2Token.objects.create(
            user=self.user,
            access_token='test-token',
            expires_at=timezone.now() + timedelta(hours=1),
            orcid_id='0000-0000-0000-0000'
        )
        
        profile, _ = OrcidProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'orcid_id': '0000-0000-0000-0000',
                'given_name': 'John',
                'family_name': 'Doe'
            }
        )
        
        response = self.client.get(reverse('orcid_app:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['has_token'])
        self.assertTrue(response.context['has_profile'])
        self.assertEqual(response.context['orcid_profile'], profile)
    
    @patch('apps.orcid_app.services.is_orcid_configured')
    def test_connect_view_not_configured(self, mock_configured):
        """Test connect view when ORCID is not configured"""
        mock_configured.return_value = False
        
        response = self.client.get(reverse('orcid_app:connect'))
        self.assertEqual(response.status_code, 302)  # Redirect back to dashboard
    
    @patch('apps.orcid_app.services.is_orcid_configured')
    @patch('apps.orcid_app.services.OrcidAuthService.get_authorization_url')
    def test_connect_view_configured(self, mock_auth_url, mock_configured):
        """Test connect view when ORCID is configured"""
        mock_configured.return_value = True
        mock_auth_url.return_value = 'https://sandbox.orcid.org/oauth/authorize?...'
        
        response = self.client.get(reverse('orcid_app:connect'))
        self.assertEqual(response.status_code, 302)  # Redirect to ORCID
        self.assertIn('orcid_oauth_state', self.client.session)
    
    def test_publications_list_no_profile(self):
        """Test publications list with no ORCID profile"""
        response = self.client.get(reverse('orcid_app:publications'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['profile'])
        self.assertEqual(len(response.context['publications']), 0)
    
    def test_api_profile_status_no_profile(self):
        """Test API profile status with no profile"""
        response = self.client.get(reverse('orcid_app:api_profile_status'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertFalse(data['connected'])
        self.assertIsNone(data['orcid_id'])


class OrcidServicesTestCase(TestCase):
    """Test ORCID services"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    @patch('apps.orcid_app.services.requests.post')
    def test_exchange_code_for_token(self, mock_post):
        """Test exchanging authorization code for token"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'access_token': 'test-access-token',
            'refresh_token': 'test-refresh-token',
            'token_type': 'bearer',
            'expires_in': 3600,
            'scope': '/authenticate',
            'orcid': '0000-0000-0000-0000'
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        token_data = OrcidAuthService.exchange_code_for_token('test-code')
        
        self.assertEqual(token_data['access_token'], 'test-access-token')
        self.assertEqual(token_data['orcid_id'], '0000-0000-0000-0000')
        self.assertIn('expires_at', token_data)
    
    def test_store_token(self):
        """Test storing ORCID token"""
        token_data = {
            'access_token': 'test-access-token',
            'refresh_token': 'test-refresh-token',
            'token_type': 'bearer',
            'scope': '/authenticate',
            'expires_at': timezone.now() + timedelta(hours=1),
            'orcid_id': '0000-0000-0000-0000'
        }
        
        token = OrcidAuthService.store_token(self.user, token_data)
        
        self.assertEqual(token.user, self.user)
        self.assertEqual(token.access_token, 'test-access-token')
        self.assertEqual(token.orcid_id, '0000-0000-0000-0000')
    
    def test_get_valid_token_no_token(self):
        """Test getting valid token when none exists"""
        token = OrcidAuthService.get_valid_token(self.user)
        self.assertIsNone(token)
    
    def test_get_valid_token_valid(self):
        """Test getting valid token when it exists and is valid"""
        stored_token = OrcidOAuth2Token.objects.create(
            user=self.user,
            access_token='test-token',
            expires_at=timezone.now() + timedelta(hours=1),
            orcid_id='0000-0000-0000-0000'
        )
        
        token = OrcidAuthService.get_valid_token(self.user)
        self.assertEqual(token, stored_token)
    
    def test_get_valid_token_expired(self):
        """Test getting valid token when it's expired"""
        OrcidOAuth2Token.objects.create(
            user=self.user,
            access_token='expired-token',
            expires_at=timezone.now() - timedelta(hours=1),
            orcid_id='0000-0000-0000-0000'
        )
        
        token = OrcidAuthService.get_valid_token(self.user)
        self.assertIsNone(token)
    
    @patch('apps.orcid_app.services.OrcidAPIService._make_request')
    def test_sync_service_initialization(self, mock_request):
        """Test ORCID sync service initialization"""
        # Create token and profile
        OrcidOAuth2Token.objects.create(
            user=self.user,
            access_token='test-token',
            expires_at=timezone.now() + timedelta(hours=1),
            orcid_id='0000-0000-0000-0000'
        )
        
        sync_service = OrcidSyncService(self.user)
        self.assertEqual(sync_service.user, self.user)
        self.assertIsNotNone(sync_service.orcid_profile)
        self.assertEqual(sync_service.orcid_profile.orcid_id, '0000-0000-0000-0000')


class OrcidIntegrationTestCase(TestCase):
    """Integration tests for ORCID functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.profile = OrcidProfile.objects.create(
            user=self.user,
            orcid_id='0000-0000-0000-0000',
            given_name='John',
            family_name='Doe'
        )
    
    def test_full_workflow_simulation(self):
        """Test a complete ORCID integration workflow"""
        # 1. Create token (simulating OAuth callback)
        token = OrcidOAuth2Token.objects.create(
            user=self.user,
            access_token='test-token',
            expires_at=timezone.now() + timedelta(hours=1),
            orcid_id='0000-0000-0000-0000'
        )
        
        # 2. Create publications (simulating sync)
        pub1 = OrcidPublication.objects.create(
            profile=self.profile,
            title='Test Publication 1',
            publication_type='journal-article',
            publication_year=2023,
            journal='Test Journal',
            doi='10.1000/test1',
            orcid_put_code='12345'
        )
        
        pub2 = OrcidPublication.objects.create(
            profile=self.profile,
            title='Test Publication 2',
            publication_type='conference-paper',
            publication_year=2022,
            orcid_put_code='12346'
        )
        
        # 3. Verify data integrity
        self.assertEqual(self.profile.get_publication_count(), 2)
        recent_pubs = self.profile.get_recent_publications()
        self.assertEqual(len(recent_pubs), 2)
        self.assertEqual(recent_pubs[0], pub1)  # More recent year first
        
        # 4. Test import capability
        self.assertTrue(pub1.can_import_to_scholar())
        self.assertTrue(pub2.can_import_to_scholar())
        
        # 5. Create sync log
        sync_log = OrcidSyncLog.objects.create(
            profile=self.profile,
            sync_type='publications',
            items_processed=2,
            items_created=2
        )
        sync_log.mark_completed('success')
        
        self.assertEqual(sync_log.status, 'success')
        self.assertEqual(sync_log.get_success_rate(), 100.0)
    
    def test_error_handling(self):
        """Test error handling in ORCID integration"""
        # Test sync log with errors
        sync_log = OrcidSyncLog.objects.create(
            profile=self.profile,
            sync_type='profile'
        )
        
        sync_log.add_error('Test error message', {'detail': 'Test error details'})
        
        self.assertEqual(sync_log.status, 'failed')
        self.assertEqual(sync_log.error_message, 'Test error message')
        self.assertEqual(sync_log.error_details['detail'], 'Test error details')
    
    def test_profile_sync_status(self):
        """Test profile sync status tracking"""
        # Initially not synced
        self.assertFalse(self.profile.is_synced)
        self.assertTrue(self.profile.needs_sync())
        
        # Mark as synced
        self.profile.is_synced = True
        self.profile.last_sync_at = timezone.now()
        self.profile.save()
        
        self.assertTrue(self.profile.is_synced)
        self.assertFalse(self.profile.needs_sync(hours=1))  # Synced within 1 hour
        self.assertTrue(self.profile.needs_sync(hours=0))   # Needs immediate sync