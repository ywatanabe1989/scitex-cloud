#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SciTeX-Cloud Billing Admin Interface
Comprehensive admin interface for subscription and billing management
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import json

from .models import (
    SubscriptionTier, UserSubscription, UsageTracking, QuotaLimit,
    BillingHistory, InstitutionalLicense, PaymentMethod, PromoCode,
    FeatureFlag
)


@admin.register(SubscriptionTier)
class SubscriptionTierAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'tier_type', 'price_monthly', 'price_yearly', 
        'max_projects', 'storage_gb', 'is_featured', 'is_active',
        'subscriber_count'
    ]
    list_filter = ['tier_type', 'is_featured', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'subscriber_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'tier_type', 'description', 'marketing_tagline')
        }),
        ('Pricing', {
            'fields': (
                'price_monthly', 'price_yearly', 'discount_percentage_yearly',
                'stripe_price_id_monthly', 'stripe_price_id_yearly'
            )
        }),
        ('Resource Limits', {
            'fields': (
                'max_projects', 'max_collaborators_per_project', 'storage_gb',
                'compute_hours_monthly', 'gpu_hours_monthly', 'api_calls_monthly'
            )
        }),
        ('Feature Controls', {
            'fields': (
                'has_watermark', 'requires_citation', 'requires_scitex_archive',
                'allows_commercial_use', 'allows_private_projects'
            )
        }),
        ('Advanced Features', {
            'fields': (
                'has_priority_support', 'has_custom_integrations', 
                'has_advanced_analytics', 'has_team_management',
                'has_institutional_licensing', 'has_white_labeling',
                'has_dedicated_support', 'has_sla_guarantee'
            )
        }),
        ('Module Access', {
            'fields': (
                'allows_scholar_unlimited', 'allows_writer_advanced',
                'allows_viz_export', 'allows_code_private_repos',
                'allows_ai_assistant'
            )
        }),
        ('Trial & Display', {
            'fields': (
                'trial_days', 'allows_trial', 'is_featured', 'is_active',
                'display_order'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'subscriber_count'),
            'classes': ('collapse',)
        })
    )
    
    def subscriber_count(self, obj):
        return obj.subscribers.filter(status__in=['trialing', 'active']).count()
    subscriber_count.short_description = 'Active Subscribers'
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly.extend(['tier_type'])  # Don't allow changing tier type
        return readonly


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'tier', 'status', 'billing_cycle', 'current_period_end',
        'days_remaining', 'monthly_price', 'is_trial_display'
    ]
    list_filter = [
        'status', 'billing_cycle', 'tier__tier_type', 'tier',
        'created_at', 'current_period_end'
    ]
    search_fields = [
        'user__username', 'user__email', 'user__first_name', 'user__last_name',
        'stripe_customer_id', 'stripe_subscription_id'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'last_activity', 'total_billed_amount',
        'days_remaining_display', 'effective_limits_display'
    ]
    
    fieldsets = (
        ('User & Plan', {
            'fields': ('user', 'tier', 'status', 'billing_cycle')
        }),
        ('Stripe Integration', {
            'fields': (
                'stripe_customer_id', 'stripe_subscription_id', 
                'stripe_payment_method_id'
            ),
            'classes': ('collapse',)
        }),
        ('Billing Periods', {
            'fields': (
                'trial_start', 'trial_end', 'current_period_start',
                'current_period_end', 'next_billing_date', 'days_remaining_display'
            )
        }),
        ('Cancellation', {
            'fields': ('canceled_at', 'cancellation_reason'),
            'classes': ('collapse',)
        }),
        ('Institutional', {
            'fields': (
                'institution_name', 'institution_domain', 'institutional_discount'
            ),
            'classes': ('collapse',)
        }),
        ('Custom Pricing', {
            'fields': ('custom_price_monthly', 'custom_limits'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'created_at', 'updated_at', 'last_activity', 'total_billed_amount',
                'effective_limits_display'
            ),
            'classes': ('collapse',)
        })
    )
    
    def days_remaining(self, obj):
        return obj.days_remaining()
    days_remaining.short_description = 'Days Remaining'
    
    def monthly_price(self, obj):
        return f"${obj.get_monthly_price()}"
    monthly_price.short_description = 'Monthly Price'
    
    def is_trial_display(self, obj):
        if obj.is_trial():
            return format_html('<span style="color: orange;">Trial</span>')
        return ''
    is_trial_display.short_description = 'Trial'
    
    def days_remaining_display(self, obj):
        days = obj.days_remaining()
        if days <= 7:
            color = 'red'
        elif days <= 30:
            color = 'orange'
        else:
            color = 'green'
        return format_html(f'<span style="color: {color};">{days} days</span>')
    days_remaining_display.short_description = 'Days Remaining'
    
    def effective_limits_display(self, obj):
        limits = obj.get_effective_limits()
        html = '<ul>'
        for key, value in limits.items():
            html += f'<li><strong>{key.replace("_", " ").title()}:</strong> {value}</li>'
        html += '</ul>'
        return format_html(html)
    effective_limits_display.short_description = 'Effective Limits'


