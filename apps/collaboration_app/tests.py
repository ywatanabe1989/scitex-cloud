"""
Tests for the Collaboration app - Team workspace and collaboration features.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import (
    Team, TeamMembership, TeamInvitation, SharedProject, 
    Comment, Review, ActivityFeed, Notification
)
from apps.core_app.models import Project


class TeamModelTests(TestCase):
    """Test Team model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
    
    def test_team_creation(self):
        """Test basic team creation"""
        team = Team.objects.create(
            name='Test Research Team',
            description='A team for testing',
            team_type='research',
            owner=self.user
        )
        
        self.assertEqual(team.name, 'Test Research Team')
        self.assertEqual(team.owner, self.user)
        self.assertEqual(team.team_type, 'research')
        self.assertTrue(team.is_active)
    
    def test_team_membership(self):
        """Test team membership functionality"""
        team = Team.objects.create(
            name='Test Team',
            owner=self.user
        )
        
        # Test owner is member
        self.assertTrue(team.is_member(self.user))
        self.assertEqual(team.get_user_role(self.user), 'owner')
        
        # Add member
        membership, message = team.add_member(self.other_user, 'contributor')
        self.assertIsNotNone(membership)
        self.assertTrue(team.is_member(self.other_user))
        self.assertEqual(team.get_user_role(self.other_user), 'contributor')
        
        # Test member count
        self.assertEqual(team.get_member_count(), 2)


class TeamViewTests(TestCase):
    """Test Team-related views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_collaboration_dashboard_view(self):
        """Test collaboration dashboard access"""
        response = self.client.get(reverse('collaboration:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_team_list_view(self):
        """Test team list view"""
        # Create a team
        team = Team.objects.create(
            name='Test Team',
            owner=self.user
        )
        
        response = self.client.get(reverse('collaboration:team_list'))
        self.assertEqual(response.status_code, 200)


class NotificationTests(TestCase):
    """Test notification system"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_notification_creation(self):
        """Test creating and managing notifications"""
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type='team_invitation',
            title='You have been invited to a team',
            message='Join our research team!',
            priority='normal'
        )
        
        self.assertEqual(notification.recipient, self.user)
        self.assertFalse(notification.is_read)
        
        # Mark as read
        notification.mark_as_read()
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)
