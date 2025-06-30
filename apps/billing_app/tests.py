#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SciTeX-Cloud Billing Tests
Tests for subscription and billing functionality
"""

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from unittest import skip

# Check if billing app is enabled
try:
    from .models import (
        SubscriptionTier, UserSubscription, UsageTracking, QuotaLimit,
        BillingHistory, PaymentMethod, PromoCode, FeatureFlag
    )
    from .services import (
        SubscriptionService, UsageService, QuotaService, FeatureAccessService
    )
    BILLING_ENABLED = True
except (ImportError, RuntimeError):
    BILLING_ENABLED = False


@skip("Billing app disabled - requires Stripe dependency")
class SubscriptionTierTestCase(TestCase):
    """Test subscription tier functionality"""
    
    def setUp(self):
        self.free_tier = SubscriptionTier.objects.create(
            name='Free',
            tier_type='free',
            description='Free tier',
            price_monthly=0,
            price_yearly=0,
            max_projects=1,
            storage_gb=1,
            compute_hours_monthly=5,
            is_active=True
        )
        
        self.individual_tier = SubscriptionTier.objects.create(
            name='Individual',
            tier_type='individual',
            description='Individual tier',
            price_monthly=29,
            price_yearly=290,
            max_projects=10,
            storage_gb=25,
            compute_hours_monthly=50,
            has_watermark=False,
            is_active=True
        )
    
    def test_tier_creation(self):
        """Test tier creation and basic properties"""
        self.assertEqual(self.free_tier.name, 'Free')
        self.assertEqual(self.free_tier.price_monthly, 0)
        self.assertTrue(self.free_tier.has_watermark)
        
        self.assertEqual(self.individual_tier.name, 'Individual')
        self.assertEqual(self.individual_tier.price_monthly, 29)
        self.assertFalse(self.individual_tier.has_watermark)
    
    def test_yearly_savings(self):
        """Test yearly savings calculation"""
        savings = self.individual_tier.get_yearly_savings()
        expected_savings = ((29 * 12) - 290) / (29 * 12) * 100
        self.assertEqual(round(savings, 1), round(expected_savings, 1))
    
    def test_feature_list(self):
        """Test feature list generation"""
        features = self.individual_tier.get_feature_list()
        self.assertIn('10 projects', features)
        self.assertIn('25GB storage', features)
        self.assertIn('No watermarks', features)


@skip("Billing app disabled - requires Stripe dependency")
class UserSubscriptionTestCase(TestCase):
    """Test user subscription functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.tier = SubscriptionTier.objects.create(
            name='Test Tier',
            tier_type='individual',
            description='Test tier',
            price_monthly=29,
            max_projects=10,
            storage_gb=25,
            trial_days=14,
            is_active=True
        )
    
    def test_subscription_creation(self):
        """Test subscription creation"""
        subscription = UserSubscription.objects.create(
            user=self.user,
            tier=self.tier,
            status='trialing',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timedelta(days=14)
        )
        
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.tier, self.tier)
        self.assertEqual(subscription.status, 'trialing')
    
    def test_subscription_is_active(self):
        """Test subscription active status"""
        subscription = UserSubscription.objects.create(
            user=self.user,
            tier=self.tier,
            status='active',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timedelta(days=30)
        )
        
        self.assertTrue(subscription.is_active())
        
        # Test expired subscription
        subscription.current_period_end = timezone.now() - timedelta(days=1)
        subscription.save()
        self.assertFalse(subscription.is_active())
    
    def test_days_remaining(self):
        """Test days remaining calculation"""
        subscription = UserSubscription.objects.create(
            user=self.user,
            tier=self.tier,
            status='active',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timedelta(days=15)
        )
        
        days_remaining = subscription.days_remaining()
        self.assertGreaterEqual(days_remaining, 14)
        self.assertLessEqual(days_remaining, 15)


