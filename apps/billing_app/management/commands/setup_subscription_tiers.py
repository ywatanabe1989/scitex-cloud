#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Django management command to set up comprehensive subscription tiers
"""

from django.core.management.base import BaseCommand
from apps.billing_app.models import SubscriptionTier


class Command(BaseCommand):
    help = 'Set up comprehensive subscription tiers for SciTeX-Cloud monetization'

    def handle(self, *args, **options):
        """Create comprehensive subscription tiers"""
        
        tiers_data = [
            {
                'name': 'Free',
                'tier_type': 'free',
                'description': 'Perfect for exploring SciTeX-Cloud with essential research tools',
                'marketing_tagline': 'Start your research journey',
                'price_monthly': 0.00,
                'price_yearly': 0.00,
                
                # Resource Limits
                'max_projects': 1,
                'max_collaborators_per_project': 1,
                'storage_gb': 1,
                'compute_hours_monthly': 5,
                'gpu_hours_monthly': 1,
                'api_calls_monthly': 100,
                
                # Feature Controls
                'has_watermark': True,
                'requires_citation': True,
                'requires_scitex_archive': True,
                'allows_commercial_use': False,
                'allows_private_projects': False,
                
                # Advanced Features
                'has_priority_support': False,
                'has_custom_integrations': False,
                'has_advanced_analytics': False,
                'has_team_management': False,
                'has_institutional_licensing': False,
                'has_white_labeling': False,
                'has_dedicated_support': False,
                'has_sla_guarantee': False,
                
                # Module Access
                'allows_scholar_unlimited': False,
                'allows_writer_advanced': False,
                'allows_viz_export': False,
                'allows_code_private_repos': False,
                'allows_ai_assistant': False,
                
                # Settings
                'trial_days': 14,
                'allows_trial': True,
                'is_featured': False,
                'is_active': True,
                'display_order': 1,
                'discount_percentage_yearly': 0,
            },
            
            {
                'name': 'Individual',
                'tier_type': 'individual',
                'description': 'For researchers and students who need more power and flexibility',
                'marketing_tagline': 'Unlock your research potential',
                'price_monthly': 29.00,
                'price_yearly': 290.00,  # 2 months free
                
                # Resource Limits
                'max_projects': 10,
                'max_collaborators_per_project': 3,
                'storage_gb': 25,
                'compute_hours_monthly': 50,
                'gpu_hours_monthly': 10,
                'api_calls_monthly': 2000,
                
                # Feature Controls
                'has_watermark': False,
                'requires_citation': True,
                'requires_scitex_archive': False,
                'allows_commercial_use': False,
                'allows_private_projects': True,
                
                # Advanced Features
                'has_priority_support': True,
                'has_custom_integrations': False,
                'has_advanced_analytics': True,
                'has_team_management': False,
                'has_institutional_licensing': False,
                'has_white_labeling': False,
                'has_dedicated_support': False,
                'has_sla_guarantee': False,
                
                # Module Access
                'allows_scholar_unlimited': True,
                'allows_writer_advanced': True,
                'allows_viz_export': True,
                'allows_code_private_repos': True,
                'allows_ai_assistant': True,
                
                # Settings
                'trial_days': 14,
                'allows_trial': True,
                'is_featured': True,
                'is_active': True,
                'display_order': 2,
                'discount_percentage_yearly': 17,  # (348-290)/348
            },
            
            {
                'name': 'Team',
                'tier_type': 'team',
                'description': 'Perfect for research teams and collaborative projects',
                'marketing_tagline': 'Collaborate without limits',
                'price_monthly': 99.00,
                'price_yearly': 990.00,  # 2 months free
                
                # Resource Limits
                'max_projects': 50,
                'max_collaborators_per_project': 15,
                'storage_gb': 100,
                'compute_hours_monthly': 200,
                'gpu_hours_monthly': 50,
                'api_calls_monthly': 10000,
                
                # Feature Controls
                'has_watermark': False,
                'requires_citation': False,
                'requires_scitex_archive': False,
                'allows_commercial_use': True,
                'allows_private_projects': True,
                
                # Advanced Features
                'has_priority_support': True,
                'has_custom_integrations': True,
                'has_advanced_analytics': True,
                'has_team_management': True,
                'has_institutional_licensing': False,
                'has_white_labeling': False,
                'has_dedicated_support': True,
                'has_sla_guarantee': True,
                
                # Module Access
                'allows_scholar_unlimited': True,
                'allows_writer_advanced': True,
                'allows_viz_export': True,
                'allows_code_private_repos': True,
                'allows_ai_assistant': True,
                
                # Settings
                'trial_days': 14,
                'allows_trial': True,
                'is_featured': True,
                'is_active': True,
                'display_order': 3,
                'discount_percentage_yearly': 17,
            },
            
            {
                'name': 'Institutional',
                'tier_type': 'institutional',
                'description': 'Comprehensive solution for universities and research institutions',
                'marketing_tagline': 'Institutional research excellence',
                'price_monthly': 299.00,
                'price_yearly': 2990.00,  # 2 months free
                
                # Resource Limits  
                'max_projects': 500,
                'max_collaborators_per_project': 100,
                'storage_gb': 1000,
                'compute_hours_monthly': 1000,
                'gpu_hours_monthly': 200,
                'api_calls_monthly': 50000,
                
                # Feature Controls
                'has_watermark': False,
                'requires_citation': False,
                'requires_scitex_archive': False,
                'allows_commercial_use': True,
                'allows_private_projects': True,
                
                # Advanced Features
                'has_priority_support': True,
                'has_custom_integrations': True,
                'has_advanced_analytics': True,
                'has_team_management': True,
                'has_institutional_licensing': True,
                'has_white_labeling': True,
                'has_dedicated_support': True,
                'has_sla_guarantee': True,
                
                # Module Access
                'allows_scholar_unlimited': True,
                'allows_writer_advanced': True,
                'allows_viz_export': True,
                'allows_code_private_repos': True,
                'allows_ai_assistant': True,
                
                # Settings
                'trial_days': 30,
                'allows_trial': True,
                'is_featured': False,
                'is_active': True,
                'display_order': 4,
                'discount_percentage_yearly': 17,
            },
            
            {
                'name': 'Enterprise',
                'tier_type': 'enterprise',
                'description': 'Custom solutions for large organizations with dedicated support',
                'marketing_tagline': 'Enterprise-grade research platform',
                'price_monthly': 999.00,
                'price_yearly': 9990.00,  # 2 months free
                
                # Resource Limits (unlimited represented as high numbers)
                'max_projects': 9999,
                'max_collaborators_per_project': 9999,
                'storage_gb': 10000,
                'compute_hours_monthly': 5000,
                'gpu_hours_monthly': 1000,
                'api_calls_monthly': 999999,
                
                # Feature Controls
                'has_watermark': False,
                'requires_citation': False,
                'requires_scitex_archive': False,
                'allows_commercial_use': True,
                'allows_private_projects': True,
                
                # Advanced Features
                'has_priority_support': True,
                'has_custom_integrations': True,
                'has_advanced_analytics': True,
                'has_team_management': True,
                'has_institutional_licensing': True,
                'has_white_labeling': True,
                'has_dedicated_support': True,
                'has_sla_guarantee': True,
                
                # Module Access
                'allows_scholar_unlimited': True,
                'allows_writer_advanced': True,
                'allows_viz_export': True,
                'allows_code_private_repos': True,
                'allows_ai_assistant': True,
                
                # Settings
                'trial_days': 30,
                'allows_trial': True,
                'is_featured': False,
                'is_active': True,
                'display_order': 5,
                'discount_percentage_yearly': 17,
            }
        ]

        created_count = 0
        updated_count = 0

        for tier_data in tiers_data:
            tier, created = SubscriptionTier.objects.update_or_create(
                tier_type=tier_data['tier_type'],
                defaults=tier_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created tier: {tier.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Updated tier: {tier.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎯 Successfully processed {created_count + updated_count} subscription tiers'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'📊 Created: {created_count} | Updated: {updated_count}'
            )
        )
        
        # Display tier summary
        self.stdout.write('\n📋 Subscription Tier Summary:')
        for tier in SubscriptionTier.objects.filter(is_active=True).order_by('display_order'):
            price_display = f'${tier.price_monthly}/month' if tier.price_monthly > 0 else 'Free'
            features_count = sum([
                not tier.has_watermark,
                not tier.requires_citation,
                tier.allows_commercial_use,
                tier.allows_private_projects,
                tier.has_priority_support,
                tier.has_custom_integrations,
                tier.has_advanced_analytics,
                tier.has_team_management,
                tier.allows_scholar_unlimited,
                tier.allows_writer_advanced,
                tier.allows_viz_export,
                tier.allows_code_private_repos,
                tier.allows_ai_assistant,
            ])
            
            self.stdout.write(
                f'  • {tier.name}: {price_display} - {tier.max_projects} projects, '
                f'{tier.storage_gb}GB storage, {features_count} premium features'
            )