@admin.register(UsageTracking)
class UsageTrackingAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'resource_type', 'amount_used', 'unit', 'module',
        'period_start', 'period_end'
    ]
    list_filter = [
        'resource_type', 'module', 'period_start', 'recorded_at'
    ]
    search_fields = ['user__username', 'user__email', 'feature']
    readonly_fields = ['recorded_at']
    date_hierarchy = 'recorded_at'
    
    fieldsets = (
        ('User & Resource', {
            'fields': ('user', 'subscription', 'resource_type', 'amount_used', 'unit')
        }),
        ('Context', {
            'fields': ('module', 'feature', 'project_id')
        }),
        ('Time Period', {
            'fields': ('period_start', 'period_end', 'recorded_at')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        })
    )


@admin.register(QuotaLimit)
class QuotaLimitAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'resource_type', 'usage_display', 'usage_percentage_display',
        'warning_threshold', 'limit_exceeded', 'period_end'
    ]
    list_filter = [
        'resource_type', 'limit_exceeded', 'warning_sent', 'period_end'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'usage_percentage_display']
    
    def usage_display(self, obj):
        return f"{obj.used_amount}/{obj.limit_amount} {obj.unit}"
    usage_display.short_description = 'Usage'
    
    def usage_percentage_display(self, obj):
        percentage = obj.usage_percentage()
        if percentage >= 100:
            color = 'red'
        elif percentage >= obj.warning_threshold:
            color = 'orange'
        else:
            color = 'green'
        return format_html(f'<span style="color: {color};">{percentage:.1f}%</span>')
    usage_percentage_display.short_description = 'Usage %'


@admin.register(BillingHistory)
class BillingHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'transaction_type', 'amount', 'currency', 'status',
        'transaction_date', 'invoice_link'
    ]
    list_filter = [
        'transaction_type', 'status', 'currency', 'transaction_date'
    ]
    search_fields = [
        'user__username', 'user__email', 'stripe_invoice_id',
        'stripe_charge_id', 'invoice_number', 'description'
    ]
    readonly_fields = ['transaction_date']
    date_hierarchy = 'transaction_date'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': (
                'user', 'subscription', 'transaction_type', 'amount', 'currency',
                'status', 'description'
            )
        }),
        ('External References', {
            'fields': (
                'stripe_invoice_id', 'stripe_charge_id', 'invoice_number'
            )
        }),
        ('Period', {
            'fields': ('transaction_date', 'period_start', 'period_end')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        })
    )
    
    def invoice_link(self, obj):
        if obj.stripe_invoice_id:
            return format_html(
                '<a href="https://dashboard.stripe.com/invoices/{}" target="_blank">View in Stripe</a>',
                obj.stripe_invoice_id
            )
        return ''
    invoice_link.short_description = 'Invoice'