@skip("Billing app disabled - requires Stripe dependency")
class UsageTrackingTestCase(TestCase):
    """Test usage tracking functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.tier = SubscriptionTier.objects.create(
            name='Test Tier',
            tier_type='individual',
            price_monthly=29,
            is_active=True
        )
        
        self.subscription = UserSubscription.objects.create(
            user=self.user,
            tier=self.tier,
            status='active',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timedelta(days=30)
        )
    
    def test_usage_recording(self):
        """Test usage recording"""
        usage = UsageService.record_usage(
            user=self.user,
            resource_type='compute_hours',
            amount=2.5,
            unit='hours',
            module='code',
            feature='execution'
        )
        
        self.assertIsNotNone(usage)
        self.assertEqual(usage.user, self.user)
        self.assertEqual(usage.resource_type, 'compute_hours')
        self.assertEqual(usage.amount_used, Decimal('2.5'))
        self.assertEqual(usage.unit, 'hours')
        self.assertEqual(usage.module, 'code')
    
    def test_usage_summary(self):
        """Test usage summary generation"""
        # Record some usage
        UsageService.record_usage(
            user=self.user,
            resource_type='compute_hours',
            amount=2.5,
            unit='hours',
            module='code'
        )
        
        UsageService.record_usage(
            user=self.user,
            resource_type='compute_hours',
            amount=1.5,
            unit='hours',
            module='code'
        )
        
        summary = UsageService.get_usage_summary(self.user)
        
        self.assertIn('compute_hours', summary)
        self.assertEqual(summary['compute_hours']['total_used'], Decimal('4.0'))
        self.assertEqual(summary['compute_hours']['unit'], 'hours')


@skip("Billing app disabled - requires Stripe dependency")
class QuotaServiceTestCase(TestCase):
    """Test quota management functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.tier = SubscriptionTier.objects.create(
            name='Test Tier',
            tier_type='individual',
            price_monthly=29,
            compute_hours_monthly=50,
            storage_gb=25,
            is_active=True
        )
        
        self.subscription = UserSubscription.objects.create(
            user=self.user,
            tier=self.tier,
            status='active',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timedelta(days=30)
        )
    
    def test_quota_initialization(self):
        """Test quota initialization"""
        QuotaService.initialize_quotas(self.subscription)
        
        compute_quota = QuotaLimit.objects.filter(
            user=self.user,
            resource_type='compute_hours'
        ).first()
        
        self.assertIsNotNone(compute_quota)
        self.assertEqual(compute_quota.limit_amount, 50)
        self.assertEqual(compute_quota.used_amount, 0)
        self.assertEqual(compute_quota.unit, 'hours')
    
    def test_quota_availability_check(self):
        """Test quota availability checking"""
        QuotaService.initialize_quotas(self.subscription)
        
        # Check initial availability
        has_quota, available = QuotaService.check_quota_availability(
            self.user, 'compute_hours', 10
        )
        
        self.assertTrue(has_quota)
        self.assertEqual(available, 50)
        
        # Add some usage
        quota = QuotaLimit.objects.get(
            user=self.user,
            resource_type='compute_hours'
        )
        quota.used_amount = 45
        quota.save()
        
        # Check availability after usage
        has_quota, available = QuotaService.check_quota_availability(
            self.user, 'compute_hours', 10
        )
        
        self.assertFalse(has_quota)
        self.assertEqual(available, 5)


@skip("Billing app disabled - requires Stripe dependency")
class FeatureAccessTestCase(TestCase):
    """Test feature access control"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.free_tier = SubscriptionTier.objects.create(
            name='Free',
            tier_type='free',
            price_monthly=0,
            allows_ai_assistant=False,
            allows_private_projects=False,
            is_active=True
        )
        
        self.premium_tier = SubscriptionTier.objects.create(
            name='Premium',
            tier_type='individual',
            price_monthly=29,
            allows_ai_assistant=True,
            allows_private_projects=True,
            is_active=True
        )
    
    def test_free_tier_access(self):
        """Test feature access for free tier"""
        subscription = UserSubscription.objects.create(
            user=self.user,
            tier=self.free_tier,
            status='active',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timedelta(days=30)
        )
        
        # Free tier shouldn't have AI assistant access
        has_ai_access = FeatureAccessService.has_feature_access(
            self.user, 'ai_assistant'
        )
        self.assertFalse(has_ai_access)
        
        # Free tier shouldn't have private projects
        has_private_projects = FeatureAccessService.has_feature_access(
            self.user, 'private_projects'
        )
        self.assertFalse(has_private_projects)
    
    def test_premium_tier_access(self):
        """Test feature access for premium tier"""
        subscription = UserSubscription.objects.create(
            user=self.user,
            tier=self.premium_tier,
            status='active',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timedelta(days=30)
        )
        
        # Premium tier should have AI assistant access
        has_ai_access = FeatureAccessService.has_feature_access(
            self.user, 'ai_assistant'
        )
        self.assertTrue(has_ai_access)
        
        # Premium tier should have private projects
        has_private_projects = FeatureAccessService.has_feature_access(
            self.user, 'private_projects'
        )
        self.assertTrue(has_private_projects)


@skip("Billing app disabled - requires Stripe dependency")
class PromoCodeTestCase(TestCase):
    """Test promo code functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.promo = PromoCode.objects.create(
            code='TEST50',
            name='Test 50% Off',
            description='50% off test promo',
            discount_type='percentage',
            discount_value=50,
            max_uses=100,
            current_uses=0,
            valid_from=timezone.now(),
            valid_until=timezone.now() + timedelta(days=30),
            is_active=True
        )
    
    def test_promo_validity(self):
        """Test promo code validity"""
        self.assertTrue(self.promo.is_valid())
        
        # Test expired promo
        self.promo.valid_until = timezone.now() - timedelta(days=1)
        self.promo.save()
        self.assertFalse(self.promo.is_valid())
        
        # Reset and test max uses
        self.promo.valid_until = timezone.now() + timedelta(days=30)
        self.promo.current_uses = 100
        self.promo.save()
        self.assertFalse(self.promo.is_valid())
    
    def test_discount_calculation(self):
        """Test discount calculation"""
        # Test percentage discount
        discount = self.promo.apply_discount(100)
        self.assertEqual(discount, 50)
        
        # Test fixed amount discount
        self.promo.discount_type = 'fixed_amount'
        self.promo.discount_value = 25
        self.promo.save()
        
        discount = self.promo.apply_discount(100)
        self.assertEqual(discount, 25)
        
        # Test fixed amount larger than total
        discount = self.promo.apply_discount(10)
        self.assertEqual(discount, 10)  # Should not exceed total amount