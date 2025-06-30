#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SciTeX-Cloud Billing URL Configuration
URL patterns for subscription and billing management
"""

from django.urls import path, include
from . import views

app_name = 'billing'

# Main billing URLs
urlpatterns = [
    # Dashboard and main pages
    path('', views.subscription_dashboard, name='dashboard'),
    path('pricing/', views.pricing_page, name='pricing'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('upgrade/', views.upgrade_subscription, name='upgrade'),
    path('cancel/', views.cancel_subscription, name='cancel'),
    
    # Payment methods
    path('payment-methods/', views.payment_methods, name='payment_methods'),
    path('payment-methods/add/', views.add_payment_method, name='add_payment_method'),
    
    # Usage and analytics
    path('usage/', views.usage_analytics, name='usage_analytics'),
    path('billing-history/', views.billing_history, name='billing_history'),
    
    # Institutional licensing
    path('institutional/', views.institutional_licenses, name='institutional'),
    path('institutional/join/', views.join_institutional_license, name='join_institutional'),
    
    # API endpoints
    path('api/', include([
        path('usage/', views.api_usage_details, name='api_usage'),
        path('quotas/', views.quota_status_api, name='api_quotas'),
        path('feature-access/', views.feature_access_check, name='api_feature_access'),
    ])),
    
    # Webhooks
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    
    # Admin
    path('admin-dashboard/', views.admin_billing_dashboard, name='admin_dashboard'),
]