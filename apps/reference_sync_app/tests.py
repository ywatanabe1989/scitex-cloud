from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from apps.scholar_app.models import SearchIndex, Author
from .models import (
    ReferenceManagerAccount,
    SyncProfile,
    SyncSession,
    ReferenceMapping,
    ConflictResolution,
    SyncLog
)


class ReferenceManagerAccountTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_account(self):
        account = ReferenceManagerAccount.objects.create(
            user=self.user,
            service='mendeley',
            account_name='Test Mendeley Account',
            external_user_id='12345'
        )
        self.assertEqual(account.service, 'mendeley')
        self.assertTrue(account.is_active)
        self.assertEqual(account.sync_count, 0)
    
    def test_token_validation(self):
        account = ReferenceManagerAccount.objects.create(
            user=self.user,
            service='zotero',
            account_name='Test Zotero Account',
            token_expires_at=timezone.now() + timezone.timedelta(hours=1)
        )
        self.assertTrue(account.is_token_valid())
        
        # Test expired token
        account.token_expires_at = timezone.now() - timezone.timedelta(hours=1)
        account.save()
        self.assertFalse(account.is_token_valid())
    
    def test_api_call_limits(self):
        account = ReferenceManagerAccount.objects.create(
            user=self.user,
            service='mendeley',
            account_name='Test Account',
            api_calls_today=0
        )
        self.assertTrue(account.can_make_api_call())
        
        # Test limit exceeded
        account.api_calls_today = 150  # Over Mendeley limit
        account.save()
        self.assertFalse(account.can_make_api_call())


class SyncProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.account = ReferenceManagerAccount.objects.create(
            user=self.user,
            service='mendeley',
            account_name='Test Account'
        )
    
    def test_create_sync_profile(self):
        profile = SyncProfile.objects.create(
            user=self.user,
            name='Test Profile',
            auto_sync=True,
            sync_frequency='daily'
        )
        profile.accounts.add(self.account)
        
        self.assertEqual(profile.name, 'Test Profile')
        self.assertTrue(profile.auto_sync)
        self.assertEqual(profile.accounts.count(), 1)
    
    def test_should_sync_now(self):
        profile = SyncProfile.objects.create(
            user=self.user,
            name='Test Profile',
            auto_sync=True,
            sync_frequency='daily',
            next_sync=timezone.now() - timezone.timedelta(hours=1)
        )
        self.assertTrue(profile.should_sync_now())
        
        # Test future sync
        profile.next_sync = timezone.now() + timezone.timedelta(hours=1)
        profile.save()
        self.assertFalse(profile.should_sync_now())
    
    def test_calculate_next_sync(self):
        profile = SyncProfile.objects.create(
            user=self.user,
            name='Test Profile',
            auto_sync=True,
            sync_frequency='daily'
        )
        next_sync = profile.calculate_next_sync()
        self.assertIsNotNone(next_sync)
        self.assertGreater(next_sync, timezone.now())


class SyncSessionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = SyncProfile.objects.create(
            user=self.user,
            name='Test Profile'
        )
    
    def test_create_sync_session(self):
        session = SyncSession.objects.create(
            profile=self.profile,
            status='pending',
            trigger='manual'
        )
        self.assertEqual(session.status, 'pending')
        self.assertEqual(session.items_processed, 0)
        self.assertEqual(session.conflicts_found, 0)
    
    def test_progress_calculation(self):
        session = SyncSession.objects.create(
            profile=self.profile,
            total_items=100,
            items_processed=25
        )
        self.assertEqual(session.progress_percentage(), 25.0)
    
    def test_mark_completed(self):
        session = SyncSession.objects.create(
            profile=self.profile,
            status='running'
        )
        session.mark_completed()
        self.assertEqual(session.status, 'completed')
        self.assertIsNotNone(session.completed_at)
    
    def test_mark_failed(self):
        session = SyncSession.objects.create(
            profile=self.profile,
            status='running'
        )
        error_msg = "Test error message"
        session.mark_failed(error_msg)
        self.assertEqual(session.status, 'failed')
        self.assertEqual(session.last_error, error_msg)
        self.assertIsNotNone(session.completed_at)


class ReferenceMappingTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.account = ReferenceManagerAccount.objects.create(
            user=self.user,
            service='mendeley',
            account_name='Test Account'
        )
        
        # Create a test paper
        author = Author.objects.create(
            first_name='John',
            last_name='Doe'
        )
        self.paper = SearchIndex.objects.create(
            title='Test Paper',
            abstract='Test abstract',
            doi='10.1234/test'
        )
    
    def test_create_mapping(self):
        mapping = ReferenceMapping.objects.create(
            local_paper=self.paper,
            service='mendeley',
            external_id='mendeley-123',
            account=self.account
        )
        self.assertEqual(mapping.service, 'mendeley')
        self.assertEqual(mapping.external_id, 'mendeley-123')
        self.assertEqual(mapping.sync_status, 'synced')


class ConflictResolutionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = SyncProfile.objects.create(
            user=self.user,
            name='Test Profile'
        )
        self.session = SyncSession.objects.create(
            profile=self.profile
        )
        self.account = ReferenceManagerAccount.objects.create(
            user=self.user,
            service='mendeley',
            account_name='Test Account'
        )
        
        # Create test paper and mapping
        author = Author.objects.create(
            first_name='John',
            last_name='Doe'
        )
        self.paper = SearchIndex.objects.create(
            title='Test Paper',
            abstract='Test abstract'
        )
        self.mapping = ReferenceMapping.objects.create(
            local_paper=self.paper,
            service='mendeley',
            external_id='mendeley-123',
            account=self.account
        )
    
    def test_create_conflict(self):
        conflict = ConflictResolution.objects.create(
            sync_session=self.session,
            reference_mapping=self.mapping,
            conflict_type='title',
            local_value={'title': 'Local Title'},
            remote_value={'title': 'Remote Title'}
        )
        self.assertEqual(conflict.conflict_type, 'title')
        self.assertFalse(conflict.is_resolved())
    
    def test_resolve_conflict(self):
        conflict = ConflictResolution.objects.create(
            sync_session=self.session,
            reference_mapping=self.mapping,
            conflict_type='title',
            local_value={'title': 'Local Title'},
            remote_value={'title': 'Remote Title'}
        )
        
        # Resolve the conflict
        conflict.resolution = 'local_wins'
        conflict.resolved_value = {'title': 'Local Title'}
        conflict.resolved_at = timezone.now()
        conflict.resolved_by = self.user
        conflict.save()
        
        self.assertTrue(conflict.is_resolved())
        self.assertEqual(conflict.resolution, 'local_wins')


class SyncLogTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = SyncProfile.objects.create(
            user=self.user,
            name='Test Profile'
        )
        self.session = SyncSession.objects.create(
            profile=self.profile
        )
    
    def test_create_log_entry(self):
        log = SyncLog.objects.create(
            sync_session=self.session,
            level='INFO',
            operation='fetch',
            message='Fetching data from Mendeley API'
        )
        self.assertEqual(log.level, 'INFO')
        self.assertEqual(log.operation, 'fetch')
        self.assertIn('Mendeley', log.message)