@admin.register(InstitutionalLicense)
class InstitutionalLicenseAdmin(admin.ModelAdmin):
    list_display = [
        'institution_name', 'institution_type', 'tier', 'user_count_display',
        'monthly_cost_display', 'is_active', 'end_date'
    ]
    list_filter = [
        'institution_type', 'tier', 'is_active', 'start_date', 'end_date'
    ]
    search_fields = [
        'institution_name', 'domain', 'admin_name', 'admin_email'
    ]
    readonly_fields = ['created_at', 'updated_at', 'monthly_cost_display']
    
    fieldsets = (
        ('Institution Information', {
            'fields': (
                'institution_name', 'institution_type', 'domain'
            )
        }),
        ('License Details', {
            'fields': (
                'tier', 'max_users', 'current_users', 'price_per_user_monthly',
                'minimum_commitment', 'discount_percentage'
            )
        }),
        ('Contact & Admin', {
            'fields': ('admin_name', 'admin_email', 'admin_user')
        }),
        ('Settings', {
            'fields': ('is_active', 'auto_approve_domain')
        }),
        ('Dates & Billing', {
            'fields': (
                'start_date', 'end_date', 'stripe_customer_id',
                'next_billing_date', 'monthly_cost_display'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_count_display(self, obj):
        percentage = (obj.current_users / obj.max_users) * 100 if obj.max_users > 0 else 0
        if percentage >= 90:
            color = 'red'
        elif percentage >= 75:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            f'<span style="color: {color};">{obj.current_users}/{obj.max_users}</span>'
        )
    user_count_display.short_description = 'Users'
    
    def monthly_cost_display(self, obj):
        return f"${obj.get_monthly_cost():.2f}"
    monthly_cost_display.short_description = 'Monthly Cost'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'card_display', 'is_default', 'is_active', 'created_at'
    ]
    list_filter = ['card_brand', 'is_default', 'is_active', 'created_at']
    search_fields = [
        'user__username', 'user__email', 'billing_name',
        'stripe_payment_method_id'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User & Card', {
            'fields': (
                'user', 'stripe_payment_method_id', 'card_brand',
                'card_last4', 'card_exp_month', 'card_exp_year'
            )
        }),
        ('Status', {
            'fields': ('is_default', 'is_active')
        }),
        ('Billing Address', {
            'fields': (
                'billing_name', 'billing_address', 'billing_city',
                'billing_state', 'billing_zip', 'billing_country'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def card_display(self, obj):
        return f"{obj.card_brand.title()} ****{obj.card_last4}"
    card_display.short_description = 'Card'


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'discount_display', 'usage_display',
        'valid_from', 'valid_until', 'is_active'
    ]
    list_filter = [
        'discount_type', 'is_active', 'new_users_only',
        'valid_from', 'valid_until'
    ]
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['created_at', 'usage_display']
    filter_horizontal = ['applicable_tiers']
    
    fieldsets = (
        ('Code Information', {
            'fields': ('code', 'name', 'description')
        }),
        ('Discount Details', {
            'fields': (
                'discount_type', 'discount_value', 'max_uses', 'current_uses'
            )
        }),
        ('Eligibility', {
            'fields': ('applicable_tiers', 'new_users_only')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'usage_display'),
            'classes': ('collapse',)
        })
    )
    
    def discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return f"{obj.discount_value}% off"
        elif obj.discount_type == 'fixed_amount':
            return f"${obj.discount_value} off"
        else:
            return f"{obj.discount_value} extra days"
    discount_display.short_description = 'Discount'
    
    def usage_display(self, obj):
        if obj.max_uses:
            percentage = (obj.current_uses / obj.max_uses) * 100
            return f"{obj.current_uses}/{obj.max_uses} ({percentage:.1f}%)"
        return f"{obj.current_uses}/∞"
    usage_display.short_description = 'Usage'


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'is_active', 'rollout_percentage', 'requires_subscription',
        'created_at'
    ]
    list_filter = [
        'is_active', 'requires_subscription', 'created_at', 'updated_at'
    ]
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['target_tiers', 'target_users']
    
    fieldsets = (
        ('Feature Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Rollout Strategy', {
            'fields': ('rollout_percentage', 'target_tiers', 'target_users')
        }),
        ('Conditions', {
            'fields': ('requires_subscription', 'min_account_age_days')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


# Register additional admin customizations
admin.site.site_header = "SciTeX-Cloud Billing Administration"
admin.site.site_title = "SciTeX Billing Admin"
admin.site.index_title = "Billing & Subscription Management"